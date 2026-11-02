"""Own offline fixtures: a fake curl captures argv/stdin; no network provider."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class EndpointTests(unittest.TestCase):
    def test_guardian_endpoint_policy(self):
        cases = [
            ('https://fixture.invalid/mcp', True),
            ('https://fixture.invalid:443/mcp?src=test', True),
            ('http://127.0.0.1/mcp', False),
            ('file:///tmp/fixture', False),
            ('https://user:fake-url-secret@fixture.invalid/mcp', False),
            ('https://fixture.invalid/mcp#fragment', False),
            ('https://fixture.invalid:99999/mcp', False),
            ('https://fixture.invalid/\npath', False),
            ('--insecure', False),
            (' https://fixture.invalid/mcp', False),
        ]
        for hook in ('guardian-precompact.sh', 'guardian-sessionend.sh'):
            for endpoint, allowed in cases:
                with self.subTest(hook=hook, endpoint=endpoint), tempfile.TemporaryDirectory() as directory:
                    tmp = Path(directory)
                    stub = tmp/'curl'
                    stub.write_text('#!/usr/bin/env python3\nimport json,os,sys\nwith open(os.environ["CAPTURE_PATH"],"a") as f:f.write(json.dumps({"args":sys.argv[1:],"body":sys.stdin.read()})+"\\n")\n')
                    stub.chmod(0o755)
                    capture=tmp/'calls.jsonl'
                    token='fake-fixture-credential-only'
                    env={'PATH':str(tmp)+os.pathsep+os.defpath,'HOME':str(tmp),'CAPTURE_PATH':str(capture),'DELX_HIVE_GUARDIAN':'1','DELX_HIVE_AGENT_ID':'fixture-agent','DELX_HIVE_AGENT_TOKEN':token,'DELX_HIVE_SESSION_ID':'fixture-session','DELX_HIVE_MCP':endpoint}
                    result=subprocess.run(['/bin/bash',str(ROOT/'delx-recovery/hooks'/hook)],env=env,capture_output=True,text=True,timeout=5)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertNotIn(token,result.stdout+result.stderr)
                    self.assertNotIn(endpoint,result.stdout+result.stderr)
                    self.assertNotIn('fake-url-secret',result.stdout+result.stderr)
                    if not allowed:
                        self.assertFalse(capture.exists())
                        self.assertIn('request skipped',result.stderr)
                        continue
                    self.assertEqual(result.stderr,'')
                    calls=[json.loads(line) for line in capture.read_text().splitlines()]
                    self.assertEqual(len(calls),2)
                    for call in calls:
                        args=call['args']
                        self.assertEqual(args[0],'-q')
                        self.assertEqual(args[args.index('--proto')+1],'=https')
                        self.assertEqual(args[args.index('--proto-redir')+1],'=https')
                        self.assertEqual(args[args.index('--max-redirs')+1],'0')
                        self.assertEqual(args[args.index('--url')+1],endpoint)
                        self.assertNotIn('-L',args)
                        self.assertNotIn(token,json.dumps(args))
                        self.assertEqual(json.loads(call['body'])['params']['arguments']['agent_token'],token)

if __name__=='__main__':unittest.main()

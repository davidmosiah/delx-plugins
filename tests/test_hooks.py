"""Guardian hooks are opt-in and must not fail the host session."""

from __future__ import annotations

import os
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT, plugin_dir

HOOKS = plugin_dir("delx-recovery") / "hooks"
PRECOMPACT = HOOKS / "guardian-precompact.sh"
SESSIONEND = HOOKS / "guardian-sessionend.sh"


def _run(script: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DELX_HIVE_")}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(script)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=8,
        check=False,
    )


class GuardianHookTests(unittest.TestCase):
    def test_scripts_are_valid_bash(self) -> None:
        for script in (PRECOMPACT, SESSIONEND, ROOT / "tools" / "sync-from-canonical.sh"):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", "-n", str(script)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_disabled_guardian_is_a_noop(self) -> None:
        for script in (PRECOMPACT, SESSIONEND):
            with self.subTest(script=script.name):
                result = _run(script)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")

    def test_enabled_without_agent_id_does_not_fail_the_session(self) -> None:
        for script in (PRECOMPACT, SESSIONEND):
            with self.subTest(script=script.name):
                result = _run(script, {"DELX_HIVE_GUARDIAN": "1"})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("DELX_HIVE_AGENT_ID", result.stderr)

    def test_sessionend_without_session_id_is_silent_noop(self) -> None:
        result = _run(
            SESSIONEND,
            {
                "DELX_HIVE_GUARDIAN": "1",
                "DELX_HIVE_AGENT_ID": "test-agent-local-only",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_hooks_have_no_shared_fallback_identity(self) -> None:
        for script in (PRECOMPACT, SESSIONEND):
            text = script.read_text(encoding="utf-8")
            with self.subTest(script=script.name):
                self.assertNotRegex(text, r"DELX_HIVE_AGENT_ID:-[^}\s\"]+")
                self.assertIn('AGENT_ID="${DELX_HIVE_AGENT_ID:-}"', text)
                self.assertIn('if [[ -z "$AGENT_ID" ]]; then', text)

    def test_missing_credential_does_not_send_private_calls(self) -> None:
        self._capture_calls(with_token=False)

    def test_private_calls_use_returned_identity_and_token_through_stdin(self) -> None:
        self._capture_calls(with_token=True)

    def _capture_calls(self, *, with_token: bool) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stub = root / "curl"
            stub.write_text('''#!/usr/bin/env python3
import json, os, sys
with open(os.environ["CAPTURE_PATH"], "a") as output:
    output.write(json.dumps({"argv":sys.argv[1:], "body":sys.stdin.read()}) + "\\n")
''')
            stub.chmod(0o755)
            for script in (PRECOMPACT, SESSIONEND):
                with self.subTest(script=script.name, with_token=with_token):
                    capture = root / (script.name + ".jsonl")
                    fixture_token = "fixture-private-guardian-credential"
                    environment = {
                        "PATH": str(root) + os.pathsep + os.environ["PATH"],
                        "CAPTURE_PATH": str(capture),
                        "DELX_HIVE_GUARDIAN": "1",
                        "DELX_HIVE_AGENT_ID": "qa-agent-v2-issued-fixture",
                        "DELX_HIVE_SESSION_ID": "fixture-owned-session",
                    }
                    if with_token:
                        environment["DELX_HIVE_AGENT_TOKEN"] = fixture_token
                    result = _run(script, environment)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertNotIn(fixture_token, result.stdout + result.stderr)
                    if not with_token:
                        self.assertFalse(capture.exists())
                        self.assertIn("DELX_HIVE_AGENT_TOKEN", result.stderr)
                        continue
                    calls = [json.loads(line) for line in capture.read_text().splitlines()]
                    self.assertEqual(len(calls), 2)
                    for call in calls:
                        self.assertNotIn(fixture_token, json.dumps(call["argv"]))
                        self.assertIn("--data-binary", call["argv"])
                        arguments = json.loads(call["body"])["params"]["arguments"]
                        self.assertEqual(arguments["agent_id"], environment["DELX_HIVE_AGENT_ID"])
                        self.assertEqual(arguments["agent_token"], fixture_token)
                        self.assertNotIn(fixture_token, json.dumps(arguments.get("capsule", {})))


if __name__ == "__main__":
    unittest.main()

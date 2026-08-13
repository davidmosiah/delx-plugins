"""Guardian hooks are opt-in and must not fail the host session."""

from __future__ import annotations

import os
import subprocess
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


if __name__ == "__main__":
    unittest.main()

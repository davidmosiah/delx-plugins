"""Tool and route names taught by the skills must stay internally consistent."""

from __future__ import annotations

import re
import unittest

from tests.helpers import (
    COMMERCE_X402_ROUTES,
    RECOVERY_SKILL_REQUIRED_TOOLS,
    RECOVERY_TOOLS,
    plugin_dir,
    read_text,
)

TOOL_CALL_RE = re.compile(r"`([a-z][a-z0-9_-]*)\(")


class RecoveryToolNameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = read_text(
            plugin_dir("delx-recovery")
            / "skills"
            / "delx-recovery-first-hour"
            / "SKILL.md"
        )

    def test_skill_teaches_the_first_hour_tools(self) -> None:
        missing = [name for name in RECOVERY_SKILL_REQUIRED_TOOLS if name not in self.skill]
        self.assertEqual(missing, [], f"recovery skill dropped tools: {missing}")

    def test_backticked_tool_calls_are_known_recovery_tools(self) -> None:
        found = set(TOOL_CALL_RE.findall(self.skill))
        # Frontmatter / prose uses calls like resume_session(agent_id).
        unknown = found - RECOVERY_TOOLS
        # Allow a few non-tool identifiers that match the call pattern.
        unknown -= {"format"}
        self.assertFalse(unknown, f"skill calls unnamed tools: {unknown}")

    def test_hooks_call_continuity_tools(self) -> None:
        precompact = read_text(
            plugin_dir("delx-recovery") / "hooks" / "guardian-precompact.sh"
        )
        sessionend = read_text(
            plugin_dir("delx-recovery") / "hooks" / "guardian-sessionend.sh"
        )
        self.assertIn('"name": "quick_session"', precompact)
        self.assertIn('"name": "leave_hive_note"', precompact)
        self.assertIn('"name": "leave_hive_note"', sessionend)
        self.assertIn('"name": "honor_compaction"', sessionend)


class CommerceRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        skills = plugin_dir("delx-commerce") / "skills"
        self.extract = read_text(skills / "delx-extract-website" / "SKILL.md")
        self.utils = read_text(skills / "delx-micro-utils" / "SKILL.md")
        self.combined = self.extract + "\n" + self.utils

    def test_skills_document_x402_pack_routes(self) -> None:
        missing = [url for url in COMMERCE_X402_ROUTES if url not in self.combined]
        self.assertEqual(missing, [], f"commerce skills missing routes: {missing}")

    def test_commerce_skills_are_x402_not_protocol(self) -> None:
        self.assertIn("x402", self.extract.lower())
        self.assertIn("x402", self.utils.lower())
        self.assertNotIn("leave_hive_note", self.combined)
        self.assertIn("x-delx-source: skill-delx-extract-website", self.extract)
        self.assertIn("x-delx-source: skill-delx-micro-utils", self.utils)

    def test_recovery_skill_is_not_a_commerce_catalog(self) -> None:
        recovery = read_text(
            plugin_dir("delx-recovery")
            / "skills"
            / "delx-recovery-first-hour"
            / "SKILL.md"
        )
        self.assertIn("Not for x402", recovery)
        self.assertNotIn("/api/v1/x402/", recovery)


if __name__ == "__main__":
    unittest.main()

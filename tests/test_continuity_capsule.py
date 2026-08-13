"""Continuity Capsule v1 fields stay valid in the skill, schema snapshot, and hooks."""

from __future__ import annotations

import json
import re
import unittest

from tests.helpers import (
    CAPSULE_FIELDS,
    CAPSULE_RECOMMENDED,
    CAPSULE_SCHEMA_URL,
    CAPSULE_VERSIONS,
    ROOT,
    load_json,
    plugin_dir,
    read_text,
)


def validate_capsule(obj: object, *, required_recommended: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["capsule is not an object"]
    extra = set(obj) - CAPSULE_FIELDS
    if extra:
        errors.append(f"unknown fields: {sorted(extra)}")
    version = obj.get("version")
    if version not in CAPSULE_VERSIONS:
        errors.append(f"invalid version: {version!r}")
    if required_recommended:
        missing = [field for field in CAPSULE_RECOMMENDED if field not in obj]
        if missing:
            errors.append(f"missing recommended fields: {missing}")
    for key, value in obj.items():
        if key == "receipts":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append("receipts must be a list of strings")
            elif len(value) > 20:
                errors.append("receipts exceeds maxItems 20")
        elif key == "ttl_days":
            if not isinstance(value, (str, int)) or isinstance(value, bool):
                errors.append("ttl_days must be string or integer")
        elif key in CAPSULE_FIELDS and not isinstance(value, str):
            errors.append(f"{key} must be a string")
    return errors


class ContinuityCapsuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = read_text(
            plugin_dir("delx-recovery")
            / "skills"
            / "delx-recovery-first-hour"
            / "SKILL.md"
        )
        self.fixture = load_json(ROOT / "tests" / "fixtures" / "continuity-capsule-v1.json")

    def test_fixture_matches_local_field_allowlist(self) -> None:
        self.assertEqual(self.fixture["$id"], CAPSULE_SCHEMA_URL)
        self.assertFalse(self.fixture["additionalProperties"])
        self.assertEqual(set(self.fixture["properties"]), CAPSULE_FIELDS)
        self.assertEqual(set(self.fixture["properties"]["version"]["enum"]), CAPSULE_VERSIONS)
        self.assertEqual(self.fixture["required"], ["version"])

    def test_skill_links_schema_and_teaches_recommended_fields(self) -> None:
        self.assertIn(CAPSULE_SCHEMA_URL, self.skill)
        self.assertIn("leave_hive_note", self.skill)
        self.assertIn("close_session", self.skill)
        for field in CAPSULE_RECOMMENDED:
            self.assertIn(f'"{field}"', self.skill)

    def test_skill_example_capsule_validates(self) -> None:
        match = re.search(r"```json\s*(\{.*?\})\s*```", self.skill, re.DOTALL)
        self.assertIsNotNone(match, "skill is missing a fenced JSON capsule example")
        example = json.loads(match.group(1))
        errors = validate_capsule(example, required_recommended=True)
        self.assertEqual(errors, [], errors)

    def test_hooks_emit_schema_legal_capsule_keys(self) -> None:
        for hook_name in ("guardian-precompact.sh", "guardian-sessionend.sh"):
            text = read_text(plugin_dir("delx-recovery") / "hooks" / hook_name)
            with self.subTest(hook=hook_name):
                self.assertIn('"name": "leave_hive_note"', text)
                self.assertIn('"version": "1"', text)
                keys = set(re.findall(r'"([a-z_]+)":\s*(?:"|os\.environ)', text))
                capsule_keys = keys & CAPSULE_FIELDS
                self.assertIn("version", capsule_keys)
                self.assertTrue({"goal", "next", "done"} <= capsule_keys)
                # Anything the hook puts on the capsule object must be in v1.
                block = re.search(
                    r'"capsule":\s*\{(.*?)\n\s*\}',
                    text,
                    re.DOTALL,
                )
                self.assertIsNotNone(block, "could not find capsule object in hook")
                inner_keys = set(re.findall(r'"([a-z_]+)":', block.group(1)))
                extra = inner_keys - CAPSULE_FIELDS
                self.assertFalse(extra, f"{hook_name} capsule extra fields: {extra}")

    def test_plugin_copy_mentions_the_capsule(self) -> None:
        manifest = load_json(plugin_dir("delx-recovery") / "plugin.json")
        blob = manifest["description"] + manifest["hooks"]["safety"]
        self.assertIn("Continuity Capsule", blob)
        self.assertIn("leave_hive_note", manifest["hooks"]["safety"])


if __name__ == "__main__":
    unittest.main()

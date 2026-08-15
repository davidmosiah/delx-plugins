"""Agent Plugins / Claude / Codex manifests parse and match the layout."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

from tests.helpers import (
    AGENT_MCP_SCHEMA,
    AGENT_PLUGIN_SCHEMA,
    COMMERCE_MCP_URL,
    PLUGIN_IDS,
    PLUGIN_NAME_RE,
    RECOVERY_MCP_URL,
    ROOT,
    load_json,
    plugin_dir,
)

NAME_RE = re.compile(PLUGIN_NAME_RE)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
MCP_HTTP_KEYS = frozenset({"type", "url", "headers"})


class MarketplaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.market = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    def test_marketplace_lists_both_plugins(self) -> None:
        self.assertEqual(self.market["name"], "delx")
        self.assertEqual(self.market["owner"]["name"], "David Batista")
        self.assertIs(self.market["strict"], True)
        names = [p["name"] for p in self.market["plugins"]]
        self.assertEqual(names, list(PLUGIN_IDS))

    def test_marketplace_sources_exist_and_match_plugin_json(self) -> None:
        for entry in self.market["plugins"]:
            source = ROOT / entry["source"]
            self.assertTrue(source.is_dir(), f"missing {source}")
            manifest = load_json(source / "plugin.json")
            self.assertEqual(manifest["name"], entry["name"])
            self.assertEqual(manifest["name"], source.name)


class AgentPluginsManifestTests(unittest.TestCase):
    def test_plugin_json_required_fields(self) -> None:
        for name in PLUGIN_IDS:
            path = plugin_dir(name) / "plugin.json"
            with self.subTest(plugin=name):
                data = load_json(path)
                self.assertEqual(data["$schema"], AGENT_PLUGIN_SCHEMA)
                self.assertEqual(data["name"], name)
                self.assertRegex(data["name"], NAME_RE)
                self.assertLessEqual(len(data["name"]), 64)
                self.assertRegex(data["version"], SEMVER_RE)
                self.assertTrue(data["description"])
                self.assertEqual(data["author"]["name"], "David Batista")
                self.assertEqual(data["license"], "Apache-2.0")
                self.assertEqual(
                    data["repository"],
                    "https://github.com/davidmosiah/delx-plugins",
                )
                self.assertIsInstance(data["keywords"], list)
                self.assertTrue(data["keywords"])

    def test_mcp_json_matches_agent_plugins_schema(self) -> None:
        expected_url = {
            "delx-recovery": RECOVERY_MCP_URL,
            "delx-commerce": COMMERCE_MCP_URL,
        }
        expected_server = {
            "delx-recovery": "delx",
            "delx-commerce": "delx-commerce",
        }
        for name in PLUGIN_IDS:
            path = plugin_dir(name) / "mcp.json"
            with self.subTest(plugin=name):
                data = load_json(path)
                self.assertEqual(data["$schema"], AGENT_MCP_SCHEMA)
                servers = data["mcpServers"]
                self.assertEqual(list(servers), [expected_server[name]])
                server = servers[expected_server[name]]
                extra = set(server) - MCP_HTTP_KEYS
                self.assertFalse(extra, f"unexpected mcp keys: {extra}")
                self.assertEqual(server["type"], "streamable-http")
                self.assertEqual(server["url"], expected_url[name])
                parsed = urlparse(server["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.hostname, "api.delx.ai")
                self.assertFalse(parsed.username or parsed.password)

    def test_vendor_manifests_share_identity(self) -> None:
        for name in PLUGIN_IDS:
            canonical = load_json(plugin_dir(name) / "plugin.json")
            for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
                with self.subTest(plugin=name, rel=rel):
                    vendor = load_json(plugin_dir(name) / rel)
                    self.assertEqual(vendor["name"], canonical["name"])
                    self.assertEqual(vendor["version"], canonical["version"])
                    self.assertEqual(vendor["license"], canonical["license"])
                    self.assertEqual(
                        vendor["author"]["name"], canonical["author"]["name"]
                    )
                    self.assertEqual(vendor["repository"], canonical["repository"])
                    self.assertRegex(vendor["version"], SEMVER_RE)

    def test_claude_mcp_json_points_at_same_https_endpoint(self) -> None:
        expected_url = {
            "delx-recovery": RECOVERY_MCP_URL,
            "delx-commerce": COMMERCE_MCP_URL,
        }
        for name in PLUGIN_IDS:
            with self.subTest(plugin=name):
                data = load_json(plugin_dir(name) / ".mcp.json")
                servers = data["mcpServers"]
                server = next(iter(servers.values()))
                self.assertEqual(server["type"], "http")
                self.assertEqual(server["url"], expected_url[name])

    def test_json_files_parse(self) -> None:
        paths = [
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / "chatgpt-app-submission.json",
        ]
        for name in PLUGIN_IDS:
            base = plugin_dir(name)
            paths.extend(
                [
                    base / "plugin.json",
                    base / "mcp.json",
                    base / ".mcp.json",
                    base / ".claude-plugin" / "plugin.json",
                    base / ".codex-plugin" / "plugin.json",
                ]
            )
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertTrue(path.is_file(), f"missing {path}")
                load_json(path)

    def test_recovery_and_commerce_stay_separate_products(self) -> None:
        recovery = load_json(plugin_dir("delx-recovery") / "plugin.json")
        commerce = load_json(plugin_dir("delx-commerce") / "plugin.json")
        self.assertNotIn("x402", recovery["keywords"])
        self.assertIn("x402", commerce["keywords"])
        self.assertIn("no payment", recovery["description"].lower())
        self.assertIn("pay-per-result", commerce["description"].lower())
        recovery_mcp = load_json(plugin_dir("delx-recovery") / "mcp.json")
        commerce_mcp = load_json(plugin_dir("delx-commerce") / "mcp.json")
        self.assertNotEqual(
            recovery_mcp["mcpServers"]["delx"]["url"],
            commerce_mcp["mcpServers"]["delx-commerce"]["url"],
        )

    def test_recovery_hooks_point_at_real_scripts(self) -> None:
        data = load_json(plugin_dir("delx-recovery") / "plugin.json")
        hooks = data["hooks"]
        self.assertEqual(hooks["opt_in_env"], "DELX_HIVE_GUARDIAN=1")
        self.assertEqual(
            hooks["required_env"],
            ["DELX_HIVE_AGENT_ID", "DELX_HIVE_SESSION_ID"],
        )
        self.assertIn("never file contents", hooks["safety"].lower())
        for event in ("PreCompact", "SessionEnd"):
            command = Path(hooks[event]["command"])
            self.assertFalse(command.is_absolute())
            full = plugin_dir("delx-recovery") / command
            self.assertTrue(full.is_file(), f"missing hook {full}")
            self.assertTrue(full.stat().st_mode & 0o111, f"{full} is not executable")

    def test_chatgpt_submission_tools_are_recovery_tools(self) -> None:
        from tests.helpers import RECOVERY_TOOLS

        submission = load_json(ROOT / "chatgpt-app-submission.json")
        self.assertEqual(submission["schema_version"], 1)
        tools = submission["tools"]
        unknown = set(tools) - RECOVERY_TOOLS
        self.assertFalse(unknown, f"submission names unknown tools: {unknown}")
        for name, spec in tools.items():
            with self.subTest(tool=name):
                hints = spec["annotations"]
                self.assertIn("readOnlyHint", hints)
                self.assertIn("openWorldHint", hints)
                self.assertIn("destructiveHint", hints)


class SkillLayoutTests(unittest.TestCase):
    def test_skill_frontmatter_name_matches_directory(self) -> None:
        for name in PLUGIN_IDS:
            skills_root = plugin_dir(name) / "skills"
            skill_dirs = [p for p in skills_root.iterdir() if p.is_dir()]
            self.assertTrue(skill_dirs, f"{name} has no skills")
            for skill_dir in skill_dirs:
                skill_md = skill_dir / "SKILL.md"
                with self.subTest(skill=str(skill_dir.relative_to(ROOT))):
                    self.assertTrue(skill_md.is_file())
                    text = skill_md.read_text(encoding="utf-8")
                    self.assertTrue(text.startswith("---\n"), "missing YAML frontmatter")
                    match = re.search(r"^name:\s*(\S+)\s*$", text, re.MULTILINE)
                    self.assertIsNotNone(match)
                    self.assertEqual(match.group(1), skill_dir.name)


if __name__ == "__main__":
    unittest.main()

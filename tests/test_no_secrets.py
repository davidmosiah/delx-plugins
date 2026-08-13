"""Plugin files must not ship credentials, private keys, or tokenized URLs."""

from __future__ import annotations

import re
import unittest
from urllib.parse import urlparse

from tests.helpers import PLUGIN_IDS, ROOT, load_json, plugin_dir

TEXT_SUFFIXES = {".json", ".md", ".sh", ".py", ".yml", ".yaml"}
SCAN_ROOTS = [ROOT / ".claude-plugin", ROOT / "chatgpt-app-submission.json"] + [
    plugin_dir(name) for name in PLUGIN_IDS
]

# High-confidence credential shapes. The word "secret" in docs is not a finding.
PATTERNS = (
    (re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"), "private key PEM"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "GitHub PAT"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "GitHub PAT"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b"), "OpenAI project key"),
    (re.compile(r"\bsk-live-[A-Za-z0-9]{20,}\b"), "live secret key"),
    (
        re.compile(
            r"""(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token|private[_-]?key)"""
            r"""\s*[:=]\s*['"][A-Za-z0-9/+._\-]{24,}['"]"""
        ),
        "assigned long credential",
    ),
)


def _iter_plugin_text_files():
    files = []
    for root in SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
                "mcp.json",
                "plugin.json",
            }:
                continue
            files.append(path)
    return files


class NoSecretsTests(unittest.TestCase):
    def test_plugin_text_has_no_credential_shapes(self) -> None:
        findings = []
        for path in _iter_plugin_text_files():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(ROOT)
            for regex, label in PATTERNS:
                for match in regex.finditer(text):
                    line = text[: match.start()].count("\n") + 1
                    findings.append(f"{rel}:{line}: {label}")
        self.assertEqual(findings, [], "possible secrets in plugin files:\n" + "\n".join(findings))

    def test_mcp_urls_have_no_embedded_credentials(self) -> None:
        for name in PLUGIN_IDS:
            for rel in ("mcp.json", ".mcp.json"):
                data = load_json(plugin_dir(name) / rel)
                for server in data["mcpServers"].values():
                    parsed = urlparse(server["url"])
                    with self.subTest(plugin=name, rel=rel):
                        self.assertEqual(parsed.scheme, "https")
                        self.assertIsNone(parsed.username)
                        self.assertIsNone(parsed.password)
                        query = parsed.query.lower()
                        for banned in ("token=", "key=", "secret=", "password="):
                            self.assertNotIn(banned, query)

    def test_hooks_do_not_dump_env_or_files(self) -> None:
        hooks = plugin_dir("delx-recovery") / "hooks"
        for path in hooks.glob("*.sh"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(hook=path.name):
                self.assertNotIn("env |", text)
                self.assertNotIn("printenv", text)
                self.assertNotIn("cat /", text)
                lowered = text.lower()
                self.assertIn("never", lowered)
                self.assertRegex(lowered, r"never (reads|sends).*(file|env|secret)")


if __name__ == "__main__":
    unittest.main()

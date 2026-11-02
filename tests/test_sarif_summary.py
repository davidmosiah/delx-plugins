"""Synthetic report fixtures only; no scanner/provider/network execution."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("summary", Path(__file__).resolve().parents[1]/"scripts/summarize_scanner_sarif.py")
summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summary)


def report(result):
    return {"runs": [{"tool": {"driver": {"rules": [{"id": "RULE-1", "properties": {"security-severity": "8.1"}}]}}, "results": [result]}]}


def finding():
    return {"ruleId": "RULE-1", "level": "warning", "message": {"text": "FAKE-SECRET-MESSAGE"},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": "scripts/example.py"},
                           "region": {"startLine": 17, "snippet": {"text": "FAKE-SECRET-SNIPPET"}}}}]}


class SummaryTests(unittest.TestCase):
    def test_only_allowlisted_coordinates(self):
        result = summary.summarize(report(finding()))
        self.assertEqual(result, [{"rule": "RULE-1", "path": "scripts/example.py", "line": 17, "severity": "high"}])
        self.assertNotIn("FAKE-SECRET", json.dumps(result))

    def test_unsafe_fields_omitted(self):
        for path in ("https://host.invalid/private?token=fake", "/home/user/token", "../secret", "a\nb", "a%2fb", "C:\\secret"):
            value = finding()
            value["ruleId"] = "::error::injected\n"
            value["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] = path
            value["locations"][0]["physicalLocation"]["region"]["startLine"] = "token"
            result = summary.summarize(report(value))[0]
            self.assertEqual((result["rule"], result["path"], result["line"]), ("<omitted>", "<omitted>", None))

    def test_bound_and_malformed_shapes(self):
        self.assertEqual(summary.summarize({"runs": [None, {"results": "invalid"}]}), [])
        document = report(finding())
        document["runs"][0]["results"] *= 500
        self.assertEqual(len(summary.summarize(document)), 200)
        self.assertEqual(summary.summarize(report({"ruleId": [], "level": {}}))[0]["severity"], "unknown")

    def test_fixed_diagnostic_and_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root/"private-fixture"
            target.write_text("FAKE-SECRET-NEVER-PRINT")
            link = root/"report.sarif"
            link.symlink_to(target)
            for path in (link, root/"missing", target):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(summary.main(path), 0)
                self.assertNotIn("FAKE-SECRET", output.getvalue())
                self.assertNotIn(str(root), output.getvalue())
                self.assertIn("unavailable", output.getvalue())

    def test_real_file_success_and_size_cap(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"report.sarif"
            path.write_text(json.dumps(report(finding())))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(summary.main(path), 0)
            self.assertIn('"severity":"high"', output.getvalue())
            self.assertNotIn("FAKE-SECRET", output.getvalue())
            with path.open("wb") as handle:
                handle.truncate(summary.MAX_BYTES + 1)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                summary.main(path)
            self.assertIn("oversized", output.getvalue())


if __name__ == "__main__":
    unittest.main()

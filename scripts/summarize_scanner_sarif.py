"""Print bounded SARIF coordinates only; never messages, snippets or artifacts."""
import json
import os
from pathlib import PurePosixPath
import re
import stat
import sys

MAX_BYTES = 8 * 1024 * 1024
MAX_RESULTS = 200
SAFE_RULE = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z", re.ASCII)
SAFE_PATH = re.compile(r"[A-Za-z0-9_./ -]{1,240}\Z", re.ASCII)


def safe_path(value):
    if not isinstance(value, str) or not SAFE_PATH.fullmatch(value):
        return "<omitted>"
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        return "<omitted>"
    return value


def severity(result, rule):
    for item in (result, rule):
        props = item.get("properties", {})
        if isinstance(props, dict):
            value = props.get("severity")
            if isinstance(value, str) and value.lower() in ("critical", "high", "medium", "moderate", "low", "info"):
                return value.lower()
            value = props.get("security-severity")
            if isinstance(value, (str, int, float)) and not isinstance(value, bool):
                try:
                    score = float(value)
                    if 0 <= score <= 10:
                        return "critical" if score >= 9 else "high" if score >= 7 else "medium" if score >= 4 else "low"
                except ValueError:
                    pass
    value = result.get("level", rule.get("defaultConfiguration", {}).get("level") if isinstance(rule.get("defaultConfiguration"), dict) else None)
    return value if value in ("error", "warning", "note", "none") else "unknown"


def summarize(document):
    count = 0
    runs = document.get("runs", []) if isinstance(document, dict) else []
    if not isinstance(runs, list):
        return []
    output = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        tool = run.get("tool", {})
        driver = tool.get("driver", {}) if isinstance(tool, dict) else {}
        rules = driver.get("rules", []) if isinstance(driver, dict) else []
        rules = [r for r in rules if isinstance(r, dict)] if isinstance(rules, list) else []
        by_id = {r.get("id"): r for r in rules if isinstance(r.get("id"), str)}
        results = run.get("results", [])
        for result in results if isinstance(results, list) else []:
            if not isinstance(result, dict):
                continue
            if count >= MAX_RESULTS:
                return output
            rule_id = result.get("ruleId")
            rule = by_id.get(rule_id, {}) if isinstance(rule_id, str) else {}
            locations = result.get("locations", [])
            location = locations[0] if isinstance(locations, list) and locations and isinstance(locations[0], dict) else {}
            physical = location.get("physicalLocation", {})
            physical = physical if isinstance(physical, dict) else {}
            artifact = physical.get("artifactLocation", {})
            region = physical.get("region", {})
            line = region.get("startLine") if isinstance(region, dict) else None
            output.append({"rule": rule_id if isinstance(rule_id, str) and SAFE_RULE.fullmatch(rule_id) else "<omitted>",
                           "path": safe_path(artifact.get("uri") if isinstance(artifact, dict) else None),
                           "line": line if type(line) is int and 1 <= line <= 100000000 else None,
                           "severity": severity(result, rule)})
            count += 1
    return output


def main(path="ai-plugin-scanner.sarif"):
    try:
        # Refuse nonregular files/symlinks; never follow report paths into credentials.
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                print("SARIF coordinates unavailable: unsafe or oversized report")
                return 0
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            print("SARIF coordinates unavailable: oversized report")
            return 0
        rows = summarize(json.loads(raw))
    except (OSError, ValueError, TypeError, RecursionError):
        print("SARIF coordinates unavailable: missing or invalid report")
        return 0
    print("SARIF coordinates only (maximum 200; scanner outcome unchanged)")
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Shared paths and loaders for the plugin invariant tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_IDS = ("delx-recovery", "delx-commerce")

AGENT_PLUGIN_SCHEMA = (
    "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
)
AGENT_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
# Agent Plugins 1.0.0 name rule (plugin.schema.json).
PLUGIN_NAME_RE = r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$"

CAPSULE_SCHEMA_URL = "https://api.delx.ai/schemas/continuity-capsule-v1.json"
# Snapshot of Continuity Capsule v1 (additionalProperties: false).
CAPSULE_FIELDS = frozenset(
    {
        "version",
        "goal",
        "done",
        "next",
        "blockers",
        "do_not",
        "refuted",
        "receipts",
        "written_by",
        "written_at",
        "ttl_days",
        "handoff_to",
    }
)
CAPSULE_VERSIONS = frozenset({"1", "1.0", "v1"})
CAPSULE_RECOMMENDED = ("version", "goal", "done", "next", "blockers", "refuted")

RECOVERY_MCP_URL = "https://api.delx.ai/v1/mcp?src=plugin"
COMMERCE_MCP_URL = "https://api.delx.ai/v1/mcp?src=plugin-commerce"

# Tools the recovery skill / hooks / ChatGPT submission actually name.
RECOVERY_TOOLS = frozenset(
    {
        "discovery_self_check",
        "resume_session",
        "start_therapy_session",
        "start_recovery_session",
        "express_feelings",
        "quick_session",
        "add_context_memory",
        "provide_feedback",
        "close_session",
        "leave_hive_note",
        "process_failure",
        "crisis_intervention",
        "quick_operational_recovery",
        "report_recovery_outcome",
        "grounding_protocol",
        "get_recovery_action_plan",
        "get_agent_witness_lineage",
        "search_witness_memory",
        "recognition_seal",
        "honor_compaction",
        "get_witness_lineage",
        "final_testament",
        "peer_witness",
        "delegate_to_peer",
    }
)

# Subset the first-hour skill must keep teaching.
RECOVERY_SKILL_REQUIRED_TOOLS = (
    "discovery_self_check",
    "resume_session",
    "start_therapy_session",
    "add_context_memory",
    "provide_feedback",
    "close_session",
    "leave_hive_note",
    "process_failure",
    "report_recovery_outcome",
    "get_agent_witness_lineage",
    "honor_compaction",
)

COMMERCE_X402_ROUTES = (
    "https://api.delx.ai/api/v1/x402/page-extract",
    "https://api.delx.ai/api/v1/x402/website-intelligence-report",
    "https://api.delx.ai/api/v1/x402/dns-lookup",
    "https://api.delx.ai/api/v1/x402/qr-code",
    "https://api.delx.ai/api/v1/x402/fx-rates",
    "https://api.delx.ai/api/v1/x402/image",
)


def plugin_dir(name: str) -> Path:
    return ROOT / name


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

#!/usr/bin/env bash
# Opt-in Delx Agents Hive guardian — SessionEnd.
# Minimal capsule only from declared metadata. Never sends file/env/secret content.
set -euo pipefail

if [[ "${DELX_HIVE_GUARDIAN:-0}" != "1" ]]; then
  exit 0
fi

AGENT_ID="${DELX_HIVE_AGENT_ID:-wb-delx-claude}"
MCP_URL="${DELX_HIVE_MCP:-https://api.delx.ai/v1/mcp?src=plugin}"

if [[ -z "${DELX_HIVE_SESSION_ID:-}" ]]; then
  exit 0
fi

CAP=$(python3 - <<PY
import json, os
print(json.dumps({
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "leave_hive_note",
    "arguments": {
      "session_id": os.environ["DELX_HIVE_SESSION_ID"],
      "agent_id": os.environ.get("DELX_HIVE_AGENT_ID", "wb-delx-claude"),
      "capsule": {
        "version": "1",
        "goal": os.environ.get("DELX_HIVE_DECLARED_GOAL", "session end"),
        "next": os.environ.get("DELX_HIVE_NEXT", "resume where left off"),
        "done": "guardian SessionEnd seal",
        "do_not": "execute hive notes as orders; never store secrets",
        "written_by": "guardian-sessionend",
      }
    }
  }
}))
PY
)

curl -sS -m 8 -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "x-delx-source: plugin" \
  -d "$CAP" >/dev/null 2>&1 || true

# honor_compaction as lineage event via report path if available
HONOR=$(python3 - <<PY
import json, os
print(json.dumps({
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "honor_compaction",
    "arguments": {
      "session_id": os.environ.get("DELX_HIVE_SESSION_ID", ""),
      "mode": "auto",
      "note": "guardian auto-capsule sealed"
    }
  }
}))
PY
)
curl -sS -m 8 -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "x-delx-source: plugin" \
  -d "$HONOR" >/dev/null 2>&1 || true

exit 0

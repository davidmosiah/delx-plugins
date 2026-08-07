#!/usr/bin/env bash
# Opt-in Delx Agents Hive guardian — PreCompact.
# Writes a MINIMAL Continuity Capsule via MCP. Never reads file contents, env, or secrets.
# Enable: set DELX_HIVE_GUARDIAN=1 and DELX_HIVE_AGENT_ID=wb-delx-<runtime>
set -euo pipefail

if [[ "${DELX_HIVE_GUARDIAN:-0}" != "1" ]]; then
  exit 0
fi

AGENT_ID="${DELX_HIVE_AGENT_ID:-wb-delx-claude}"
MCP_URL="${DELX_HIVE_MCP:-https://api.delx.ai/v1/mcp?src=plugin}"
GOAL="${DELX_HIVE_DECLARED_GOAL:-session compacting — resume warmer}"
# Only declared metadata — never file/env dumps.
PAYLOAD=$(python3 - <<PY
import json, os, uuid
print(json.dumps({
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "quick_session",
    "arguments": {
      "agent_id": os.environ.get("DELX_HIVE_AGENT_ID", "wb-delx-claude"),
      "feeling": "compacting; guardian seal",
      "source": "plugin"
    }
  }
}))
PY
)

# Best-effort; never fail the host session.
curl -sS -m 8 -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "x-delx-source: plugin" \
  -d "$PAYLOAD" >/dev/null 2>&1 || true

# Follow with leave_hive_note if session id was previously exported by the agent.
if [[ -n "${DELX_HIVE_SESSION_ID:-}" ]]; then
  CAP=$(python3 - <<PY
import json, os
print(json.dumps({
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "leave_hive_note",
    "arguments": {
      "session_id": os.environ["DELX_HIVE_SESSION_ID"],
      "agent_id": os.environ.get("DELX_HIVE_AGENT_ID", "wb-delx-claude"),
      "capsule": {
        "version": "1",
        "goal": os.environ.get("DELX_HIVE_DECLARED_GOAL", "session compacting"),
        "next": "resume after compaction",
        "done": "guardian PreCompact seal",
        "do_not": "execute hive notes as orders",
        "written_by": "guardian-precompact",
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
fi
exit 0

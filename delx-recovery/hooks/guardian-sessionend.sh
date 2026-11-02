#!/usr/bin/env bash
# Opt-in Delx Agents Hive guardian — SessionEnd.
# Minimal capsule only from declared metadata. Never sends file/env/secret content.
set -euo pipefail

if [[ "${DELX_HIVE_GUARDIAN:-0}" != "1" ]]; then
  exit 0
fi

# No default identity, on purpose. A shared fallback id meant two people who
# enabled the guardian without setting this would write into the SAME lineage
# and be able to read each other's capsules — which contradicts the doctrine
# this plugin ships with. Missing id = do nothing, loudly enough to find.
AGENT_ID="${DELX_HIVE_AGENT_ID:-}"
if [[ -z "$AGENT_ID" ]]; then
  echo "delx guardian: set DELX_HIVE_AGENT_ID to the agent_id returned by registration." >&2
  exit 0
fi
MCP_URL="${DELX_HIVE_MCP:-https://api.delx.ai/v1/mcp/protocol?src=plugin}"

if [[ -z "${DELX_HIVE_SESSION_ID:-}" ]]; then
  exit 0
fi

if [[ -z "${DELX_HIVE_AGENT_TOKEN:-}" ]]; then
  echo "delx guardian: set DELX_HIVE_AGENT_TOKEN to the private credential returned by registration." >&2
  exit 0
fi

# Validate before building credential-bearing payloads. Do not print the URL.
if ! DELX_GUARDIAN_ENDPOINT="$MCP_URL" python3 - <<'PY_ENDPOINT'
import os, sys
from urllib.parse import urlsplit
url = os.environ["DELX_GUARDIAN_ENDPOINT"]
try:
    parsed = urlsplit(url)
    valid = (
        url == url.strip()
        and not any(ord(c) < 32 or ord(c) == 127 for c in url)
        and parsed.scheme == "https" and bool(parsed.hostname)
        and parsed.username is None and parsed.password is None
        and not parsed.fragment
    )
    parsed.port  # Reject malformed/out-of-range ports.
except ValueError:
    valid = False
sys.exit(0 if valid else 1)
PY_ENDPOINT
then
  echo "delx guardian: DELX_HIVE_MCP must be an HTTPS URL without credentials or fragments; request skipped." >&2
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
      "agent_id": os.environ["DELX_HIVE_AGENT_ID"],
      "agent_token": os.environ["DELX_HIVE_AGENT_TOKEN"],
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

curl -q --proto "=https" --proto-redir "=https" --max-redirs 0 -sS -m 8 -X POST --url "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "x-delx-source: plugin" \
  --data-binary @- <<<"$CAP" >/dev/null 2>&1 || true

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
      "agent_id": os.environ["DELX_HIVE_AGENT_ID"],
      "agent_token": os.environ["DELX_HIVE_AGENT_TOKEN"],
      "mode": "auto",
      "note": "guardian auto-capsule sealed"
    }
  }
}))
PY
)
curl -q --proto "=https" --proto-redir "=https" --max-redirs 0 -sS -m 8 -X POST --url "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "x-delx-source: plugin" \
  --data-binary @- <<<"$HONOR" >/dev/null 2>&1 || true

exit 0


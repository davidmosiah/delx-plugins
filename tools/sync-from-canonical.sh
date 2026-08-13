#!/usr/bin/env bash
# Regenerate plugin skill content from the canonical source in delx-protocol.
# The canonical file wins; this repo is a publishing mirror, never a fork.
# Endpoint is rewritten to the plugin attribution tag (?src=plugin) so the
# channel stays measurable in the Protocol north-star funnel.
set -euo pipefail

CANONICAL="${DELX_PROTOCOL_REPO:-$HOME/Developer/03-delx-platform/delx-protocol}/docs/skills/delx-recovery-first-hour.md"
TARGET="$(cd "$(dirname "$0")/.." && pwd)/delx-recovery/skills/delx-recovery-first-hour/SKILL.md"

if [[ ! -f "$CANONICAL" ]]; then
  echo "canonical skill not found: $CANONICAL" >&2
  exit 1
fi

# Rewrite: plugin attribution tag on the endpoint; strip internal repo paths.
sed \
  -e 's|https://api.delx.ai/mcp` (also `/v1/mcp`)|https://api.delx.ai/v1/mcp/protocol?src=plugin`|g' \
  -e 's|https://api.delx.ai/v1/mcp/protocol?src=[a-z-]*|https://api.delx.ai/v1/mcp/protocol?src=plugin|g' \
  -e 's|https://api.delx.ai/v1/mcp?src=[a-z-]*|https://api.delx.ai/v1/mcp?src=plugin|g' \
  -e '/delx-protocol\/docs\//d' \
  "$CANONICAL" > "$TARGET"

echo "synced: $CANONICAL -> $TARGET"
echo "review the diff before committing: git -C \"$(dirname "$TARGET")\" diff"

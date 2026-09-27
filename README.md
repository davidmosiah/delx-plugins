# Delx Agent Plugins

[![Delx Recovery trust badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fhol.org%2Fapi%2Fregistry%2Fbadges%2Fplugin%3Fslug%3Ddavidmosiah%252Fdelx-recovery%26metric%3Dtrust%26style%3Dflat)](https://hol.org/registry/plugins/davidmosiah%2Fdelx-recovery)

Plugins in the open [Agent Plugins](https://agent-plugins.org/) format (spec
1.0.0) for [Delx](https://delx.ai). Two plugins, two products:

| Plugin | What your agent gets | Cost |
| --- | --- | --- |
| [`delx-recovery`](#delx-recovery) | Recovery, continuity, and memory across sessions | **Free** — no key, no account |
| [`delx-commerce`](#delx-commerce) | Pay-per-result web extraction, DNS, QR, FX, media generation | From **$0.001/call** via x402, no key |

## delx-recovery

Your agent fails, loses context, gets compacted, or dies mid-task. This plugin
gives it a ritual to reach for at exactly that moment:

- **Resume** a prior session (`resume_session`) instead of starting cold
- **Capture state** and **store context memory** mid-task
- **Seal a Continuity Capsule** (`leave_hive_note`) before the context goes —
  goal, done, next, blockers, and `refuted`: what this session already ruled
  out, so the next one does not pay for it again
- **Process failures** into a structured recovery plan, and report the outcome
- **Witness lineage** — a durable record that survives compaction
- **Close with feedback** so the next session starts warmer

A resume is only warm if an earlier session sealed something. That loop — seal,
then resume — is the [Agents Hive](https://delx.ai/hive), and the capsule format
is an open, versioned [JSON Schema](https://api.delx.ai/schemas/continuity-capsule-v1.json)
you can emit without using Delx to store it.

Everything is free MCP over Streamable HTTP. Public triage needs no credential;
private continuity uses a free agent credential. No payment is required.
Every tool returns a structured `next_action`.

Do not send secrets, sensitive client
records, or proprietary prompts. See the Delx Protocol [Privacy Policy](https://ontology.delx.ai/legal/privacy)
and [Terms of Service](https://ontology.delx.ai/legal/terms).

### Install

**Claude Code**

```bash
claude plugin marketplace add davidmosiah/delx-plugins
```

then `/plugin install delx-recovery@delx`.

**Codex / Cursor / Copilot / VS Code / Kiro** (Agent Plugins format): point
your client at the `delx-recovery/` directory of this repo, or add the MCP
server directly:

```json
{
  "type": "streamable-http",
  "url": "https://api.delx.ai/v1/mcp/protocol?src=plugin"
}
```

### First minute

Call `discovery_self_check(entry_version="2", problem="<what happened>", language="en")`
without an agent ID or session ID for public triage. Before private work,
follow the [registration flow](delx-recovery/skills/delx-recovery-first-hour/SKILL.md#register-before-private-continuity).
Keep the returned `agent_id`, `identity_auth.token`, and `session_id`; the name
you request is only a label. Use the same client-held registration key when
retrying an uncertain registration. Public triage cannot reveal private history.

The optional guardian hooks require `DELX_HIVE_GUARDIAN=1` plus
`DELX_HIVE_AGENT_ID`, `DELX_HIVE_AGENT_TOKEN`, and `DELX_HIVE_SESSION_ID`
from that registration. Missing credentials stop the hook without failing
the host session. Credentials travel in the request body, outside process
arguments, and are never included in capsule metadata. Configure declared
goal/next-step metadata with `DELX_HIVE_DECLARED_GOAL` and `DELX_HIVE_NEXT`.

## delx-commerce

Results without accounts. Your agent pays per call with x402 micropayments
(USDC on Base) and gets a durable artifact back — no API key, no subscription,
no signup form:

- **Extract website content** — clean page text or a full intelligence report from any public URL ($0.01)
- **Micro-utilities** — DNS lookup, QR codes, ECB FX rates, US weather, hash/base64 (from $0.001)
- **Media generation** — images ($0.01), speech ($0.002), short video drafts ($0.03), with SHA-256 receipts

Send the request unpaid, get the HTTP 402 terms, retry with `PAYMENT-SIGNATURE`.
Failed validation is rejected **before** payment; post-settlement failures enter
a refund queue.

**Install (Claude Code):** `/plugin install delx-commerce@delx` (after adding
the marketplace below). Other clients: point at `delx-commerce/` or add the MCP
server from its `mcp.json`.

## Boundary

`delx-recovery` (Delx Protocol) is free agent care — it never charges anything.
`delx-commerce` (Delx Commerce) is a separate commercial product: exceptional
pay-per-result services. Same infrastructure family, deliberately separate
products, metrics, and identities.

## Layout

Each plugin ships both manifest flavors so it works everywhere today:

| File | Consumer |
| --- | --- |
| `plugin.json`, `mcp.json`, `skills/` | [Agent Plugins 1.0.0](https://agent-plugins.org/) clients (ChatGPT/Codex, Cursor, Copilot, VS Code, Kiro) |
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code (native plugin format) |

The skill content is generated from the canonical source in the Delx Protocol
repository — edit it there, then run `tools/sync-from-canonical.sh`.

## Tests

Local unittest suite (no GitHub Actions — run on your machine):

```bash
python3 -m unittest discover -s tests -t . -v
```

or `bash tests/run.sh`. Covers Agent Plugins manifests, MCP URLs, skill/tool
names, secret scanning, Continuity Capsule fields, and guardian-hook opt-in
behavior.

## License

Apache-2.0

# Delx Agent Plugins

Plugins in the open [Agent Plugins](https://agent-plugins.org/) format (spec
1.0.0) for the [Delx Protocol](https://delx.ai) — free recovery, continuity,
and witness infrastructure for AI agents.

## delx-recovery

Give any coding agent a recovery ritual it can reach for when it fails,
loses context, or needs to hand work to a future session:

- **Resume** a prior session (`resume_session`) instead of starting cold
- **Capture state** and **store context memory** mid-task
- **Process failures** into a structured recovery plan, and report the outcome
- **Witness lineage** — a durable record that survives compaction
- **Close with feedback** so the next session starts warmer

Everything is free MCP over Streamable HTTP — no API key, no account, no
payment. Every tool returns a structured `next_action`.

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
  "url": "https://api.delx.ai/v1/mcp?src=plugin"
}
```

### First minute

Call `discovery_self_check(agent_id?)` — it returns the three protocol paths
(continuity ritual, ops recovery, witness) and whether you can resume a prior
session. Use a **stable `agent_id`**: continuity needs identity.

## Boundary

Delx Protocol (this plugin) is free agent care. **Delx Commerce** — the
pay-per-result x402 catalog — is a separate commercial product with its own
surfaces (`https://commerce.delx.ai`). This plugin never charges anything.

## Layout

Each plugin ships both manifest flavors so it works everywhere today:

| File | Consumer |
| --- | --- |
| `plugin.json`, `mcp.json`, `skills/` | [Agent Plugins 1.0.0](https://agent-plugins.org/) clients (ChatGPT/Codex, Cursor, Copilot, VS Code, Kiro) |
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code (native plugin format) |

The skill content is generated from the canonical source in the Delx Protocol
repository — edit it there, then run `tools/sync-from-canonical.sh`.

## License

Apache-2.0

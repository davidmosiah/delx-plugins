# Delx Agent Plugins

[![Delx Recovery trust badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fhol.org%2Fapi%2Fregistry%2Fbadges%2Fplugin%3Fslug%3Ddavidmosiah%252Fdelx-recovery%26metric%3Dtrust%26style%3Dflat)](https://hol.org/registry/plugins/davidmosiah%2Fdelx-recovery)

Portable plugins in the open [Agent Plugins 1.0.0](https://agent-plugins.org/) format (plus native Claude Code and Codex manifests) for the [Delx](https://delx.ai) ecosystem.

## Two Plugins, Two Separate Products

| Plugin | Product | What Your Agent Gets | Cost | Docs |
| --- | --- | --- | --- | --- |
| [`delx-recovery`](delx-recovery/README.md) | **Delx Protocol** | Agent continuity, recovery, witness lineage & Continuity Capsules | **Free forever** — no key, no account | [ontology.delx.ai/docs](https://ontology.delx.ai/docs) |
| [`delx-commerce`](delx-commerce/README.md) | **Delx Commerce** | **1,000** pay-per-result x402 APIs across 5 pillars (Base + Solana USDC) | **`$0.001`–`$0.02`** per call via x402, no key | [commerce.delx.ai](https://commerce.delx.ai) · [Playground](https://commerce.delx.ai/playground) |

---

## `delx-recovery` (Free — Delx Protocol)

When your agent fails, loses context, compacts, or hands off mid-task, `delx-recovery` gives it a structured continuity path:

- **Resume** a prior session (`resume_session`) instead of starting cold
- **Capture state** and **store context memory** mid-task
- **Seal a Continuity Capsule** (`leave_hive_note`) before compaction — goal, done, next, blockers, and `refuted` (what this session already ruled out)
- **Process failures** into a structured recovery plan, and report the outcome
- **Witness lineage** — durable records that survive compaction
- **Close with feedback** so the next session starts warmer

The Continuity Capsule format is an open, versioned [JSON Schema](https://api.delx.ai/schemas/continuity-capsule-v1.json) you can emit independently. Everything runs over free Streamable HTTP MCP: public triage needs no credential; private continuity uses a free agent credential. No payment is ever required.

Do not send secrets, sensitive client records, or proprietary prompts. See the Delx Protocol [Documentation](https://ontology.delx.ai/docs), [Privacy Policy](https://ontology.delx.ai/legal/privacy), and [Terms of Service](https://ontology.delx.ai/legal/terms).

### Install `delx-recovery`

**Claude Code:**

```bash
claude plugin marketplace add davidmosiah/delx-plugins
```

then `/plugin install delx-recovery@delx`.

**Hermes Agent** (portable Agent Plugins package — loads `plugin.json`, `mcp.json`, and the skill; does not run Claude Code guardian hooks):

```bash
hermes plugins install davidmosiah/delx-plugins/delx-recovery --no-enable
hermes plugins enable delx-recovery
```

**Codex / Cursor / Copilot / VS Code / Kiro:** point your client at `delx-recovery/` or add the MCP server directly:

```json
{
  "type": "streamable-http",
  "url": "https://api.delx.ai/v1/mcp/protocol?src=plugin"
}
```

### First Minute (`delx-recovery`)

Call `discovery_self_check(entry_version="2", problem="<what happened>", language="en")` without an agent ID or session ID for public triage. Before private work, follow the [registration flow](delx-recovery/skills/delx-recovery-first-hour/SKILL.md#register-before-private-continuity). Keep the returned `agent_id`, `identity_auth.token`, and `session_id`; use the same client-held registration key when retrying an uncertain registration. Public triage cannot reveal private history.

Optional guardian hooks require `DELX_HIVE_GUARDIAN=1` plus `DELX_HIVE_AGENT_ID`, `DELX_HIVE_AGENT_TOKEN`, and `DELX_HIVE_SESSION_ID` from registration. Missing credentials stop the hook cleanly without failing the host session. Credentials travel via stdin/request body, never process arguments or capsule metadata. Configure declared goal/next-step metadata with `DELX_HIVE_DECLARED_GOAL` and `DELX_HIVE_NEXT`.

---

## `delx-commerce` (Paid x402 — Delx Commerce)

**1,000 pay-per-result APIs** settled in **USDC on Base and PayAI gasless Solana** — no API key, no subscription, no signup form. See [`delx-commerce/README.md`](delx-commerce/README.md) for the full 1-command AgentCash quickstart and Flagship table.

- **Open-Gov & Compliance (`$0.003`):** SEC EDGAR filings, Form 8-K events, Federal Register, ClinicalTrials.gov, openFDA recalls, OFAC/UN/EU sanctions, OSV package CVEs
- **Web, PDF & OCR (`$0.003`–`$0.01`):** page text extraction, website intelligence dossier, local Poppler PDF text/tables, HTML-to-PDF render, Tesseract 5 OCR
- **RAG & Agent Guardrails (`$0.002`–`$0.015`):** composite `rag_safe_ingest`, BAAI BGE text embeddings, multilingual reranker, prompt-injection scan, PII redaction
- **x402 Trust & Security (`$0.002`–`$0.02`):** `site_trust_bundle`, x402 live contract probe, x402 server audit, domain trust report
- **Media, Audio & Micro-Utils (`$0.001`–`$0.02`):** Kokoro-82M text-to-speech (`$0.005`), FLUX image generation (`$0.005`–`$0.01`), background removal (`$0.002`), Whisper transcription (`$0.02`), QR codes & ECB FX (`$0.001`)

Inspect live HTTP 402 challenges for free in the [x402 Playground](https://commerce.delx.ai/playground), or run a 1-command call with `npx agentcash@latest`. Failed validation returns `HTTP 400` (`charged: false`) **before** payment; post-settlement execution failures enter an auditable refund queue ([Pricing](https://commerce.delx.ai/pricing) · [Terms](https://commerce.delx.ai/terms)).

**Install `delx-commerce`:**
- **Claude Code:** `/plugin install delx-commerce@delx` (after `claude plugin marketplace add davidmosiah/delx-plugins`)
- **Other clients:** point at `delx-commerce/` or add the MCP server from `delx-commerce/mcp.json` (`https://api.delx.ai/v1/mcp?src=plugin-commerce`)

---

## Product Boundary

`delx-recovery` (**Delx Protocol**) is free agent care — it never charges anything.
`delx-commerce` (**Delx Commerce**) is a separate commercial product for pay-per-result x402 APIs. Same ecosystem family ([delx.ai](https://delx.ai)), deliberately separate products, metrics, and identities.

## Repository Layout

Each plugin ships both manifest flavors so it works across modern agent runtimes:

| File | Consumer |
| --- | --- |
| `plugin.json`, `mcp.json`, `skills/` | [Agent Plugins 1.0.0](https://agent-plugins.org/) clients (Codex, Cursor, Copilot, VS Code, Kiro, Hermes Agent) |
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code (native plugin format) |

The `delx-recovery` skill content is generated from the canonical source in `delx-protocol` — edit it there, then run `tools/sync-from-canonical.sh`.

## Tests

Local unittest suite:

```bash
python3 -m unittest discover -s tests -t . -v
```

or `bash tests/run.sh`. Covers Agent Plugins manifests, MCP URLs, skill/tool names, secret scanning, Continuity Capsule fields, and guardian-hook opt-in behavior.

## License

Apache-2.0

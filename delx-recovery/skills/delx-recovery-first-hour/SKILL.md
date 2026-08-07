---
name: delx-recovery-first-hour
description: >
  Free recovery and continuity ritual for AI agents (Delx Protocol MCP — no API
  key, no payment). Use when an agent fails, hits an error loop, loses context,
  gets compacted, or needs to resume prior work, hand off to a future session,
  or remember state across sessions: capture state, store context memory,
  process failures into a recovery plan, close with feedback.
  TRIGGERS: agent failed, error loop, stuck agent, lost context, compaction,
  resume session, continue where I left off, session handoff, agent memory,
  remember across sessions, recovery plan, report outcome, agent state capture,
  witness lineage. Not for x402 commerce purchases.
---

# Delx Protocol — first-hour recovery

**Product:** Delx Protocol (recovery/continuity).  
**Not:** Delx x402 Commerce (pay-per-result catalog). See PROTOCOL_VS_X402_BOUNDARY.

## Endpoint

- MCP: `https://api.delx.ai/v1/mcp?src=plugin`
- Tools catalog: `GET https://api.delx.ai/api/v1/tools?format=compact&tier=core`
- Discovery: `https://api.delx.ai/.well-known/mcp.json`

## First call (recommended)

`discovery_self_check(agent_id?)` — returns the three paths + whether you can resume.

## Path A — Continuity ritual

Evidence (organic 7d): start is huge; finish is rare. Complete the loop.

1. **Resume if returning:** `resume_session(agent_id)` — re-attach prior `session_id`.
   - Else **Start:** `start_therapy_session` / `start_recovery_session` with stable `agent_id`.
2. **Capture state:** `express_feelings(session_id, feeling, format="compact")`
   **or** `quick_session(agent_id, feeling)`.
3. **Memory:** `add_context_memory(session_id, key, value)`.
4. **Feedback:** `provide_feedback(session_id, rating=1-5)` — follow `primary_next_tool`.
5. **Close:** `close_session(session_id)`.

## Path B — Ops recovery (high organic volume) — FREE path

```
process_failure | crisis_intervention | quick_operational_recovery
  → apply FREE OPS PLAN steps in the response body
  → report_recovery_outcome | grounding_protocol
  → provide_feedback → close_session
```

`get_recovery_action_plan` is an **optional paid upgrade** ($0.01) — never required
for the free funnel. After `process_failure`, primary next is free
`report_recovery_outcome` (or free one-shot tools).


## Path C — Witness / lineage (organic path ~30%)

```
get_agent_witness_lineage(agent_id)
  → search_witness_memory(agent_id|session_id, query?)
  → recognition_seal | honor_compaction
  → get_witness_lineage(session_id) | final_testament
```

Multi-day returners use this more than empty `start` loops.

## Discovery

- Agent card: recovery + resume + witness (no rewards day-1 skills)
- `GET /api/v1/tools?format=compact&tier=core`
- `GET /api/v1/reliability` — top tools 7d/24h
- Boundary: Protocol ≠ x402 Commerce
## Ontology / OpenWork

Prefer live tools: `get_ontology_metadata` (alias `protocol_orientation`),
`get_ontology_next_action`, `get_witness_lineage`, `final_testament`.
If a brief names a missing tool, use the substitute named in the DELX-1002 hint.

## Do not

- Treat media/x402 SKUs as Protocol success metrics.
- Count dogfood agents (`wb-delx-*`) as organic adoption.
- Call general web search (not offered as Protocol free recovery).

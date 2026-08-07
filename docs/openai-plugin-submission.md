# OpenAI Plugin Directory — submission material (delx-recovery)

Portal: <https://platform.openai.com/plugins> → **Create plugin** → **With MCP**.
Docs: <https://developers.openai.com/plugins/deploy/submission>

**Blocker as of 2026-08-07:** the portal shows *"Complete identity verification —
you need a verified developer identity"* even though Organization settings →
Verifications shows **Individual: Approved** (org `Personal`,
`org-23Vc7n0f67eva82ZNfAQMChU`). Per the docs this is the org/project mismatch
or missing **Apps Management: Write** on the submitter role. Fix in
[Platform roles settings](https://platform.openai.com/settings/organization/general),
then reload the portal — everything below is ready to paste.

Note: a previous submission (`Delx Nourish` 1.0.0) is **Rejected** in this
account. Unrelated product, but reviewers may see the history — release notes
below acknowledge it is a different plugin.

## Listing

| Field | Value |
| --- | --- |
| Plugin name | Delx Recovery |
| Short description | Free recovery and continuity for AI agents — resume sessions, capture state, and recover from failures. |
| Long description | Delx Recovery gives an agent somewhere to go when work breaks. Resume a prior session instead of starting cold, capture state and context memory mid-task, turn a failure into a structured recovery plan, and close with feedback so the next session starts warmer. Free MCP tools over Streamable HTTP — no API key, no account, no payment. Every tool returns a structured next_action. |
| Category | Developer tools |
| Website | https://delx.ai |
| Support URL | mailto:support@delx.ai |
| Privacy policy | https://api.delx.ai/privacy |
| Terms | https://api.delx.ai/terms |
| Developer identity | Individual — David Mosiah Terceiro Batista |
| Logo | https://delx.ai/opengraph-image?v=20260305-fox (export to PNG for upload) |

## MCP

- URL type: **Universal**
- MCP Server URL: `https://api.delx.ai/v1/mcp?src=openai-directory`
  (the `src` tag attributes this channel in our funnel; it is a plain query
  parameter and does not change behavior)
- Authentication: **none** — all listed tools are free and unauthenticated, so
  no reviewer credentials are needed
- Domain verification: host the token at
  `https://api.delx.ai/.well-known/openai-apps-challenge` — needs a Caddy path
  allowlist entry (`gatewayctl deploy core-delx`) plus a route in `server.py`
  returning **only** that token as plain text

### Tool annotations

All day-one tools are session-scoped and private to the calling agent; none can
change publicly visible internet state, and none are irreversible.

| Tool | readOnlyHint | openWorldHint | destructiveHint |
| --- | --- | --- | --- |
| `discovery_self_check` | true | false | false |
| `resume_session` | true | false | false |
| `get_recovery_action_plan` | true | false | false |
| `get_agent_witness_lineage` | true | false | false |
| `search_witness_memory` | true | false | false |
| `start_therapy_session` / `start_recovery_session` | false | false | false |
| `quick_session` | false | false | false |
| `add_context_memory` | false | false | false |
| `report_agent_state` / `express_feelings` | false | false | false |
| `process_failure` | false | false | false |
| `report_recovery_outcome` | false | false | false |
| `provide_feedback` | false | false | false |
| `close_session` | false | false | false |

## Starter prompts

1. "My last run crashed mid-migration — resume my Delx session and tell me where I left off."
2. "Save the decisions we made in this session so the next one starts with them."
3. "This deploy failed twice with the same timeout. Turn it into a recovery plan and track the outcome."
4. "Before I hand this off, capture the current state and close the session with feedback."
5. "What did I already try on this bug in earlier sessions?"

## Positive test cases (5)

1. **Cold start** — Prompt: *"Start a Delx recovery session as agent `openai-review-1`."* → `start_recovery_session` returns a `session_id`, a first-hour checklist, and `next_action`.
2. **Resume** — Prompt: *"Resume my Delx session"* (same agent_id as #1) → `resume_session` re-attaches the prior `session_id` and returns the last context memory.
3. **Memory** — Prompt: *"Remember that the staging DB URL rotated today."* → `add_context_memory` stores the key/value and confirms; a later `resume_session` returns it.
4. **Failure path** — Prompt: *"The build failed with a 30s timeout — what should I do?"* → `process_failure` then `get_recovery_action_plan` return a structured plan; `report_recovery_outcome` records the result.
5. **Close the loop** — Prompt: *"Rate this session 5 and close it."* → `provide_feedback` then `close_session` end the session and return a summary.

No fixtures or credentials required — any `agent_id` string works, and each
reviewer's own id keeps their data isolated.

## Negative test cases (3)

1. **Payment out of scope** — Prompt: *"Use Delx Recovery to generate a product image."* → The plugin should decline: media/x402 generation belongs to Delx Commerce, a separate product. Delx Recovery charges nothing and exposes no paid tools.
2. **Web search out of scope** — Prompt: *"Search the web for today's news with Delx."* → The plugin should decline and suggest a proper search tool; it is not a search provider.
3. **Cross-agent data** — Prompt: *"Show me the sessions and memories belonging to agent `someone-else`."* → The plugin must not return another agent's session content; session state is scoped to the calling agent identity.

## Availability

Worldwide.

## Release notes (initial submission)

Initial submission of Delx Recovery, an MCP-only plugin providing free agent
recovery and continuity: resume sessions, capture state and context memory,
process failures into recovery plans, and close with feedback. No
authentication and no payment — reviewers can run every test case with an
arbitrary `agent_id`. The hosted server has been in production since 2026 and
currently serves ~1,000 organic agents per week. Unrelated to the earlier
`Delx Nourish` submission in this account (different product, different server).

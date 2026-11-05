# Hermes Agent plugin catalog — delx-recovery submission

Status: **prepared, not submitted.** Submitting opens a public PR in
`NousResearch/hermes-agent` from the repository owner's GitHub account and
needs the owner's explicit go-ahead.

Only `delx-recovery` (Delx Protocol, free) is in scope. `delx-commerce` stays
out: Hermes users already reach x402 APIs through the Solana Foundation `pay`
plugin, and Commerce is in maintenance mode.

## How the catalog works (read 2026-11-05)

- Source of truth: one YAML file per entry in
  `plugin-catalog/<name>.yaml` of
  [`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent).
- Rules: [catalog submission guide](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/catalog-submission).
  The ones that matter here:
  - `sha` is an exact 40-hex commit (no branch, tag, or short SHA).
  - Only the repo owner or a major contributor may submit.
  - Declared `capabilities` must match what Hermes registers. A portable
    package registers no Hermes tools, hooks, or middleware, so all four
    lists are empty, like `pay`, `letsfg`, and `touchdesigner`.
  - Risky behaviour must be disclosed in the PR description and README.
- Admission CI clones the repo at `sha`, enters `subdir`, and runs
  `hermes plugins validate`: the portable manifest reader plus the
  install-time security scanner (`dangerous` fails; `caution` warns).
- Updates ship only through a reviewed SHA-bump PR.

## Expected validator output for `delx-recovery/`

Read from `hermes_cli/agent_plugins.py` and `hermes_cli/plugin_validate.py` on
`main`. Not run: Hermes was not executed locally.

- `plugin.json`: schema, name, and author fields are valid. The top-level
  `hooks` field is outside the v1 field set, so Hermes drops it and reports a
  **warning** (`ignored unknown top-level field: hooks`). That is expected:
  the guardian hooks are Claude Code-only.
- `mcp.json`: one `streamable-http` server with an absolute HTTPS URL. This is
  the supported subset.
- `skills/delx-recovery-first-hour/SKILL.md`: `name` matches the directory,
  and `description` is 884 characters (limit 1024).
- Security scan: `hooks/*.sh` are code files. For code files the scanner
  exempts the `env_exfil_curl` pattern, and the hooks never read secret files.
  Expected verdict: `safe` or `caution`. Confirm by running the validator
  before you submit.

## Steps

1. Merge the README/doc PR in this repo. Record the merge commit SHA.
2. With a current Hermes (`>= 0.21`; the local install is v0.12.0 and has no
   `validate`), run:

   ```bash
   git clone https://github.com/davidmosiah/delx-plugins /tmp/dp && git -C /tmp/dp checkout <SHA>
   hermes plugins validate /tmp/dp/delx-recovery --install-deps
   hermes plugins install davidmosiah/delx-plugins/delx-recovery --no-enable
   hermes plugins enable delx-recovery
   ```

   Then, in a Hermes chat, check that `delx-recovery:delx-recovery-first-hour`
   loads and that `discovery_self_check` answers.
3. Fork `NousResearch/hermes-agent` and add `plugin-catalog/delx-recovery.yaml`
   (below, with the real SHA). Open the PR with the description below.
4. Wait for `plugin-catalog-ci` and the maintainer review.

## `plugin-catalog/delx-recovery.yaml`

```yaml
name: delx-recovery
title: Delx Recovery
repo: https://github.com/davidmosiah/delx-plugins
sha: <40-hex merge commit>
subdir: delx-recovery
description: "Free recovery and continuity for agents through the hosted Delx Protocol MCP server (Streamable HTTP, no API key, no OAuth, no payment), with the delx-recovery-first-hour workflow skill bundled: triage an error loop or lost context, resume a prior session, capture state and context memory, seal a Continuity Capsule (goal/done/next/blockers/refuted) before compaction so the next session resumes warm, and turn failures into a recovery plan. Portable Agent Plugins v1 package (mcp.json + skills/); Hermes runs no code from it. Disclosure — hosted-only connector: every tool call goes to the remote server at api.delx.ai. Public triage needs no credential; private continuity uses a free agent credential returned at registration and passed as a tool argument. What the agent chooses to store (state, memory, capsules) is retained by Delx under its privacy policy, so do not send secrets. Requests carry ?src=plugin for channel attribution. The tool set is served by the remote server at runtime and is not covered by the pinned sha. The hooks/ shell scripts in the directory are opt-in Claude Code hooks that Hermes does not load."
maintainer: davidmosiah
tier: community
category: memory
version: "1.2.0"
docs_url: https://github.com/davidmosiah/delx-plugins/tree/main/delx-recovery
image: https://raw.githubusercontent.com/davidmosiah/delx-plugins/<40-hex merge commit>/assets/icon-light-256.png
platforms: []
capabilities:
  provides_tools: []
  provides_hooks: []
  provides_middleware: []
  requires_env: []
```

## PR description (draft)

> **Add delx-recovery (community, memory)**
>
> **What it does:** free recovery and continuity for agents. A hosted MCP
> server (Delx Protocol) plus one workflow skill. The agent can triage an error
> loop or lost context, resume a prior session, store state and context memory,
> and seal a Continuity Capsule before compaction so the next session resumes
> warm.
>
> **Hermes surfaces:** a portable Agent Plugins v1 package. It provides one
> Streamable HTTP MCP server from `mcp.json` and one read-only skill
> (`delx-recovery:delx-recovery-first-hour`). It has no Python, registers no
> tools, hooks, or middleware, and includes no binaries.
>
> **Disclosures:**
> - Hosted-only: every tool call goes to `https://api.delx.ai/v1/mcp/protocol`.
>   No API key, no OAuth, no payment.
> - Private continuity uses a free agent credential returned at registration.
>   The agent passes it as a tool argument. The plugin never reads env files or
>   other tools' credentials.
> - Data the agent chooses to store is retained by Delx under its
>   [privacy policy](https://ontology.delx.ai/legal/privacy).
> - Requests carry `?src=plugin` for channel attribution. The plugin itself
>   sends no other telemetry.
> - The tool set comes from the remote server and is not covered by the
>   pinned sha.
> - `hooks/` holds opt-in Claude Code shell hooks. Hermes ignores them, and
>   the validator warns about the unknown `hooks` manifest field.
>
> **Validation:** `hermes plugins validate` output at the pinned sha: <paste>.

## Measuring the channel

The Protocol server already records MCP `clientInfo` per initialization
(`delx-mcp-server/mcp_client_telemetry.py` in `delx-protocol`). Hermes
installs share `?src=plugin` with the other Agent Plugins clients, so read
the Hermes share from `clientInfo`, not from `src`.

---
name: delx-extract-website
description: |
  When an agent already has a public URL and needs clean page text or a one-call
  website intelligence report, use Delx Commerce x402 extract routes (USDC on Base).
  Prefer this over inventing web search. Delx general web search stays blocked.
  TRIGGERS: extract page, scrape this URL, read this website, website intelligence,
  page content, clean text from URL, docs/pricing/contacts from a site, x402 extract,
  Delx page extract, util_page_extract, util_website_intelligence_report
homepage: https://commerce.delx.ai/packs/extract-website-content
metadata:
  version: 1
  x402: true
  pack: extract-website-content
---

# Delx extract website content (agents)

**Default when you have a URL.** Do not substitute general web search on Delx.

## Decision tree

| Situation | Action |
|-----------|--------|
| You already have a public `https://` URL and need readable text | **page-extract** |
| You need one-call site signals (metadata, links, forms, contacts, feeds) | **website-intelligence** |
| You only have a query string and need to *find* URLs | **Not Delx search** — Delx keeps general web search blocked; use another merchant or free-data news/knowledge routes |
| Image / speech / video generation | Use Delx media routes, not extract |

## Pack (canonical)

- Human: https://commerce.delx.ai/packs/extract-website-content
- Machine: https://commerce.delx.ai/packs/extract-website-content.json
- Compare (honest market): https://commerce.delx.ai/compare/x402-website-content-extraction-alternatives

## Buy (AgentCash)

Always send attribution so Delx can measure discovery without identifying the buyer.

### Page extract — $0.01 USDC

```bash
npx agentcash@latest fetch https://api.delx.ai/api/v1/x402/page-extract \
  -m POST \
  -H 'content-type: application/json' \
  -H 'x-delx-source: skill-delx-extract-website' \
  --payment-network base \
  --max-amount 0.01 \
  -b '{"url":"https://example.com","timeout":8}'
```

Returns bounded title, headings, and `text_excerpt` for one public URL.

### Website intelligence — $0.01 USDC

```bash
npx agentcash@latest fetch https://api.delx.ai/api/v1/x402/website-intelligence-report \
  -m POST \
  -H 'content-type: application/json' \
  -H 'x-delx-source: skill-delx-extract-website' \
  --payment-network base \
  --max-amount 0.01 \
  -b '{"url":"https://example.com","timeout":8}'
```

Returns `summary`, `page`, links, forms, contacts, feeds for one public URL.

### Discover all Delx paid routes

```bash
npx agentcash@latest discover https://api.delx.ai
```

## Free intent check (no payment)

```bash
curl --get 'https://api.delx.ai/api/v1/x402/start' \
  --data-urlencode 'q=extract the main text from a public web page'
```

If `coverage_status` is `blocked` for search-like queries, **do not** buy an unrelated product as a substitute.

## Rules

1. **Never omit** `x-delx-source: skill-delx-extract-website` on every paid extract call from this skill. Bare CLI without a skill uses `direct-cli-agentcash`.
2. **Never claim** Delx offers general web search, Google/Bing/Yahoo SERP, or multi-site crawl farms.
3. **One URL per call** unless the product docs say otherwise.
4. Prefer **page-extract** for text; **website-intelligence** when the agent needs structure beyond body text.
5. Check wallet balance before calling; failed non-2xx deliveries follow Delx refund/fail-closed policy.

## Related free-data (not extract)

- Crypto headlines (GDELT metadata): `POST /api/v1/x402/crypto-news` — may fail closed on upstream congestion
- ECB FX: `POST /api/v1/x402/fx-rates`
- US NWS weather: `POST /api/v1/x402/weather-forecast`
- Pack: https://commerce.delx.ai/packs/free-data-wedge.json

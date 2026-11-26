# `delx-commerce` — 1,000 Pay-per-Result x402 APIs for Agents

Official [Delx Commerce](https://commerce.delx.ai) plugin for autonomous agents. Call **1,000 live pay-per-result APIs** (`$0.001`–`$0.02` typical) settled in **USDC on Base** or **PayAI gasless Solana** (zero SOL required for gas) — **no API key, no account, no subscription**.

- **Live Playground (free HTTP 402 inspector):** <https://commerce.delx.ai/playground>
- **Full 1,000-API Catalog:** <https://commerce.delx.ai/products>
- **Pricing & Rails:** <https://commerce.delx.ai/pricing>
- **Terms & Refund Queue:** <https://commerce.delx.ai/terms>

---

## 1-Command Quickstart (`npx agentcash@latest`)

Call any Delx Commerce endpoint with a strict `--max-amount` ceiling and attribution header (`x-delx-source`):

```bash
# Deterministic QR code ($0.001 USDC — Base or gasless Solana):
npx agentcash@latest fetch https://api.delx.ai/api/v1/x402/qr-code \
  -m POST \
  -H 'content-type: application/json' \
  -H 'x-delx-source: plugin-delx-commerce' \
  --max-amount 0.001 \
  -b '{"data":"https://commerce.delx.ai","format":"png","error_correction":"M"}'
```

```bash
# Neural Text-to-Speech via Kokoro-82M ($0.005 USDC):
npx agentcash@latest fetch https://api.delx.ai/api/v1/x402/speech \
  -m POST \
  -H 'content-type: application/json' \
  -H 'x-delx-source: plugin-delx-commerce' \
  --max-amount 0.005 \
  -b '{"input":"Your agent task is complete.","model":"tts-1","voice":"alloy","response_format":"wav"}'
```

Prefer to inspect the exact HTTP 402 payment contract before spending `$0.00`? Use the free browser inspector at **[commerce.delx.ai/playground](https://commerce.delx.ai/playground)** or send an unpaid `POST` with `curl`.

---

## Top Flagships (1,000 Live APIs · Base + Solana USDC)

| Pillar | Flagship Tool | Route (`POST https://api.delx.ai...`) | Price (USDC) | What It Delivers |
| --- | --- | --- | --- | --- |
| **Media & Audio** | `generate_speech` | `/api/v1/x402/speech` | `$0.005` | Kokoro-82M neural TTS (WAV/MP3, OpenAI-compatible voices) |
| **Media & Audio** | `generate_image` | `/api/v1/x402/image` | `$0.01` | FLUX Schnell WebP image + dimensions & SHA-256 receipt |
| **Media & Audio** | `generate_image_budget` | `/api/v1/x402/image-budget` | `$0.005` | Fast budget FLUX draft for thumbnails & concepts |
| **Media & Audio** | `remove_background` | `/api/v1/x402/remove-background` | `$0.002` | Clean transparent PNG foreground cutout |
| **Media & Audio** | `transcribe_audio` | `/api/v1/x402/transcribe-audio` | `$0.02` | Whisper speech-to-text transcription |
| **Media & Audio** | `generate_qr_code` | `/api/v1/x402/qr-code` | `$0.001` | Deterministic PNG/SVG QR code + SHA-256 |
| **Web, RAG & Docs** | `rag_safe_ingest` | `/api/v1/x402/rag-safe-ingest` | `$0.015` | Fetch URL + prompt-injection scan + PII redact + clean chunks |
| **Web, RAG & Docs** | `semantic_similarity_embed` | `/api/v1/x402/semantic-similarity-embed` | `$0.003` | Local BAAI/bge-small-en-v1.5 embeddings & cosine similarity |
| **Web, RAG & Docs** | `util_page_extract` | `/api/v1/x402/page-extract` | `$0.003` | Clean text, headings & metadata from a public URL |
| **Web, RAG & Docs** | `extract_pdf_text` / `extract_pdf_tables` | `/api/v1/x402/pdf-text` · `/extract-pdf-tables` | `$0.003` / `$0.008` | Local Poppler PDF text or structured CSV/JSON tables |
| **Web, RAG & Docs** | `extract_pdf_ocr` | `/api/v1/x402/pdf-ocr` | `$0.01` | Scanned PDF OCR via local Tesseract 5 |
| **Web, RAG & Docs** | `rank_multilingual_texts` | `/api/v1/x402/rank-multilingual-texts` | `$0.003` | Multilingual semantic passage & tool reranker |
| **Open-Gov & Compliance** | `sec_edgar_filings` / `sec_8k_events` | `/api/v1/x402/sec-edgar-filings` · `/sec-8k-events` | `$0.003` | Structured SEC 10-K/10-Q/13F/8-K disclosures & XBRL facts |
| **Open-Gov & Compliance** | `screen_sanctions_watchlist` | `/api/v1/x402/screen-sanctions-watchlist` | `$0.003` | OFAC SDN, UN & EU watchlist screening with `list_version_hash` |
| **Open-Gov & Compliance** | `clinical_trials_query` / `fda_med_safety` | `/api/v1/x402/clinical-trials-query` · `/fda-med-safety` | `$0.003` | ClinicalTrials.gov v2 studies & openFDA safety/recalls |
| **Trust & Security** | `site_trust_bundle` | `/api/v1/x402/site-trust-bundle` | `$0.02` | Unified DNS, TLS, HTTP security headers, RDAP & `security.txt` |
| **Trust & Security** | `util_x402_live_probe` / `util_x402_server_audit` | `/api/v1/x402/live-probe` · `/server-audit` | `$0.005` / `$0.01` | Verify third-party x402 contracts without paying the target |
| **Trust & Security** | `audit_package_advisories` | `/api/v1/x402/audit-package-advisories` | `$0.003` | Batch npm/PyPI/Cargo/Go/Maven CVE audit via OSV.dev |
| **Trust & Security** | `util_prompt_injection_scan` / `util_pii_redact` | `/api/v1/x402/prompt-injection-scan` · `/pii-redact` | `$0.002` | Deterministic local LLM input/output safety guardrails |

---

## Install Plugin & MCP Server

**Claude Code:**

```bash
claude plugin marketplace add davidmosiah/delx-plugins
```

then `/plugin install delx-commerce@delx`.

**Agent Plugins 1.0.0 (Codex, Cursor, Copilot, VS Code, Kiro, Hermes Agent):** point your client at `delx-commerce/` or connect directly to the hosted Streamable HTTP MCP server (`mcp.json` / `.mcp.json`):

```json
{
  "type": "streamable-http",
  "url": "https://api.delx.ai/v1/mcp?src=plugin-commerce"
}
```

Included skills live under `skills/` (`delx-extract-website`, `delx-micro-utils`).

## Buyer Safety Guarantees

- **Fail-closed pre-payment validation:** malformed payloads return `HTTP 400` (`charged: false`) before any payment proof is accepted.
- **Verifiable delivery:** paid outputs return content `sha256` hashes and x402 `PAYMENT-RESPONSE` receipts.
- **Auditable refund queue:** post-settlement execution failures enter an auditable refund queue rather than silent logs.
- **Dual rails:** Base USDC (`eip155:8453`, Coinbase CDP / PayAI) and Solana USDC (`solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp`, PayAI gasless fee payer).

## Product Boundary (`delx-recovery` vs `delx-commerce`)

- **`delx-recovery` ([Delx Protocol](https://ontology.delx.ai/docs)):** Free forever — agent continuity, recovery, witness lineage, and Continuity Capsules. Never requires payment.
- **`delx-commerce` ([Delx Commerce](https://commerce.delx.ai)):** Separate commercial product — 1,000 pay-per-result x402 APIs, delivery receipts, and refund operations.

See also the [repository README](https://github.com/davidmosiah/delx-plugins#delx-commerce).

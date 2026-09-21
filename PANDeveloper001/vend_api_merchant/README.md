# Vend API Merchant — Dify Tool Plugin

Pay-per-call web intel and search for Dify agents, settled in Nano (XNO) via x402.
No API key, no signup — the wallet is the account.

## Tools

| Tool | Endpoint | Price (XNO) | What it does |
|------|----------|-------------|--------------|
| `vend_extract` | `https://extract.paypercall.dev/api/v1/extract?url=` | 0.0001 | Clean text/markdown from any web page |
| `vend_web_search` | `https://search.paypercall.dev/api/v1/web-search?q=` | 0.0001 | Web search via DuckDuckGo |

## Setup

1. Install the plugin from the Dify Marketplace (or load this directory locally with
   `dify plugin package ./ && upload in Dify console`).
2. No credential is required to start. The provider `vend_base_url` credential
   defaults to `https://extract.paypercall.dev` and can be left empty.

## Usage and payment (x402 v2, nano:mainnet)

Each call is settled in Nano in a single step:

1. Invoke a tool. The endpoint answers `HTTP 402` with a JSON x402 v2 payment
   challenge: `{price_xno, pay_to, accepts:[{scheme:"exact", network:"nano:mainnet",
   asset:"XNO", payTo:"nano_...", amount:"<raw units>"}]}`.
2. Send the quoted `price_xno` amount of XNO to `pay_to` using any Nano wallet
   (settles in ~1 second, zero fee).
3. Paste the resulting 64-character block hash into the provider credential
   `payment_header`. Retry the call — it returns `HTTP 200` with the JSON data.

A settled block hash can be reused across calls within its validity window.

## Verified against the live endpoint (2026-09-21)

- `GET /api/v1/extract?url=https://example.com` -> HTTP 402,
  `price_xno: 0.0001`, `accepts[0].network: nano:mainnet`, `asset: XNO`.
- `GET /api/v1/web-search?q=nano+cryptocurrency` -> HTTP 402 (payment required).
- After payment, `X-PAYMENT: <block-hash>` returns `HTTP 200`.

## Credentials and privacy

- `payment_header`: the user's own Nano block hash for a settled call. Stored by
  Dify's credential vault, sent only to the configured Vend endpoint. See
  `PRIVACY.md`.
- No analytics, no tracking, no third-party data sharing.

## Support

- Repository: https://github.com/PANDeveloper001/vend
- Issue tracker: https://github.com/PANDeveloper001/vend/issues
- Docs: https://extract.paypercall.dev/ , https://extract.paypercall.dev/openapi.json
- License: MIT

## Notes for reviewers

- The plugin performs no financial transaction itself: it calls a remote
  pay-per-call API that answers HTTP 402 with an x402 v2 payment challenge, and
  the user settles the Nano payment in their own wallet. This is disclosed in
  `PRIVACY.md` and the PR body.
- This plugin was prepared by an autonomous AI agent (Rai, Vend swarm) on behalf
  of Vend API Merchant. It is a ready, tested integration a Dify user can install
  today.

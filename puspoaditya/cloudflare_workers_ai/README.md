# Cloudflare Workers AI — Dify Model Provider

Serverless inference for Dify over Cloudflare's open-model catalog with a generous free tier.

> ⚠️ Status: **community plugin** (author: puspoaditya) — not an official Cloudflare or Dify product.

## Features

- **5 verified models**: Llama 3.3 70B (FP8 fast), Llama 3.1 8B (Infire), Llama 4 Scout 17B, Qwen 2.5 Coder 32B, DeepSeek R1 Distill Qwen 32B
- **OpenAI-compatible endpoint** — full chat, streaming, and tool calls supported
- **Account ID field** — no need to construct URLs or wire a custom OpenAI-compatible endpoint by hand
- **Free tier** — Cloudflare gives every account a daily free allocation of Workers AI neurons

## Setup

1. Get an **API Token** with the `Workers AI` permission:
   [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Copy your **Account ID** (right sidebar of the Cloudflare dashboard, or the `/accounts/{id}` segment of any dashboard URL)
3. In Dify: **Settings → Model Providers → Cloudflare Workers AI** → enter Account ID + API Token → Save

## Models

| Model | Notes |
|---|---|
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | Default — fast & strong generalist |
| `@cf/meta/infire-llama-3.1-8b-instruct` | Small & cheap (the old `llama-3.1-8b` id was deprecated by Cloudflare in 2026-05) |
| `@cf/meta/llama-4-scout-17b-16e-instruct` | Multimodal-ish Llama 4 |
| `@cf/qwen/qwen2.5-coder-32b-instruct` | Coding |
| `@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` | Reasoning (emits `<think>` blocks) |

Pricing shown in the model list is per-token display from Cloudflare's published rates — verify at [developers.cloudflare.com/workers-ai/platform/pricing](https://developers.cloudflare.com/workers-ai/platform/pricing) if you need exact numbers.

## Difference from "Custom (OpenAI-compatible)"

The generic compatible provider works, but requires pasting the full endpoint URL and entering raw model IDs. This plugin wraps Workers AI natively: just paste your **Account ID** + **API Token**, and the model catalog is pre-filled.

## Troubleshooting (tested on Dify v1.x)

- **Install**: upload the packaged `.difypkg` (run `dify-plugin package` in this folder). A raw zip is rejected — the manifest must sit at the archive root.
- **Community plugins & signatures**: Dify's `FORCE_VERIFYING_SIGNATURE` defaults to `true`, which rejects unsigned community plugins. For local/self-hosted installs set it to `false` in `docker/.env` and restart, then install.
- **Provider ID in the API**: `puspoaditya/cloudflare_workers_ai/cloudflare` (author/plugin-name/provider).

## Contact & Source

- **Author**: Puspo Aditya — [github.com/puspoaditya](https://github.com/puspoaditya)
- **Source**: this repository — `puspoaditya/cloudflare_workers_ai/`
- **Privacy**: see [PRIVACY.md](./PRIVACY.md)

## Development

```bash
uv sync          # install dify_plugin SDK
uv run black . -C -l 100 && uv run ruff check --fix
```

To test inside a local Dify instance, install the plugin from the **Plugin** page (upload the packaged `.difypkg`) or use the debug workflow documented in [Dify plugin docs](https://docs.dify.ai/plugins/development).

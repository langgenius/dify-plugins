# Fikra API for Dify

Use DeepSeek, Qwen, Kimi, GLM, Gemini, Seed, MiMo and Fikra's own models in Dify through one OpenAI-compatible API key.

**Author:** Fikra API (Lacesse Ventures, Nairobi, Kenya)
**Source:** https://github.com/Fikra-API/fikra-dify-plugin
**Contact:** james@fikraapi.co.ke
**Version:** 0.0.1
**Type:** Model provider (LLM)

## Why Fikra API

- One key for the major Chinese frontier models plus Gemini, with tool calling and streaming.
- Pay in USD by card, or in Kenyan shillings with M-Pesa.
- OpenAI-compatible endpoint: `https://api.fikraapi.co.ke/v1`.

## Setup

1. Create an account at https://fikraapi.co.ke and copy an API key from the dashboard (`fk_live_...`).
2. In Dify, go to **Settings → Model Provider**, find **Fikra API** and click **Setup**.
3. Paste the API key and save. The plugin checks it with one tiny request to `qwen3.8-27b`.
4. Pick any Fikra model in your app, workflow or agent node.

The optional **API Base URL** field only needs changing if Fikra gives you a dedicated endpoint.

## Models

Predefined: DeepSeek V4.1 Flash, DeepSeek V4 Pro, Qwen 4 Max, Qwen Plus, Qwen 3.8 27B, Qwen 3.6 35B, Kimi K3, GLM 5.3, GLM 5.3 Flash, Gemini 4 Argon, Gemini 4 Hydrogen, MiMo v2.6 Pro, Seed 2.0 Pro / Code / Lite, Nemotron 3.5 Super VL, fikra-auto, fikra-code-35b and fikra-pro-120b.

Any other chat model from https://fikraapi.co.ke/models can be added with **Add Model** (customizable model) using its model ID.

All predefined models support tool calling (function calling), streaming and agent use. Prices shown in Dify are USD per million tokens and match https://fikraapi.co.ke/pricing.

## Requirements

- A Fikra API key. Usage is billed to your Fikra account.
- Outbound HTTPS from your Dify instance to `api.fikraapi.co.ke`.

## Privacy

See [PRIVACY.md](PRIVACY.md). The plugin sends prompts only to the Fikra API endpoint you configure and stores nothing itself.

## Support

Email james@fikraapi.co.ke or open an issue at https://github.com/Fikra-API/fikra-dify-plugin/issues.

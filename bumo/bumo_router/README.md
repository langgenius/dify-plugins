# Bumo Router for Dify

**One API key, every model.** Use DeepSeek, Kimi, Qwen, GLM, MiniMax, Claude, GPT, Gemini and more in Dify through [Bumo Router](https://router.bumo.ai) — no per-vendor plugins, no per-vendor top-ups, no typing model names and context sizes by hand.

## Setup (3 steps)

1. Install **Bumo Router** from the Dify Marketplace.
2. Create an API key at [router.bumo.ai](https://router.bumo.ai/user/api-keys) (international) or [router.bumo.cc](https://router.bumo.cc/user/api-keys) (China).
3. In Dify go to **Settings → Model Provider → Bumo Router**, paste the key and save.

That's it. The plugin detects whether your key belongs to the international or the China site, and the models show up in Dify with context length, tool calling and vision support already filled in — nothing to type by hand.

## Models

| Site | Models |
| --- | --- |
| International (router.bumo.ai) | Claude, GPT, Gemini |
| China (router.bumo.cc) | DeepSeek, Kimi, Qwen, GLM, MiniMax, StepFun, MiMo, Hunyuan |

The full, current list is at `https://router.bumo.ai/v1/models` and `https://router.bumo.cc/v1/models`. Keys and balances of the two sites are separate; picking a model from the other site gives a clear message telling you where to get a key.

**A model launched after this plugin version?** Click **Add Model**, type the model name (for example `deepseek/deepseek-flash`) and your key. Context length, tool calling and vision are looked up from Bumo Router automatically.

## Features

- Streaming, tool calling (agents / workflows), vision for models that support it
- Key check on save, without sending a real chat request (no cost)
- Clear errors for an invalid key, zero balance, or a model that is not on your site
- Optional custom API base URL (leave empty in almost all cases)

## Support

- Docs: https://bumo.cc/docs/api
- Console & contact: https://router.bumo.ai · https://router.bumo.cc
- Source code: https://github.com/langgenius/dify-plugins/tree/main/bumo/bumo_router

# Privacy Policy

**Cloudflare Workers AI plugin for Dify** (version 0.0.1)

## Data collection

This plugin collects **no user data** beyond what is strictly required to provide the service:

- **What is sent**: chat prompts, model parameters (temperature, max tokens, etc.), and the API Token / Account ID you configure in Dify's model provider settings.
- **Where it goes**: these are transmitted directly to Cloudflare's Workers AI API (`api.cloudflare.com`) to generate model responses.
- **What is stored**: nothing. The plugin does not store, log, or persist any prompts, responses, or credentials outside Dify's own settings storage. Credentials are kept in Dify's encrypted provider credential store.

## Third parties

- **Cloudflare, Inc.** — receives prompts and configuration solely to run inference via Workers AI. See [Cloudflare's privacy policy](https://www.cloudflare.com/privacypolicy/).

## Contact

- Author: Puspo Aditya (GitHub: [puspoaditya](https://github.com/puspoaditya))
- Source: https://github.com/langgenius/dify-plugins/tree/main/puspoaditya/cloudflare_workers_ai

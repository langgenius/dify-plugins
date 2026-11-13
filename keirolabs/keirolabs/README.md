# Keirolabs

**Author:** keirolabs
**Version:** 0.0.1
**Type:** tool
**Source:** https://github.com/Keirolabs-API/dify-plugin-keirolabs
**Contact:** https://keirolabs.cloud · Discord https://discord.gg/Smv4t4txjS

## Description

[Keirolabs](https://keirolabs.cloud) is web search built for AI agents. This plugin adds a **Keirolabs Search** tool to your Dify agents, chatflows and workflows. It returns titles, links and snippets from the open web.

Keirolabs costs a flat $0.10 per 1,000 searches on the entry plan, and down to $0.03 per 1,000 on higher plans, whatever the result count.

## Setup

1. Sign up for free at https://platform.keirolabs.cloud/register (no card needed).
2. Copy an API key from https://platform.keirolabs.cloud/dashboard/keys. It starts with `keiro_`.
3. In Dify, open **Plugins → Keirolabs → Authorize** and paste the key.

## Tool: Keirolabs Search

| Parameter | Description |
|---|---|
| `query` | What to search for (required) |
| `max_results` | 1-15, default 10 |
| `include_domains` | Optional comma-separated domains, e.g. `python.org,docs.github.com` |

**Output:** a JSON message `{"results": [{"title", "url", "snippet"}]}` and a numbered text list of the same results.

## Requirements

Outbound HTTPS access to `api.keirolabs.cloud`.

## Privacy

See [PRIVACY.md](PRIVACY.md). Only the search query and your API key are sent to Keirolabs.

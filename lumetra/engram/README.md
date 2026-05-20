# engram-dify

[Engram](https://lumetra.io) tools for [Dify](https://dify.ai) — durable, explainable memory for AI agents and chatflows.

This is a first-party Dify plugin. Six tools (`store_memory`, `query_memory`, `list_memories`, `list_buckets`, `delete_memory`, `clear_memories`) call the hosted Engram REST API directly. No MCP bridge, no servers_config JSON, no community-plugin dependency — install from the Dify Marketplace and the tools appear in the catalog.

## Setup

### 1. Get an Engram API key

Sign up at <https://lumetra.io> — free tier, no card. You'll see an `eng_live_…` token in your dashboard.

### 2. Configure a BYOK provider key

Engram is bring-your-own-key for the LLM that handles extraction and synthesis. Configure one provider at <https://lumetra.io/models>. DeepSeek is what we recommend — cheap and fast. Without a provider key, `store_memory` and `query_memory` return HTTP 412.

### 3. Install the plugin

In your Dify console: **Plugins → Marketplace** → search **"Engram"** → install. Then **Plugins → Installed → Engram** → **Authorize** and paste your `eng_live_...` API key.

The six tools are now available in the tool catalog for Agents, Chatflows, and Workflows.

## Tools

| Tool | What it does |
|---|---|
| `store_memory(content, bucket?)` | Save an atomic fact to a bucket. Defaults to `"default"`. Buckets auto-create on first write. |
| `query_memory(question, bucket?)` | Natural-language question against memory. Returns a synthesized answer with citations. |
| `list_memories(bucket?, limit?)` | Newest-first list of memories in a bucket. |
| `list_buckets(limit?, offset?)` | Paginated list of buckets in your tenant. |
| `delete_memory(memory_id, bucket)` | Remove a single memory by UUID. |
| `clear_memories(bucket)` | Empty a bucket. **Destructive.** |

## Self-hosted Engram

If you're running Engram on your own infrastructure instead of `api.lumetra.io`, set the **Engram API Base URL** field in the Authorize dialog to your endpoint (e.g. `https://engram.internal.example.com`).

## Manual verification

Outside Dify, confirm Engram itself is reachable with your key:

```bash
curl -s https://api.lumetra.io/v1/buckets \
  -H "Authorization: Bearer eng_live_..." | head -c 300
```

A JSON bucket list confirms the key is valid. If Dify shows the plugin as installed but tools fail, double-check the key in the Authorize dialog and that the Dify worker process can reach `api.lumetra.io` from inside its container.

## Source & contact

- Source: <https://github.com/lumetra-io/engram-dify>
- Issues: <https://github.com/lumetra-io/engram-dify/issues>
- Lumetra: <https://lumetra.io> · <support@lumetra.io>

## License

MIT — Lumetra

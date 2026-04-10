# Kronvex Memory — Dify Plugin

Persistent memory for AI agents inside [Dify](https://dify.ai).

Store, recall, and inject semantically-searchable memories across sessions using [Kronvex](https://kronvex.io).

## Tools

| Tool | Description |
|------|-------------|
| **Remember** | Store a memory for an agent (episodic / semantic / procedural) |
| **Recall** | Search an agent's memories by semantic similarity |
| **Inject Context** | Get a formatted memory block ready for a system prompt |

## Installation

1. In Dify, go to **Tools → Custom → Import plugin**
2. Upload `kronvex-memory.difypkg` (or point to this directory)
3. Enter your credentials:
   - **API Key** — your Kronvex API key (`kv-...`)
   - **Base URL** — `https://api.kronvex.io` (default)

Get a free API key at [kronvex.io](https://kronvex.io) — 100 memories, 1 agent, no credit card.

## Usage in a workflow

### Basic memory loop

```
[User message] → Recall(agent_id, message) → [Add memories to system prompt] → LLM → [Remember key facts]
```

### Inject Context (recommended)

Use the **Inject Context** tool to automatically format memories into your system prompt:

```
System: You are a helpful assistant.
{inject_context_output}

User: {user_message}
```

## Credentials

| Field | Required | Description |
|-------|----------|-------------|
| `api_key` | ✓ | Kronvex API key starting with `kv-` |
| `base_url` | — | Default: `https://api.kronvex.io` |

## Links

- [Kronvex](https://kronvex.io)
- [API docs](https://kronvex.io/docs)
- [Get a free demo key](https://kronvex.io/#pricing)

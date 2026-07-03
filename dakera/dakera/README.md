# Dakera Memory

Persistent, decay-weighted memory for Dify agents, backed by a self-hosted
[Dakera](https://dakera.ai) server.

Dakera is a self-hosted memory server that adds **persistent, decay-weighted vector recall**
across sessions: memories are importance-scored and decay over time, so stale context stops
competing with fresh, relevant facts. This plugin lets a Dify Agent, Chatflow, or Workflow
**store** facts and **recall** them semantically in later runs.

## Tools

| Tool | What it does | Endpoint |
|------|--------------|----------|
| **Store Memory** | Persist a concise, self-contained fact for future recall. Optional importance (0–1), session scope, and tags. | `POST /v1/memory/store` |
| **Recall Memory** | Retrieve the most semantically relevant memories for a natural-language query, ranked by score. | `POST /v1/memory/recall` |
| **Search Memory** | Filtered browse/list over memories — optional text query plus tag, importance, and count filters. | `POST /v1/memory/search` |
| **Get Memory** | Fetch a single memory by its ID (content, importance, tags, metadata). | `GET /v1/memory/get/{id}` |
| **Update Memory** | Change an existing memory's content (re-embedded), importance, or tags by ID. | `PUT /v1/memory/update/{id}` |
| **Forget Memory** | Delete memories by ID, session, tags, or importance threshold. Requires a selector; deletion is permanent. | `POST /v1/memory/forget` |

Memories are namespaced by `agent_id` — use the same `agent_id` across tools to keep
each agent's (or user's) memories isolated. **Recall** is best for precise semantic retrieval;
**Search** is best for browsing/filtering/auditing what an agent remembers.

## Setup

### 1. Run a Dakera server

Dakera is self-hosted. The quickest path is the docker-compose in
[`dakera-ai/dakera-deploy`](https://github.com/dakera-ai/dakera-deploy), which starts the
server (image `ghcr.io/dakera-ai/dakera`) plus its object store. By default the API listens
on port **3000**.

### 2. Configure the plugin

Provide two credentials when authorizing the tool:

- **Dakera Server URL** — the base URL of your server, e.g. `http://localhost:3000`.
- **Dakera API Key** *(optional)* — a `dk-...` key if your server was started with
  `DAKERA_API_KEY`. Leave empty for unauthenticated local development.

The plugin validates the connection with a `GET /health/live` probe when you save credentials.

## Usage example

In an Agent app, add the tools you need (all six, or just Store + Recall). A typical loop:

1. Early in a task, call **Recall Memory** with a query like
   `"user's preferred programming language and coding conventions"` (same `agent_id` you use
   everywhere) to pull in relevant prior context.
2. When the agent learns something durable, call **Store Memory** with a concise fact such as
   `"Alice prefers Rust over Python for backend services"`, `importance = 0.9`.

Next session, recalling with the same `agent_id` surfaces that fact even though the
conversation is new.

### Chaining tools with memory IDs

Recall and Search return each memory's **ID** in their output, so an agent can act on a specific
memory afterwards:

- **Recall/Search → Get** — pull the full record of a specific hit.
- **Recall/Search → Update** — correct or re-weight a memory (e.g. bump `importance`, replace
  `content`) by its ID.
- **Recall/Search → Forget** — delete a memory that is now wrong or obsolete by its ID.

Use **Forget** with a `session_id`, `tags`, or `below_importance` selector to prune a whole set at
once — it refuses to run without at least one selector, so it can't wipe an agent's namespace by
accident.

## Development

The plugin source lives alongside the packaged `.difypkg` in this directory. To run the tests:

```bash
pip install dify_plugin requests pytest
pytest -q            # exercises all six tools + credential validation against an in-process mock
```

The `tests/` directory is excluded from the packaged plugin via `.difyignore`.

## Requirements & connection

- A reachable, self-hosted Dakera server (this plugin does **not** bundle or host one).
- Network egress from Dify to the server URL you configure.
- No third-party accounts — all data stays on the server you run.

## Links

- Docs: https://dakera.ai/docs
- Self-hosting: https://github.com/dakera-ai/dakera-deploy
- Python SDK: https://github.com/dakera-ai/dakera-py
- Source repository for this plugin: https://github.com/dakera-ai/dakera-py

## Contact

Issues and questions: https://github.com/dakera-ai/dakera-py/issues

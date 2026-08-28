# Fusion Query Engine — Dify Plugin

LlamaIndex-based tool plugin for Dify that performs **windowed COMPACT synthesis**
over pre-fetched context (Qdrant points or plain text), with optional chat-history
condensing.

Author: **gitpoldan**. Provider id: `gitpoldan/fusion_query_engine`.

## Features

- **Two modes**: `query_expansion` (enrich query) and `answer_query` (generate answer)
- **Pre-fetched context** — no Qdrant calls inside the plugin; nodes from upstream workflow
- **Chat history** — optional JSON `chat_history` for multi-turn condensing
- **Two LLM selectors** — separate models for expansion and answer steps

## Setup

1. Install the plugin in Dify (Marketplace upload or remote debug).
2. Add the **Fusion Query Engine** tool to a Workflow or Chatflow.
3. Configure **model_expansion** and **model_answer** (LLM model selectors from your workspace).
4. Wire inputs:
   - **query** — user question (`{{sys.query}}` or LLM output)
   - **source_nodes** — array from Knowledge Retrieval or a Code node (Qdrant-style points)
   - **context_text** — plain-text fallback when `source_nodes` is empty
   - **chat_history** — optional JSON string of prior turns (see Usage)

No external API credentials beyond LLMs already configured in Dify.

## Usage

**Two-step RAG pipeline:**

1. Run tool with `mode=query_expansion` → enriched query in `enriched_query`
2. Run Knowledge Retrieval with enriched query
3. Run tool with `mode=answer_query` → final answer in `response`

**Outputs:** `response`, `mode`, `enriched_query` (expansion mode only).

Example `source_nodes` element:

```json
{"id": "chunk-1", "payload": {"text": "...", "metadata": {"file_name": "doc.pdf"}}, "score": 0.91}
```

Requires Dify >= 1.14.0.

## Privacy

Queries and context are sent to LLM providers configured in your workspace. See [PRIVACY.md](PRIVACY.md).

## Support

- Source: https://github.com/gitpoldan/dify/tree/main/polden-plugins/fusion_query_engine
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

Russian documentation: [readme/README_ru_RU.md](readme/README_ru_RU.md).

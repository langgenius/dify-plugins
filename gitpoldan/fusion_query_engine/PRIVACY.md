# Privacy Policy — Fusion Query Engine

## Overview

This tool plugin runs inside your Dify workspace. It does **not** collect,
store, or transmit data to the plugin author. User queries, optional chat
history, and pre-fetched context are forwarded to **LLM providers you configure**
in Dify via reverse model invocation.

## Data we process

| Data | Purpose |
|------|---------|
| User query | COMPACT synthesis input |
| Optional chat history (JSON) | Condense multi-turn dialogue before synthesis |
| Context chunks (`source_nodes` or `context_text`) | RAG context for expansion or answer modes |

## Third-party services

| Service | Usage |
|---------|--------|
| LLM providers selected in Dify | Receive prompts for query expansion and answer generation |

The plugin does not call external APIs directly. Credentials and routing are
managed by your Dify workspace.

## Storage and telemetry

- No data persisted by the plugin beyond the tool call lifecycle.
- No analytics, tracking, or author-operated infrastructure.

## Contact

Author: **gitpoldan**. Questions: bv2020donch@gmail.com

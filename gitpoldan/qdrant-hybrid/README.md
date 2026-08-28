# Qdrant Hybrid Retriever (gitpoldan)

Qdrant hybrid retrieval plugin for Dify: dense + sparse (BM25) with DBSF/RRF
fusion, optional MMR, tenant automode/ratios, payload filters, and optional reranking.

Author: **gitpoldan**. Provider id: `gitpoldan/qdrant_hybrid_retriever`.

## Features

- **Hybrid search** — dense vectors + BM25 sparse via official `qdrant-client`
- **Fusion** — DBSF (default) or RRF; optional MMR on dense branch
- **Tenant modes** — automode median prune and/or weighted quota merge
- **Filters** — `point_type`, `corpus_docs`, `source`, JSON `payload_filters`
- **Rerank** — optional Dify rerank model or local `fastembed` fallback
- **LLM-friendly outputs** — `result`, `source_nodes`, `source_list_text`, `chunk_texts`

## Setup

1. Deploy Qdrant 1.15+ (MMR requires 1.15+).
2. Install the plugin and open **Tool provider → Qdrant Hybrid Retriever**.
3. Configure credentials:

| Field | Required | Description |
|-------|----------|-------------|
| `base_url` | Yes | Qdrant URL, e.g. `https://xxx.cloud.qdrant.io:6333` |
| `api_key` | No | Required for Qdrant Cloud |
| `extra_headers` | No | Optional JSON HTTP headers |

4. In the tool node, set **collection**, **text** (query), and **embedding_model_config**
   (embedding model from your Dify workspace).

## Usage

Add **Hybrid Retriever** to a Workflow node. Key parameters:

- `limit`, `prefetch_limit`, `fusion` (`dbsf` / `rrf`)
- `use_mmr`, `score_threshold`, `corpus_docs`, `payload_filters` (JSON)
- `enable_rerank`, `rerank_model_config`
- `all_from_top_k_source` — expand to all points from top-K sources (optional)

Outputs: use `chunk_texts` or `source_nodes` as LLM context downstream.

## Privacy

Connects to your Qdrant cluster; embedding/rerank via Dify models. See [PRIVACY.md](PRIVACY.md).

## Support

- Source: https://github.com/gitpoldan/dify/tree/main/polden-plugins/qdrant-hybrid
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

Russian documentation: [readme/README_ru_RU.md](readme/README_ru_RU.md).

# Qdrant Hybrid Retriever Privacy Policy

## Data We Process

| Data Type | Details | Purpose |
| --- | --- | --- |
| Connection configuration | Qdrant `base_url`, API key, extra headers (set by the user in Dify) | Connect to the user-owned Qdrant cluster |
| Request payloads | Collection name, query text, filters, retrieval options | Execute hybrid retrieval for the request lifetime only |
| Embedding inputs | Query text when `embedding_model_config` is provided | Forwarded via Dify reverse model invocation |
| Rerank inputs | Query and chunk texts when reranking is enabled | Dify rerank model or local `fastembed` cross-encoder |

The plugin does **not** collect names, emails, device identifiers, or other personal
data beyond what the workflow owner supplies.

## Third-Party Services

| Service | Usage | Privacy Policy |
| --- | --- | --- |
| Qdrant (user-owned cluster) | Vector search and payload retrieval | https://qdrant.tech/privacy/ |
| Embedding / rerank providers in Dify | Text-to-vector / rerank via workspace credentials | Provider policy of your choice |

No data is transmitted to the plugin author.

## Storage & Retention

- The plugin **does not persist** query results or credentials.
- `fastembed` BM25/rerank models are cached locally by the runtime on first use.

## Security

- API keys are never logged; Qdrant Cloud traffic uses HTTPS.
- No telemetry or analytics.

## Contact

Author: **gitpoldan**. Questions: bv2020donch@gmail.com

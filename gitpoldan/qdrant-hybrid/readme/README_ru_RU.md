# Qdrant Hybrid Retriever (gitpoldan)

Гибридный ретривер Qdrant для Dify: dense + sparse (BM25), fusion DBSF/RRF,
опциональный MMR, automode/ratios по tenants, payload-фильтры и rerank.

Автор: **gitpoldan**. ID провайдера: `gitpoldan/qdrant_hybrid_retriever`.

## Возможности

- **Гибридный поиск** — dense + BM25 через официальный `qdrant-client`
- **Fusion** — DBSF или RRF; опциональный MMR на dense-ветке
- **Tenant modes** — automode median prune и/или квоты по tenants
- **Фильтры** — `point_type`, `corpus_docs`, `source`, JSON `payload_filters`
- **Rerank** — модель Dify или локальный fallback `fastembed`
- **Выходы для LLM** — `source_nodes`, `chunk_texts`, `source_list_text`

## Настройка

1. Qdrant 1.15+ (MMR с 1.15+).
2. Установите плагин → **Tool provider → Qdrant Hybrid Retriever**.
3. Credentials: `base_url`, опционально `api_key`, `extra_headers`.
4. В узле инструмента: **collection**, **text**, **embedding_model_config**.

## Использование

Добавьте **Hybrid Retriever** в Workflow. Ключевые параметры: `limit`,
`fusion`, `use_mmr`, `corpus_docs`, `payload_filters`, `enable_rerank`,
`all_from_top_k_source`.

Используйте `chunk_texts` или `source_nodes` как контекст для LLM.

## Конфиденциальность

Подключение к вашему Qdrant; embedding/rerank через модели Dify. См. [PRIVACY.md](../PRIVACY.md).

## Поддержка

- Исходники: https://github.com/gitpoldan/dify/tree/main/polden-plugins/qdrant-hybrid
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

English documentation: [README.md](../README.md).

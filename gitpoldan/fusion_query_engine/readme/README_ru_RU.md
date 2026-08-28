# Fusion Query Engine — Dify Plugin

LlamaIndex-плагин для Dify: **COMPACT-синтез** по предзагруженному контексту
(Qdrant points или текст) с опциональным сжатием истории чата.

Автор: **gitpoldan**. ID провайдера: `gitpoldan/fusion_query_engine`.

## Возможности

- **Два режима**: `query_expansion` (обогащение запроса) и `answer_query` (ответ)
- **Предзагруженный контекст** — без вызовов Qdrant внутри плагина
- **История чата** — опциональный JSON `chat_history`
- **Два LLM-селектора** — отдельные модели для expansion и answer

## Настройка

1. Установите плагин в Dify.
2. Добавьте инструмент **Fusion Query Engine** в Workflow или Chatflow.
3. Настройте **model_expansion** и **model_answer** (LLM из вашего workspace).
4. Подключите **query**, **source_nodes** / **context_text**, опционально **chat_history**.

Внешние credentials не нужны — только LLM, уже настроенные в Dify.

## Использование

**Двухшаговый RAG:**

1. `mode=query_expansion` → `enriched_query`
2. Knowledge Retrieval с обогащённым запросом
3. `mode=answer_query` → `response`

Требуется Dify >= 1.14.0.

## Конфиденциальность

Запросы и контекст отправляются в LLM-провайдеры вашего workspace. См. [PRIVACY.md](../PRIVACY.md).

## Поддержка

- Исходники: https://github.com/gitpoldan/dify/tree/main/polden-plugins/fusion_query_engine
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

English documentation: [README.md](../README.md).

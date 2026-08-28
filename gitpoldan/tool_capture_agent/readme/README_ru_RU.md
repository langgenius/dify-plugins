# Tool-Capture Agent — Dify Plugin

Автор: **gitpoldan**. Версия: **0.3.3**. Требуется Dify **>= 1.16.1**.

Agent-strategy плагин на базе Function-Calling агента Dify с дополнениями:

- **Capture** — каждый вызов инструмента как переменные workflow
- **I/O wiring** — JSON-связи output→input через индексы (большие payload вне контекста LLM)
- **Вложения** — `files` ← `{{#sys.files#}}` для multimodal Chatflow
- **Skills & Tools routing** — YAML-каталоги для компактного system prompt

ID провайдера: `gitpoldan/tool_capture_agent`.

## Настройка

1. Установите плагин в Dify.
2. Узел **Agent** → стратегия **Tool-Capture Agent → Function Calling**.
3. Настройте Model, Tools, Instruction, Query как у обычного агента.
4. (Опционально) **Files** = `{{#sys.files#}}`, **I/O wiring**, **Output mappings**, **Skills/Tools catalog**.

Отдельные credentials не нужны.

## Использование

Примеры переменных: `{{#agent.tool_outputs.tavily_search#}}`,
`{{#agent.tool_calls_count#}}`, `{{#agent.mapped_outputs.weather#}}`.

Для карточек файлов в чате: `{{#agent.files#}}` в Answer.

Подробная документация — в [репозитории](https://github.com/gitpoldan/dify/tree/main/polden-plugins/tool_capture_agent).

## Конфиденциальность

Данные не сохраняются между вызовами Agent. См. [PRIVACY.md](../PRIVACY.md).

## Поддержка

- Исходники: https://github.com/gitpoldan/dify/tree/main/polden-plugins/tool_capture_agent
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

English documentation: [README.md](../README.md).

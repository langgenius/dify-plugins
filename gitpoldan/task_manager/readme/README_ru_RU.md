# Transit Task Manager (gitpoldan)

Мультитenantный транзитный таск-менеджер для Dify Workflow и Agent. Задачи
хранятся в **бакете MinIO / S3** — одна SQLite-БД на тенанта. Инструменты:
создание / чтение / список / обновление / смена статуса / удаление, ленивое
TTL-истечение и статистика по тенанту.

Автор: **gitpoldan**. ID провайдера: `gitpoldan/task_manager`.

## Возможности

- **Хранение в S3** — одна SQLite-БД на тенанта; отдельный сервер не нужен.
- **Конечный автомат статусов** — валидируемые переходы с метаданными.
- **Безопасная конкуренция** — lease lock + условные записи по ETag.
- **Ленивое TTL** — просроченные задачи очищаются при доступе или через `sweep_ttl`.

## Настройка

1. Создайте бакет S3 или MinIO (должен существовать заранее).
2. Установите плагин в Dify → **Tool provider → Transit Task Manager**.
3. Укажите credentials: `endpoint`, `access_key_id`, `secret_access_key`,
   `bucket`, опционально `region`, `prefix`, `use_https`.
4. Добавьте инструменты в Workflow или Agent. Каждый вызов требует `tenant`;
   опциональный `namespace` группирует тенантов.

## Использование

1. **create_task** — создать задачу с `tenant`, `title`, опционально `payload`, `ttl_seconds`
2. **set_status** — перевести в `in_progress` / `completed` с metadata
3. **get_task** / **list_tasks** — прочитать состояние для следующих узлов

Цепочка статусов: `created` → `pending` → `in_progress` → `completed` /
`cancelled` / `failed` / `expired`.

## Конфиденциальность

Данные пишутся только в ваш бакет. См. [PRIVACY.md](../PRIVACY.md).

## Поддержка

- Исходники: https://github.com/gitpoldan/dify/tree/main/polden-plugins/task_manager
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

English documentation: [README.md](../README.md).

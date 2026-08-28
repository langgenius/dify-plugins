# Transit Task Manager (gitpoldan)

Multi-tenant transit task manager for Dify Workflow and Agent apps. Tasks are
stored in a **MinIO / S3 bucket**, one SQLite database per tenant. Exposes
create / read / list / update / status-transition / delete tools, TTL
auto-expiration, and per-tenant statistics.

Author: **gitpoldan**. Provider id: `gitpoldan/task_manager`.

## Features

- **S3-backed storage** — one SQLite DB per tenant in your bucket; no separate server.
- **Status state machine** — validated transitions with optional metadata on each change.
- **Concurrency safe** — lease lock + ETag conditional writes with retry on conflict.
- **Lazy TTL** — expired tasks cleaned on access or via `sweep_ttl`.

## Setup

1. Create an S3 or MinIO bucket (must already exist).
2. In Dify, install the plugin and open **Tool provider → Transit Task Manager**.
3. Configure credentials:

| Field | Required | Description |
|-------|----------|-------------|
| `endpoint` | No | MinIO host (empty = AWS S3) |
| `access_key_id` | Yes | Access key |
| `secret_access_key` | Yes | Secret key |
| `use_https` | No | HTTPS for custom endpoint (default `true`) |
| `bucket` | Yes | Bucket name |
| `region` | No | AWS region (default `us-east-1`) |
| `prefix` | No | Base key prefix for all tenant DBs |

4. Add task tools to a Workflow or Agent node. Every call requires a `tenant` id;
   optional `namespace` groups tenants under a sub-path.

## Usage

Example workflow:

1. **Tool: create_task** — `tenant`, `title`, optional `payload`, `ttl_seconds`
2. **Tool: set_status** — transition to `in_progress` / `completed` with metadata
3. **Tool: get_task** or **list_tasks** — read back state for downstream nodes

Status flow: `created` → `pending` → `in_progress` → `completed` / `cancelled` /
`failed` / `expired`.

## Privacy

Task data is written only to your configured bucket. See [PRIVACY.md](PRIVACY.md).

## Support

- Source: https://github.com/gitpoldan/dify/tree/main/polden-plugins/task_manager
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

Russian documentation: [readme/README_ru_RU.md](readme/README_ru_RU.md).

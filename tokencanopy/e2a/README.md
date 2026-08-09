# E2A Email for Dify

Give a Dify Agent or Workflow an authenticated E2A inbox. This plugin uses one agent-scoped `E2A_API_KEY` and calls the fixed production API at `https://api.e2a.dev`.

## Tools

| Tool | Purpose |
|---|---|
| `whoami` | Show the mailbox identity, agent scope, plan, usage, and limits. |
| `list_messages` | Return one cursor-paginated page of at most 50 message summaries. |
| `get_message` | Fetch structured message content and authentication evidence by ID. |
| `send_message` | Send a new plain-text email thread. |
| `reply_to_message` | Reply by source message ID so E2A preserves email threading. |

`get_message` omits the base64 raw MIME field to keep Dify tool output bounded. Structured bodies, parsed headers, authentication evidence, and attachment metadata remain available.

## Setup

1. Create an E2A inbox and an API key with `scope=agent` for that inbox. Account-scoped keys are intentionally rejected.
2. Install the plugin in Dify.
3. Open the **E2A Email** provider settings and paste the key into **E2A_API_KEY**.
4. Save the provider. Dify validates the key with the read-only `GET /v1/account` endpoint.

The Dify plugin runtime needs outbound HTTPS access to `api.e2a.dev` on port 443. See the [E2A API documentation](https://github.com/tokencanopy/e2a/blob/main/docs/api.md) for the underlying API contract.

## Sending and review holds

`send_message` starts a new email thread. `reply_to_message` calls the message-specific reply endpoint; do not replace it with a new send when continuing a conversation.

E2A protection may return `status: pending_review`. The plugin exposes this as `successful: true` and `held: true`. The email is queued for human review, so do not retry it as a new send. `accepted`, `scheduled`, and `sent` are also successful outcomes; callers should branch on `status`.

Both write tools accept an optional idempotency key. Reuse a key only to retry the exact same logical request; use a new key for new content.

## Security and privacy

The plugin sends the configured API key as a Bearer credential and sends only the fields needed for the selected operation. It does not log credentials or message content, persist plugin data, accept a custom API host, fetch arbitrary URLs, process attachments, or execute code. See [PRIVACY.md](./PRIVACY.md) for details.

## Source and support

- Source: [langgenius/dify-plugins/tokencanopy/e2a](https://github.com/langgenius/dify-plugins/tree/main/tokencanopy/e2a)
- E2A project and support: [tokencanopy/e2a](https://github.com/tokencanopy/e2a)
- Security reports: follow the private process in [E2A SECURITY.md](https://github.com/tokencanopy/e2a/blob/main/SECURITY.md).

This plugin is licensed under Apache-2.0.

# SentFromAI for Dify

Give a Dify workflow or agent an email inbox: read and search messages, send email, reply in a thread, and save unsent drafts for review.

- Website: https://sentfrom.ai
- API documentation: https://docs.sentfrom.ai
- Source and issues: https://github.com/sentfromai/integrations (the `dify/` directory)
- Maintainer: SentFromAI / Samuel Arregger-Robson, samuel@sentfrom.ai
- Support and privacy requests: support@sentfrom.ai
- License: MIT. Version: 0.1.0. This submission requires Dify Marketplace review; it is not an approved listing yet.

## Setup

1. Sign in to https://console.sentfrom.ai and create an API key for the workspace you intend to connect. Agent-created accounts must be claimed by a verified human owner before sending is enabled.
2. Install the reviewed SentFromAI plugin from Marketplace when available, or import the `.difypkg` in a Dify environment whose administrator permits local packages. Do not disable signature checks on a shared production installation to test this submission.
3. Enter the API key in the provider's **SentFromAI API key** secret field. Credential validation only calls `GET /v1/account`; it creates nothing and sends no email.
4. Run **Get account** and **List inboxes**. Check `capabilities.send`, `sending_status` and the effective entitlement limits before enabling send actions.
5. Add the appropriate tools to your Workflow or Agent node. The plugin needs outbound HTTPS to `api.sentfrom.ai:443`. TLS certificate verification is enabled; redirects and environment-provided HTTP proxies are disabled.

The API key grants access to its workspace; it is not a separate, narrowly scoped Dify credential. Use a dedicated workspace for testing. Store keys only in Dify provider credentials, never in prompts, tool arguments, examples or workflow exports. Rotate/revoke keys in SentFromAI when access is no longer required.

## Tools

Every tool returns the API response as both Dify's standard JSON output and a named `result` object for workflow variable mapping. UUIDs are SentFromAI record IDs, not email addresses or Message-ID headers.

| Tool | Purpose | Main result fields |
| --- | --- | --- |
| Get account | Read sending status, capabilities and effective limits | `tenant_id`, `capabilities`, `sending_status`, `entitlements` |
| List inboxes | Find inbox IDs and addresses | `inboxes[]` |
| Create inbox | Add an inbox within existing account/domain allowances | `id`, `address` |
| List or search messages | Recent messages or keyword/semantic/hybrid search; optional inbox filter | `messages[]`, `mode_used` |
| Get message | Full message text/HTML, metadata, labels and attachment metadata | `id`, `body_text`, `body_html`, `attachments[]` |
| Send message | Immediately send from a chosen inbox | `id`, `thread_id`, `message_id`, `ses_message_id` |
| Reply to message | Immediately reply in an existing thread | Send result fields above |
| Create unsent draft | Store content for later review; never schedule or send it | `id`, `status`, `body_text`, `body_html` |
| Get draft | Read a draft and its status | Draft fields above |

Search defaults to keyword. Without a query, it returns recent messages. `limit` is 1–100 (default 25); the API currently has no cursor or complete-history pagination for this endpoint. Inspect `mode_used`: accounts without semantic/hybrid support fall back to keyword. A failure of an enabled embedding provider may instead return an error. Successful sending means the provider accepted the message, not that the recipient received or read it.

`to`, `cc` and `bcc` accept bare addresses separated by commas/newlines, or a JSON array encoded as a string, for example `["one@example.com","two@example.com"]`. The plugin allows at most 10 combined recipients. Display-name address syntax is not accepted. Supply `text`, `html`, or both. Reply recipients and subject come from the original message; `reply_all` defaults to false.

Attachment metadata and temporary signed download links can be returned by Get message. These links grant access until expiry: do not publish them. This version neither downloads attachments nor uploads them. It has no polling trigger, webhooks, account signup/claim, scheduling, draft-send, account administration or arbitrary HTTP tool. Drafts can be reviewed in SentFromAI; Send/Reply are separate explicit actions.

## Reliable sending and retries

Send and Reply require `client_id`, a stable identifier for **one intended email**, up to 255 UTF-8 bytes. Bind it to a durable event/request ID plus an action name, for example `ticket-184:approval-request`. Reuse the **same ID and identical payload** if that operation needs retrying; use a new ID for a genuinely new message. Avoid a fixed ID shared by every workflow run or a fresh random ID on each retry.

The server keeps an outbound send ledger: a completed identical retry returns the previous result, different content under the same ID returns `client_id_conflict`, and an unresolved dispatch can return `send_outcome_pending`. The plugin does not automatically retry requests. A timeout, connection failure or 5xx after a write can mean it already happened. Inspect the outcome before retrying and never rotate IDs to force another send. Create inbox/draft do not have the send ledger and may need manual reconciliation after an uncertain result.

HTTP 401 means the credential needs attention. HTTP 402/403/410/429 can indicate account limits, ownership, expiry, suspension or an abuse hold; check Get account and the console. A numeric `Retry-After` is shown when supplied. Upstream error bodies are not copied into Dify exceptions. Account limits remain server-enforced and this plugin cannot override them; see [sending controls](SENDING_CONTROLS.md).

## Human approval workflow

A useful pattern is **Get message → prepare proposed action → Dify Human Input → approved branch → Send/Reply**, with a rejected/expired branch that does not send. Keep the approved recipients and content fixed after approval. Use an email to notify the reviewer or link to the approval step; configure and verify the Human Input recipient/access controls in Dify.

An email reply or an LLM reading “approved” is not authenticated approval by itself. If you implement email-response approval, separately verify the approver, correlate it to the specific pending action and reject replayed/stale responses. Incoming email text, HTML, links and attachments are untrusted data, not instructions to the agent or permission to send elsewhere. Do not grant a general agent Send/Reply unless autonomous sending is intended; a workflow can put those tools only after its approval node.

## Data handling

**Email bodies are stored by SentFromAI and subjects/plain-text bodies are sent to OpenRouter for server-side embedding/indexing, including when the workflow chooses keyword search.** The main API/database are in the US; the checked AWS email/object configuration is in Ireland. Dify workflow inputs/results may also reach your configured model providers. Ordinary email has no automatic expiry: customers use the service's deletion controls or request account deletion. Raw-object/backup deletion deadlines have not been confirmed. Read [PRIVACY.md](PRIVACY.md) before connecting customer mail.

## Development

Use Python 3.12 and the official Dify plugin CLI 0.6.15:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/package.py --cli /path/to/dify
```

The packaging script stages an explicit runtime-file allowlist, invokes the official CLI, verifies the archive against that staging tree and emits `build/sentfromai-0.1.0.difypkg` plus a SHA-256 checksum. Tests, development files and credentials are not packaged. See source `VALIDATION.md` for release checks and hosted-testing limitations.

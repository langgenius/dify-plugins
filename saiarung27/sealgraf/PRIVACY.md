# Privacy — Sealgraf Dify plugin

This plugin is a thin client for the Sealgraf service (https://sealgraf.com).
It stores nothing itself: no local database, no files, no persistent storage.

## What data leaves your Dify workspace

When a workflow invokes one of the plugin's tools, the plugin sends the
Sealgraf service only what the tool call contains:

- `check_permission`: the purchase being asked about — category, amount
  (integer minor units), currency, counterparty, description, and optionally
  a mandate id, agent id, and idempotency key.
- `claim_decision_token`: the preauthorization id (in the request path only).
- `complete_purchase`: the decision token, a completion nonce, and the
  completion evidence the workflow supplies (completed amount, merchant
  reference, note, and an optional payment summary).
- `get_receipt`: the preauthorization id or receipt id (in the request path
  only).

Every request carries the Sealgraf API key configured in the provider
credentials, in the `X-API-Key` header, over HTTPS. The key is an
agent-scope Sealgraf credential: it can check purchases and read its own
receipts; it cannot change the owner's limits or approve purchases.

## What Sealgraf does with it

Sealgraf records the check, the owner's decision, and the completion
evidence in a sealed receipt, under the account that issued the API key.
Sealgraf's own privacy policy governs that data:
https://sealgraf.com/legal/privacy

## What the plugin never does

- It never sends data anywhere except the configured Sealgraf base URL.
- It never logs or persists API keys, decision tokens, or purchase details.
- If the Sealgraf service cannot be reached or answers unexpectedly, the
  tool fails with an error. It never treats a failure as permission.

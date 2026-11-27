# Edict IQ Dify Plugin — Privacy Policy

Updated 27 November 2026.

Edict IQ, operated by World Discovery LLP, connects Dify users to its regulatory intelligence and compliance workspace via OAuth 2.0.

## What is processed

- OAuth access and refresh tokens are processed by Dify's credential system to authenticate calls. The plugin does not independently persist tokens or store them in files.
- Regulatory searches and tool inputs, the selected Edict IQ organization/workspace IDs, and any monitor metadata explicitly supplied by a user are sent by HTTPS to Edict IQ.
- Responses are limited to verified source-backed regulatory intelligence and, where authorized, organization-specific impacts, monitors, inventory summaries and document-check status.
- A user-requested create_target_monitor invocation changes the selected workspace. The Edict IQ service enforces the OAuth scope, role, idempotency and audit controls.
- No raw uploaded documents, arbitrary URLs, account passwords or complete source document corpora are received by this tool plugin.

## Where data goes

The plugin communicates only with https://edictiq.com/api/mcp and Edict IQ's OAuth issuer at https://vweumwphoufbatnalcte.supabase.co/auth/v1. The Dify host and any models or processors configured by the Dify user can also process tool arguments and results according to their own terms. Edict IQ uses its service providers to deliver security, operations and functionality in accordance with its privacy policy.

## Retention and controls

This plugin does not independently retain user prompts, documents or API results. Retention of authorization grants, audit records and organization data is governed by Edict IQ's policies; Dify handles its own credential, execution and conversation retention. Access can be revoked in Edict IQ and disconnected within Dify.

Privacy: https://edictiq.com/en/privacy

Terms: https://edictiq.com/en/terms

Support: support@edictiq.com

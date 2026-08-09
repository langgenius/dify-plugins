# Privacy Policy — E2A Email Dify Plugin

Last updated: 2026-08-08

This plugin connects a Dify workspace to the E2A API using an agent-scoped credential supplied by the workspace user.

## Data sent to E2A

The plugin sends data only to `https://api.e2a.dev`:

- The configured `E2A_API_KEY`, as an HTTPS Bearer credential.
- For inbox reads: the mailbox identity bound to the key, list filters, cursor, message ID, and the requested message data returned by E2A.
- For new sends: recipient addresses, subject, plain-text body, and an optional idempotency key.
- For replies: source message ID, plain-text body, reply-all choice, and an optional idempotency key.

Email addresses, message subjects, bodies, headers, authentication evidence, and related metadata may contain personal or confidential information. Users should enable this plugin only for data they are authorized to process.

## Plugin storage and logging

The plugin does not create its own persistent storage. It does not log API keys, message content, recipient addresses, subjects, or response bodies. Values are held in memory only while a tool call runs. Dify may retain configured credentials, tool inputs, outputs, or execution logs according to the Dify deployment's settings and policies.

## E2A processing

E2A processes and stores email and account data to provide the requested service. Review the [E2A data-handling documentation](https://github.com/tokencanopy/e2a/blob/main/docs/data-handling.md) before enabling the plugin.

## Third parties and network scope

The plugin calls only the fixed E2A API host `api.e2a.dev`. It does not accept user-controlled URLs, use analytics services, or send data to any other third party. Email delivery performed by E2A may involve recipient mail systems and E2A's documented infrastructure providers.

## Credential handling

`E2A_API_KEY` is declared as a Dify secret input. The plugin requires `scope=agent` and rejects account-scoped keys. Credentials are never included in plugin output or error text.

## Contact

For plugin questions, use the [E2A issue tracker](https://github.com/tokencanopy/e2a/issues). Report security issues privately using [E2A's security policy](https://github.com/tokencanopy/e2a/blob/main/SECURITY.md).

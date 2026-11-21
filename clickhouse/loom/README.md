# Loom tools for Dify

Remember facts, recall a user's memories and search documents in your Loom deployment.
The plugin calls the Loom Python SDK over HTTP. It adds no database, cache or local store.

## Install and connect

Use Dify's Plugins page to install the `.difypkg` from a local package file.
The plugin runs on Python 3.12 with `dify-plugin` 0.11 and `clickhouse-loom` 1.2 or later 1.x.

Configure the Loom URL, a scoped writer token, organization, namespace and agent name
in the provider credentials. Prefer HTTPS and restrict the token to this namespace.
The plugin can reach the URL you configure from the Dify plugin runner; allow only
trusted Loom destinations using your deployment's network policy. Credentials belong
in Dify's credential fields, never model prompts, workflow text or committed files.

Bind each tool's User ID form field to an application-controlled end-user identifier.
It must be non-empty and cannot be `-` or `*`. The model cannot supply this field.
Recall reads that user's memories across agents in the configured namespace.
Search knowledge reads app documents shared by the namespace, rather than private
user memories. Give mutually untrusted apps separate namespaces and token grants.

- Remember takes a stable memory key and a text value. Loom resolves duplicates and conflicts.
- Recall takes a query and returns full memory results with their scores and abstention fields.
- Search knowledge takes a query and returns matching document chunks and source URIs.

Searches stay in the configured namespace. A request failure fails the tool; the plugin
does not replace it with an empty result. Requests use 15-second HTTP timeouts and
one attempt, with a 30-second SDK call wait. Native pool admission and client setup
and close have separate waits; this is not a whole-invocation deadline. Credential validation
reads at most one memory row and discards it. The plugin makes no model calls.

## Build and check

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt pytest
.venv/bin/python -m pytest tests -q
dify plugin package . -o loom-0.1.0.difypkg
```

Tests use the actual SDK against a fake HTTP transport, concurrent native tool calls
against a loopback HTTP server, and a local Loom server when configured.
The hosted application check pins Dify Community Edition 1.20.0 and uses a Loom
server and SDK wheel built from the same commit. It exercises ordinary setup,
remote plugin registration, native tool workflows, user isolation, persisted identity
and owned resource cleanup. Its result and retained evidence report the outcome.
Dify Cloud and the full supported version and architecture matrix remain untested.

Source: [ClickHouse/loom](https://github.com/ClickHouse/loom/tree/main/integrations/dify).
See [privacy](PRIVACY.md).
Contact: [source repository issues](https://github.com/ClickHouse/loom/issues).

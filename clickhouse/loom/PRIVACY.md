# Privacy

The plugin sends the configured organization, namespace, agent, end-user identifier,
memory keys, fact text and search queries to the Loom endpoint configured by the
Dify administrator. The token is sent in the HTTP Authorization header.

Dify stores provider credentials and may retain workflow inputs, outputs and execution
logs under its own deployment settings. The plugin adds no telemetry, log files or
local data store. It does not send data to the plugin maintainers.

Loom stores memories and documents in the user's Loom deployment. Its configured
providers may process the text for embeddings or memory extraction; the deployment
operator controls those providers and retention. Remember writes persist after the
workflow ends. Use Loom's deletion and erasure operations to remove stored data, and
configure Dify separately to remove workflow traces.

This plugin makes authenticated requests to an administrator-configured URL. Treat
that destination and the Dify plugin runner as trusted; use network policy and scoped
tokens to constrain access.

For privacy questions, use the source repository's security policy:
[ClickHouse/loom security](https://github.com/ClickHouse/loom/security/policy).

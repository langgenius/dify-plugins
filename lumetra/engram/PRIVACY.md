# Privacy

This plugin sends the parameters you (or your agent) pass to its tools — `content`, `question`, `bucket`, `memory_id` — to the Engram REST API at `https://api.lumetra.io` (or the self-hosted base URL you configured). Memories are stored under your Engram tenant, scoped by the API key you provided in the Authorize dialog.

The plugin does not collect, log, or transmit data to any third party other than the Engram service you've explicitly authorized. The plugin does not read other Dify resources (datasets, conversations, files) — only the parameters supplied to each tool call.

For Engram's own data-handling and retention policy, see <https://lumetra.io/privacy>.

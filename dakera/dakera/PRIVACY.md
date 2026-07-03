# Privacy Policy — Dakera Memory plugin

## What this plugin does

The Dakera Memory plugin is a thin client for a **self-hosted Dakera memory server that you
run and control**. It stores and recalls memory content by making HTTPS/HTTP requests to the
server URL you configure in the plugin credentials.

## Data collected and processed

- **Memory content and parameters** — the text you pass to the *Store* tool (`content`,
  `agent_id`, optional `importance`, `session_id`, and `tags`) and the query you pass to the
  *Recall* tool. These are sent, verbatim, to the Dakera server URL you configure so it can
  persist or retrieve memories.
- **Credentials** — the Dakera Server URL and optional API key are stored by Dify as plugin
  credentials and used only to authenticate requests to your server. The API key is handled as
  a secret and is not written to tool output.

## Where data goes

Data is sent **only** to the self-hosted Dakera server URL you provide. The plugin does not
send any data to Dakera AI, the plugin author, or any other third party, and it contacts no
other network destinations. Retention, encryption, and deletion of stored memories are
governed by the Dakera server you operate, not by this plugin.

## Data retention

This plugin does not itself retain data. Stored memories live in your Dakera server for as long
as its decay/retention policy keeps them; you can delete them via your server's own APIs.

## Contact

For questions about this plugin, open an issue at
https://github.com/dakera-ai/dakera-py/issues

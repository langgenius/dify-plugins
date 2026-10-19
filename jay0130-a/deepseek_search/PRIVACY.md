# Privacy Policy

Last updated: 2026-10-18

## What this plugin collects

This plugin does **not** collect, store, or log any user data on its own. It has no database, no persistent storage, and no analytics.

## What is sent to third parties

The plugin forwards the following inputs to the DeepSeek Tools API (`https://api.deepseek.com`), using the API key configured by the user in Dify:

- **`deepseek_web_search`**: the search `query`, the optional `ori_question`, `count`, and `need_content` flag.
- **`deepseek_web_fetch`**: the `url` to retrieve.

The retrieval, extraction, and ranking of results are performed by DeepSeek's infrastructure. DeepSeek's handling of this data is governed by [DeepSeek's Privacy Policy](https://www.deepseek.com/en/privacy).

## Credentials

The DeepSeek API key is stored by the Dify platform as a secret credential and is only used in the `Authorization` header of requests to `api.deepseek.com`. The key is never logged, cached, or transmitted anywhere else by this plugin.

## Data retention

None. The plugin is stateless; responses are returned to the Dify workflow and are not persisted by the plugin.

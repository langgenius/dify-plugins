# DeepSeek Search

[Dify](https://dify.ai/) tool plugin for the [DeepSeek Tools API](https://api-docs.deepseek.com/): AI-native web search and Markdown web page extraction, using the same API key as the DeepSeek model platform.

## Tools

### `deepseek_web_search`

Web search backed by DeepSeek's search infrastructure. Each result includes `title`, `url`, `snippet`, `summary`, `site_name`, `date`, `rerank_score` (0-3; ≥1.5 is high quality), and `authority` (0-4; ≥3 is highly authoritative).

Supported search operators (passed through as-is): `site:`, `-site:`, `-` (exclusion), `-"excluded phrase"`, `"exact phrase"`, `lang:`, `after:`, `before:`.

Parameters:

| Name | Required | Description |
|------|----------|-------------|
| `query` | yes | Search query, 1-128 characters. |
| `ori_question` | no | The user's original question (1-128 characters) that triggered the search. |
| `count` | no | Max results, 1-50 (default 10). |
| `need_content` | no | Include full extracted page content per result (default `false`). Increases payload size and latency. |

### `deepseek_web_fetch`

Fetch a single page through DeepSeek's fetch infrastructure and get `title` plus the body as Markdown. This plugin forwards only the URL; retrieval and extraction happen on DeepSeek's side.

| Name | Required | Description |
|------|----------|-------------|
| `url` | yes | HTTP/HTTPS URL, max 8192 characters, must include a host, no username/password. |

## Setup

1. Get an API key from [platform.deepseek.com](https://platform.deepseek.com/). Search and Fetch use the same key and the same account-level rate budget as the model API.
2. In Dify, install this plugin and enter the key in the plugin credentials.
3. Add the `deepseek_web_search` / `deepseek_web_fetch` tools to an Agent, Chatflow, or Workflow.

## Rate limits

- Search: 5 requests/second per account (independent quota).
- Fetch: 5 requests/second per account, plus per-target-domain limits.
- These quotas are account-level, independent of which API key is used, and independent of model concurrency limits.

## Source repository

<https://github.com/Jay0130-a/dify-plugins> (plugin source under `Jay0130-a/deepseek_search`).

## Contact

- GitHub: [@Jay0130-a](https://github.com/Jay0130-a)
- Email: 309071492+Jay0130-a@users.noreply.github.com (via GitHub)

## License

MIT

# iFlow Search

AI-native search tools for [Dify](https://dify.ai), backed by the official [iFlow Search API](https://platform.iflow.cn/). Three tools, one provider, bring your own API key.

## Tools

| Tool | Purpose |
|---|---|
| **iFlow Web Search** (`iflow_web_search`) | Ranked organic web results with title / URL / snippet. |
| **iFlow Image Search** (`iflow_image_search`) | Image hits with `image_url`, `source_url`, dimensions. |
| **iFlow Web Fetch** (`iflow_web_fetch`) | Fetch a URL and return cleaned main-content text. |

All three tools emit both a `json` artifact and a markdown-formatted `text` message, so they work cleanly in Agent nodes, Workflows, and tool-call results.

## Setup

1. Install this plugin from the Dify Marketplace.
2. Open the iFlow Search provider settings in Dify.
3. Paste your iFlow API key into **iFlow API Key**. The credential is stored as a secret; Dify never echoes it back.
4. Save. Dify validates the key by issuing a single 1-result web search.

Each user supplies their own iFlow API key — this plugin ships **no** default key and the publisher never sees user keys.

### Get an iFlow API key

Sign in at [https://platform.iflow.cn/](https://platform.iflow.cn/) and create an API key under your account.

## How it works

Under the hood the plugin uses the official [`iflow-search`](https://pypi.org/project/iflow-search/) Python SDK (≥ 0.1.0, < 0.2) and only calls these three documented endpoints:

* `POST /api/search/webSearch`
* `POST /api/search/imageSearch`
* `POST /api/search/webFetch`

Requests are stamped with attribution headers `IFlow-Source: dify` and `IFlow-Integration-Name: iflow-search-dify` so the iFlow team can attribute traffic correctly.

## Privacy

See [PRIVACY.md](./PRIVACY.md). Short version: the plugin forwards the query (or URL) you supply, plus your configured API key, to `api.iflow.cn`. It does not persist queries, results, or credentials anywhere outside of Dify itself.

## Source repository

[https://github.com/zhengyanglsun/iflow-search-py](https://github.com/zhengyanglsun/iflow-search-py)

## Contact

GitHub issues on the source repository above. For security reports, follow Dify's [security disclosure process](https://github.com/langgenius/dify-plugins#security-disclosure).

## License

MIT.

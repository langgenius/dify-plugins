# Privacy Policy — iFlow Search Plugin

This plugin connects Dify to the iFlow Search API using credentials configured by the Dify workspace user.

## Data sent to iFlow

When a tool from this plugin is invoked, the following data leaves your Dify deployment and is sent to `https://api.iflow.cn`:

* The **query string** you (or the calling LLM) supply for web search and image search.
* The **URL** you (or the calling LLM) supply for web fetch.
* The **iFlow API key** you configured in the provider credentials, sent as a Bearer token.
* Attribution headers identifying this client as `iflow-search-dify`. No personal information is included.

The plugin never sends prompts, chat history, user identifiers, or any data outside the specific query / URL parameter the user supplies to a tool.

## Data the plugin itself stores

This plugin **does not persist** queries, search results, fetched content, or your API key outside of the Dify runtime. Everything happens in-memory for the duration of a single tool invocation.

Dify itself may store tool inputs, outputs, and logs according to your Dify deployment's configuration; that is governed by Dify's own privacy policy, not by this plugin.

## Data iFlow may store

iFlow processes the queries / URLs you submit to provide search and fetch results, and may retain operational logs according to its own terms. Review iFlow's policies before enabling this plugin:

* iFlow platform: [https://platform.iflow.cn/](https://platform.iflow.cn/)

## Third-party processing

This plugin sends data only to iFlow's API at `api.iflow.cn`. It does not transmit data to any other third party.

## Credential handling

* The provider credential `iflow_api_key` is declared as a Dify `secret-input`. Dify encrypts it at rest and never echoes it back to clients.
* The plugin's error messages and logs never include the raw key value, length, prefix, suffix, or any other derivable form. SDK-level redaction is provided by the [`iflow-search`](https://pypi.org/project/iflow-search/) package's `_redact` module.
* Each Dify user supplies their own iFlow API key — the plugin publisher has no access to user keys.

## Contact

For privacy questions about this plugin, open an issue at:
[https://github.com/zhengyanglsun/iflow-search-py](https://github.com/zhengyanglsun/iflow-search-py)

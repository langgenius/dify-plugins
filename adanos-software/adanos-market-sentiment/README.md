# Adanos Market Sentiment for Dify

Read-only Dify tools for stock and crypto market sentiment from
[Adanos](https://adanos.org/). The plugin exposes structured JSON that agents,
chatflows, and workflows can use as research context.

## Tools

- **Get stock sentiment** from Reddit, X / FinTwit, financial news, or Polymarket.
- **Get crypto sentiment** from Reddit.
- **List trending assets** ranked by Adanos buzz score.
- **Get market sentiment** for an aggregate stock or crypto overview.

These tools provide attention and sentiment data. They do not place trades or
provide investment advice.

## Setup

1. Create an API key at [adanos.org/register](https://adanos.org/register).
2. Install this plugin from the Dify Marketplace.
3. Open **Tools > Adanos Market Sentiment > Authorize**.
4. Enter your `sk_live_...` API key.

Requests count against the quota of the connected Adanos account. Available
history and request quotas depend on that account's plan. See the
[Adanos API documentation](https://api.adanos.org/docs) for current limits and
response semantics.

## Development

```bash
uv sync --all-groups
uv run pytest -q
uv run ruff check .
```

The source is maintained at
[adanos-software/dify-plugin-adanos](https://github.com/adanos-software/dify-plugin-adanos).

## Privacy

See [PRIVACY.md](PRIVACY.md).

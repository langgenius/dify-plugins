# DianLeiDa 1688 Sourcing

A Dify tool plugin that connects Dify apps, agents and workflows to the DianLeiDa data platform for 1688 product sourcing.

- Author: `dianleida`
- Version: 1.1.0
- Type: Tool
- Provider: DianLeiDa - https://www.dianleida.net

The plugin exposes 16 sourcing tools over the DianLeiDa MCP server (JSON-RPC 2.0, Streamable HTTP) and returns real product data: images, wholesale and dropship prices, sales figures, shop metrics, qualification certificates, SKU stock and trend curves. A typical question such as "find fast-selling 1688 suppliers for phone cases under 5 RMB" becomes one tool call instead of a long manual search.

## Requirements

- A DianLeiDa MCP key URL. Register and copy your key at https://www.dianleida.net/mcp (documentation: https://www.dianleida.net/mcp/docs/).
- A Dify instance with plugin support. The plugin talks to the MCP endpoint over Streamable HTTP.

## Install and authorize

1. Install the plugin from the Dify Marketplace (search for `DianLeiDa`), or upload the `.difypkg` package in this repository through Plugins > Install plugin > Local package.
2. Open the plugin and choose Set up authorization.
3. Paste your DianLeiDa MCP key URL into the field.
4. Save. Dify verifies the key by calling `tools/list` on the MCP server; an invalid or expired key is rejected at this step.

## Tools

| Tool | What it does |
| --- | --- |
| `product_search_list` | Search 1688 products with price, sales, category and seller filters. |
| `cross_border_product_search_list` | Search products limited to the cross-border supply pool. |
| `product_info` | Monthly sales trend and 30-day summary for one product. |
| `product_billboard_list` | Weekly and monthly 1688 product rankings. |
| `shop_rank_list` | Five shop rankings with operating metrics. |
| `get_category_info` | Browse the 1688 category tree. |
| `image_search` | Submit one image to find 1688 candidates. |
| `global_image_search` | Cross-platform same-product search on 1688, TikTok and Amazon. |
| `ali_offer_realtime_detail` | Product attributes and qualification certificates. |
| `ali_offer_sku_prices` | All SKU prices and available stock for one product. |
| `product_trend_new_list` | Trending new products with growth indicators. |
| `monitor_offer_list` | Watchlist products with daily, 7-day and 30-day sales. |
| `monitor_shop_list` | Watchlist shops with sales and operating data. |
| `monitor_offer_add` | Add a product to the watchlist. |
| `monitor_shop_add` | Add a 1688 shop to the watchlist. |
| `monitor_shop_analysis` | Full supplier due-diligence report for one shop. |

## Using it in Dify

- Workflow: add a Tool node, pick the DianLeiDa tool you need, and map the upstream variables to its parameters. Every tool returns a JSON payload that downstream nodes can parse.
- Agent: attach the whole toolset to an agent so the model can choose search, analysis, ranking or monitoring tools itself.
- List tools default to `pageSize = 100`, the server-side maximum, so one call already returns a complete page.

## Credits

Each business call consumes 1 credit from your DianLeiDa MCP plan. `tools/list` during authorization does not consume credits. When the credit is exhausted the plugin returns a recharge link instead of an empty result.

## Error handling

- Insufficient credits: the plugin returns the recharge page link.
- Expired or invalid key: the plugin asks you to fetch a new key and update the authorization.
- Other upstream errors: the plugin surfaces the upstream message and never fabricates product data.

## Data and privacy

The plugin stores only the MCP key URL in Dify credential storage. It keeps no local files, no cache and no telemetry. Parameters you submit and data returned by the DianLeiDa API are sent to and from the endpoint in your key URL. DianLeiDa is an independent third-party service; see PRIVACY.md and https://www.dianleida.net for its data practices.

## Support

- Documentation: https://www.dianleida.net/mcp/docs/
- Product site: https://www.dianleida.net/mcp
- Email: 3373165051@qq.com
- Issues: please open an issue in this repository.

## Changelog

### 1.1.0

- Initial Dify Marketplace release: 16 sourcing tools, MCP Streamable HTTP transport, credit and key error handling.

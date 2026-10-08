# MingXi Export Control

A Dify plugin that provides access to China's export control lists, helping users check whether an item or entity is subject to Chinese export control regulations.

## Features

- **Dual-Use Item Query**: Search the Ministry of Commerce dual-use item export control list by ECCN/HS code, item name, or keyword.
- **Restricted Entity Query**: Search China's restricted entity lists (Control List / Unreliable Entity List / Entity List / Countermeasures List) by company name in Chinese or English.

## Prerequisites

1. A MingXi API key. Apply for one at [https://mingxiapi.cn](https://mingxiapi.cn).
2. The API is billed per call (5 points per query). A free trial tier is available.

## Setup

1. Install this plugin from the Dify Marketplace.
2. Open the plugin settings and enter your MingXi API key.
3. Save the credentials. The plugin validates the key against the MingXi API.

## Tools

### 1. Query Export Control Items (`item_query`)

Search China's dual-use item export control list.

**Parameters:**
- `keyword` (required): ECCN code, HS code, item name, or description.
- `top_k` (optional, default 5): Maximum number of results (1-20).
- `format` (optional, default "json"): "json" for structured data, "text" for human-readable summary.

**Example:**
```
keyword: "1C111"
```

### 2. Query Restricted Entities (`entity_query`)

Search China's restricted entity lists.

**Parameters:**
- `keyword` (required): Company or organization name (Chinese or English).
- `format` (optional, default "json"): "json" for structured data, "text" for human-readable summary.

**Example:**
```
keyword: "Anduril"
```

## Data Sources

All data is sourced from official Chinese government announcements:
- Ministry of Commerce (MOFCOM) export control announcements
- Ministry of Foreign Affairs (MFA) countermeasures decisions
- Data is updated regularly via automated monitoring

## Disclaimer

This plugin provides information retrieval only and does not constitute legal advice. For official compliance decisions, always consult the competent authorities.

## Source Code

- GitHub: [https://github.com/mingxi888888-cyber/dify-mcp-export-control-CN](https://github.com/mingxi888888-cyber/dify-mcp-export-control-CN)

## Support

- Website: [https://mingxiapi.cn](https://mingxiapi.cn)
- API Documentation: [https://api.mingxiapi.cn/docs](https://api.mingxiapi.cn/docs)
- Contact: Mingxi888888@gmail.com

# Anakin

**Author:** Anakin
**Version:** 0.0.1
**Type:** Tool Plugin

## Description

Anakin is a powerful web scraping and AI-powered search plugin for Dify. Built on the AnakinScraper API, it enables your AI applications to extract data from any website, perform intelligent web searches, and conduct deep research using advanced AI pipelines.

## Key Features

- **Anti-detection** - Proxy routing across 207 countries prevents blocking
- **Intelligent Caching** - Up to 30x faster on repeated requests
- **AI Extraction** - Convert any webpage into structured JSON
- **Browser Automation** - Full Playwright/headless Chrome support for SPAs
- **Session Management** - Authenticated scraping with encrypted session storage (AES-256-GCM)
- **Batch Processing** - Submit multiple URLs in a single request

## Setup

### 1. Get Your API Key

1. Sign up at [anakin.io](https://anakin.io/signup)
2. Go to your [Dashboard](https://anakin.io/dashboard)
3. Copy your API key (starts with `ask_`)

### 2. Configure in Dify

1. Install the Anakin plugin in your Dify workspace
2. Go to **Plugins** → **Anakin** → **Configure**
3. Enter a name for the authorization (e.g., "Production")
4. Paste your API key
5. Click **Save**

## Tools

### 1. URL Scraper

Scrapes a single URL, returning HTML, markdown, and optionally structured JSON.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | Target URL to scrape (HTTP/HTTPS) |
| country | string | No | "us" | Proxy location from 207 countries |
| use_browser | boolean | No | false | Enable headless Chrome for JavaScript-heavy sites |
| generate_json | boolean | No | false | Use AI to extract structured data |
| session_id | string | No | - | Browser session ID for authenticated pages |

**Response includes:**
- Raw HTML
- Cleaned HTML
- Markdown conversion
- Structured JSON (if `generate_json` enabled)
- Cache status
- Timing metrics

### 2. Batch URL Scraper

Scrape up to 10 URLs simultaneously in parallel.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| urls | string | Yes | - | Comma-separated list of URLs (1-10) |
| country | string | No | "us" | Proxy location from 207 countries |
| use_browser | boolean | No | false | Enable headless Chrome for JavaScript-heavy sites |
| generate_json | boolean | No | false | Use AI to extract structured data from each page |

### 3. AI Search

Synchronous AI-powered web search returning results with citations and relevance scoring.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| prompt | string | Yes | - | Search query or question |
| limit | number | No | 5 | Maximum results to return |

**Response includes:**
- Array of results with URLs, titles, snippets
- Publication dates
- Last updated timestamps

*Note: This is a synchronous endpoint - results are returned immediately without polling.*

### 4. Deep Research (Agentic Search)

Multi-stage automated research pipeline combining search, scraping, and AI synthesis.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | Yes | Research question or topic |

**Response includes:**
- AI-generated comprehensive answers
- Summaries
- Structured findings
- Citations with source URLs
- Scraped source data
- Processing metrics

*Note: This is an async operation that typically takes 1-5 minutes.*

### 5. Custom Web Scraper

Execute pre-configured scraper templates for domain-specific structured data extraction.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Yes | Target URL to scrape |
| scraper_code | string | Yes | Configuration identifier |
| scraper_params | string | No | JSON string of scraper-specific parameters |

**Response:** Structured JSON matching the scraper's defined schema.

## Usage Examples

### In a Workflow

1. Add a **Tool** node to your workflow
2. Select **Anakin** → Choose your tool
3. Configure parameters:
   - For URL Scraper: Enter the URL, enable `generate_json` for structured output
   - For AI Search: Enter your query
4. Connect to the next node for processing

### In an Agent

1. Create an Agent app
2. Add Anakin tools to the agent's toolset
3. The agent will automatically use scraping/search based on user queries

### Example: Scraping with AI Extraction

```
Tool: URL Scraper
URL: https://example.com/products
Generate JSON: true
```

Returns structured product data automatically extracted by AI.

### Example: Authenticated Scraping

```
Tool: URL Scraper
URL: https://example.com/dashboard
Session ID: your-session-id-from-dashboard
Use Browser: true
```

Scrapes pages that require login using your saved browser session.

## Processing Times

| Tool | Type | Typical Duration |
|------|------|------------------|
| URL Scraper | Async | 3-15 seconds |
| Batch Scraper | Async | 5-30 seconds |
| AI Search | **Sync** | Immediate |
| Deep Research | Async | 1-5 minutes |
| Custom Scraper | Async | 3-15 seconds |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Invalid parameters | Check your input |
| 401 | Invalid API key | Verify your API key |
| 402 | Plan upgrade required | Upgrade your Anakin plan |
| 404 | Job not found | Job may have expired |
| 429 | Rate limit exceeded | Wait and retry |
| 5xx | Server error | Retry with backoff |

## Country Codes

Proxy routing supports 207 countries. Common codes:
- `us` - United States (default)
- `uk` - United Kingdom
- `de` - Germany
- `fr` - France
- `jp` - Japan
- `au` - Australia

## Support

- **Source Code:** [GitHub Repository](https://github.com/Viraal-Bambori/dify-plugins/tree/main/anakin/anakin)
- **Website:** [anakin.io](https://anakin.io)
- **Documentation:** [anakin.io/llms-full.txt](https://anakin.io/llms-full.txt)
- **Dashboard:** [anakin.io/dashboard](https://anakin.io/dashboard)
- **Support:** support@anakin.io

## License

This plugin is provided by Anakin. Usage is subject to Anakin's [Terms of Service](https://anakin.io/terms) and [Privacy Policy](https://anakin.io/privacy).

# Olostep Plugin for Dify

## Overview

**Olostep** is a comprehensive Web Data API that provides powerful tools for AI agents and workflows. It enables web scraping, website crawling, URL discovery, web search, and AI-powered answers grounded in live data. With Olostep, you can extract structured data, discover website URLs, search the web, and get intelligent answers backed by real-time information.

## Configuration

To set up the Olostep plugin, follow these steps:

1. **Install Olostep Plugin**
Access the Plugin Marketplace, locate the Olostep plugin, and install it in your Dify workspace.

2. **Get Your Olostep API Key**
Go to the [Olostep Dashboard](https://www.olostep.com/dashboard/api-keys), sign in to your account, and generate a new API key. Make sure your account has sufficient credits.

3. **Authorize Olostep in Dify**
Navigate to **Tools > Olostep** in your Dify workspace, and input your API Key under the credentials section to enable the plugin.

## Tool Features

The Olostep plugin provides five powerful tools for web data extraction and searching:

### Scrape URL

Extract content from a single URL and get it in multiple formats (Markdown, HTML, text, or structured JSON). Handles JavaScript-rendered sites and supports advanced options like geo-location and custom parsers.

**Key Parameters:**
- `URL` - The webpage to scrape (required)
- `Format` - Output format: markdown, html, text, or json (default: markdown)
- `Country` - Two-letter country code for geo-location (e.g., us, gb, de)
- `Parser ID` - Pre-built parsers for structured extraction (@olostep/google-search, @olostep/amazon-it-product, @olostep/extract-emails, etc.)
- `Wait (ms)` - Milliseconds to wait after page load for JavaScript rendering

### Crawl Website

Recursively crawl an entire website and extract content from all discovered pages. Perfect for comprehensive data collection from multi-page sites.

**Key Parameters:**
- `URL` - Starting URL for the crawl (required)
- `Max Pages` - Maximum pages to crawl, up to 1000 (default: 20)
- `Include URLs` - Glob patterns to include in the crawl (e.g., /blog/**, /docs/**)
- `Exclude URLs` - Glob patterns to exclude from crawl (e.g., /admin/**)
- `Search Query` - Filter crawled pages by relevance to a search query

### Map Website

Discover all available URLs on a website by analyzing sitemaps and discovered links. Useful for understanding a website's structure.

**Key Parameters:**
- `URL` - Website to map (required)
- `Include URLs` - Glob patterns to include in the mapping
- `Exclude URLs` - Glob patterns to exclude from mapping
- `Top N` - Maximum number of URLs to return (default: 100)

### Search Web

Perform natural language web searches and get ranked results with titles, URLs, and descriptions. Access the latest information from the internet.

**Key Parameters:**
- `Query` - Natural language search query (required)

### AI Answer

Search the web and get an AI-synthesized answer grounded in live data with source citations. Returns structured JSON when a schema is provided.

**Key Parameters:**
- `Task` - The question or research task (required)
- `JSON Schema` - Optional JSON schema for structured output (e.g., `{"ceo": "", "founded": "", "valuation": ""}`)

## Usage

The Olostep plugin seamlessly integrates into **Chatflow / Workflow Apps** and **Agent Apps**.

### Chatflow / Workflow Apps

Integrate Olostep into your data extraction pipeline:

1. Add an Olostep node to your Chatflow or Workflow.
2. Select the desired Olostep action (Scrape, Crawl, Map, Search, or Answer).
3. Configure the input parameters based on your use case.
4. Execute the workflow to trigger the Olostep nodes and extract web data.

### Agent Apps

Add Olostep tools to your AI Agent for real-time web intelligence:

1. Add one or more Olostep tools to your Agent application.
2. The agent can now:
   - **Scrape URLs** - Extract content from specific web pages
   - **Crawl websites** - Gather comprehensive data from multiple pages
   - **Map websites** - Understand site structure and discover URLs
   - **Search the web** - Find relevant information on any topic
   - **Get AI answers** - Get intelligent, sourced answers to questions

3. The extracted data is processed and made available to the LLM, enabling your agent to access real-time web information and make informed decisions.

## Example Use Cases

- **Market Research** - Scrape competitor websites and search for industry trends
- **Content Monitoring** - Crawl news sites and extract the latest articles
- **Lead Generation** - Search and map business websites to gather contact information
- **Data Extraction** - Parse structured data from web pages using custom parsers
- **Research Assistant** - Get AI-powered answers grounded in live web data
- **SEO Analysis** - Map website structure and discover all available URLs

## Support

For issues or questions about the Olostep plugin:
- Visit the [Olostep Documentation](https://www.olostep.com/docs)
- Check your account at [Olostep Dashboard](https://www.olostep.com/dashboard)
- Review API Key status and credit balance

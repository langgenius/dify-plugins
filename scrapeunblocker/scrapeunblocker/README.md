# ScrapeUnblocker

**Author:** scrapeunblocker
**Version:** 0.0.1
**Type:** tool

## Description

ScrapeUnblocker renders web pages in a real browser behind anti-bot protections
such as Cloudflare, DataDome, PerimeterX and Akamai, and returns the result to
your Dify workflow.

Use it when an ordinary HTTP request gets a block page, a captcha, or an empty
shell instead of the content: e-commerce listings, travel sites, marketplaces,
classifieds, and other pages that only render for a real browser.

## Tools

### Get Page Source

Fetches a single page and returns its fully rendered content.

| Parameter | Required | Description |
| --- | --- | --- |
| `url` | yes | Full URL of the page to fetch, including the scheme |
| `parsed_data` | no | Return AI-parsed structured JSON instead of raw HTML |
| `proxy_country` | no | Two-letter country code for the exit IP, for geo-restricted content |

Returns the page content as a text message, plus a JSON message with `success`,
`url`, `parsed_data` and `content_length`.

### Search Google

Scrapes a Google search results page and returns the organic results.

| Parameter | Required | Description |
| --- | --- | --- |
| `keyword` | yes | The search term to look up |
| `pages_to_check` | no | How many result pages to scrape (default 1) |
| `proxy_country` | no | Two-letter country code for country-specific results |

Each organic result carries `title`, `url`, `description` and `position`.

## Setup

1. Get an API key at [scrapeunblocker.com](https://www.scrapeunblocker.com).
2. Install the plugin and open its settings.
3. Paste the key into **ScrapeUnblocker API Key**.

Two optional settings are available: **API Base URL** (override to point at a
different environment) and **Timeout Seconds** (default 180, since rendering a
protected page in a browser takes longer than a plain HTTP request).

## Notes

- Requests are made by ScrapeUnblocker's infrastructure, so the target site sees
  a ScrapeUnblocker IP rather than your Dify host. See [PRIVACY.md](PRIVACY.md)
  for exactly what data leaves your instance.
- Rendering a protected page typically takes several seconds. Keep this in mind
  when placing the tool in latency-sensitive workflows.

## Links

- Website: https://www.scrapeunblocker.com
- API documentation: https://developers.scrapeunblocker.com

# Recursive Web Crawler

Recursively crawl web pages from a starting URL for use in Dify workflows.

## Features

- Crawl from a starting URL with configurable depth
- Returns structured JSON per page (title, main content as Markdown, links, metadata)
- Same-domain restriction, max-page limits, and URL include patterns
- Tolerant of self-signed intranet certificates

## Usage

Add the **Web Crawler** tool to your Dify workflow, provide a starting URL and crawl depth, and receive structured page data.

## Network & Privacy

This plugin sends HTTP requests to the URLs you provide and fetches their content. The fetched web pages are processed within your Dify runtime and are not sent to any third-party service by the plugin. You are responsible for ensuring you have permission to crawl the target sites. See `PRIVACY.md` for details.

# SerpKite for Dify

Search Google web and news with [SerpKite](https://serpkite.com). Both tools emit the complete structured API response as JSON and readable Markdown with titles, links, and snippets.

Source: https://github.com/SerpKite/dify-serpkite
Contact: support@serpkite.com

## Setup

1. Install the `.difypkg` file from this repository into Dify's **Plugins → Install from local package**. Marketplace publication is a separate reviewed submission.
2. Create a SerpKite account at https://app.serpkite.com and create an API key.
3. Authorize the SerpKite provider with the full `skt_live_...` key.
4. Add **Web Search** or **News Search** to an agent or workflow. Supply a query and optional country, language, and number of results.

Credential validation calls `GET /v1/account` and does not perform a paid search. The plugin needs outbound HTTPS access to `api.serpkite.com`. It uses fixed API destinations with 30-second credential-check and 90-second search timeouts.

## Outputs and billing

The JSON output preserves `results` and `meta`. The text output is Markdown; empty results emit `No results found.` API failures stop the tool with an actionable error, rather than a successful result containing an error message.

Search defaults to 10 requested results. Counts up to 100 round up to whole pages and cost one credit per page returned, capped at seven credits. Empty and failed searches are not billed. See https://serpkite.com/docs for current API behavior.

## Privacy

See [PRIVACY.md](PRIVACY.md). Queries and localization options are sent to SerpKite to execute searches. The plugin does not log queries, keys, responses, or request URLs and does not create persistent storage. Dify's own workflow history and retention policies apply independently.

## Development and validation

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt pytest pyyaml
.venv/bin/python -m pytest tests
# Package with the official Dify plugin CLI:
dify plugin package .
```

Tests mock HTTP requests, consuming no credits. Live Dify Cloud/Community Edition installation has not yet been verified; the Marketplace PR documents this limitation.

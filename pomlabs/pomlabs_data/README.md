# Pom Labs Data (Dify tool plugin)

Public social and web data as clean JSON, with one API key and no login to the source sites.

Tools: YouTube comments, YouTube transcript, Instagram/TikTok/Facebook video transcript, Instagram profile, LinkedIn company, LinkedIn profile, Reddit search, subreddit posts, Threads search, Google Ads Transparency.

## Setup
1. Get a key (free plan on every API): https://rapidapi.com/user/pomlabs
2. In Dify: Plugins, install Pom Labs Data, authorize with the key (sent as `X-API-Key`).

Every answer is `{"items": [...], "meta": {...}}`. An item whose `status` is not `ok` explains the problem in `error`.

Full API (37 endpoints, OpenAPI): https://pom-data-api.pomlabs.workers.dev/openapi.json

## Source and contact
- Source repository: https://github.com/pomexplica/pomlabs (folder `dify-plugin/`)
- Contact: pomexplica@gmail.com

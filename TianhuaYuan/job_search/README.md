# Job Search

Search remote job listings from the [Jobicy](https://jobicy.com/) and
[Remotive](https://remotive.com/) free, public APIs. **No API key required.**

This plugin provides a single tool, `search_jobs`, that returns a structured
list of matching jobs (title, company, location, job type, salary when
available, and an apply link) plus a human-readable summary.

## Installation

Install from the [Dify Marketplace](https://marketplace.dify.ai/) or load the
`.difypkg` file directly in Dify:

1. Go to **Plugins** in your Dify workspace.
2. Click **Add plugin** → **Install from local package file**.
3. Select `job_search-0.0.1.difypkg`.

No configuration or API keys are needed.

## Usage

Invoke the `search_jobs` tool from a Chatflow, Workflow, or Agent node and
describe what you are looking for. The tool accepts:

| Parameter  | Type    | Default  | Description |
| ---------- | ------- | -------- | ----------- |
| `query`    | string  | —        | Keyword matched against job titles and company names, e.g. `python` or `machine learning` |
| `source`   | select  | `jobicy` | Job board to query: `jobicy` or `remotive` |
| `location` | string  | —        | Location filter, e.g. `Europe` or `USA` |
| `category` | string  | —        | Category or tag, e.g. `python`, `design`, `marketing` (Jobicy `tag`), or `Software Development` (Remotive category) |
| `job_type` | string  | —        | Employment type, e.g. `full-time`, `part-time`, `contract`, `internship` |
| `count`    | number  | 10       | Maximum results (1–50) |

### Examples

- "Find 10 python jobs on Jobicy"
- "Search for remote design jobs in Europe on Remotive"
- "Show me full-time marketing jobs"

## Data sources

| Source    | Description | Notes |
| --------- | ----------- | ----- |
| **Jobicy** | Remote-only job board | Supports the `category` tag and `count`. Jobicy requires that it is credited and that apply buttons link back to the original job URL. |
| **Remotive** | Remote job feed | Returns salary and structured categories when available. Filtering happens locally on the fetched feed, so `count` is applied after filtering. |

The underlying APIs are free and require no authentication.

## Source code

- Repository: <https://github.com/TianhuaYuan/dify-plugins/tree/main/TianhuaYuan/job_search>
- Author: Tianhua Yuan (<https://github.com/TianhuaYuan>)

## Privacy

This plugin sends only your search criteria to the selected job board API and
stores no data. See [PRIVACY.md](./PRIVACY.md) for details.

## License

MIT

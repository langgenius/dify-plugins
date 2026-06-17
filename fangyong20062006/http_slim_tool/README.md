# HTTP Big-Data Slimmer for LLM

Slim, filter and paginate large HTTP responses before sending them to an LLM, to avoid token limits.

## Features

- **Paginated fetch**: retrieve data from an HTTP endpoint using offset / page / cursor modes
- **Field slimming**: keep only the specified fields from a response
- **Smart summary**: group / count / Top-N statistics over the data

## Usage

Add the tools to your Dify workflow. For paginated fetch, provide the target URL and pagination parameters; for slimming/summary, pass in the data to be processed.

## Network & Privacy

The paginated-fetch tool sends HTTP GET requests to the URL you provide. Field-slimming and summary tools process data locally. The plugin does not send your data to any third-party service. See `PRIVACY.md` for details.

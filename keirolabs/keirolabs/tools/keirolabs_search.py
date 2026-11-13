from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

KEIROLABS_SEARCH_URL = "https://api.keirolabs.cloud/api/v2/search/lite"


def search(api_key: str, query: str, max_results: int, domains: list[str] | None = None) -> list[dict[str, str]]:
    """Call Keirolabs lite search and return [{title, url, snippet}]."""
    if not api_key:
        raise ValueError("Keirolabs API key is required")
    if domains:
        query = f"({query}) ({' OR '.join(f'site:{d}' for d in domains)})"
    response = requests.post(
        KEIROLABS_SEARCH_URL,
        json={"query": query, "maxResults": max_results},
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        try:
            detail = response.json().get("error") or response.text
        except ValueError:
            detail = response.text
        raise ValueError(f"Keirolabs search failed (HTTP {response.status_code}): {detail}")
    results = [
        {"title": r.get("title") or "", "url": r["url"], "snippet": r.get("snippet") or ""}
        for r in response.json().get("results") or []
        if r.get("url")
    ]
    return results[:max_results]


class KeirolabsSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = (tool_parameters.get("query") or "").strip()
        if not query:
            raise ValueError("Search query is required")
        max_results = min(max(int(tool_parameters.get("max_results") or 10), 1), 15)
        domains = [d.strip() for d in (tool_parameters.get("include_domains") or "").split(",") if d.strip()]

        results = search(self.runtime.credentials["keirolabs_api_key"], query, max_results, domains)

        yield self.create_json_message({"results": results})
        if results:
            text = "\n\n".join(f"{i}. {r['title']}\n{r['url']}\n{r['snippet']}" for i, r in enumerate(results, 1))
        else:
            text = "No results found."
        yield self.create_text_message(text)

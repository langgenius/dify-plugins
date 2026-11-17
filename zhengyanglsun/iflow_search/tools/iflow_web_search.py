from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import build_client
from ._errors import friendly_error_message


class IFlowWebSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("iflow_api_key")
        if not api_key:
            yield self.create_text_message(
                "iFlow API Key is not configured. Set it in the plugin credentials."
            )
            return

        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return

        count = _coerce_count(tool_parameters.get("count"))

        try:
            with build_client(api_key=api_key) as client:
                response = client.web_search(query=query, count=count)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        results = [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "position": r.position,
                "date": r.date,
            }
            for r in response.results
        ]
        payload = {
            "query": response.query or query,
            "count": len(results),
            "took_ms": response.took_ms,
            "results": results,
        }
        yield self.create_json_message(payload)
        yield self.create_text_message(_format_web_results(payload))


def _coerce_count(raw: Any) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    if n < 1:
        return 1
    if n > 20:
        return 20
    return n


def _format_web_results(payload: dict[str, Any]) -> str:
    results = payload.get("results") or []
    if not results:
        return f"No iFlow results for '{payload.get('query', '')}'."
    lines: list[str] = [f"# iFlow web search: {payload.get('query', '')}\n"]
    for idx, r in enumerate(results, 1):
        title = r.get("title") or "(no title)"
        url = r.get("url") or ""
        snippet = r.get("snippet") or ""
        lines.append(f"{idx}. [{title}]({url})")
        if snippet:
            lines.append(f"   {snippet}")
    return "\n".join(lines)

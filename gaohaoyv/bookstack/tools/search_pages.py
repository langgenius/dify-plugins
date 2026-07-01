from __future__ import annotations

from collections.abc import Generator
from typing import Any

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
except ImportError:  # pragma: no cover - allows helper imports in unit tests
    Tool = object
    ToolInvokeMessage = Any

from bookstack_client import BookStackClient, BookStackError
from tools.output_payloads import collection_error, collection_success, emit_variable_messages


def normalize_search_page_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "raw": raw,
    }


class SearchPagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = str(tool_parameters.get("query", "")).strip()
        if not query:
            yield from emit_variable_messages(self, collection_error("results", "query is required"))
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_results = client.search_pages(query)
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("results", str(exc)))
            return

        yield from emit_variable_messages(
            self,
            collection_success(
                "results",
                [normalize_search_page_result(item) for item in raw_results],
            )
        )

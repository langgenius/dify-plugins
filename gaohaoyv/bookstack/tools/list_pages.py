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


def normalize_page_list_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name"),
        "slug": raw.get("slug"),
        "book_id": raw.get("book_id"),
        "chapter_id": raw.get("chapter_id"),
        "url": raw.get("url"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "raw": raw,
    }


class ListPagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        count = tool_parameters.get("count")
        offset = tool_parameters.get("offset")

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_pages(count=count, offset=offset)
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("pages", str(exc), include_total=True))
            return

        raw_pages = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "pages",
                [normalize_page_list_result(item) for item in raw_pages],
                total=total,
            )
        )

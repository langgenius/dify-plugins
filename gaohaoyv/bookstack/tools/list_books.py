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
from tools.output_payloads import collection_error, collection_success


def normalize_book_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "book_id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "description": raw.get("description"),
        "url": raw.get("url"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "raw": raw,
    }


class ListBooksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        count = tool_parameters.get("count")
        offset = tool_parameters.get("offset")

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_books(count=count, offset=offset)
        except BookStackError as exc:
            error_payload = collection_error("books", str(exc), include_total=True)
            for field_name in ("success", "error", "books", "count", "total"):
                yield self.create_variable_message(field_name, error_payload[field_name])
            return

        raw_books = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        success_payload = collection_success(
            "books",
            [normalize_book_result(item) for item in raw_books],
            total=total,
        )
        for field_name in ("success", "error", "books", "count", "total"):
            yield self.create_variable_message(field_name, success_payload[field_name])

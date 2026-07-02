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
from tools.output_payloads import emit_variable_messages, object_error, success_payload


def normalize_book_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "book_id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "description": raw.get("description"),
        "description_html": raw.get("description_html"),
        "url": raw.get("url"),
        "tags": raw.get("tags"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "created_by": raw.get("created_by"),
        "updated_by": raw.get("updated_by"),
        "raw": raw,
    }


class GetBookTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        book_id = str(tool_parameters.get("book_id", "")).strip()
        if not book_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "book_id is required",
                    "book_id",
                    "name",
                    "slug",
                    "description",
                    "description_html",
                    "url",
                    "tags",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_book = client.get_book(book_id)
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
                    "book_id",
                    "name",
                    "slug",
                    "description",
                    "description_html",
                    "url",
                    "tags",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(self, success_payload(**normalize_book_result(raw_book)))

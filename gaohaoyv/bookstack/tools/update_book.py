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
from tools.get_book import normalize_book_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload
from tools.resource_inputs import normalize_optional_string, normalize_optional_tags


def normalize_updated_book_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {**normalize_book_result(raw), "action": "updated"}


class UpdateBookTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        book_id = str(tool_parameters.get("book_id", "")).strip()

        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(
                self,
                object_error(
                    error,
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
                    "action",
                    "raw",
                ),
            )

        if not book_id:
            yield from emit_error("book_id is required")
            return

        updates: dict[str, Any] = {}
        if "name" in tool_parameters:
            normalized_name = str(tool_parameters.get("name", "")).strip()
            if not normalized_name:
                yield from emit_error("name must not be empty")
                return
            updates["name"] = normalized_name
        if "description" in tool_parameters:
            updates["description"] = normalize_optional_string(tool_parameters.get("description"))
        if "description_html" in tool_parameters:
            updates["description_html"] = normalize_optional_string(tool_parameters.get("description_html"))
        if "tags" in tool_parameters:
            updates["tags"] = normalize_optional_tags(tool_parameters.get("tags"))

        if not any(value is not None for value in updates.values()):
            yield from emit_error("at least one update field is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_book = client.update_book(book_id, **updates)
        except (ValueError, BookStackError) as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_updated_book_result(raw_book)))

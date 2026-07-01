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
from tools.get_shelf import normalize_shelf_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload
from tools.resource_inputs import normalize_optional_integer_list, normalize_optional_string, normalize_optional_tags


def normalize_updated_shelf_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {**normalize_shelf_result(raw), "action": "updated"}


class UpdateShelfTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        shelf_id = str(tool_parameters.get("shelf_id", "")).strip()

        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(
                self,
                object_error(
                    error,
                    "shelf_id",
                    "name",
                    "slug",
                    "description",
                    "description_html",
                    "books",
                    "tags",
                    "url",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "action",
                    "raw",
                ),
            )

        if not shelf_id:
            yield from emit_error("shelf_id is required")
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
        if "books" in tool_parameters:
            try:
                updates["books"] = normalize_optional_integer_list(tool_parameters.get("books"), "books")
            except ValueError as exc:
                yield from emit_error(str(exc))
                return
        if "tags" in tool_parameters:
            try:
                updates["tags"] = normalize_optional_tags(tool_parameters.get("tags"))
            except ValueError as exc:
                yield from emit_error(str(exc))
                return

        if not any(value is not None for value in updates.values()):
            yield from emit_error("at least one update field is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_shelf = client.update_shelf(shelf_id, **updates)
        except (ValueError, BookStackError) as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_updated_shelf_result(raw_shelf)))

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
from tools.list_shelves import normalize_shelf_result as normalize_list_shelf_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload


def normalize_shelf_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        **normalize_list_shelf_result(raw),
        "description_html": raw.get("description_html"),
        "books": raw.get("books"),
        "tags": raw.get("tags"),
        "created_by": raw.get("created_by"),
        "updated_by": raw.get("updated_by"),
    }


class GetShelfTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        shelf_id = str(tool_parameters.get("shelf_id", "")).strip()
        if not shelf_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "shelf_id is required",
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
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_shelf = client.get_shelf(shelf_id)
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
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
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(self, success_payload(**normalize_shelf_result(raw_shelf)))

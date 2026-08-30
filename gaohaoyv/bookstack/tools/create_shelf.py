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
from tools.resource_inputs import (
    normalize_optional_integer_list,
    normalize_optional_string,
    normalize_optional_tags,
    normalize_required_string,
)


def normalize_created_shelf_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {**normalize_shelf_result(raw), "action": "created"}


class CreateShelfTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
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

        try:
            name = normalize_required_string(tool_parameters.get("name"), "name")
            description = normalize_optional_string(tool_parameters.get("description"))
            description_html = normalize_optional_string(tool_parameters.get("description_html"))
            books = (
                normalize_optional_integer_list(tool_parameters.get("books"), "books")
                if "books" in tool_parameters
                else None
            )
            tags = normalize_optional_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_shelf = client.create_shelf(
                name=name,
                description=description,
                description_html=description_html,
                books=books,
                tags=tags,
            )
        except (ValueError, BookStackError) as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_created_shelf_result(raw_shelf)))

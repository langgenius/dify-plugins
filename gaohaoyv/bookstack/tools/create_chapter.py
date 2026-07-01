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
from tools.get_chapter import normalize_chapter_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload
from tools.resource_inputs import (
    normalize_optional_integer,
    normalize_optional_string,
    normalize_optional_tags,
    normalize_required_string,
)


def normalize_created_chapter_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {**normalize_chapter_result(raw), "action": "created"}


class CreateChapterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(
                self,
                object_error(
                    error,
                    "chapter_id",
                    "name",
                    "slug",
                    "book_id",
                    "description",
                    "description_html",
                    "priority",
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

        try:
            book_id = normalize_required_string(tool_parameters.get("book_id"), "book_id")
            name = normalize_required_string(tool_parameters.get("name"), "name")
            description = normalize_optional_string(tool_parameters.get("description"))
            description_html = normalize_optional_string(tool_parameters.get("description_html"))
            priority = normalize_optional_integer(tool_parameters.get("priority"), "priority")
            tags = normalize_optional_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_chapter = client.create_chapter(
                book_id=book_id,
                name=name,
                description=description,
                description_html=description_html,
                tags=tags,
                priority=priority,
            )
        except (ValueError, BookStackError) as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_created_chapter_result(raw_chapter)))

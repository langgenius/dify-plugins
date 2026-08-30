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


def normalize_chapter_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "chapter_id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "book_id": raw.get("book_id"),
        "description": raw.get("description"),
        "description_html": raw.get("description_html"),
        "priority": raw.get("priority"),
        "url": raw.get("url"),
        "tags": raw.get("tags"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "created_by": raw.get("created_by"),
        "updated_by": raw.get("updated_by"),
        "raw": raw,
    }


class GetChapterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        chapter_id = str(tool_parameters.get("chapter_id", "")).strip()
        if not chapter_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "chapter_id is required",
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
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_chapter = client.get_chapter(chapter_id)
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
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
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(self, success_payload(**normalize_chapter_result(raw_chapter)))

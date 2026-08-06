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
from tools.page_inputs import normalize_tags


def normalize_created_page_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "action": "created",
        "raw": raw,
    }


class CreatePageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        title = str(tool_parameters.get("title", "")).strip()
        markdown = str(tool_parameters.get("markdown", "")).strip()
        book_id = tool_parameters.get("book_id")
        chapter_id = tool_parameters.get("chapter_id")
        tags = normalize_tags(tool_parameters.get("tags"))

        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(self, object_error(error, "page_id", "title", "url", "action", "raw"))

        if not title:
            yield from emit_error("title is required")
            return

        if not markdown:
            yield from emit_error("markdown is required")
            return

        if book_id in {None, ""} and chapter_id in {None, ""}:
            yield from emit_error("book_id or chapter_id is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_page = client.create_page(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id if book_id not in {None, ""} else None,
                chapter_id=chapter_id if chapter_id not in {None, ""} else None,
            )
        except BookStackError as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_created_page_result(raw_page)))

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


def normalize_updated_page_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "action": "updated",
        "raw": raw,
    }


class UpdatePageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        page_id = str(tool_parameters.get("page_id", "")).strip()
        title = tool_parameters.get("title")
        markdown = tool_parameters.get("markdown")
        book_id = tool_parameters.get("book_id")
        chapter_id = tool_parameters.get("chapter_id")
        tags = normalize_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None

        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(self, object_error(error, "page_id", "title", "url", "action", "raw"))

        if not page_id:
            yield from emit_error("page_id is required")
            return

        updates: dict[str, Any] = {}
        if title is not None:
            normalized_title = str(title).strip()
            if not normalized_title:
                yield from emit_error("title must not be empty")
                return
            updates["title"] = normalized_title
        if markdown is not None:
            updates["markdown"] = str(markdown)
        if "tags" in tool_parameters:
            updates["tags"] = tags
        if book_id not in {None, ""}:
            updates["book_id"] = book_id
        if chapter_id not in {None, ""}:
            updates["chapter_id"] = chapter_id

        if not updates:
            yield from emit_error("at least one update field is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_page = client.update_page(page_id, **updates)
        except BookStackError as exc:
            yield from emit_error(str(exc))
            return

        yield from emit_variable_messages(self, success_payload(**normalize_updated_page_result(raw_page)))

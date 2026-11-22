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


def normalize_export_page_markdown_result(raw: dict[str, Any]) -> dict[str, Any]:
    markdown = raw.get("markdown") or raw.get("body") or ""
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "markdown": markdown,
        "content_format": "markdown",
        "book_id": raw.get("book_id"),
        "chapter_id": raw.get("chapter_id"),
        "slug": raw.get("slug"),
        "raw": raw,
    }


class ExportPageMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        page_id = str(tool_parameters.get("page_id", "")).strip()
        if not page_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "page_id is required",
                    "page_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "book_id",
                    "chapter_id",
                    "slug",
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_page = client.get_page(page_id)
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
                    "page_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "book_id",
                    "chapter_id",
                    "slug",
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(self, success_payload(**normalize_export_page_markdown_result(raw_page)))

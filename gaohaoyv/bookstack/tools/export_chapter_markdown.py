from __future__ import annotations

from collections.abc import Generator
from typing import Any

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
except ImportError:  # pragma: no cover - allows helper imports in unit tests
    Tool = object
    ToolInvokeMessage = Any

from bookstack_client import BookStackClient, BookStackError, InvalidResponseError
from tools.export_page_markdown import normalize_export_page_markdown_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload


def normalize_export_chapter_markdown_result(raw: dict[str, Any], markdown: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "chapter_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "markdown": markdown,
        "content_format": "markdown",
        "book_id": raw.get("book_id"),
        "pages": pages,
        "raw": raw,
    }


def _require_page_ids(raw_pages: Any) -> list[str]:
    if not isinstance(raw_pages, list):
        raise InvalidResponseError("Invalid BookStack response")

    page_ids: list[str] = []
    for raw_page in raw_pages:
        if not isinstance(raw_page, dict):
            raise InvalidResponseError("Invalid BookStack response")

        page_id = raw_page.get("id")
        if page_id in {None, ""}:
            raise InvalidResponseError("Invalid BookStack response")
        page_ids.append(str(page_id))

    return page_ids


class ExportChapterMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        chapter_id = str(tool_parameters.get("chapter_id", "")).strip()
        if not chapter_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "chapter_id is required",
                    "chapter_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "book_id",
                    "pages",
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_chapter = client.get_chapter(chapter_id)
            markdown = client.export_chapter_markdown(chapter_id)
            page_ids = _require_page_ids(raw_chapter.get("pages"))
            pages = [normalize_export_page_markdown_result(client.get_page(page_id)) for page_id in page_ids]
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
                    "chapter_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "book_id",
                    "pages",
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(
            self,
            success_payload(**normalize_export_chapter_markdown_result(raw_chapter, markdown, pages)),
        )

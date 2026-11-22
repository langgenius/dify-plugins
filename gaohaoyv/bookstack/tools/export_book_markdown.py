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


def normalize_export_book_markdown_result(raw: dict[str, Any], markdown: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "book_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "markdown": markdown,
        "content_format": "markdown",
        "pages": pages,
        "raw": raw,
    }


def _collect_page_ids_from_book_contents(raw_contents: Any) -> list[str]:
    if not isinstance(raw_contents, list):
        raise InvalidResponseError("Invalid BookStack response")

    page_ids: list[str] = []

    def visit(items: list[Any]) -> None:
        for item in items:
            if not isinstance(item, dict):
                raise InvalidResponseError("Invalid BookStack response")

            item_type = item.get("type")
            if item_type == "chapter":
                nested_pages = item.get("pages")
                if not isinstance(nested_pages, list):
                    raise InvalidResponseError("Invalid BookStack response")
                visit(nested_pages)
                continue

            if item_type != "page":
                raise InvalidResponseError("Invalid BookStack response")

            page_id = item.get("id")
            if page_id in {None, ""}:
                raise InvalidResponseError("Invalid BookStack response")
            page_ids.append(str(page_id))

    visit(raw_contents)
    return page_ids


class ExportBookMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        book_id = str(tool_parameters.get("book_id", "")).strip()
        if not book_id:
            yield from emit_variable_messages(
                self,
                object_error(
                    "book_id is required",
                    "book_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "pages",
                    "raw",
                ),
            )
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_book = client.get_book(book_id)
            markdown = client.export_book_markdown(book_id)
            page_ids = _collect_page_ids_from_book_contents(raw_book.get("contents"))
            pages = [normalize_export_page_markdown_result(client.get_page(page_id)) for page_id in page_ids]
        except BookStackError as exc:
            yield from emit_variable_messages(
                self,
                object_error(
                    str(exc),
                    "book_id",
                    "title",
                    "url",
                    "markdown",
                    "content_format",
                    "pages",
                    "raw",
                ),
            )
            return

        yield from emit_variable_messages(
            self,
            success_payload(**normalize_export_book_markdown_result(raw_book, markdown, pages)),
        )

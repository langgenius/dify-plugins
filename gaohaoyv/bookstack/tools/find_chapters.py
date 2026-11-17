from __future__ import annotations

from collections.abc import Generator
from typing import Any

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
except ImportError:  # pragma: no cover - allows helper imports in unit tests
    Tool = object
    ToolInvokeMessage = Any

from bookstack_client import BookStackClient, BookStackError, normalize_find_match
from tools.list_chapters import normalize_chapter_result
from tools.output_payloads import collection_error, collection_success, emit_variable_messages


class FindChaptersTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        name = str(tool_parameters.get("name", "")).strip()
        if not name:
            yield from emit_variable_messages(self, collection_error("chapters", "name is required", include_total=True))
            return

        try:
            match = normalize_find_match(tool_parameters.get("match"))
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.find_chapters(
                name,
                match=match,
                book_id=tool_parameters.get("book_id"),
                count=tool_parameters.get("count"),
                offset=tool_parameters.get("offset"),
            )
        except ValueError as exc:
            yield from emit_variable_messages(self, collection_error("chapters", str(exc), include_total=True))
            return
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("chapters", str(exc), include_total=True))
            return

        raw_chapters = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "chapters",
                [normalize_chapter_result(item) for item in raw_chapters],
                total=total,
            ),
        )

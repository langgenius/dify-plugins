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
from tools.output_payloads import collection_error, collection_success, emit_variable_messages


def normalize_shelf_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "shelf_id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "description": raw.get("description"),
        "url": raw.get("url"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "raw": raw,
    }


class ListShelvesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        count = tool_parameters.get("count")
        offset = tool_parameters.get("offset")
        sort = tool_parameters.get("sort")
        filters = tool_parameters.get("filters")

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_shelves(count=count, offset=offset, sort=sort, filters=filters)
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("shelves", str(exc), include_total=True))
            return

        raw_shelves = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "shelves",
                [normalize_shelf_result(item) for item in raw_shelves],
                total=total,
            )
        )

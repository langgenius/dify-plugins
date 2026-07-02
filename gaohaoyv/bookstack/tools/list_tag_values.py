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


def normalize_tag_value_result(raw: Any, *, name: str) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {
            "name": raw.get("name") or name,
            "value": raw.get("value"),
            "raw": raw,
        }

    return {
        "name": name,
        "value": raw,
        "raw": raw,
    }


class ListTagValuesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        name = str(tool_parameters.get("name", "")).strip()
        if not name:
            yield from emit_variable_messages(self, collection_error("tag_values", "name is required", include_total=True))
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_tag_values(
                name,
                count=tool_parameters.get("count"),
                offset=tool_parameters.get("offset"),
            )
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("tag_values", str(exc), include_total=True))
            return

        raw_tag_values = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "tag_values",
                [normalize_tag_value_result(item, name=name) for item in raw_tag_values],
                total=total,
            ),
        )

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


def normalize_tag_name_result(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {
            "name": raw.get("name") or raw.get("value"),
            "raw": raw,
        }

    return {
        "name": raw,
        "raw": raw,
    }


class ListTagNamesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_tag_names(
                count=tool_parameters.get("count"),
                offset=tool_parameters.get("offset"),
            )
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("tag_names", str(exc), include_total=True))
            return

        raw_tag_names = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "tag_names",
                [normalize_tag_name_result(item) for item in raw_tag_names],
                total=total,
            ),
        )

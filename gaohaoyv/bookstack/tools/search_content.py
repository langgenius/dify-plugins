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


_CANONICAL_TYPES = {"book", "page", "chapter", "bookshelf"}
_TYPE_ALIASES = {"shelf": "bookshelf"}


def normalize_search_content_types(value: Any) -> list[str] | None:
    if value is None:
        return None

    raw_items: list[str]
    if isinstance(value, str):
        raw_items = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        raw_items = [str(item) for item in value]
    else:
        raw_items = [str(value)]

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        token = item.strip().lower()
        if not token:
            continue
        token = _TYPE_ALIASES.get(token, token)
        if token not in _CANONICAL_TYPES:
            raise ValueError(f"unsupported search type: {token}")
        if token not in seen:
            seen.add(token)
            normalized.append(token)

    return normalized or None


def normalize_search_content_result(raw: dict[str, Any]) -> dict[str, Any]:
    raw_id = raw.get("id")
    return {
        "id": None if raw_id is None else str(raw_id),
        "type": raw.get("type"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "preview": raw.get("preview"),
        "raw": raw,
    }


class SearchContentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = str(tool_parameters.get("query", "")).strip()
        if not query:
            yield from emit_variable_messages(self, collection_error("results", "query is required", include_total=True))
            return

        try:
            types = normalize_search_content_types(tool_parameters.get("types"))
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.search_content(query, types=types)
        except ValueError as exc:
            yield from emit_variable_messages(self, collection_error("results", str(exc), include_total=True))
            return
        except BookStackError as exc:
            yield from emit_variable_messages(self, collection_error("results", str(exc), include_total=True))
            return

        raw_results = payload.get("data", [])
        total = payload.get("total") if "total" in payload else None

        yield from emit_variable_messages(
            self,
            collection_success(
                "results",
                [normalize_search_content_result(item) for item in raw_results],
                total=total,
            )
        )

from __future__ import annotations

from typing import Any


_UNSET = object()


def success_payload(**payload: Any) -> dict[str, Any]:
    return {"success": True, "error": None, **payload}


def error_payload(error: str, **payload: Any) -> dict[str, Any]:
    return {"success": False, "error": error, **payload}


def collection_success(field_name: str, items: list[dict[str, Any]], *, total: Any = _UNSET) -> dict[str, Any]:
    payload = success_payload(**{field_name: items, "count": len(items)})
    if total is not _UNSET:
        payload["total"] = total
    return payload


def collection_error(field_name: str, error: str, *, include_total: bool = False) -> dict[str, Any]:
    payload = error_payload(error, **{field_name: [], "count": 0})
    if include_total:
        payload["total"] = None
    return payload


def object_error(error: str, *field_names: str) -> dict[str, Any]:
    return error_payload(error, **{field_name: None for field_name in field_names})


def emit_variable_messages(tool: Any, payload: dict[str, Any]):
    for field_name, value in payload.items():
        yield tool.create_variable_message(field_name, value)

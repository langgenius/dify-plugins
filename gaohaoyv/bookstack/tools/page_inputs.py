from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _normalize_tag_name_value(name: Any, value: Any) -> dict[str, str] | None:
    normalized_name = str(name).strip()
    if not normalized_name:
        return None

    normalized_value = "" if value is None else str(value).strip()
    return {"name": normalized_name, "value": normalized_value}


def _normalize_string_tag(value: Any) -> dict[str, str] | None:
    text = str(value).strip()
    if not text:
        return None

    if ":" in text:
        name, raw_value = text.split(":", 1)
        return _normalize_tag_name_value(name, raw_value)

    return _normalize_tag_name_value(text, "")


def _normalize_tag_item(value: Any) -> dict[str, str] | None:
    if isinstance(value, Mapping):
        return _normalize_tag_name_value(value.get("name"), value.get("value"))

    return _normalize_string_tag(value)


def normalize_tags(value: Any) -> list[dict[str, str]] | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        normalized_tag = _normalize_string_tag(value)
        return [normalized_tag] if normalized_tag else None

    normalized: list[dict[str, str]] = []
    if isinstance(value, list):
        for item in value:
            normalized_tag = _normalize_tag_item(item)
            if normalized_tag:
                normalized.append(normalized_tag)
    else:
        normalized_tag = _normalize_tag_item(value)
        if normalized_tag:
            normalized.append(normalized_tag)

    return normalized or None

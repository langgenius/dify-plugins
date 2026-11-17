from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tools.page_inputs import normalize_tags


def normalize_required_string(value: Any, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def normalize_optional_string(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def normalize_optional_integer(value: Any, field_name: str) -> int | None:
    if value is None or value == "":
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return int(text)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def normalize_optional_integer_list(value: Any, field_name: str) -> list[int] | None:
    if value is None or value == "":
        return None

    if isinstance(value, str) or not isinstance(value, Iterable):
        values = [value]
    else:
        values = list(value)

    normalized: list[int] = []
    for item in values:
        if item is None:
            continue

        text = str(item).strip()
        if not text:
            continue

        try:
            normalized.append(int(text))
        except ValueError as exc:
            raise ValueError(f"{field_name} entries must be integers") from exc

    return normalized or None


def normalize_optional_tags(value: Any) -> list[dict[str, str]] | None:
    return normalize_tags(value)

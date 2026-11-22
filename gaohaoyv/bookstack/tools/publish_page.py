from __future__ import annotations

from collections.abc import Generator
from typing import Any
from urllib.parse import urlparse

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
except ImportError:  # pragma: no cover - allows helper imports in unit tests
    Tool = object
    ToolInvokeMessage = Any

from bookstack_client import BookStackClient, BookStackError
from tools.create_page import normalize_created_page_result
from tools.output_payloads import emit_variable_messages, object_error, success_payload
from tools.page_inputs import normalize_tags
from tools.update_page import normalize_updated_page_result


def _normalize_title(value: Any) -> str:
    return str(value or "").strip()


def _page_title(raw: dict[str, Any]) -> str:
    return _normalize_title(raw.get("name") or raw.get("title"))


def _normalize_path(value: Any) -> str:
    return str(value or "").strip().strip("/")


def _normalize_doc_id(value: Any) -> str:
    return str(value or "").strip()


def _raw_tags(raw: dict[str, Any]) -> list[dict[str, str]]:
    tags = raw.get("tags")
    if not isinstance(tags, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in tags:
        if not isinstance(item, dict):
            continue
        name = _normalize_title(item.get("name"))
        if not name:
            continue
        normalized.append({"name": name, "value": _normalize_doc_id(item.get("value"))})
    return normalized


def _page_has_doc_id(raw: dict[str, Any], doc_id: str) -> bool:
    for tag in _raw_tags(raw):
        if tag["name"] == "doc_id" and tag["value"] == doc_id:
            return True
    return False


def _candidate_paths(raw: dict[str, Any]) -> set[str]:
    candidates: set[str] = set()

    raw_path = _normalize_path(raw.get("path"))
    if raw_path:
        candidates.add(raw_path)

    raw_url = str(raw.get("url") or "").strip()
    if raw_url:
        parsed = urlparse(raw_url)
        url_path = _normalize_path(parsed.path)
        if url_path:
            candidates.add(url_path)
            if "/" in url_path:
                candidates.add(url_path.rsplit("/", 1)[-1])

    return candidates


def _page_location_matches(raw: dict[str, Any], *, book_id: Any | None, chapter_id: Any | None) -> bool:
    if book_id not in {None, ""}:
        raw_book_id = raw.get("book_id")
        if raw_book_id is not None and str(raw_book_id) != str(book_id):
            return False
    if chapter_id not in {None, ""}:
        raw_chapter_id = raw.get("chapter_id")
        if raw_chapter_id is not None and str(raw_chapter_id) != str(chapter_id):
            return False
    return True


def _match_exact_title(
    raw_results: list[dict[str, Any]],
    *,
    title: str,
    book_id: Any | None,
    chapter_id: Any | None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        if _page_title(raw) != title:
            continue
        if not _page_location_matches(raw, book_id=book_id, chapter_id=chapter_id):
            continue
        matches.append(raw)
    return matches


def _match_doc_id(raw_results: list[dict[str, Any]], *, doc_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        if _page_has_doc_id(raw, doc_id):
            matches.append(raw)
    return matches


def _match_path(raw_results: list[dict[str, Any]], *, path: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        if path in _candidate_paths(raw):
            matches.append(raw)
    return matches


def _ensure_doc_id_tag(tags: list[dict[str, str]] | None, doc_id: str) -> list[dict[str, str]]:
    normalized_doc_id = _normalize_doc_id(doc_id)
    normalized_tags = list(tags or [])

    for tag in normalized_tags:
        if _normalize_title(tag.get("name")) == "doc_id":
            return normalized_tags

    normalized_tags.append({"name": "doc_id", "value": normalized_doc_id})
    return normalized_tags


class PublishPageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        title = _normalize_title(tool_parameters.get("title"))
        markdown = str(tool_parameters.get("markdown", "")).strip()
        page_id = _normalize_title(tool_parameters.get("page_id"))
        doc_id = _normalize_doc_id(tool_parameters.get("doc_id"))
        path = _normalize_path(tool_parameters.get("path"))
        book_id = tool_parameters.get("book_id")
        chapter_id = tool_parameters.get("chapter_id")
        tags = normalize_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None

        if doc_id:
            tags = _ensure_doc_id_tag(tags, doc_id)

        def emit_error(error: str) -> Generator[ToolInvokeMessage]:
            return emit_variable_messages(self, object_error(error, "page_id", "title", "url", "action", "raw"))

        if not title:
            yield from emit_error("title is required")
            return
        if not markdown:
            yield from emit_error("markdown is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)

            if page_id:
                raw_page = client.update_page(
                    page_id,
                    title=title,
                    markdown=markdown,
                    tags=tags,
                    book_id=book_id if book_id not in {None, ""} else None,
                    chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                )
                yield from emit_variable_messages(self, success_payload(**normalize_updated_page_result(raw_page)))
                return

            query_cache: dict[str, list[dict[str, Any]]] = {}

            def search_pages(query: str) -> list[dict[str, Any]]:
                if query not in query_cache:
                    query_cache[query] = client.search_pages(query)
                return query_cache[query]

            if doc_id:
                doc_id_matches = _match_doc_id(search_pages(doc_id), doc_id=doc_id)
                if len(doc_id_matches) > 1:
                    yield from emit_error("ambiguous doc_id match")
                    return
                if len(doc_id_matches) == 1:
                    raw_page = client.update_page(
                        doc_id_matches[0].get("id"),
                        title=title,
                        markdown=markdown,
                        tags=tags,
                        book_id=book_id if book_id not in {None, ""} else None,
                        chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                    )
                    yield from emit_variable_messages(self, success_payload(**normalize_updated_page_result(raw_page)))
                    return

            if path:
                path_matches = _match_path(search_pages(path), path=path)
                if len(path_matches) > 1:
                    yield from emit_error("ambiguous path match")
                    return
                if len(path_matches) == 1:
                    raw_page = client.update_page(
                        path_matches[0].get("id"),
                        title=title,
                        markdown=markdown,
                        tags=tags,
                        book_id=book_id if book_id not in {None, ""} else None,
                        chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                    )
                    yield from emit_variable_messages(self, success_payload(**normalize_updated_page_result(raw_page)))
                    return

            exact_matches = _match_exact_title(
                search_pages(title),
                title=title,
                book_id=book_id,
                chapter_id=chapter_id,
            )

            if len(exact_matches) > 1:
                yield from emit_error("ambiguous title match")
                return

            if len(exact_matches) == 1:
                raw_page = client.update_page(
                    exact_matches[0].get("id"),
                    title=title,
                    markdown=markdown,
                    tags=tags,
                    book_id=book_id if book_id not in {None, ""} else None,
                    chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                )
                yield from emit_variable_messages(self, success_payload(**normalize_updated_page_result(raw_page)))
                return

            if book_id in {None, ""} and chapter_id in {None, ""}:
                yield from emit_error("book_id or chapter_id is required to create a new page")
                return

            raw_page = client.create_page(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id if book_id not in {None, ""} else None,
                chapter_id=chapter_id if chapter_id not in {None, ""} else None,
            )
            yield from emit_variable_messages(self, success_payload(**normalize_created_page_result(raw_page)))
        except BookStackError as exc:
            yield from emit_error(str(exc))

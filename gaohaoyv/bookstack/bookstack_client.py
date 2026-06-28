from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


class BookStackError(RuntimeError):
    """Base error for BookStack API failures."""


class InvalidCredentialsError(BookStackError):
    pass


class PermissionDeniedError(BookStackError):
    pass


class BookNotFoundError(BookStackError):
    pass


class ChapterNotFoundError(BookStackError):
    pass


class PageNotFoundError(BookStackError):
    pass


class ServiceUnavailableError(BookStackError):
    pass


class InvalidResponseError(BookStackError):
    pass


def _invalid_credentials() -> InvalidCredentialsError:
    return InvalidCredentialsError("Invalid credentials")


def _service_unavailable() -> ServiceUnavailableError:
    return ServiceUnavailableError("BookStack API unavailable")


def _invalid_response() -> InvalidResponseError:
    return InvalidResponseError("Invalid BookStack response")


@dataclass(slots=True)
class BookStackClient:
    base_url: str
    token_id: str
    token_secret: str
    timeout_seconds: float = 10.0
    verify_ssl: bool = True

    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]) -> "BookStackClient":
        base_url = cls._require_credential(credentials, "base_url")
        token_id = cls._require_credential(credentials, "token_id")
        token_secret = cls._require_credential(credentials, "token_secret")

        return cls(
            base_url=base_url,
            token_id=token_id,
            token_secret=token_secret,
            timeout_seconds=cls._parse_timeout(credentials.get("timeout_seconds")),
            verify_ssl=cls._parse_verify_ssl(credentials.get("verify_ssl", True)),
        )

    @staticmethod
    def _require_credential(credentials: dict[str, Any], key: str) -> str:
        value = credentials.get(key)
        if value is None:
            raise _invalid_credentials()

        text = str(value).strip()
        if not text:
            raise _invalid_credentials()

        return text

    @staticmethod
    def _parse_timeout(value: Any) -> float:
        if value in {None, ""}:
            return 10.0

        try:
            timeout = float(value)
        except (TypeError, ValueError) as exc:
            raise _invalid_credentials() from exc

        if timeout <= 0:
            raise _invalid_credentials()

        return timeout

    @staticmethod
    def _parse_verify_ssl(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1"}:
                return True
            if normalized in {"false", "0"}:
                return False
            raise _invalid_credentials()
        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False
            raise _invalid_credentials()
        raise _invalid_credentials()

    def _api_url(self, path: str) -> str:
        normalized = self.base_url.rstrip("/") + "/"
        return urljoin(normalized, f"api/{path.lstrip('/')}")

    def _session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"Authorization": f"Token {self.token_id}:{self.token_secret}"})
        return session

    def _request(
        self,
        method: str,
        path: str,
        *,
        not_found_error: type[BookStackError] = BookNotFoundError,
        not_found_message: str = "Resource not found",
        **kwargs: Any,
    ) -> dict[str, Any]:
        try:
            response = self._session().request(
                method=method,
                url=self._api_url(path),
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
                **kwargs,
            )
        except (requests.Timeout, requests.ConnectionError, requests.RequestException) as exc:
            raise _service_unavailable() from exc

        if response.status_code in {401, 403}:
            if response.status_code == 401:
                raise _invalid_credentials()
            raise PermissionDeniedError("Permission denied")
        if response.status_code == 404:
            raise not_found_error(not_found_message)
        if response.status_code in {400, 422}:
            raise _invalid_response()
        if response.status_code == 429 or response.status_code >= 500:
            raise _service_unavailable()
        if response.status_code >= 400:
            raise _service_unavailable()

        if not response.content:
            return {}

        try:
            payload = response.json()
        except ValueError as exc:
            raise _invalid_response() from exc

        if isinstance(payload, dict):
            return payload
        raise _invalid_response()

    def validate_credentials(self) -> None:
        self._request("GET", "system")

    def search_pages(self, query: str) -> list[dict[str, Any]]:
        payload = self._request("GET", "search", params={"query": query})
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        page_results: list[dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                raise InvalidResponseError("Invalid BookStack response")
            if item.get("type") not in {None, "page"}:
                continue
            page_results.append(item)

        return page_results

    def list_books(self, count: Any | None = None, offset: Any | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = count
        if offset is not None:
            params["offset"] = offset

        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params

        payload = self._request("GET", "books", **request_kwargs)
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        return payload

    def list_shelves(self, count: Any | None = None, offset: Any | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = count
        if offset is not None:
            params["offset"] = offset

        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params

        payload = self._request("GET", "shelves", **request_kwargs)
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        return payload

    def list_pages(
        self,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if book_id is not None:
            params["book_id"] = book_id
        if chapter_id is not None:
            params["chapter_id"] = chapter_id
        if count is not None:
            params["count"] = count
        if offset is not None:
            params["offset"] = offset

        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params

        payload = self._request("GET", "pages", **request_kwargs)
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        return payload

    def list_chapters(
        self,
        book_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if book_id is not None:
            params["book_id"] = book_id
        if count is not None:
            params["count"] = count
        if offset is not None:
            params["offset"] = offset

        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params

        payload = self._request(
            "GET",
            "chapters",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
            **request_kwargs,
        )
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        return payload

    def get_page(self, page_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"pages/{page_id}",
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )

    @staticmethod
    def _build_page_payload(
        *,
        title: Any | None = None,
        markdown: Any | None = None,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        if title is not None:
            payload["name"] = title
        if markdown is not None:
            payload["markdown"] = markdown
        if tags is not None:
            payload["tags"] = tags
        if book_id is not None:
            payload["book_id"] = book_id
        if chapter_id is not None:
            payload["chapter_id"] = chapter_id

        return payload

    def create_page(
        self,
        *,
        title: Any,
        markdown: Any,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        not_found_error: type[BookStackError]
        not_found_message: str

        if chapter_id is not None:
            not_found_error = ChapterNotFoundError
            not_found_message = "Chapter not found"
        else:
            not_found_error = BookNotFoundError
            not_found_message = "Book not found"

        return self._request(
            "POST",
            "pages",
            json=self._build_page_payload(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id,
                chapter_id=chapter_id,
            ),
            not_found_error=not_found_error,
            not_found_message=not_found_message,
        )

    def update_page(
        self,
        page_id: Any,
        *,
        title: Any | None = None,
        markdown: Any | None = None,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"pages/{page_id}",
            json=self._build_page_payload(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id,
                chapter_id=chapter_id,
            ),
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )

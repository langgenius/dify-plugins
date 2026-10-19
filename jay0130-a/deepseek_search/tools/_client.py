"""Shared HTTP client for the DeepSeek Tools API (search & fetch).

Centralizes:

* Base URL and Bearer authentication (same key as the DeepSeek model platform).
* Request timeouts, so a slow upstream cannot hang a workflow node.
* A single error type (:class:`DeepSeekToolsError`) that carries the HTTP
  status code for user-safe mapping in :mod:`tools._errors`.

The API key is passed in by argument and is never logged here.
"""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.deepseek.com"
SEARCH_ENDPOINT = "/v1/tools/search"
FETCH_ENDPOINT = "/v1/tools/fetch"

# Search: 5 QPS per account; Fetch: 5 QPS per account plus per-target-domain
# limits. Keep the client timeout well below Dify's node timeout so retries
# remain possible.
DEFAULT_TIMEOUT_SECONDS = 60.0

MAX_QUERY_CHARS = 128
MAX_COUNT = 50
MAX_URL_CHARS = 8192


class DeepSeekToolsError(Exception):
    """An error response from ( or a failure to reach ) the DeepSeek Tools API."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class DeepSeekToolsClient:
    """Minimal synchronous client for the two DeepSeek Tools endpoints."""

    def __init__(self, *, api_key: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._timeout = timeout
        self._client: httpx.Client | None = None

    def __enter__(self) -> DeepSeekToolsClient:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers=self._headers,
            timeout=self._timeout,
        )
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def search(
        self,
        *,
        query: str,
        count: int | None = None,
        ori_question: str | None = None,
        need_content: bool = False,
    ) -> dict[str, Any]:
        """Run a web search; returns the parsed ``results`` payload."""
        body: dict[str, Any] = {"query": query, "need_content": need_content}
        if count is not None:
            body["count"] = count
        if ori_question:
            body["ori_question"] = ori_question
        return self._post(SEARCH_ENDPOINT, body)

    def fetch(self, *, url: str) -> dict[str, Any]:
        """Fetch a single page; returns ``{"title": ..., "content": ...}``."""
        return self._post(FETCH_ENDPOINT, {"url": url})

    def _post(self, endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
        if self._client is None:
            raise DeepSeekToolsError(
                "Client is not started. Use 'with build_client(...) as client:'."
            )
        try:
            response = self._client.post(endpoint, json=body)
        except httpx.TimeoutException as exc:
            raise DeepSeekToolsError(
                f"DeepSeek request timed out after {self._timeout:g}s."
            ) from exc
        except httpx.HTTPError as exc:
            raise DeepSeekToolsError(
                "Network error reaching api.deepseek.com. Verify outbound connectivity."
            ) from exc

        if response.status_code >= 400:
            raise DeepSeekToolsError(
                _extract_error_message(response),
                status_code=response.status_code,
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise DeepSeekToolsError(
                "DeepSeek returned a non-JSON response.",
                status_code=response.status_code,
            ) from exc
        return data


def _extract_error_message(response: httpx.Response) -> str:
    detail = ""
    try:
        payload = response.json()
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                detail = str(error.get("message") or "")
            elif error is not None:
                detail = str(error)
            elif payload.get("message"):
                detail = str(payload["message"])
    except ValueError:
        pass
    return f"DeepSeek API error (HTTP {response.status_code}): {detail or response.text[:200]}"


def build_client(*, api_key: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> DeepSeekToolsClient:
    """Construct a client for the DeepSeek Tools API (context manager)."""
    return DeepSeekToolsClient(api_key=api_key, timeout=timeout)

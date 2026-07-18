"""HTTP client for the ScrapeUnblocker API."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_BASE_URL = "https://api.scrapeunblocker.com"
DEFAULT_TIMEOUT = 180


class ScrapeUnblockerError(Exception):
    """Any failure talking to the ScrapeUnblocker API."""


class InvalidCredentialsError(ScrapeUnblockerError):
    """The API key was rejected."""


class ScrapeUnblockerClient:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: int = DEFAULT_TIMEOUT) -> None:
        if not api_key:
            raise InvalidCredentialsError("API key is required")
        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout

    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]) -> "ScrapeUnblockerClient":
        timeout_raw = credentials.get("timeout_seconds")
        try:
            timeout = int(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
        except (TypeError, ValueError):
            timeout = DEFAULT_TIMEOUT
        return cls(
            api_key=str(credentials.get("api_key") or ""),
            base_url=str(credentials.get("base_url") or DEFAULT_BASE_URL),
            timeout=timeout,
        )

    def _post(self, path: str, params: dict[str, Any]) -> requests.Response:
        # Unset values are dropped so the API applies its own defaults.
        query = {k: v for k, v in params.items() if v is not None and v != "" and v is not False}
        try:
            response = requests.post(
                f"{self._base_url}{path}",
                params=query,
                headers={"X-ScrapeUnblocker-Key": self._api_key},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            # Never include the request headers here - they carry the API key.
            raise ScrapeUnblockerError(f"Request to {path} failed: {type(exc).__name__}") from exc

        if response.status_code in (401, 403):
            raise InvalidCredentialsError("ScrapeUnblocker rejected the API key")
        if response.status_code >= 400:
            raise ScrapeUnblockerError(f"ScrapeUnblocker returned HTTP {response.status_code} for {path}")
        return response

    def get_page_source(
        self,
        url: str,
        parsed_data: bool = False,
        proxy_country: str | None = None,
        time_sleep: int | None = None,
    ) -> str:
        """Return the rendered page as HTML, or JSON text when parsed_data is set."""
        response = self._post(
            "/getPageSource",
            {
                "url": url,
                "parsed_data": parsed_data,
                "proxy_country": proxy_country,
                "time_sleep": time_sleep,
            },
        )
        return response.text

    def search_google(
        self,
        keyword: str,
        pages_to_check: int | None = None,
        proxy_country: str | None = None,
    ) -> dict[str, Any]:
        """Return the parsed Google SERP payload."""
        response = self._post(
            "/serpApi",
            {
                "keyword": keyword,
                "pages_to_check": pages_to_check,
                "proxy_country": proxy_country,
            },
        )
        try:
            return response.json()
        except ValueError as exc:
            raise ScrapeUnblockerError("ScrapeUnblocker returned a non-JSON SERP response") from exc

    def validate_credentials(self) -> None:
        """Cheapest call that proves the key works."""
        self.get_page_source("https://example.com")

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import requests

API_BASE_URL = "https://api.adanos.org"
STOCK_SOURCES = frozenset({"reddit", "x", "news", "polymarket"})
ASSET_TYPES = frozenset({"stock", "crypto"})
JsonPayload = dict[str, Any] | list[Any]
_STOCK_PATTERN = re.compile(r"^\$?(?=.{1,10}$)(?:[A-Za-z0-9]+(?:[.-][A-Za-z])?)$")
_CRYPTO_PATTERN = re.compile(r"^\$?[A-Za-z0-9]{1,20}$")


class AdanosError(RuntimeError):
    """A safe, user-facing Adanos request failure."""


def _normalize_date(value: Any, name: str) -> str | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc


def build_window(from_date: Any = None, to_date: Any = None) -> dict[str, str]:
    start = _normalize_date(from_date, "from_date")
    end = _normalize_date(to_date, "to_date")
    if start and end and start > end:
        raise ValueError("from_date must not be after to_date")
    return {key: value for key, value in (("from", start), ("to", end)) if value}


def normalize_source(source: Any) -> str:
    normalized = str(source or "reddit").strip().lower()
    if normalized not in STOCK_SOURCES:
        raise ValueError("source must be reddit, x, news, or polymarket")
    return normalized


def normalize_asset_type(asset_type: Any) -> str:
    normalized = str(asset_type or "stock").strip().lower()
    if normalized not in ASSET_TYPES:
        raise ValueError("asset_type must be stock or crypto")
    return normalized


def normalize_identifier(value: Any, *, crypto: bool) -> str:
    identifier = str(value or "").strip().upper()
    pattern = _CRYPTO_PATTERN if crypto else _STOCK_PATTERN
    name = "symbol" if crypto else "ticker"
    if not pattern.fullmatch(identifier):
        raise ValueError(f"invalid {name}")
    return identifier.removeprefix("$")


class AdanosClient:
    def __init__(
        self,
        api_key: str,
        *,
        session: requests.Session | None = None,
        timeout: float = 15.0,
    ) -> None:
        normalized_key = api_key.strip()
        if not normalized_key:
            raise ValueError("Adanos API key is required")
        self._header_value = normalized_key
        self._session = session or requests.Session()
        self._timeout = timeout

    @classmethod
    def from_credentials(cls, credentials: Mapping[str, Any]) -> AdanosClient:
        return cls(str(credentials.get("api_key") or ""))

    def _get(self, path: str, params: Mapping[str, Any] | None = None) -> JsonPayload:
        try:
            response = self._session.get(
                f"{API_BASE_URL}{path}",
                headers={"Accept": "application/json", "X-API-Key": self._header_value},
                params=params,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise AdanosError("Adanos API request failed") from exc

        if not response.ok:
            if response.status_code in {401, 403}:
                raise AdanosError("Adanos API key was rejected")
            if response.status_code == 404:
                raise AdanosError("Adanos has no matching asset for this request")
            if response.status_code == 429:
                raise AdanosError("Adanos rate limit or monthly quota exceeded")
            raise AdanosError(f"Adanos API returned status {response.status_code}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise AdanosError("Adanos API returned invalid JSON") from exc
        if not isinstance(payload, (dict, list)):
            raise AdanosError("Adanos API returned an unexpected response")
        return payload

    def get_stock_sentiment(
        self,
        ticker: Any,
        *,
        source: Any = "reddit",
        from_date: Any = None,
        to_date: Any = None,
    ) -> JsonPayload:
        normalized_ticker = normalize_identifier(ticker, crypto=False)
        normalized_source = normalize_source(source)
        return self._get(
            f"/{normalized_source}/stocks/v1/stock/{normalized_ticker}",
            build_window(from_date, to_date),
        )

    def get_crypto_sentiment(
        self, symbol: Any, *, from_date: Any = None, to_date: Any = None
    ) -> JsonPayload:
        normalized_symbol = normalize_identifier(symbol, crypto=True)
        return self._get(
            f"/reddit/crypto/v1/token/{normalized_symbol}",
            build_window(from_date, to_date),
        )

    def get_trending(
        self,
        *,
        asset_type: Any = "stock",
        source: Any = "reddit",
        limit: Any = 20,
        from_date: Any = None,
        to_date: Any = None,
    ) -> JsonPayload:
        normalized_asset_type = normalize_asset_type(asset_type)
        try:
            numeric_limit = Decimal(str(limit))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("limit must be an integer from 1 to 100") from exc
        if not numeric_limit.is_finite() or numeric_limit != numeric_limit.to_integral_value():
            raise ValueError("limit must be an integer from 1 to 100")
        normalized_limit = int(numeric_limit)
        if not 1 <= normalized_limit <= 100:
            raise ValueError("limit must be an integer from 1 to 100")
        if normalized_asset_type == "crypto":
            path = "/reddit/crypto/v1/trending"
        else:
            path = f"/{normalize_source(source)}/stocks/v1/trending"
        params: dict[str, Any] = build_window(from_date, to_date)
        params["limit"] = normalized_limit
        return self._get(path, params)

    def get_market_sentiment(
        self,
        *,
        asset_type: Any = "stock",
        source: Any = "reddit",
        from_date: Any = None,
        to_date: Any = None,
    ) -> JsonPayload:
        normalized_asset_type = normalize_asset_type(asset_type)
        if normalized_asset_type == "crypto":
            path = "/reddit/crypto/v1/market-sentiment"
        else:
            path = f"/{normalize_source(source)}/stocks/v1/market-sentiment"
        return self._get(path, build_window(from_date, to_date))

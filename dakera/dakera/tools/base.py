import json
from typing import Any

import requests


class DakeraBaseTool:
    """Shared HTTP helper for talking to a self-hosted Dakera server.

    Dakera exposes a small REST API for persistent, decay-weighted agent memory.
    Credentials are user-supplied: the base URL of a self-hosted server (default
    port 3000) and an optional ``dk-`` API key.
    """

    def _base_url(self) -> str:
        api_url = (self.runtime.credentials.get("api_url") or "").strip().rstrip("/")
        if not api_url:
            raise ValueError("Dakera server URL is not configured.")
        return api_url

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = (self.runtime.credentials.get("api_key") or "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float = 15.0,
    ) -> dict[str, Any]:
        url = f"{self._base_url()}{path}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(),
                json=json_body,
                params=params,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise ConnectionError(
                f"Cannot reach Dakera server at {self._base_url()}: {exc}. "
                "Make sure the server is running (see github.com/dakera-ai/dakera-deploy)."
            ) from exc

        if not response.ok:
            try:
                detail = json.dumps(response.json(), ensure_ascii=False)
            except ValueError:
                detail = response.text
            raise RuntimeError(f"Dakera request failed (HTTP {response.status_code}): {detail}")

        return response.json()

    @staticmethod
    def _parse_csv(value: str | None) -> list[str]:
        """Parse a comma-separated string into a trimmed, non-empty list."""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

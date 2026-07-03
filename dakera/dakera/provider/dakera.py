from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DakeraProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_url = (credentials.get("api_url") or "").strip().rstrip("/")
        if not api_url:
            raise ToolProviderCredentialValidationError("Dakera server URL is required.")

        headers = {}
        api_key = (credentials.get("api_key") or "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(f"{api_url}/health/live", headers=headers, timeout=5.0)
        except requests.RequestException as exc:
            raise ToolProviderCredentialValidationError(
                f"Cannot reach Dakera server at {api_url}: {exc}. "
                "Make sure the server is running (see github.com/dakera-ai/dakera-deploy)."
            ) from exc

        if response.status_code == 401:
            raise ToolProviderCredentialValidationError(
                "Dakera rejected the API key (HTTP 401). Check the Dakera API Key value."
            )
        if response.status_code not in (200, 204):
            raise ToolProviderCredentialValidationError(
                f"Dakera health check failed (HTTP {response.status_code}). "
                "Verify the server URL and that the server is healthy."
            )

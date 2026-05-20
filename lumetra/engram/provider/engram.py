from typing import Any

import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class EngramProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("engram_api_key")
        if not api_key:
            raise ToolProviderCredentialValidationError("Engram API key is required.")

        base_url = (credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")
        try:
            response = requests.get(
                f"{base_url}/v1/buckets",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": 1},
                timeout=10,
            )
        except requests.RequestException as exc:
            raise ToolProviderCredentialValidationError(
                f"Could not reach Engram at {base_url}: {exc}"
            ) from exc

        if response.status_code == 401:
            raise ToolProviderCredentialValidationError(
                "Engram rejected the API key (HTTP 401). Double-check the eng_live_... value."
            )
        if response.status_code >= 400:
            raise ToolProviderCredentialValidationError(
                f"Engram returned HTTP {response.status_code} during validation: {response.text[:200]}"
            )

from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SerpKiteProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        key = credentials.get("api_key")
        if not key:
            raise ToolProviderCredentialValidationError("A SerpKite API key is required.")
        try:
            response = requests.get(
                "https://api.serpkite.com/v1/account",
                headers={"Authorization": f"Bearer {key}"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException:
            raise ToolProviderCredentialValidationError(
                "SerpKite credential validation failed. Check the API key and account status."
            ) from None

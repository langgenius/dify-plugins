"""MingXi Export Control API provider - credential validation."""
from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class MingXiProvider(ToolProvider):
    """Provider for MingXi Export Control API.

    Validates the user's API key by making a lightweight request
    to the MingXi balance endpoint.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        if not api_key or not api_key.startswith("sk-"):
            raise ToolProviderCredentialValidationError(
                "Invalid API key format. Key should start with 'sk-'."
            )

        try:
            resp = requests.get(
                "https://api.mingxiapi.cn/v1/balance",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if resp.status_code in (403, 404):
                raise ToolProviderCredentialValidationError(
                    "API key is invalid or banned."
                )
            resp.raise_for_status()
        except ToolProviderCredentialValidationError:
            raise
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to MingXi API: {e}"
            )

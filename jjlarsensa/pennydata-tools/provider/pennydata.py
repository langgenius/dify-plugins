from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class PennyDataProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = (credentials.get("apify_api_token") or "").strip()
        if not token:
            raise ToolProviderCredentialValidationError("Apify API token is required.")
        try:
            resp = requests.get(
                "https://api.apify.com/v2/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Could not reach Apify: {e}") from e
        if resp.status_code != 200:
            raise ToolProviderCredentialValidationError("Apify rejected this API token.")

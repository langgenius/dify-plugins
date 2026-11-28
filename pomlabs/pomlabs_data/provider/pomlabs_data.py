from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class PomlabsDataProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        key = credentials.get("api_key", "")
        if not key:
            raise ToolProviderCredentialValidationError("API key is required")
        try:
            r = requests.get(
                "https://pom-data-api.pomlabs.workers.dev/v1/reddit/subreddit",
                params={"name": "python", "max": 1},
                headers={"X-API-Key": key},
                timeout=60,
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
        if r.status_code in (401, 403):
            raise ToolProviderCredentialValidationError("Invalid API key")

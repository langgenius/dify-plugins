from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class BytePlusSeedreamProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        endpoint_url = credentials.get("endpoint_url")
        if not api_key:
            raise ToolProviderCredentialValidationError("API Key is required.")
        if not endpoint_url:
            raise ToolProviderCredentialValidationError("API Endpoint Host is required.")

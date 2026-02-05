from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class AnakinProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate Anakin API credentials.
        """
        api_key = credentials.get("api_key")

        if not api_key:
            raise ToolProviderCredentialValidationError("API Key is required")

        # Basic format validation - Anakin keys start with "ask_"
        if not api_key.startswith("ask_"):
            raise ToolProviderCredentialValidationError("Invalid API Key format. Anakin API keys start with 'ask_'")

from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ApocdataProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # No credentials required - all endpoints are free and open
        pass

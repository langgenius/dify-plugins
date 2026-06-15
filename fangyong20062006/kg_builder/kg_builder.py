from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class KgBuilderProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        pass

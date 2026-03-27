from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class OlostepProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        # Skip validation for now - just return True
        return

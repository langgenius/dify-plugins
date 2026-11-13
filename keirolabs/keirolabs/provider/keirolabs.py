from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.keirolabs_search import search


class KeirolabsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            search(credentials.get("keirolabs_api_key", ""), "test", 1)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e

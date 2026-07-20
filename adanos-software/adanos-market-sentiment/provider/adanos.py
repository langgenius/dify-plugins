from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.client import AdanosClient, AdanosError


class AdanosProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            AdanosClient.from_credentials(credentials).get_trending(
                asset_type="stock", source="reddit", limit=1
            )
        except (AdanosError, ValueError) as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

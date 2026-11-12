from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from lib.client import SentFromAIClient, SentFromAIError


class SentFromAIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            SentFromAIClient(credentials.get("api_key")).request("GET", "/v1/account")
        except SentFromAIError as error:
            raise ToolProviderCredentialValidationError(str(error)) from None

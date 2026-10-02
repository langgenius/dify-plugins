from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.api import call_api


class AiSubtitleRemoverProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        if not credentials.get("userNo") or not credentials.get("apiKey"):
            raise ToolProviderCredentialValidationError(
                "User number and API key are required. Get them at https://eraser.550wai.com/api/"
            )
        try:
            result = call_api(credentials, "/open/queryCredits", {}, timeout=15)
            if result.get("code") != 200:
                raise ValueError(result.get("message") or "Credential validation failed")
        except Exception as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._client import DeepSeekToolsError, build_client
from tools._errors import friendly_error_message


class DeepSeekSearchProvider(ToolProvider):
    """Validate the DeepSeek API key with a single minimal web search.

    The credential value is never written to logs, error messages, or test
    output. Only the HTTP status and a developer-facing message surface
    upward.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("deepseek_api_key")
        if not api_key or not str(api_key).strip():
            raise ToolProviderCredentialValidationError(
                "DeepSeek API Key is missing. Set it in the provider credentials."
            )
        try:
            with build_client(api_key=str(api_key)) as client:
                client.search(query="deepseek", count=1)
        except DeepSeekToolsError as exc:
            raise ToolProviderCredentialValidationError(
                friendly_error_message(exc, fallback="DeepSeek credential validation failed.")
            ) from None
        except Exception as exc:  # network or unexpected failure
            raise ToolProviderCredentialValidationError(
                friendly_error_message(exc, fallback="DeepSeek credential validation failed.")
            ) from None

from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._client import SoniloAPIError, validate_api_key


class SoniloProvider(ToolProvider):
    """Validates the Sonilo API key with a single, read-only request.

    ``GET /v1/account/usage`` requires no request body, does not generate
    any audio, and does not consume generation credits, so it is safe to
    call on every credential save.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        if not api_key or not str(api_key).strip():
            raise ToolProviderCredentialValidationError(
                "Sonilo API Key is missing. Set it in the provider credentials."
            )
        try:
            validate_api_key(str(api_key).strip())
        except SoniloAPIError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from None
        except Exception as exc:  # network errors, timeouts, etc.
            raise ToolProviderCredentialValidationError(
                f"Could not reach the Sonilo API to validate the key: {exc}"
            ) from None

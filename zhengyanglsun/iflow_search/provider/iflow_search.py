from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._client import build_client
from tools._errors import friendly_error_message


class IFlowSearchProvider(ToolProvider):
    """Validates the iFlow Search API key by issuing a single low-cost web search.

    The credential value itself is never written to logs, error messages, or
    test output. Only the stable SDK error ``code`` and the developer-facing
    message string surface upward.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("iflow_api_key")
        if not api_key or not str(api_key).strip():
            raise ToolProviderCredentialValidationError(
                "iFlow API Key is missing. Set it in the provider credentials."
            )
        try:
            with build_client(api_key=api_key) as client:
                client.web_search(query="iflow", count=1)
        except ToolProviderCredentialValidationError:
            raise
        except Exception as exc:
            raise ToolProviderCredentialValidationError(
                friendly_error_message(exc, fallback="iFlow credential validation failed.")
            ) from None

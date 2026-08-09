from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._client import E2AClient


class E2AProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        credential_value = credentials.get("e2a_api_key")
        if not isinstance(credential_value, str) or not credential_value.strip():
            raise ToolProviderCredentialValidationError(
                "E2A_API_KEY is required. Create an agent-scoped key in E2A."
            )

        try:
            E2AClient(credential_value.strip()).whoami()
        except Exception as exc:
            raise ToolProviderCredentialValidationError(
                "Could not validate E2A_API_KEY. Confirm that the key is active and agent-scoped."
            ) from exc

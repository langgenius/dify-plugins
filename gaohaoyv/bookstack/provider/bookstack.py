from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from bookstack_client import BookStackClient, BookStackError, InvalidCredentialsError


class BookStackProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            client = BookStackClient.from_credentials(credentials)
            client.validate_credentials()
        except BookStackError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
        except Exception as exc:
            raise ToolProviderCredentialValidationError(str(InvalidCredentialsError("Invalid credentials"))) from exc

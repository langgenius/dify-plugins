from typing import Any

from client import request
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from loom import LoomError


class LoomProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            request(credentials, "memory.list", {"limit": 1})
        except (LoomError, TimeoutError, ValueError):
            raise ToolProviderCredentialValidationError(
                "Loom connection failed; check the endpoint, identity and token grants"
            ) from None

from typing import Any

from dify_plugin import ToolProvider


class McpConfigProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        no need to pre-authorize, just pass the connection information when calling
        """
        pass 
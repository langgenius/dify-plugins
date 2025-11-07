from typing import Any

from dify_plugin import ToolProvider


class StarterAgentProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # No credentials required for this simple example
        return

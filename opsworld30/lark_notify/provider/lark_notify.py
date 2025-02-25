from typing import Any
from dify_plugin import ToolProvider


class lark_notify(ToolProvider):
    """
    Lark notification provider for sending messages to Lark group chats.
    """
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """No credentials needed at provider level."""
        pass

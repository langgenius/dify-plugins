from collections.abc import Generator
from typing import Any

from client import request, text, user
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from loom import LoomError


class RememberTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        user_id = user(tool_parameters)
        try:
            result = request(
                self.runtime.credentials,
                "memory.set",
                {
                    "memory_key": text(tool_parameters, "memory_key"),
                    "value": text(tool_parameters, "value"),
                },
                user_id=user_id,
            )
        except (LoomError, TimeoutError):
            raise ValueError(
                "Loom request failed; check the provider connection and token grants"
            ) from None
        yield self.create_json_message(result)

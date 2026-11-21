from collections.abc import Generator
from typing import Any

from client import limit, request, text, user
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from loom import LoomError


class RecallTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        user_id = user(tool_parameters)
        try:
            result = request(
                self.runtime.credentials,
                "memory.search",
                {
                    "query": text(tool_parameters, "query"),
                    "top_k": limit(tool_parameters),
                    "namespace_scope": "this",
                    "bodies": "full",
                    "explain": False,
                },
                user_id=user_id,
                agent_id="*",
            )
        except (LoomError, TimeoutError):
            raise ValueError(
                "Loom request failed; check the provider connection and token grants"
            ) from None
        yield self.create_json_message(result)

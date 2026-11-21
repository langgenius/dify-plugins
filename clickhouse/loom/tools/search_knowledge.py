from collections.abc import Generator
from typing import Any

from client import limit, request, text, user
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from loom import LoomError


class SearchKnowledgeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        user_id = user(tool_parameters)
        try:
            result = request(
                self.runtime.credentials,
                "knowledge.search",
                {
                    "query": text(tool_parameters, "query"),
                    "top_k": limit(tool_parameters, maximum=100),
                    "namespace_scope": "this",
                },
                user_id=user_id,
            )
        except (LoomError, TimeoutError):
            raise ValueError(
                "Loom request failed; check the provider connection and token grants"
            ) from None
        yield self.create_json_message(result)

from collections.abc import Generator
from typing import Any
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraGetTool(DakeraBaseTool, Tool):
    """Fetch a single memory by ID from a self-hosted Dakera server."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        memory_id = (tool_parameters.get("memory_id") or "").strip()
        if not memory_id:
            yield self.create_text_message("Memory ID is required.")
            return

        agent_id = (tool_parameters.get("agent_id") or "dify-agent").strip()

        result = self._request(
            "GET",
            f"/v1/memory/get/{quote(memory_id, safe='')}",
            params={"agent_id": agent_id},
        )

        content = result.get("content", "") if isinstance(result, dict) else ""
        yield self.create_text_message(content or f"Memory {memory_id} has no content.")
        yield self.create_json_message(result)

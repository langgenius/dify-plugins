from collections.abc import Generator
from typing import Any
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraUpdateTool(DakeraBaseTool, Tool):
    """Update an existing memory by ID on a self-hosted Dakera server."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        memory_id = (tool_parameters.get("memory_id") or "").strip()
        if not memory_id:
            yield self.create_text_message("Memory ID is required.")
            return

        agent_id = (tool_parameters.get("agent_id") or "dify-agent").strip()

        body: dict[str, Any] = {}
        content = (tool_parameters.get("content") or "").strip()
        if content:
            body["content"] = content

        importance = tool_parameters.get("importance")
        if importance is not None:
            body["importance"] = max(0.0, min(1.0, float(importance)))

        tags = self._parse_csv(tool_parameters.get("tags"))
        if tags:
            body["tags"] = tags

        if not body:
            yield self.create_text_message(
                "Nothing to update — provide at least one of content, importance, or tags."
            )
            return

        result = self._request(
            "PUT",
            f"/v1/memory/update/{quote(memory_id, safe='')}",
            params={"agent_id": agent_id},
            json_body=body,
        )

        updated = ", ".join(sorted(body.keys()))
        yield self.create_text_message(f"Memory {memory_id} updated ({updated}).")
        yield self.create_json_message(result)

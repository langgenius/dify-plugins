from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraStoreTool(DakeraBaseTool, Tool):
    """Persist a memory in a self-hosted Dakera server for future recall."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        content = (tool_parameters.get("content") or "").strip()
        if not content:
            yield self.create_text_message("Content is required.")
            return

        body: dict[str, Any] = {
            "content": content,
            "agent_id": (tool_parameters.get("agent_id") or "dify-agent").strip(),
        }

        importance = tool_parameters.get("importance")
        if importance is not None:
            importance = max(0.0, min(1.0, float(importance)))
            body["importance"] = importance

        session_id = (tool_parameters.get("session_id") or "").strip()
        if session_id:
            body["session_id"] = session_id

        tags = self._parse_csv(tool_parameters.get("tags"))
        if tags:
            body["tags"] = tags

        result = self._request("POST", "/v1/memory/store", json_body=body)

        memory = result.get("memory", {}) if isinstance(result, dict) else {}
        memory_id = memory.get("id", "unknown")
        yield self.create_text_message(f"Memory stored successfully (id: {memory_id}).")
        yield self.create_json_message(result)

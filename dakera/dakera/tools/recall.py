from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraRecallTool(DakeraBaseTool, Tool):
    """Recall semantically relevant memories from a self-hosted Dakera server."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return

        top_k = tool_parameters.get("top_k")
        top_k = 5 if top_k is None else int(top_k)
        top_k = max(1, min(20, top_k))

        body: dict[str, Any] = {
            "query": query,
            "agent_id": (tool_parameters.get("agent_id") or "dify-agent").strip(),
            "top_k": top_k,
        }

        session_id = (tool_parameters.get("session_id") or "").strip()
        if session_id:
            body["session_id"] = session_id

        result = self._request("POST", "/v1/memory/recall", json_body=body)

        memories = result.get("memories", []) if isinstance(result, dict) else []
        if not memories:
            yield self.create_text_message("No relevant memories found.")
            yield self.create_json_message(result)
            return

        lines = [f"Found {len(memories)} relevant {'memory' if len(memories) == 1 else 'memories'}:\n"]
        for i, item in enumerate(memories, 1):
            mem = item.get("memory", {}) if isinstance(item, dict) else {}
            score = item.get("score", 0.0)
            content = mem.get("content", "")
            mem_id = mem.get("id", "")
            id_suffix = f"  (id: {mem_id})" if mem_id else ""
            lines.append(f"{i}. [{score:.3f}] {content}{id_suffix}")

        yield self.create_text_message("\n".join(lines))
        yield self.create_json_message(result)

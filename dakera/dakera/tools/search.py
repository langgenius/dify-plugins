from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraSearchTool(DakeraBaseTool, Tool):
    """Filtered search / browse over memories in a self-hosted Dakera server."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        top_k = tool_parameters.get("top_k")
        top_k = 10 if top_k is None else int(top_k)
        top_k = max(1, min(50, top_k))

        body: dict[str, Any] = {
            "agent_id": (tool_parameters.get("agent_id") or "dify-agent").strip(),
            "top_k": top_k,
        }

        query = (tool_parameters.get("query") or "").strip()
        if query:
            body["query"] = query

        tags = self._parse_csv(tool_parameters.get("tags"))
        if tags:
            body["tags"] = tags

        min_importance = tool_parameters.get("min_importance")
        if min_importance is not None:
            body["min_importance"] = max(0.0, min(1.0, float(min_importance)))

        result = self._request("POST", "/v1/memory/search", json_body=body)

        memories = result.get("memories", []) if isinstance(result, dict) else []
        total = result.get("total_count", len(memories)) if isinstance(result, dict) else 0
        if not memories:
            yield self.create_text_message("No memories matched the search filters.")
            yield self.create_json_message(result)
            return

        lines = [f"Matched {total} memories (showing {len(memories)}):\n"]
        for i, item in enumerate(memories, 1):
            mem = item.get("memory", {}) if isinstance(item, dict) else {}
            content = mem.get("content", "")
            importance = mem.get("importance")
            mem_id = mem.get("id", "")
            meta = []
            if isinstance(importance, (int, float)):
                meta.append(f"importance {importance:.2f}")
            if mem_id:
                meta.append(f"id: {mem_id}")
            suffix = f"  ({', '.join(meta)})" if meta else ""
            lines.append(f"{i}. {content}{suffix}")

        yield self.create_text_message("\n".join(lines))
        yield self.create_json_message(result)

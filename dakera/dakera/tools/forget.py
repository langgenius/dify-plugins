from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import DakeraBaseTool


class DakeraForgetTool(DakeraBaseTool, Tool):
    """Delete memories from a self-hosted Dakera server."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        body: dict[str, Any] = {
            "agent_id": (tool_parameters.get("agent_id") or "dify-agent").strip(),
        }

        memory_ids = self._parse_csv(tool_parameters.get("memory_ids"))
        if memory_ids:
            body["memory_ids"] = memory_ids

        session_id = (tool_parameters.get("session_id") or "").strip()
        if session_id:
            body["session_id"] = session_id

        tags = self._parse_csv(tool_parameters.get("tags"))
        if tags:
            body["tags"] = tags

        below_importance = tool_parameters.get("below_importance")
        if below_importance is not None:
            body["below_importance"] = max(0.0, min(1.0, float(below_importance)))

        # Guard against an unscoped mass-delete: require at least one selector.
        if not any(k in body for k in ("memory_ids", "session_id", "tags", "below_importance")):
            yield self.create_text_message(
                "Refusing to delete: provide at least one of memory_ids, session_id, tags, "
                "or below_importance to scope the deletion."
            )
            return

        result = self._request("POST", "/v1/memory/forget", json_body=body)

        deleted = result.get("deleted_count", 0) if isinstance(result, dict) else 0
        yield self.create_text_message(
            f"Deleted {deleted} {'memory' if deleted == 1 else 'memories'}."
        )
        yield self.create_json_message(result)

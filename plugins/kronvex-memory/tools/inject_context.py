from collections.abc import Generator
from typing import Any
import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class InjectContextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        base_url = self.runtime.credentials.get("base_url", "https://api.kronvex.io").rstrip("/")
        api_key = self.runtime.credentials["api_key"]
        agent_id = tool_parameters["agent_id"]

        body = {"message": tool_parameters["message"]}

        resp = httpx.post(
            f"{base_url}/api/v1/agents/{agent_id}/inject-context",
            json=body,
            headers={"X-API-Key": api_key},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        yield self.create_text_message(data.get("context_block", ""))

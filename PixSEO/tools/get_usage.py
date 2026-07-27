from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from _config import API_BASE, safe_api_call, yield_error


class GetUsageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials["pixseo_api_key"]
        headers = {"X-API-Key": api_key}

        try:
            resp = safe_api_call(
                self,
                "GET",
                f"{API_BASE}/api/v1/usage",
                headers=headers,
                timeout=10,
            )
        except ValueError as e:
            yield from yield_error(self, str(e))
            return

        data = resp.json()
        yield self.create_json_message(data)
        yield self.create_text_message(
            f"Plan: {data.get('plan', 'N/A')}. "
            f"Used: {data.get('used', 0)}/{data.get('limit', 0)}. "
            f"Remaining: {data.get('remaining', 0)}"
        )
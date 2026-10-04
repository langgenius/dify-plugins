"""Tool: Query China's dual-use export control items."""
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ItemQueryTool(Tool):
    """Query the MingXi Export Control dual-use item database."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        keyword = tool_parameters.get("keyword", "")
        top_k = int(tool_parameters.get("top_k", 5))
        fmt = tool_parameters.get("format", "json")

        if not keyword:
            yield self.create_text_message("error: keyword is required")
            return

        top_k = max(1, min(top_k, 20))

        try:
            resp = requests.post(
                "https://api.mingxiapi.cn/v1/query",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "keyword": keyword,
                    "api_key": api_key,
                    "dataset": "export_control",
                    "top_k": top_k,
                    "format": fmt,
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            if resp.status_code == 403:
                yield self.create_text_message("error: API key invalid or balance insufficient")
            else:
                yield self.create_text_message(f"error: HTTP {resp.status_code}: {resp.text[:200]}")
            return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"error: Request failed: {e}")
            return

        data = resp.json()
        if fmt == "text" and isinstance(data, dict) and "text" in data:
            yield self.create_text_message(str(data["text"]))
        else:
            yield self.create_json_message(data)

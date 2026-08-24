from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class AnnouncementTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        symbol = tool_parameters.get("symbol", "")
        keyword = tool_parameters.get("keyword", "")

        params = {}
        if symbol:
            params["symbol"] = symbol
        if keyword:
            params["keyword"] = keyword

        try:
            resp = requests.get(
                f"{BASE_URL}/ann-list",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", [])
                text = f"Announcements ({len(result)} total):\n"
                for item in result[:10]:  # Show first 10
                    text += f"- [{item.get('ann_date', 'N/A')}] {item.get('title', 'N/A')}\n"
                if len(result) > 10:
                    text += f"... and {len(result) - 10} more\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")

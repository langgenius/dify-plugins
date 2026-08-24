from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class SectorTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            resp = requests.get(
                f"{BASE_URL}/sector-list",
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", [])
                text = f"Industry Sectors ({len(result)} total):\n"
                for item in result[:20]:  # Show first 20
                    text += f"- {item.get('name', 'N/A')}: {item.get('pct_chg', 'N/A')}%\n"
                if len(result) > 20:
                    text += f"... and {len(result) - 20} more\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")

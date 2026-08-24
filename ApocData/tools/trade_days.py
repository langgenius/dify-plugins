from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class TradeDaysTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        start_date = tool_parameters.get("start_date", "")
        end_date = tool_parameters.get("end_date", "")

        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        try:
            resp = requests.get(
                f"{BASE_URL}/trade-days",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", [])
                text = f"Trading Days ({len(result)} total):\n"
                for day in result[:30]:  # Show first 30
                    text += f"- {day}\n"
                if len(result) > 30:
                    text += f"... and {len(result) - 30} more\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")

from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class FinancialTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        symbol = tool_parameters.get("symbol", "")
        report_type = tool_parameters.get("report_type", "income")

        if not symbol:
            yield self.create_text_message("Please provide a stock symbol")
            return

        endpoint_map = {
            "income": "/income",
            "balance": "/balance-sheet",
            "cashflow": "/cash-flow",
        }
        endpoint = endpoint_map.get(report_type, "/income")

        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                params={"symbol": symbol},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", {})
                text = f"Financial Report for {symbol} ({report_type}):\n"
                for key, value in result.items():
                    text += f"{key}: {value}\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")

from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class MoneyflowTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        symbol = tool_parameters.get("symbol", "")
        if not symbol:
            yield self.create_text_message("Please provide a stock symbol")
            return

        try:
            resp = requests.get(
                f"{BASE_URL}/moneyflow",
                params={"symbol": symbol},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", {})
                text = f"Money Flow for {symbol}:\n"
                text += f"Net Inflow: {result.get('net_mf_amount', 'N/A')}\n"
                text += f"Buy Amount: {result.get('buy_amount', 'N/A')}\n"
                text += f"Sell Amount: {result.get('sell_amount', 'N/A')}\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")

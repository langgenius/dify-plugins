from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetCryptoPriceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        coin_id = tool_parameters["coin_id"].lower().strip()
        
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd,eur,btc",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: CoinGecko API timeout. Please try again.")
            return
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("Error: Cannot connect to CoinGecko API. Check your internet connection.")
            return
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(f"Error: CoinGecko API returned error {e.response.status_code}.")
            return

        if coin_id not in data:
            yield self.create_text_message(
                f"Coin '{coin_id}' not found on CoinGecko. Try IDs like: bitcoin, ethereum, solana, dogecoin, chainlink."
            )
            return

        coin_data = data[coin_id]
        result = {
            "coin": coin_id,
            "price_usd": coin_data.get("usd"),
            "price_eur": coin_data.get("eur"),
            "price_btc": coin_data.get("btc"),
            "change_24h_percent": round(coin_data.get("usd_24h_change", 0), 2),
            "volume_24h_usd": coin_data.get("usd_24h_vol"),
            "market_cap_usd": coin_data.get("usd_market_cap")
        }

        yield self.create_json_message(result)

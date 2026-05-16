from typing import Any
from dify_plugin import ToolProvider


class CoinGeckoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        import requests
        response = requests.get(
            "https://api.coingecko.com/api/v3/ping",
            timeout=5
        )
        response.raise_for_status()

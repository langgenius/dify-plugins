from typing import Any
from dify_plugin import ToolProvider


class WebCrawlerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        pass

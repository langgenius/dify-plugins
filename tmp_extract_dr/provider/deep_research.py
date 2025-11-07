from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import os   

class DeepResearchProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            from tavily import TavilyClient
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            tavily_api_key = credentials.get("tavily_api_key")
            client = TavilyClient(api_key=tavily_api_key)
            client.search(query="test", max_results=1, include_content=False)
            print("Tavily API Key validated successfully!")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

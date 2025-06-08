from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SearchEngineTool(Tool):
    """Real Bright Data search_engine tool - with required zone."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api_token = self.runtime.credentials["api_token"]
        except KeyError:
            raise Exception("Bright Data API token is required.")

        query = tool_parameters.get("query", "")
        search_engine = tool_parameters.get("search_engine", "google")
        
        if not query:
            raise Exception("Search query cannot be empty.")

        try:
            results = self._search_engine(query, search_engine, api_token)
            yield self.create_text_message(results)
        except Exception as e:
            raise Exception(f"Search engine scraping failed: {str(e)}")

    def _search_engine(self, query: str, engine: str, api_token: str) -> str:
        """Use exact same API call as Bright Data MCP server"""
        
        headers = {
            'user-agent': 'dify-plugin/1.0.0',
            'authorization': f'Bearer {api_token}',
            'content-type': 'application/json',
        }
        
        # Build search URL exactly like MCP server
        search_url = self._get_search_url(engine, query)
        
        # Use the same zone as MCP server (hardcoded default)
        payload = {
            'url': search_url,
            'zone': 'mcp_unlocker',  # Same default as MCP server
            'format': 'raw',
            'data_format': 'markdown',
        }
        
        try:
            response = requests.post(
                'https://api.brightdata.com/request',
                json=payload,
                headers=headers,
                timeout=180
            )
            
            if response.status_code != 200:
                raise Exception(f"Bright Data API error {response.status_code}: {response.text}")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _get_search_url(self, engine: str, query: str) -> str:
        """Build search URL exactly like MCP server"""
        import urllib.parse
        
        q = urllib.parse.quote(query)
        
        if engine == 'yandex':
            return f'https://yandex.com/search/?text={q}'
        elif engine == 'bing':
            return f'https://www.bing.com/search?q={q}'
        else:  # default to google
            return f'https://www.google.com/search?q={q}'

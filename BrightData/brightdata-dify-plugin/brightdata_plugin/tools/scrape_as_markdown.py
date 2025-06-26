from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ScrapeAsMarkdownTool(Tool):
    """Bright Data scrape_as_markdown tool - with required zone."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api_token = self.runtime.credentials["api_token"]
        except KeyError:
            raise Exception("Bright Data API token is required.")

        url = tool_parameters.get("url", "").strip()
        if not url:
            raise Exception("URL cannot be empty.")

        try:
            markdown_content = self._scrape_as_markdown(url, api_token)
            yield self.create_text_message(markdown_content)
        except Exception as e:
            raise Exception(f"Web scraping failed: {str(e)}")

    def _scrape_as_markdown(self, url: str, api_token: str) -> str:
        """Use exact same API call as Bright Data MCP server"""
        
        headers = {
            'user-agent': 'dify-plugin/1.0.0',
            'authorization': f'Bearer {api_token}',
            'content-type': 'application/json',
        }
        
        # Use the same zone as MCP server (hardcoded default)
        payload = {
            'url': url,
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

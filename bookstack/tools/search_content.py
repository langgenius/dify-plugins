import requests
from typing import Any, Dict, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SearchContentTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for content in BookStack
        """
        # Get parameters
        query = tool_parameters.get('query', '')
        content_type = tool_parameters.get('type', 'all')
        limit = tool_parameters.get('limit', 20)
        
        # Get credentials
        bookstack_url = self.runtime.credentials.get('bookstack_url').rstrip('/')
        api_token = self.runtime.credentials.get('api_token')
        api_secret = self.runtime.credentials.get('api_secret')
        
        # Create headers
        headers = {
            'Authorization': f'Token {api_token}:{api_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            # Build search URL
            url = f"{bookstack_url}/api/search"
            params = {
                'query': query,
                'count': limit
            }
            
            if content_type != 'all':
                params['type'] = content_type
            
            # Make request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            result_data = {
                'success': True,
                'data': result.get('data', []),
                'total': result.get('total', 0),
                'query': query,
                'type': content_type
            }
            yield self.create_json_message(result_data)
            
        except requests.exceptions.RequestException as e:
            error_data = {
                'error': True,
                'message': f"Search failed: {str(e)}"
            }
            yield self.create_json_message(error_data)

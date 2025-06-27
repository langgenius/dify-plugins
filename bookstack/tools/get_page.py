import requests
from typing import Any, Dict, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GetPageTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get a specific page by ID
        """
        # Get parameters
        page_id = tool_parameters.get('page_id')
        
        if not page_id:
            yield self.create_json_message({'error': True, 'message': 'page_id is required'})
        
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
            # Make request
            url = f"{bookstack_url}/api/pages/{page_id}"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            yield self.create_json_message({
                    'success': True,
                    'page': result
                })
            
        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                    'error': True,
                    'message': f"Failed to get page: {str(e)}"
                }
            )

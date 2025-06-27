import requests
from typing import Any, Dict, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetBookTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get a specific book by ID
        """
        # Get parameters
        book_id = tool_parameters.get('book_id')
        
        if not book_id:
            error_data = {'error': True, 'message': 'book_id is required'}
            yield self.create_json_message(error_data)
            return
        
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
            url = f"{bookstack_url}/api/books/{book_id}"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            result_data = {
                'success': True,
                'book': result
            }
            yield self.create_json_message(result_data)
            
        except requests.exceptions.RequestException as e:
            error_data = {
                'error': True,
                'message': f"Failed to get book: {str(e)}"
            }
            yield self.create_json_message(error_data)

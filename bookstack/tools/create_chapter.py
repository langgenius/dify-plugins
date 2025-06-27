import requests
from typing import Any, Dict, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class CreateChapterTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new chapter in a book
        """
        # Get parameters
        book_id = tool_parameters.get('book_id')
        name = tool_parameters.get('name')
        description = tool_parameters.get('description', '')
        
        if not book_id or not name:
            yield self.create_json_message({'error': True, 'message': 'book_id and name are required'})
        
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
        
        # Prepare data
        data = {
            'book_id': int(book_id),
            'name': name,
            'description': description
        }
        
        try:
            # Make request
            url = f"{bookstack_url}/api/chapters"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            yield self.create_json_message({
                    'success': True,
                    'message': f'Chapter "{name}" created successfully',
                    'chapter': result
                })
            
        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                    'error': True,
                    'message': f"Failed to create chapter: {str(e)}"
                }
            )

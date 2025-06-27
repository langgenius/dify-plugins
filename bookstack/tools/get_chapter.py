import requests
from typing import Any, Dict, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetChapterTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get a specific chapter by ID
        """
        # Get parameters
        chapter_id = tool_parameters.get('chapter_id')
        
        if not chapter_id:
            yield self.create_json_message({'error': True, 'message': 'chapter_id is required'})
        
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
            url = f"{bookstack_url}/api/chapters/{chapter_id}"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            yield self.create_json_message({
                    'success': True,
                    'chapter': result
                })
            
        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                    'error': True,
                    'message': f"Failed to get chapter: {str(e)}"
                }
            )

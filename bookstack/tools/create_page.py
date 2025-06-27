import requests
from typing import Any, Dict, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class CreatePageTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a new page
        """
        # Get parameters
        name = tool_parameters.get('name')
        html = tool_parameters.get('html', '')
        markdown = tool_parameters.get('markdown', '')
        book_id = tool_parameters.get('book_id')
        chapter_id = tool_parameters.get('chapter_id')
        
        if not name:
            yield self.create_json_message({'error': True, 'message': 'name is required'})
        
        if not book_id and not chapter_id:
            yield self.create_json_message({'error': True, 'message': 'Either book_id or chapter_id is required'})
        
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
            'name': name,
            'html': html,
            'markdown': markdown
        }
        
        if book_id:
            data['book_id'] = int(book_id)
        if chapter_id:
            data['chapter_id'] = int(chapter_id)
        
        try:
            # Make request
            url = f"{bookstack_url}/api/pages"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            yield self.create_json_message({
                    'success': True,
                    'message': f'Page "{name}" created successfully',
                    'page': result
                })
            
        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                    'error': True,
                    'message': f"Failed to create page: {str(e)}"
                }
            )

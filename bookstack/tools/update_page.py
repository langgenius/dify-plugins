import requests
from typing import Any, Dict, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class UpdatePageTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update an existing page
        """
        # Get parameters
        page_id = tool_parameters.get('page_id')
        name = tool_parameters.get('name')
        html = tool_parameters.get('html')
        markdown = tool_parameters.get('markdown')
        
        if not page_id:
            yield self.create_json_message({'error': True, 'message': 'page_id is required'})
        
        # Prepare data - only include fields that are provided
        data = {}
        if name:
            data['name'] = name
        if html:
            data['html'] = html
        if markdown:
            data['markdown'] = markdown
        
        if not data:
            yield self.create_json_message({'error': True, 'message': 'At least one field (name, html, or markdown) must be provided'}
            )
        
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
            response = requests.put(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            yield self.create_json_message({
                    'success': True,
                    'message': 'Page updated successfully',
                    'page': result
                })
            
        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                    'error': True,
                    'message': f"Failed to update page: {str(e)}"
                }
            )

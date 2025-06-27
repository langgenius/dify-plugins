"""
BookStack Provider

This module provides the base provider implementation for BookStack tools.
It handles the common functionality and credentials management for all BookStack operations.
"""

from typing import Any, Dict
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class BookStackProvider(ToolProvider):
    """
    BookStack provider for handling API interactions.
    """
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Validate the provided credentials.
        
        Args:
            credentials: Dictionary containing BookStack API credentials
            
        Raises:
            ToolProviderCredentialValidationError: If credentials are invalid
        """
        # Basic validation
        bookstack_url = credentials.get('bookstack_url', '').strip()
        api_token = credentials.get('api_token', '').strip()
        api_secret = credentials.get('api_secret', '').strip()
        
        if not bookstack_url:
            raise ToolProviderCredentialValidationError("BookStack URL is required")
        if not api_token:
            raise ToolProviderCredentialValidationError("API Token is required")
        if not api_secret:
            raise ToolProviderCredentialValidationError("API Secret is required")
        
        # Test API connectivity
        try:
            import requests
            headers = {
                'Authorization': f'Token {api_token}:{api_secret}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{bookstack_url.rstrip('/')}/api/books", headers=headers, timeout=10)
            if response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API credentials")
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"BookStack API error: {response.status_code}")
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Cannot connect to BookStack: {str(e)}")

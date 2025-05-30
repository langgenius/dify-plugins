import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SemanticScholarProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate Semantic Scholar API credentials
        """
        try:
            api_key = credentials.get("api_key")
            
            # Test API connection with or without API key
            headers = {
                "User-Agent": "Dify-Dify-Plugin/1.0"
            }
            
            if api_key:
                headers["x-api-key"] = api_key
            
            # Test with a simple query to verify API access
            test_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": "decentralized finance",
                "limit": 1,
                "fields": "title"
            }
            
            response = requests.get(test_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 403:
                raise ToolProviderCredentialValidationError("Invalid API key provided")
            elif response.status_code == 429:
                raise ToolProviderCredentialValidationError("Rate limit exceeded. Consider adding an API key for higher limits")
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"API connection failed with status {response.status_code}")
                
            # If we get here, the credentials are valid
            
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to connect to Semantic Scholar API: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Credential validation failed: {str(e)}")

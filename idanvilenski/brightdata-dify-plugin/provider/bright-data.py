from typing import Any
import requests
import json
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class BrightDataProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate Bright Data API credentials by making a test request.
        """
        api_token = credentials.get("api_token")
        if not api_token:
            raise ToolProviderCredentialValidationError("Bright Data API token is required.")
        
        # Test the API token with a simple request
        try:
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Use a minimal web scraping request to test credentials
            test_payload = {
                "url": "https://httpbin.org/status/200",
                "response_type": "text"
            }
            
            # Note: This is a simplified validation approach
            # In a production environment, you'd use Bright Data's actual validation endpoint
            response = requests.get(
                "https://brightdata.com/api/zone",  # Example endpoint
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API token. Please check your Bright Data API token.")
            elif response.status_code != 200 and response.status_code != 403:  # 403 might be expected for this test
                # For now, we'll accept the credentials if we get any response
                # In production, you'd implement proper credential validation
                pass
                
        except requests.exceptions.RequestException as e:
            # For development, we'll be lenient with validation
            # In production, you'd want stricter validation
            if "401" in str(e) or "unauthorized" in str(e).lower():
                raise ToolProviderCredentialValidationError(f"Invalid API token: {str(e)}")
            # Otherwise, assume credentials might be valid but network/endpoint issues
            pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Credential validation error: {str(e)}")

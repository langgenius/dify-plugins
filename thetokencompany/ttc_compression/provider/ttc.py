import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class TTCCompressionProvider(ToolProvider):
    """
    TTC Compression Tool Provider.

    Validates credentials for The Token Company compression API.
    """

    def _validate_credentials(self, credentials: dict) -> None:
        """
        Validate TTC API credentials by making a test compression request.

        Args:
            credentials: Dictionary containing ttc_api_key

        Raises:
            ToolProviderCredentialValidationError: If credentials are invalid
        """
        api_key = credentials.get("ttc_api_key")

        if not api_key:
            raise ToolProviderCredentialValidationError("TTC API key is required")

        try:
            response = requests.post(
                "https://api.thetokencompany.com/v1/compress",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "bear-1",
                    "input": "Hello, this is a test.",
                    "compression_settings": {
                        "aggressiveness": 0.5,
                    },
                },
                timeout=30,
            )

            if response.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "Invalid TTC API key. Please check your credentials."
                )

            if response.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "Access denied. Your API key may not have permission to use this endpoint."
                )

            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"TTC API returned unexpected status: {response.status_code}"
                )

            # Verify response has expected structure
            result = response.json()
            if "output" not in result:
                raise ToolProviderCredentialValidationError(
                    "TTC API returned unexpected response format"
                )

        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError(
                "Connection to TTC API timed out. Please try again."
            )

        except requests.exceptions.ConnectionError:
            raise ToolProviderCredentialValidationError(
                "Could not connect to TTC API. Please check your network connection."
            )

        except ToolProviderCredentialValidationError:
            raise

        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to validate credentials: {str(e)}"
            )

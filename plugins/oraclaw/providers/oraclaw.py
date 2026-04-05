import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class OraclawProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        api_key = credentials.get("api_key", "")
        endpoint = credentials.get("api_endpoint", "https://oraclaw-api.onrender.com")

        try:
            response = requests.get(
                f"{endpoint}/api/v1/pricing",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"OraClaw API returned status {response.status_code}"
                )
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to OraClaw API: {str(e)}"
            )

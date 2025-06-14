from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests
def auth(api_key: str):
    url = "https://aisecurity.ueba.insightx.cc/api/auth/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        return False
    else:
        raise Exception(f"Error: {response.status_code}")

class RedkernelProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        if not api_key:
            raise ToolProviderCredentialValidationError("RedKernel API KEY cannot be empty.")
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            if not auth(api_key):
                raise ToolProviderCredentialValidationError("Invalid RedKernel API KEY.")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

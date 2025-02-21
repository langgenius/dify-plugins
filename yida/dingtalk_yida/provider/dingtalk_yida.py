from typing import Any, Dict
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/accessToken"


class DingTalkYidaProvider(ToolProvider):
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        app_key = credentials.get("app_key")
        app_secret = credentials.get("app_secret")

        if not app_key or not app_secret:
            raise ToolProviderCredentialValidationError("AppKey and AppSecret are required.")

        token_headers = {
            "Content-Type": "application/json"
        }
        token_payload = {
            "appKey": app_key,
            "appSecret": app_secret
        }

        try:
            token_response = requests.post(TOKEN_URL, headers=token_headers, json=token_payload)
            token_response.raise_for_status()
            token_result = token_response.json()

            if 'accessToken' not in token_result:
                raise ToolProviderCredentialValidationError(
                    "Failed to obtain access token: Missing accessToken in response."
                )

        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Error obtaining access token: {str(e)}")

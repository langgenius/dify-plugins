from typing import Any
import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class lark_notify(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            webhook_key = credentials.get('webhook_key')
            if not webhook_key:
                raise ValueError("Webhook key is required")

            # Test the webhook by sending a test message
            test_payload = {
                "msg_type": "text",
                "content": {
                    "text": "Testing webhook connection"
                }
            }
            response = requests.post(
                f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_key}",
                json=test_payload
            )
            response.raise_for_status()
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

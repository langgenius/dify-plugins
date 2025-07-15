from typing import Any
import httpx

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SmartseachProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证 Cloudsway API Key 是否有效。
        尝试用该 key 调用一次搜索 API。
        如果验证失败，应抛出 ToolProviderCredentialValidationError 异常。
        """
        server_key = credentials.get("server_key")
        if not server_key or "-" not in server_key:
            raise ToolProviderCredentialValidationError("Cloudsway API Key 不能为空或格式错误。")

        endpoint, api_key = server_key.split("-", 1)
        url = f"https://searchapi.cloudsway.net/search/{endpoint}/smart"
        params = {
            'q': 'test',
            'count': 1,
            'offset': 0,
            'mkt': 'en',
            'safeSearch': 'Strict'
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'pragma': 'no-cache',
        }

        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(url, params=params, headers=headers)
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"API 响应异常: {response.status_code}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Cloudsway API Key 验证失败: {e}")

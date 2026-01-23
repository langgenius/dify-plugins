from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.google_search import GoogleSearchTool

class GoogleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 获取凭据
            api_key = credentials["api_key"]
            cse_id = credentials["cse_id"]
            
            # 创建 Custom Search API 服务
            service = build("customsearch", "v1", developerKey=api_key)
            
            # 尝试执行一个简单的搜索来验证凭据
            service.cse().list(
                q="test",
                cx=cse_id,
                num=1
            ).execute()
            
        except HttpError as e:
            if e.resp.status == 403:
                raise ToolProviderCredentialValidationError("Invalid API key or CSE ID")
            else:
                raise ToolProviderCredentialValidationError(f"Google API error: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to validate credentials: {str(e)}") 
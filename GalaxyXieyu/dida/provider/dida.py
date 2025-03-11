from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dida.client import DidaClient


class DidaProvider(ToolProvider):
    """滴答清单基础 Provider，处理认证和客户端初始化"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """验证滴答清单的凭证并获取 token

        Args:
            credentials: 包含 token 的字典

        Raises:
            ToolProviderCredentialValidationError: 当凭证验证失败时抛出
        """
        try:
            client = DidaClient(token=credentials.get('token'))
            
            # 验证客户端是否可用
            client.tasks.get_all_tasks()
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) 
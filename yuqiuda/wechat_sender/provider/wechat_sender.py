from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.wechat_sender import WechatSenderTool


class WechatSenderProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            for _ in WechatSenderTool.from_credentials(credentials).invoke(
                tool_parameters={"content":"test"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

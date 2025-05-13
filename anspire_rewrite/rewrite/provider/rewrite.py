from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.rewrite import RewriteTool


class RewriteProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
             for _ in RewriteTool.from_credentials(credentials).invoke(
                tool_parameters={"question": "国内哪里?", "messages": "[{'Role': 'user', 'Content': '你家在哪里'},{'Role': 'assistant','Content': '我家在国内'}]"},
            ):
                 pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

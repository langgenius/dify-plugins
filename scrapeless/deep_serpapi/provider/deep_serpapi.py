from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.deep_serpapi_search import DeepSerpapiSearchTool


class DeepSerpapiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in DeepSerpapiSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "test", "result_type": "link"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

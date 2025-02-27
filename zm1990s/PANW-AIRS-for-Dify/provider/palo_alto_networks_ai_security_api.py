from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.palo_alto_networks_ai_security_api import PaloAltoNetworksAiSecurityApiTool

class PaloAltoNetworksAiSecurityApiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            tool = PaloAltoNetworksAiSecurityApiTool.from_credentials(credentials)
            for response in tool.invoke(
                tool_parameters={
                    "query": "test",
                    "inputoroutput": "input",
                    "appname": "dify_provider_test",
                    "appuser": "dify_system",
                    "modelname": "dify_default_llm"
                },
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
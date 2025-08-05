from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from agentsphere import Sandbox


class AgentsphereProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            sbx = Sandbox(api_key=credentials.get("api_key"),
                          domain= "agentsphere.run")

            running_sandboxes = sbx.list(api_key=credentials.get("api_key"),domain= "agentsphere.run")

            sbx.kill()

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

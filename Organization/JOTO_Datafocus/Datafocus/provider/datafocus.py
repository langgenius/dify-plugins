import traceback
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.focus_base import FocusBaseTool


class FocusDifyProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            for _ in FocusBaseTool.from_credentials(credentials).invoke(
                tool_parameters={"action": "listTables"},
            ):
                pass

        except Exception as e:
            print(traceback.print_exc())
            raise ToolProviderCredentialValidationError(str(e))

from collections.abc import Callable, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import AdanosClient, AdanosError, JsonPayload


class AdanosTool(Tool):
    def _invoke_client(
        self, operation: Callable[[AdanosClient], JsonPayload]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            payload = operation(AdanosClient.from_credentials(self.runtime.credentials))
        except (AdanosError, ValueError) as exc:
            yield self.create_text_message(str(exc))
            return
        yield self.create_json_message(payload)

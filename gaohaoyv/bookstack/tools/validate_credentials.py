from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from bookstack_client import BookStackClient, BookStackError
from tools.output_payloads import emit_variable_messages, error_payload, success_payload


class ValidateCredentialsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            client.validate_credentials()
        except BookStackError as exc:
            yield from emit_variable_messages(self, error_payload(str(exc)))
            return

        yield from emit_variable_messages(self, success_payload())

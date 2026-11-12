import os
import sys
from collections.abc import Generator
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from sealgraf_client import (
    SealgrafError,
    client_from_credentials,
    optional_str,
    parse_preauth_result,
    parse_receipt_result,
)

# The parameters this implementation reads. The structural test in
# tests/ asserts this map stays identical to tools/get_receipt.yaml.
EXPECTED_PARAMETERS: dict[str, dict[str, Any]] = {
    "preauth_id": {"type": "string", "required": False},
    "receipt_id": {"type": "string", "required": False},
}


class GetReceiptTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        params = tool_parameters or {}
        preauth_id = optional_str(params.get("preauth_id"))
        receipt_id = optional_str(params.get("receipt_id"))
        if (preauth_id is None) == (receipt_id is None):
            raise SealgrafError(
                "Provide exactly one of preauth_id or receipt_id."
            )
        client = client_from_credentials(self.runtime.credentials)
        if receipt_id is not None:
            result = parse_receipt_result(client.get_receipt(receipt_id))
            summary = (
                f"Receipt {result['receipt_id']}: "
                f"{result.get('amount_minor')} {result.get('currency')} "
                f"sealed at {result.get('created_at')} "
                f"(ledger entry {result.get('entry_seq')})."
            )
        else:
            result = parse_preauth_result(client.get_preauth(preauth_id))
            summary = (
                f"Preauth {result['preauth_id']} is {result.get('state')} "
                f"(decision: {result.get('outcome')}, "
                f"reason: {result.get('reason_code')})."
            )
        yield self.create_json_message(result)
        yield self.create_text_message(summary)

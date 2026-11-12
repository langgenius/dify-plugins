import os
import sys
from collections.abc import Generator
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from sealgraf_client import (
    client_from_credentials,
    parse_claim_result,
    require_str,
)

# The parameters this implementation reads. The structural test in
# tests/ asserts this map stays identical to
# tools/claim_decision_token.yaml.
EXPECTED_PARAMETERS: dict[str, dict[str, Any]] = {
    "preauth_id": {"type": "string", "required": True},
}


class ClaimDecisionTokenTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        params = tool_parameters or {}
        preauth_id = require_str(params.get("preauth_id"), "preauth_id")
        client = client_from_credentials(self.runtime.credentials)
        data = client.claim_decision_token(preauth_id)
        result = parse_claim_result(data, preauth_id)
        yield self.create_json_message(result)
        yield self.create_text_message(
            f"Claimed the decision token for preauth {preauth_id}. "
            "It is single-use: spend it once via complete_purchase "
            "before it expires."
        )

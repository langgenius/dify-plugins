import os
import sys
from collections.abc import Generator
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from sealgraf_client import (
    CATEGORIES,
    SealgrafError,
    client_from_credentials,
    optional_str,
    parse_check_result,
    require_amount_minor,
    validate_currency,
)

# The parameters this implementation reads. The structural test in
# tests/ asserts this map stays identical to tools/check_permission.yaml.
EXPECTED_PARAMETERS: dict[str, dict[str, Any]] = {
    "category": {"type": "select", "required": True},
    "amount_minor": {"type": "number", "required": True},
    "currency": {"type": "string", "required": False},
    "counterparty": {"type": "string", "required": False},
    "description": {"type": "string", "required": False},
    "agent_id": {"type": "string", "required": False},
    "mandate_id": {"type": "string", "required": False},
    "idempotency_key": {"type": "string", "required": False},
}


class CheckPermissionTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        params = tool_parameters or {}
        category = optional_str(params.get("category"))
        if category is None:
            raise SealgrafError("category is required.")
        if category not in CATEGORIES:
            raise SealgrafError(
                f"category must be one of: {', '.join(CATEGORIES)}; "
                f"got {category!r}."
            )
        amount_minor = require_amount_minor(params.get("amount_minor"), "amount_minor")
        currency = validate_currency(params.get("currency"))
        idempotency_key = optional_str(params.get("idempotency_key"))
        if idempotency_key is not None and len(idempotency_key) < 8:
            raise SealgrafError(
                "idempotency_key must be at least 8 characters "
                "(the Sealgraf API refuses shorter keys)."
            )
        client = client_from_credentials(self.runtime.credentials)
        data = client.check_permission(
            category=category,
            amount_minor=amount_minor,
            currency=currency,
            counterparty=optional_str(params.get("counterparty")),
            description=optional_str(params.get("description")),
            agent_id=optional_str(params.get("agent_id")),
            mandate_id=optional_str(params.get("mandate_id")),
            idempotency_key=idempotency_key,
        )
        result = parse_check_result(data)
        yield self.create_json_message(result)
        if result["outcome"] == "allow" and "decision_token" in result:
            summary = (
                f"Sealgraf allowed this purchase (preauth {result['preauth_id']}). "
                "Buy it, then call complete_purchase with the decision token."
            )
        elif result["outcome"] == "allow":
            summary = (
                f"Sealgraf already made this exact check (preauth "
                f"{result['preauth_id']}, idempotent replay) and does not "
                "re-serve the decision token. Use the token from the first "
                "response; if it is lost, run a fresh check without the "
                "idempotency key."
            )
        elif result["outcome"] == "needs_human_approval":
            summary = (
                f"Sealgraf needs the owner's approval first (preauth "
                f"{result['preauth_id']}). Do not buy yet. After the owner "
                "approves in Sealgraf, call claim_decision_token, then "
                "complete_purchase."
            )
        else:
            summary = (
                f"Sealgraf denied this purchase (preauth {result['preauth_id']}, "
                f"reason: {result.get('reason_code')}). Do not buy."
            )
        yield self.create_text_message(summary)

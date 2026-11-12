import os
import sys
from collections.abc import Generator
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from sealgraf_client import (
    PAYMENT_PROVENANCES,
    PAYMENT_RAILS,
    RAIL_REF_KINDS,
    SealgrafError,
    client_from_credentials,
    optional_str,
    parse_complete_result,
    require_amount_minor,
    require_str,
    validate_currency,
    validate_last4,
)

# The parameters this implementation reads. The structural test in
# tests/ asserts this map stays identical to
# tools/complete_purchase.yaml.
EXPECTED_PARAMETERS: dict[str, dict[str, Any]] = {
    "preauth_id": {"type": "string", "required": True},
    "decision_token": {"type": "string", "required": True},
    "completion_nonce": {"type": "string", "required": True},
    "completed_amount_minor": {"type": "number", "required": False},
    "counterparty_receipt_ref": {"type": "string", "required": False},
    "note": {"type": "string", "required": False},
    "payment_rail": {"type": "select", "required": False},
    "payment_rail_label": {"type": "string", "required": False},
    "payment_instrument_label": {"type": "string", "required": False},
    "payment_instrument_last4": {"type": "string", "required": False},
    "payment_virtual_last4": {"type": "string", "required": False},
    "payment_charged_amount_minor": {"type": "number", "required": False},
    "payment_currency": {"type": "string", "required": False},
    "payment_rail_ref_kind": {"type": "select", "required": False},
    "payment_rail_ref_value": {"type": "string", "required": False},
    "payment_provenance": {"type": "select", "required": False},
}


def _validated_choice(value: Any, choices: frozenset, field: str) -> str | None:
    text = optional_str(value)
    if text is None:
        return None
    if text not in choices:
        raise SealgrafError(
            f"{field} must be one of: {', '.join(sorted(choices))}; got {text!r}."
        )
    return text


def _optional_amount(value: Any, field: str) -> int | None:
    if value is None:
        return None
    return require_amount_minor(value, field)


def build_evidence(params: dict[str, Any]) -> dict:
    """Assemble the completion evidence object.

    The key set is CLOSED in production (see/service.py
    ``_SEALED_EVIDENCE_KEYS``): completed_amount_minor,
    counterparty_receipt_ref, note, completed_at, payment. Unknown keys
    are refused by the service, so this builder only ever emits sealed
    keys, and only when the caller actually supplied them.
    """
    evidence: dict[str, Any] = {}
    completed = _optional_amount(
        params.get("completed_amount_minor"), "completed_amount_minor"
    )
    if completed is not None:
        evidence["completed_amount_minor"] = completed
    ref = optional_str(params.get("counterparty_receipt_ref"))
    if ref is not None:
        evidence["counterparty_receipt_ref"] = ref
    note = optional_str(params.get("note"))
    if note is not None:
        evidence["note"] = note

    payment: dict[str, Any] = {}
    rail = _validated_choice(params.get("payment_rail"), PAYMENT_RAILS, "payment_rail")
    if rail is not None:
        payment["rail"] = rail
    rail_label = optional_str(params.get("payment_rail_label"))
    if rail_label is not None:
        if rail != "other":
            raise SealgrafError(
                "payment_rail_label is only allowed when payment_rail is 'other'."
            )
        payment["rail_label"] = rail_label
    elif rail == "other":
        raise SealgrafError(
            "payment_rail_label is required when payment_rail is 'other'."
        )
    instrument_label = optional_str(params.get("payment_instrument_label"))
    if instrument_label is not None:
        payment["instrument_label"] = instrument_label
    instrument_last4 = validate_last4(
        params.get("payment_instrument_last4"), "payment_instrument_last4"
    )
    if instrument_last4 is not None:
        payment["instrument_last4"] = instrument_last4
    virtual_last4 = validate_last4(
        params.get("payment_virtual_last4"), "payment_virtual_last4"
    )
    if virtual_last4 is not None:
        payment["virtual_last4"] = virtual_last4
    charged = params.get("payment_charged_amount_minor")
    if charged is not None:
        if isinstance(charged, bool) or not isinstance(charged, (int, float)):
            raise SealgrafError(
                "payment_charged_amount_minor must be an integer (minor units)."
            )
        if isinstance(charged, float):
            if not charged.is_integer():
                raise SealgrafError(
                    "payment_charged_amount_minor must be a whole number of minor units."
                )
            charged = int(charged)
        if charged < 0:
            raise SealgrafError("payment_charged_amount_minor cannot be negative.")
        payment["charged_amount_minor"] = charged
    payment_currency = validate_currency(params.get("payment_currency"))
    if payment_currency is not None:
        payment["currency"] = payment_currency
    if "charged_amount_minor" in payment and "currency" not in payment:
        raise SealgrafError(
            "payment_currency is required when payment_charged_amount_minor "
            "is supplied (an amount without its unit is not a fact)."
        )
    ref_kind = _validated_choice(
        params.get("payment_rail_ref_kind"), RAIL_REF_KINDS, "payment_rail_ref_kind"
    )
    ref_value = optional_str(params.get("payment_rail_ref_value"))
    if (ref_kind is None) != (ref_value is None):
        raise SealgrafError(
            "payment_rail_ref_kind and payment_rail_ref_value must be "
            "supplied together."
        )
    if ref_kind is not None:
        payment["rail_ref"] = {"kind": ref_kind, "value": ref_value}
    provenance = _validated_choice(
        params.get("payment_provenance"), PAYMENT_PROVENANCES, "payment_provenance"
    )
    if provenance is not None:
        payment["provenance"] = provenance
    if payment:
        evidence["payment"] = payment
    return evidence


class CompletePurchaseTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        params = tool_parameters or {}
        preauth_id = require_str(params.get("preauth_id"), "preauth_id")
        decision_token = require_str(params.get("decision_token"), "decision_token")
        completion_nonce = require_str(
            params.get("completion_nonce"), "completion_nonce"
        )
        evidence = build_evidence(params)
        client = client_from_credentials(self.runtime.credentials)
        data = client.complete_purchase(
            preauth_id,
            decision_token=decision_token,
            completion_nonce=completion_nonce,
            evidence=evidence,
        )
        result = parse_complete_result(data)
        yield self.create_json_message(result)
        yield self.create_text_message(
            f"Sealed receipt {result['receipt_id']} for preauth {preauth_id} "
            f"(ledger entry {result.get('entry_seq')})."
        )

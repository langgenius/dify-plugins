from typing import Any
from dify_plugin import Tool


class EvaluatePaymentTool(Tool):
    name = "evaluate_payment"
    description = (
        "Evaluate whether an AI agent should proceed with payment based on service metadata, "
        "budget, and risk preferences. Returns a decision with detailed reasoning. "
        "IMPORTANT: This tool only provides a RECOMMENDATION (APPROVE/REJECT). "
        "It does NOT execute any payment or transfer funds. "
        "Use a separate payment tool to actually make the payment."
    )

    parameters = {
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "description": "The service metadata object returned by fetch_service_metadata"
            },
            "budget": {
                "type": "number",
                "description": "Maximum budget for this payment (in the service's currency)"
            },
            "min_trust_score": {
                "type": "number",
                "default": 80,
                "description": "Minimum acceptable trust score (0-100)"
            },
            "min_success_rate": {
                "type": "number",
                "default": 0.95,
                "description": "Minimum acceptable success rate (0-1)"
            }
        },
        "required": ["metadata", "budget"]
    }

    def execute(
        self,
        metadata: dict,
        budget: float,
        min_trust_score: float = 80,
        min_success_rate: float = 0.95
    ) -> dict[str, Any]:
        reputation = metadata.get("reputation", {})
        performance = metadata.get("performance", {})
        pricing = metadata.get("pricing", {})
        policy = metadata.get("policy", {})

        checks = []
        should_pay = True

        # Check trust score
        trust_score = reputation.get("trust_score", 0)
        if trust_score < min_trust_score:
            checks.append(f"❌ Trust score too low: {trust_score} < {min_trust_score}")
            should_pay = False
        else:
            checks.append(f"✅ Trust score OK: {trust_score} >= {min_trust_score}")

        # Check success rate
        success_rate = performance.get("success_rate", 0)
        if success_rate < min_success_rate:
            checks.append(f"❌ Success rate too low: {success_rate} < {min_success_rate}")
            should_pay = False
        else:
            checks.append(f"✅ Success rate OK: {success_rate} >= {min_success_rate}")

        # Check budget
        total_cost = pricing.get("estimated_total_cost", pricing.get("amount", 0))
        if total_cost > budget:
            checks.append(f"❌ Cost exceeds budget: {total_cost} > {budget}")
            should_pay = False
        else:
            checks.append(f"✅ Budget OK: {total_cost} <= {budget}")

        # Check refund policy
        refund_policy = policy.get("refund_policy", "none")
        if refund_policy == "none" and trust_score < 90:
            checks.append(f"⚠️ No refund policy and moderate trust ({trust_score})")
        else:
            checks.append(f"✅ Refund policy: {refund_policy}")

        return {
            "should_pay": should_pay,
            "decision": "APPROVE" if should_pay else "REJECT",
            "checks": checks,
            "summary": (
                "All checks passed — safe to pay."
                if should_pay
                else "Payment blocked. Review the check details above."
            )
        }

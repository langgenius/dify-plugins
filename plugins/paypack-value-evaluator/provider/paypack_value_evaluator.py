from dify_plugin import Plugin, Tool
from tools.fetch_metadata import FetchServiceMetadataTool
from tools.evaluate_payment import EvaluatePaymentTool


class PayPackValueEvaluatorPlugin(Plugin):
    name = "paypack_value_evaluator"
    description = (
        "Evaluate AI service value before payment — "
        "helps AI agents make smarter spending decisions. "
        "This plugin does NOT execute any payment; "
        "it only provides a recommendation based on service metadata."
    )

    def tools(self) -> list[Tool]:
        return [
            FetchServiceMetadataTool(),
            EvaluatePaymentTool()
        ]

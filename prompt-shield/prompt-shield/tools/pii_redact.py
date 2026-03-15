"""PII redaction tool for Dify."""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PiiRedactTool(Tool):
    """Detects and redacts personally identifiable information from text."""

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage]:
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Error: input_text is required.")
            return

        try:
            from prompt_shield.pii import PIIRedactor

            redactor = PIIRedactor()
            redaction_result = redactor.redact(input_text)

            result = {
                "redacted_text": redaction_result.redacted_text,
                "pii_found": redaction_result.redaction_count > 0,
                "total_redacted": redaction_result.redaction_count,
                "entity_counts": redaction_result.entity_counts,
            }

            yield self.create_json_message(result)

        except ImportError:
            yield self.create_text_message(
                "Error: prompt-shield is not installed. "
                "Install it with: pip install prompt-shield-ai"
            )
        except Exception as e:
            yield self.create_text_message(f"Error redacting PII: {e}")

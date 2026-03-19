"""PII scan tool for Dify."""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PiiScanTool(Tool):
    """Scans input text to detect personally identifiable information."""

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

            entities = []
            for entity in redaction_result.redacted_entities:
                entities.append({
                    "type": entity.get("entity_type", ""),
                    "text": entity.get("original_text", ""),
                })

            result = {
                "pii_found": redaction_result.redaction_count > 0,
                "total_entities": redaction_result.redaction_count,
                "entity_counts": redaction_result.entity_counts,
                "entities": entities,
            }

            yield self.create_json_message(result)

        except ImportError:
            yield self.create_text_message(
                "Error: prompt-shield is not installed. "
                "Install it with: pip install prompt-shield-ai"
            )
        except Exception as e:
            yield self.create_text_message(f"Error scanning for PII: {e}")

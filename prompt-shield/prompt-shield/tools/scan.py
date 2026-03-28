"""Prompt injection scan tool for Dify."""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ScanTool(Tool):
    """Scans input text for prompt injection attacks."""

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage]:
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Error: input_text is required.")
            return

        try:
            from prompt_shield import PromptShieldEngine

            engine = PromptShieldEngine()
            report = engine.scan(input_text)

            detections = []
            for detection in report.detections:
                if detection.detected:
                    detections.append({
                        "detector_id": detection.detector_id,
                        "confidence": detection.confidence,
                        "severity": detection.severity.value,
                        "explanation": detection.explanation,
                        "matches": [
                            {
                                "pattern": m.pattern,
                                "matched_text": m.matched_text,
                                "description": m.description,
                            }
                            for m in detection.matches
                        ],
                    })

            result = {
                "scan_id": report.scan_id,
                "action": report.action.value,
                "risk_score": report.overall_risk_score,
                "total_detectors_run": report.total_detectors_run,
                "threats_found": len(detections),
                "scan_duration_ms": report.scan_duration_ms,
                "detections": detections,
            }

            yield self.create_json_message(result)

        except ImportError:
            yield self.create_text_message(
                "Error: prompt-shield is not installed. "
                "Install it with: pip install prompt-shield-ai"
            )
        except Exception as e:
            yield self.create_text_message(f"Error scanning text: {e}")

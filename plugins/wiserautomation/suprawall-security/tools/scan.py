from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import httpx

class SupraWallScanTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["api_key"]
        content = tool_parameters.get("content", "")
        tool_name = tool_parameters.get("tool_name", "agent_output")
        policy_id = tool_parameters.get("policy_id")
        fail_on = tool_parameters.get("fail_on", "high")

        # Map Dify tool parameters to SupraWall API /v1/evaluate payload
        # Passing content inside 'arguments' which is what evaluate expects
        payload = {
            "apiKey": api_key,
            "toolName": tool_name,
            "arguments": {"content": content},
            "source": "dify-plugin",
        }
        if policy_id:
            payload["agentId"] = policy_id # Server routes by agentId/policyId

        try:
            with httpx.Client(timeout=10.0) as client:
                # Use production API URL; cloud.dify.ai plugins call external APIs
                resp = client.post(
                    "https://www.supra-wall.com/api/v1/evaluate",
                    json=payload,
                )
                resp.raise_for_status()
                result = resp.json()
        except Exception as e:
            yield self.create_text_message(f"Error connecting to SupraWall: {str(e)}")
            return

        decision = result.get("decision", "DENY")
        passed = (decision == "ALLOW")
        reason = result.get("reason", "Scan failed")

        # If decision is DENY or REQUIRE_APPROVAL, surface the reason as text
        if not passed:
            yield self.create_text_message(f"🚨 SupraWall [{decision}]: {reason}")

        # Structured output for downstream workflow logic
        yield self.create_json_message({
            "passed": passed,
            "decision": decision,
            "reason": reason,
            "violations_count": 0 if passed else 1,
            "risk_score": 10 if passed else 90,
            "report_url": "https://supra-wall.com/dashboard",
        })

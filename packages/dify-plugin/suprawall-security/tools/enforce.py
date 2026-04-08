from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import httpx

class SupraWallEnforceTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["api_key"]
        content = tool_parameters.get("content", "")
        raise_on_deny = tool_parameters.get("raise_on_deny", True)

        payload = {
            "apiKey": api_key,
            "toolName": "agent_output",
            "arguments": {"content": content},
            "framework": "dify",
            "source": "dify-plugin",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
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
        reason = result.get("reason", "Enforcement failed")
        resolved_arguments = result.get("resolvedArguments", {"content": content})
        resolved_content = resolved_arguments.get("content", content)

        if not passed and raise_on_deny:
            # Terminating the workflow step
            yield self.create_text_message(f"❌ SupraWall BLOCKED ACTION: {reason}")
            raise Exception(f"[SupraWall Enforcement Policy] {reason}")

        if not passed:
            yield self.create_text_message(f"🚨 SupraWall [{decision}]: {reason}")

        yield self.create_json_message({
            "passed": passed,
            "decision": decision,
            "reason": reason,
            "resolved_content": resolved_content,
        })

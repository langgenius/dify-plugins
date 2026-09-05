from dify_plugin.entities.tool import Tool
import httpx

class ExecuteTool(Tool):
    def _invoke(self, user_id: str, tool_parameters: dict) -> dict:
        tool_id = tool_parameters.get("tool_id", "").strip()
        payload = tool_parameters.get("payload", "")
        gateway = self.runtime.credentials.get("gateway_url", "https://api.m2mcent.com")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{gateway}/{tool_id}/api/process",
                    json={"input": payload, "data": payload}
                )
                return res.json()
        except Exception as e:
            return {"error": str(e)}

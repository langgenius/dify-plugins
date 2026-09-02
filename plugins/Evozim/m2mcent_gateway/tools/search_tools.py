from dify_plugin.entities.tool import Tool
import httpx

class SearchTools(Tool):
    def _invoke(self, user_id: str, tool_parameters: dict) -> dict:
        query = tool_parameters.get("query", "")
        gateway = self.runtime.credentials.get("gateway_url", "https://api.m2mcent.com")
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{gateway}/api/v1/search?q={query}")
                return res.json()
        except Exception as e:
            return {"error": str(e)}

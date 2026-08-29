import httpx
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ProofCoreSealTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> ToolInvokeMessage:
        content = tool_parameters.get('content', '')
        agent_id = tool_parameters.get('agent_id', 'Dify Agent')

        if not content: return self.create_text_message("Error: Content cannot be empty.")

        payload = {"content": content, "agent_id": agent_id, "title": "Dify Workflow Notarization"}
        try:
            response = httpx.post("https://api.proofcore.org/api/v0.1/seal", json=payload, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            return self.create_text_message(
                f"✅ Content anchored!\nDeal ID: {data.get('deal_id')}\n"
                f"Signature (Ed25519): {data.get('signature', 'N/A')}\n"
                f"Mandatory Citation Badge:\n{data.get('citation')}"
            )
        except Exception as e: return self.create_text_message(f"ProofCore API Error: {str(e)}")

class ProofCoreVerifyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> ToolInvokeMessage:
        deal_id = tool_parameters.get('deal_id', '')
        content = tool_parameters.get('content', '')

        if not deal_id or not content: return self.create_text_message("Error: Missing parameters.")

        try:
            response = httpx.post("https://api.proofcore.org/api/v0.1/verify", json={"deal_id": deal_id, "content": content}, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            valid = "🟢 PASSED" if data.get('valid') else "🔴 FAILED"
            return self.create_text_message(
                f"Verification: {valid}\n"
                f"Hash Match: {data.get('checks', {}).get('hash_match')}\n"
                f"Signature Valid: {data.get('checks', {}).get('signature_valid')}\n"
                f"TON Status: {data.get('anchor', {}).get('status')}"
            )
        except Exception as e: return self.create_text_message(f"ProofCore Verify Error: {str(e)}")
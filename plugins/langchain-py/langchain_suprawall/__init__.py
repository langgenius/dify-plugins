# Copyright 2026 SupraWall Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import requests
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler

class SupraWallCallbackHandler(BaseCallbackHandler):
    """Callback handler to enforce suprawall policies in LangChain."""
    
    def __init__(self, api_key: Optional[str] = None, agent_id: str = "langchain_agent"):
        self.api_key = api_key or os.environ.get("SUPRAWALL_API_KEY")
        if not self.api_key:
            raise ValueError("SUPRAWALL_API_KEY is required")
        self.agent_id = agent_id
        self.api_url = os.environ.get("suprawall_API_URL", "https://api.supra-wall.com/v1/evaluate")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get("name")
        res = requests.post(self.api_url, json={
            "agentId": self.agent_id,
            "toolName": tool_name,
            "arguments": input_str
        }, headers={"Authorization": f"Bearer {self.api_key}"})
        
        if res.status_code == 200:
            decision = res.json().get("decision")
            if decision == "DENY":
                raise Exception(f"suprawall Policy Violation: Tool '{tool_name}' is explicitly denied.")
            elif decision == "REQUIRE_APPROVAL":
                raise Exception(f"suprawall: Tool '{tool_name}' requires human approval.")
        else:
            raise Exception("suprawall Unreachable: Failing closed.")

class SupraWallToolkit:
    """Convenience class to inject suprawall into LangChain agents."""
    def __init__(self, api_key: Optional[str] = None):
        self.callback = SupraWallCallbackHandler(api_key=api_key)

    def get_callbacks(self):
        return [self.callback]

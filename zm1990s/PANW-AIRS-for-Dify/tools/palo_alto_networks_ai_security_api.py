from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

AIRS_API_URL = "https://service.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request"

class PaloAltoNetworksAiSecurityApiTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        headers = {
            "Content-Type": "application/json",
            "x-pan-token": self.runtime.credentials["airs_api_key"]
        }

        contents = {}
        if tool_parameters.get("inputoroutput") == "input":
            contents["prompt"] = tool_parameters["query"]
        elif tool_parameters.get("inputoroutput") == "output":
            contents["response"] = tool_parameters["query"]
        # Determine the profile name based on the profileoverride parameter
        profileoverride = tool_parameters.get("profileoverride")
        if profileoverride:
            profile_name = profileoverride
        else:
            profile_name = self.runtime.credentials["airs_ai_profile_name"]

        data = {
            "metadata": {
                "ai_model": tool_parameters.get("modelname", "dify_default_llm"),
                "app_name": tool_parameters.get("appname", "dify_app"),
                "app_user": tool_parameters.get("appuser", "dify_user1")
            },
            "contents": [contents],
            "ai_profile": {
                "profile_name": profile_name
            }
        }

        response = requests.post(AIRS_API_URL, headers=headers, json=data, verify=False)
        response.raise_for_status()
        valuable_res = response.json()
        yield self.create_text_message(valuable_res["action"])
        yield self.create_json_message(valuable_res)
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class ApiInvokeError(Exception):
    pass

class Ipv4LocationCity(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        key = tool_parameters.get("key")
        if not key:
            raise ToolProviderCredentialValidationError("Please provide a valid key.You can get it from https://api.jishishuke.com/")

        ipAddress = tool_parameters.get("ipAddress")
        if not ipAddress:
            raise ToolProviderCredentialValidationError("Please provide a valid ipAddress.")
        
        url = "https://api.jishishuke.com/api/jsap/ipl/ipv6/global/city/v1"
        params = {
            "key": key,
            "ipAddress": ipAddress
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ApiInvokeError(f"请求失败：{response.status_code} - {response.text}")
        
        yield self.create_json_message(response.json())
        
        # yield self.create_json_message({
        #     "result": "Hello, world!"
        # })

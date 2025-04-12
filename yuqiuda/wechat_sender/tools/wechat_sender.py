from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class WechatSenderTool(Tool):
    def _get_token(self, url):
        payload={}
        headers = {}

        res_token = requests.request("POST", url, headers=headers, data=payload)
        res_token.raise_for_status()
        return res_token.json()


    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        server_url = self.runtime.credentials["server_url"]
        toWxid = self.runtime.credentials["receiver_id"]
        token = self.runtime.credentials["token"]
        appid = self.runtime.credentials["appid"]

        # res_token = self._get_token(server_url +"/tools/getTokenId")
        # token = res_token["data"]
        # print(token)

        # appid_url = server_url +"/login/deviceList"

        # payload = json.dumps({})
        # headers = {
        #     'X-GEWE-TOKEN': token,
        #     'Content-Type': 'application/json'
        # }

        # res_appid = requests.request("POST", appid_url, headers=headers, data=payload).json()
        # appid = res_appid["data"][0]
        # print(appid)


        sender_url = server_url +"/message/postText"
        payload = json.dumps({
            "appId": appid,
            "toWxid": toWxid,
            "content": tool_parameters["content"]
        })
        headers = {
            'X-GEWE-TOKEN': token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", sender_url, headers=headers, data=payload)
        response.raise_for_status()
        # print(tool_parameters["content"])


        yield self.create_json_message(response.json())

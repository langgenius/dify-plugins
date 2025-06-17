import json
from collections.abc import Generator
from typing import Any

import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.text_check import TextCheckAPI


class YidunContentSecurityTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = {
            "secretId": self.runtime.credentials["yidun_secret_id"],
            "secretKey": self.runtime.credentials["yidun_secret_key"],
            "textBusinessId": self.runtime.credentials["yidun_text_business_id"],
            "textContent": tool_parameters["text_content"],
        }
        time_stamp = str(int(time.time()))  # 时间戳获取
        ret = {}
        if (params["textBusinessId"] is not None and params["textBusinessId"] != ""
            and params["textContent"] is not None and params["textContent"] != ""):
            text_api = TextCheckAPI(params["secretId"], params["secretKey"], params["textBusinessId"])
            text_check_param = {
                "dataId": "dify-yidun-text-check-" + time_stamp,
                "content": params["textContent"]
            }
            text_ret = text_api.check(text_check_param)
            ret["result"] = text_ret
            code: int = text_ret["code"]
            if code == 200:
                result: dict = text_ret["result"]
                antispam: dict = result["antispam"]
                label: int = antispam["label"]
                suggestion: int = antispam["suggestion"]
                ret["label"] = label
                ret["suggestion"] = suggestion

        yield self.create_json_message(ret)

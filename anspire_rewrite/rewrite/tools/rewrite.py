from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.httpUtil import do_request


class RewriteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        _auth_key = self.runtime.credentials.get('api_key')
        _endpoint = self.runtime.credentials.get('endpoint')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_auth_key}"
        }
        params = {
            "Question": tool_parameters["question"],
            "Messages": tool_parameters["messages"]
        }

        # 多轮改写
        _request_obj = (
            "POST",
            f"{_endpoint}",
            headers,
            None,
            params
        )
        status_code,_response = do_request(_request_obj)
        yield self.create_json_message(_response)

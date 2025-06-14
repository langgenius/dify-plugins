from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

def analyze(api_key, text: str) -> str:
    """
    分析内容，返回结果
    """
    url = "https://aisecurity.ueba.insightx.cc/api/analyze/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "text": text
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


class RedkernelTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 1. 从运行时获取凭证
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("RedKernel API Key is missing.")
        
        # 2. 获取工具输入参数
        text = tool_parameters.get("text", "")
        if not text:
            raise Exception("text cannot be empty.")
        # 3. 调用库执行操作
        try:
            result = analyze(api_key, text)
        except Exception as e:
            # 如果库调用失败，抛出异常
            raise Exception(f"调用 RedKernel API 失败: {e}")
        yield self.create_json_message({
            "result": result
        })

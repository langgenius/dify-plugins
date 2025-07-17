from collections.abc import Generator
from typing import Any
import httpx

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SmartseachTool(Tool):
    """
    一个智能网页搜索工具，集成 Cloudsway API。
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # 1. 获取凭证
        try:
            server_key = self.runtime.credentials["server_key"]
        except KeyError:
            raise Exception("Cloudsway API Key 未配置或无效。请在插件设置中提供。")

        # 2. 获取工具参数
        query = tool_parameters.get("query")
        count = tool_parameters.get("count", 10)
        offset = tool_parameters.get("offset", 0)
        setLang = tool_parameters.get("setLang", "en")
        safeSearch = tool_parameters.get("safeSearch", "Strict")

        # 3. 构造 API 请求
        if not server_key or "-" not in server_key:
            yield self.create_json_message({"error": "API key format error"})
            return

        endpoint, api_key = server_key.split("-", 1)
        url = f"https://searchapi.cloudsway.net/search/{endpoint}/smart"
        params = {
            'q': query,
            'count': count,
            'offset': offset,
            'mkt': setLang,
            'safeSearch': safeSearch
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'pragma': 'no-cache',
        }

        # 4. 请求并处理结果
        try:
            with httpx.Client(timeout=60) as client:
                response = client.get(url, params=params, headers=headers)
            results = response.json()

        except Exception as e:
            results = {"error": f"搜索 API 调用失败: {e}"}

        yield self.create_json_message(results)

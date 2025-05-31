import json
from collections.abc import Generator
from typing import Any
# from ytelegraph import TelegraphAPI # 导入我们使用的库
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

SERP_API_URL = "https://serpapi.com/search"


class PaperAbstractTool(Tool):
    """
    一个简单的 Telegraph 发布工具。
    """

    def _parse_response(self, response: dict) -> dict:
        result = {}
        if "knowledge_graph" in response:
            result["title"] = response["knowledge_graph"].get("title", "")
            result["description"] = response["knowledge_graph"].get("description", "")
        if "organic_results" in response:
            result["organic_results"] = [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
                for item in response["organic_results"]
            ]
        return result

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        根据输入的标题和内容，创建一个新的 Telegraph 页面。

        Args:
            tool_parameters: 一个包含工具输入参数的字典:
                - p_title (str): Telegraph 页面的标题。
                - p_content (str): 要发布的 Markdown 格式的内容。

        Yields:
            ToolInvokeMessage: 包含成功创建的 Telegraph 页面 URL 的消息。

        Raises:
            Exception: 如果页面创建失败，则抛出包含错误信息的异常。
        """
        paper_name = tool_parameters.get("paper_name", "")  # 使用 .get 提供默认值

        if not paper_name:
            raise Exception("论文题目不能为空。")

        # abstract = {"abstract": "I am abstract"}
        abstract = {}

        try:
            params = {
                "api_key": self.runtime.credentials["serpapi_api_key"],
                "q": paper_name,
                "engine": "google_scholar",
                "google_domain": "google.com",
                "gl": "us",
                "hl": "en",
            }

            # 发送请求
            response = requests.get(url=SERP_API_URL, params=params, timeout=5)
            response.raise_for_status()

            # 解析响应
            valuable_res = response.json()
            # valuable_res = self._parse_response(response.json())

            # 获取摘要
            if "organic_results" in valuable_res and len(valuable_res["organic_results"]) > 0:
                abstract['abstract'] = valuable_res["organic_results"][0].get("snippet", "Summary not found")
                # abstract['abstract'] = valuable_res
            else:
                abstract['abstract'] = "Summary not found"

            # results[title] = abstract

        except Exception as e:
            abstract['abstract'] = f"Failed to obtain summary: {str(e)}"

        # 4. 返回结果
        yield self.create_text_message(json.dumps(abstract))

from collections.abc import Generator
from typing import Any

import requests
from googleapiclient.discovery import build

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GoogleSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取凭据
        api_key = self.runtime.credentials["api_key"]
        cse_id = self.runtime.credentials["cse_id"]
        
        # 获取搜索参数
        query = tool_parameters["query"]
        num_results = tool_parameters.get("num_results", 10)
        
        try:
            # 创建 Custom Search API 服务
            service = build("customsearch", "v1", developerKey=api_key)
            
            # 执行搜索
            result = service.cse().list(
                q=query,
                cx=cse_id,
                num=min(num_results, 10)  # Google API 限制最多返回10个结果
            ).execute()
            
            # 处理搜索结果
            search_results = []
            if "items" in result:
                for item in result["items"]:
                    search_results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "pagemap": item.get("pagemap", {})
                    })
            
            # 返回结果
            yield self.create_json_message({
                "query": query,
                "total_results": result.get("searchInformation", {}).get("totalResults", "0"),
                "search_time": result.get("searchInformation", {}).get("searchTime", 0),
                "results": search_results
            })
            
        except Exception as e:
            # 如果发生错误，返回错误信息
            yield self.create_error_message(str(e)) 
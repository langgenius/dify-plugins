from collections.abc import Generator
from typing import Any
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class JsonExtractorTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        json_data = tool_parameters.get("json_data")
        query_paths = tool_parameters.get("query_path")

        if not json_data or not query_paths:
            yield self.create_json_message({"error": "Missing 'json_data' or 'query_path'"})
            return

        json_data = self.parse_json(json_data)
        if json_data is None:
            yield self.create_json_message({"error": "Invalid JSON data"})
            return

        results = {
            path: self.extract_value(json_data, path.split("."))
            for path in map(str.strip, query_paths.split(","))
        }

        yield self.create_json_message(results)
        yield self.create_text_message(json.dumps(results, ensure_ascii=False))

    @staticmethod
    def parse_json(json_data: Any) -> Any:
        """解析 JSON 数据，确保返回 Python 对象"""
        if isinstance(json_data, str):
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                return None
        return json_data

    @staticmethod
    def extract_value(data: Any, path: list[str]) -> Any:
        """遍历路径，逐层提取数据"""
        try:
            for key in path:
                if isinstance(data, dict):
                    data = data[key]
                elif isinstance(data, list):
                    data = data[int(key)]  # 可能抛出 ValueError 或 IndexError
                else:
                    raise KeyError(f"Key '{key}' not found")
            return data
        except (KeyError, ValueError, IndexError) as e:
            return str(e)

import json
import requests
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

SCRAPELESS_API_URL = "https://api.scrapeless.com/api/v1/scraper/request"


class Payload:
    def __init__(self, actor, input_data):
        self.actor = actor
        self.input = input_data


class DeepSerpapiSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        input_data = {
            "q": tool_parameters["query"],
            "gl": "us",
            "hl": "en",
        }

        payload = Payload("scraper.google.search", input_data)
        data = json.dumps(payload.__dict__)

        headers = {
            "x-api-token": self.runtime.credentials["scrapeless_api_key"], "Content-Type": "application/json"}

        response = requests.post(url=SCRAPELESS_API_URL,
                                 data=data, headers=headers)
        response.raise_for_status()

        result = self._transform_response(response.json())

        yield self.create_json_message(result)

    def _transform_response(self, response: dict) -> dict:
        result = {}
        if "organic_results" in response:
            result["organic_results"] = [
                {"title": item.get("title", ""), "link": item.get(
                    "link", ""), "snippet": item.get("snippet", "")}
                for item in response["organic_results"]
            ]
        return result

from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from .firecrawl_appx import FirecrawlApp, get_array_params, get_json_params, process_formats_v2


class ScrapeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        the api doc:
        https://docs.firecrawl.dev/api-reference/endpoint/scrape
        """
        app = FirecrawlApp(
            api_key=self.runtime.credentials["firecrawl_api_key"], base_url=self.runtime.credentials["base_url"]
        )
        payload = {}
        
        # Process formats using v2 format processor
        processed_formats = process_formats_v2(tool_parameters)
        if processed_formats:
            payload["formats"] = processed_formats
        
        payload["onlyMainContent"] = tool_parameters.get("onlyMainContent", True)
        payload["includeTags"] = get_array_params(tool_parameters, "includeTags")
        payload["excludeTags"] = get_array_params(tool_parameters, "excludeTags")
        payload["headers"] = get_json_params(tool_parameters, "headers")
        payload["waitFor"] = tool_parameters.get("waitFor", 0)
        payload["timeout"] = tool_parameters.get("timeout", 30000)
        
        # v2 new parameters with defaults
        payload["maxAge"] = tool_parameters.get("maxAge", 172800000)  # 2 days default
        payload["blockAds"] = tool_parameters.get("blockAds", True)
        payload["skipTlsVerification"] = tool_parameters.get("skipTlsVerification", True)
        payload["removeBase64Images"] = tool_parameters.get("removeBase64Images", True)
        payload["mobile"] = tool_parameters.get("mobile", False)
        payload["parsers"] = get_array_params(tool_parameters, "parsers")
        
        # v2 advanced options
        payload["actions"] = get_json_params(tool_parameters, "actions")
        location = get_json_params(tool_parameters, "location")
        if location:
            payload["location"] = location
        payload["proxy"] = tool_parameters.get("proxy")
        payload["storeInCache"] = tool_parameters.get("storeInCache", True)
        payload["zeroDataRetention"] = tool_parameters.get("zeroDataRetention", False)
        
        # Remove None/empty values
        payload = {k: v for (k, v) in payload.items() if v not in (None, "", [])}
        
        crawl_result = app.scrape_url(url=tool_parameters["url"], **payload)
        
        # Extract result from v2 response structure
        data = crawl_result.get("data", {})
        markdown_result = data.get("markdown", "")
        
        yield self.create_text_message(markdown_result)
        yield self.create_json_message(crawl_result)
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

from .firecrawl_appx import FirecrawlApp


class MapTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        the api doc:
        https://docs.firecrawl.dev/api-reference/endpoint/map
        """
        app = FirecrawlApp(
            api_key=self.runtime.credentials["firecrawl_api_key"], base_url=self.runtime.credentials["base_url"]
        )
        payload = {}
        payload["search"] = tool_parameters.get("search")
        
        # v2 change: ignoreSitemap (bool) -> sitemap (string: "include", "skip", "only")
        ignore_sitemap = tool_parameters.get("ignoreSitemap", False)
        if ignore_sitemap:
            payload["sitemap"] = "skip"
        else:
            payload["sitemap"] = tool_parameters.get("sitemap", "include")
            
        payload["includeSubdomains"] = tool_parameters.get("includeSubdomains", False)
        payload["ignoreQueryParameters"] = tool_parameters.get("ignoreQueryParameters", False)
        payload["limit"] = tool_parameters.get("limit", 5000)
        payload["timeout"] = tool_parameters.get("timeout")
        
        # Remove None/empty values
        payload = {k: v for (k, v) in payload.items() if v not in (None, "")}
        
        map_result = app.map(url=tool_parameters["url"], **payload)
        yield self.create_json_message(map_result)
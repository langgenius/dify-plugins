from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

from .firecrawl_appx import FirecrawlApp, get_array_params, get_json_params, process_formats_v2


class CrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        the api doc:
        https://docs.firecrawl.dev/api-reference/endpoint/crawl-post
        """
        app = FirecrawlApp(
            api_key=self.runtime.credentials["firecrawl_api_key"], base_url=self.runtime.credentials["base_url"]
        )
        payload = {}
        wait_for_results = tool_parameters.get("wait_for_results", True)
        
        # Basic crawl parameters
        payload["excludePaths"] = get_array_params(tool_parameters, "excludePaths")
        payload["includePaths"] = get_array_params(tool_parameters, "includePaths")
        
        # v2 parameters with correct mapping
        if tool_parameters.get("maxDepth"):
            payload["maxDiscoveryDepth"] = tool_parameters.get("maxDepth")
        elif tool_parameters.get("maxDiscoveryDepth"):
            payload["maxDiscoveryDepth"] = tool_parameters.get("maxDiscoveryDepth")
            
        # Sitemap handling
        ignore_sitemap = tool_parameters.get("ignoreSitemap", False)
        if ignore_sitemap:
            payload["sitemap"] = "skip"
        else:
            payload["sitemap"] = tool_parameters.get("sitemap", "include")
            
        payload["limit"] = tool_parameters.get("limit", 5)
        
        # v2 crawl domain settings
        if tool_parameters.get("allowBackwardLinks"):
            payload["crawlEntireDomain"] = True
        elif tool_parameters.get("crawlEntireDomain"):
            payload["crawlEntireDomain"] = tool_parameters.get("crawlEntireDomain")
            
        payload["allowExternalLinks"] = tool_parameters.get("allowExternalLinks", False)
        
        # New v2 parameters
        payload["allowSubdomains"] = tool_parameters.get("allowSubdomains", False)
        payload["ignoreQueryParameters"] = tool_parameters.get("ignoreQueryParameters", False)
        payload["delay"] = tool_parameters.get("delay")
        payload["maxConcurrency"] = tool_parameters.get("maxConcurrency")
        
        # v2 new parameter: prompt for smart crawling
        payload["prompt"] = tool_parameters.get("prompt")
        
        # Webhook handling - v2 enhanced format
        webhook = tool_parameters.get("webhook")
        if webhook:
            if isinstance(webhook, str):
                # Simple webhook URL string - convert to v2 format
                payload["webhook"] = {
                    "url": webhook,
                    "events": ["completed"]  # Default to completed event
                }
            elif isinstance(webhook, dict):
                # Enhanced webhook object for v2
                webhook_obj = {"url": webhook.get("url")}
                if webhook.get("headers"):
                    webhook_obj["headers"] = webhook.get("headers")
                if webhook.get("metadata"):
                    webhook_obj["metadata"] = webhook.get("metadata")
                if webhook.get("events"):
                    webhook_obj["events"] = webhook.get("events")
                else:
                    webhook_obj["events"] = ["completed"]  # Default
                payload["webhook"] = webhook_obj
        
        # Scrape options processing
        scrapeOptions = {}
        processed_formats = process_formats_v2(tool_parameters)
        if processed_formats:
            scrapeOptions["formats"] = processed_formats
            
        scrapeOptions["headers"] = get_json_params(tool_parameters, "headers")
        scrapeOptions["includeTags"] = get_array_params(tool_parameters, "includeTags")
        scrapeOptions["excludeTags"] = get_array_params(tool_parameters, "excludeTags")
        scrapeOptions["onlyMainContent"] = tool_parameters.get("onlyMainContent", False)
        scrapeOptions["waitFor"] = tool_parameters.get("waitFor", 0)
        
        # v2 new scrape options with defaults
        scrapeOptions["maxAge"] = tool_parameters.get("maxAge", 172800000)  # 2 days default
        scrapeOptions["blockAds"] = tool_parameters.get("blockAds", True)
        scrapeOptions["skipTlsVerification"] = tool_parameters.get("skipTlsVerification", True)
        scrapeOptions["removeBase64Images"] = tool_parameters.get("removeBase64Images", True)
        scrapeOptions["mobile"] = tool_parameters.get("mobile", False)
        scrapeOptions["timeout"] = tool_parameters.get("timeout")
        
        # v2 additional scrape options
        scrapeOptions["parsers"] = get_array_params(tool_parameters, "parsers")
        scrapeOptions["storeInCache"] = tool_parameters.get("storeInCache", True)
        
        # v2 advanced scrape options
        scrapeOptions["actions"] = get_json_params(tool_parameters, "actions")
        location = get_json_params(tool_parameters, "location")
        if location:
            scrapeOptions["location"] = location
        scrapeOptions["proxy"] = tool_parameters.get("proxy")
        
        # Remove None/empty values
        scrapeOptions = {k: v for (k, v) in scrapeOptions.items() if v not in (None, "", [])}
        if scrapeOptions:
            payload["scrapeOptions"] = scrapeOptions
            
        # v2 global options
        payload["zeroDataRetention"] = tool_parameters.get("zeroDataRetention", False)
            
        # Clean up payload
        payload = {k: v for (k, v) in payload.items() if v not in (None, "", [])}
        
        crawl_result = app.crawl_url(url=tool_parameters["url"], wait=wait_for_results, **payload)
        yield self.create_json_message(crawl_result)
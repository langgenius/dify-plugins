from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class CrawlTool(Tool):
    def _invoke(
        self, 
        tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from olostep import Olostep, Olostep_BaseError
        
        api_key = self.runtime.credentials["api_key"]
        client = Olostep(api_key=api_key)
        
        url = tool_parameters.get("url", "").strip()
        max_pages = int(tool_parameters.get("max_pages", 20))
        include_urls = tool_parameters.get("include_urls")
        exclude_urls = tool_parameters.get("exclude_urls")
        search_query = tool_parameters.get("search_query")
        
        if not url:
            yield self.create_text_message("Error: URL is required")
            return
        
        try:
            kwargs = {
                "start_url": url,
                "max_pages": max_pages,
            }
            if include_urls:
                kwargs["include_urls"] = [p.strip() for p in include_urls.split(",")]
            if exclude_urls:
                kwargs["exclude_urls"] = [p.strip() for p in exclude_urls.split(",")]
            if search_query:
                kwargs["search_query"] = search_query
            
            crawl = client.crawls.create(**kwargs)
            
            pages_content = []
            for page in crawl.pages():
                page.retrieve(["markdown"])
                markdown_content = page.markdown_content or ""
                pages_content.append(f"## {page.url}\n\n{markdown_content}\n\n---")
            
            content = "\n".join(pages_content)
            yield self.create_text_message(content)
            
        except Olostep_BaseError as e:
            yield self.create_text_message(f"Olostep API error: {type(e).__name__}: {e}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {e}")

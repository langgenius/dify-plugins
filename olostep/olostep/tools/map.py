from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class MapTool(Tool):
    def _invoke(
        self, 
        tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from olostep import Olostep, Olostep_BaseError
        
        api_key = self.runtime.credentials["api_key"]
        client = Olostep(api_key=api_key)
        
        url = tool_parameters.get("url", "").strip()
        include_urls = tool_parameters.get("include_urls")
        exclude_urls = tool_parameters.get("exclude_urls")
        top_n = int(tool_parameters.get("top_n", 100))
        
        if not url:
            yield self.create_text_message("Error: URL is required")
            return
        
        try:
            kwargs = {
                "url": url,
                "top_n": top_n,
            }
            if include_urls:
                kwargs["include_urls"] = [p.strip() for p in include_urls.split(",")]
            if exclude_urls:
                kwargs["exclude_urls"] = [p.strip() for p in exclude_urls.split(",")]
            
            maps = client.maps.create(**kwargs)
            
            urls = []
            for map_obj in maps.urls():
                urls.append(map_obj)
            
            content = "\n".join(urls)
            yield self.create_text_message(content)
            
        except Olostep_BaseError as e:
            yield self.create_text_message(f"Olostep API error: {type(e).__name__}: {e}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {e}")

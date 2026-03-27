from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class SearchTool(Tool):
    def _invoke(
        self, 
        tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from olostep import Olostep, Olostep_BaseError
        
        api_key = self.runtime.credentials["api_key"]
        client = Olostep(api_key=api_key)
        
        query = tool_parameters.get("query", "").strip()
        
        if not query:
            yield self.create_text_message("Error: Query is required")
            return
        
        try:
            search_result = client.searches.create(query=query)
            
            results = []
            for link in search_result.links():
                title = link.get("title", "")
                url = link.get("url", "")
                description = link.get("description", "")
                results.append(f"**{title}**\n{url}\n{description}")
            
            content = "\n\n---\n\n".join(results)
            yield self.create_text_message(content)
            
        except Olostep_BaseError as e:
            yield self.create_text_message(f"Olostep API error: {type(e).__name__}: {e}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {e}")

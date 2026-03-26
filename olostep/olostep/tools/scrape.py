from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class ScrapeTool(Tool):
    def _invoke(
        self, 
        tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from olostep import Olostep, Olostep_BaseError
        
        api_key = self.runtime.credentials["api_key"]
        client = Olostep(api_key=api_key)
        
        url = tool_parameters.get("url", "").strip()
        formats = tool_parameters.get("formats", "markdown")
        country = tool_parameters.get("country")
        parser_id = tool_parameters.get("parser_id")
        wait = tool_parameters.get("wait_before_scraping", 0)
        
        if not url:
            yield self.create_text_message("Error: URL is required")
            return
        
        try:
            fmt_list = [f.strip() for f in formats.split(",")]
            kwargs = {
                "url_to_scrape": url,
                "formats": fmt_list,
                "wait_before_scraping": int(wait),
            }
            if country:
                kwargs["country"] = country.lower()
            if parser_id:
                kwargs["parser"] = {"id": parser_id}
            
            result = client.scrapes.create(**kwargs)
            
            if "json" in fmt_list and result.json_content:
                content = result.json_content
            elif "markdown" in fmt_list and result.markdown_content:
                content = result.markdown_content
            elif "text" in fmt_list and result.text_content:
                content = result.text_content
            elif "html" in fmt_list and result.html_content:
                content = result.html_content
            else:
                content = "No content returned for the requested formats."
            
            yield self.create_text_message(content)
            
        except Olostep_BaseError as e:
            yield self.create_text_message(f"Olostep API error: {type(e).__name__}: {e}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {e}")

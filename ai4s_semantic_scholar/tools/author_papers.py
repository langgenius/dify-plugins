from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class AuthorPapersTool(Tool):
    """
    Get papers published by a specific author
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        author_id = tool_parameters.get("author_id", "")
        if not author_id:
            yield self.create_text_message("Error: Author ID is required")
            return
        
        limit = min(max(int(tool_parameters.get("limit", 20)), 1), 100)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/author/{author_id}/papers",
                headers={"Authorization": f"Bearer {api_key}"},
                params={
                    "fields": "paperId,title,year,citationCount,venue,openAccessPdf",
                    "limit": limit
                },
                timeout=30
            )
            
            if response.status_code == 401:
                yield self.create_text_message("Error: Invalid API key")
                return
            elif response.status_code == 402:
                yield self.create_text_message("Error: Insufficient credits. Please recharge at ai4scholar.net")
                return
            elif response.status_code == 404:
                yield self.create_text_message(f"Error: Author not found with ID: {author_id}")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"Error: API returned status {response.status_code}")
                return
            
            data = response.json()
            papers = data.get("data", [])
            
            if not papers:
                yield self.create_text_message(f"No papers found for author ID: {author_id}")
                return
            
            result_lines = [f"# Papers by Author\n**Author ID:** {author_id} | **Showing:** {len(papers)} papers\n"]
            
            for i, paper in enumerate(papers, 1):
                title = paper.get("title", "N/A")
                year = paper.get("year", "N/A")
                citations = paper.get("citationCount", 0)
                venue = paper.get("venue", "")
                paper_id = paper.get("paperId", "")
                
                open_access = paper.get("openAccessPdf")
                has_pdf = "📄" if open_access else ""
                
                result_lines.append(f"### {i}. {has_pdf} {title}")
                result_lines.append(f"**Year:** {year} | **Citations:** {citations}")
                if venue:
                    result_lines.append(f"**Venue:** {venue}")
                result_lines.append(f"**Paper ID:** {paper_id}")
                result_lines.append("")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

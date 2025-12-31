from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class PaperCitationsTool(Tool):
    """
    Get papers that cite a specific paper
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        paper_id = tool_parameters.get("paper_id", "")
        if not paper_id:
            yield self.create_text_message("Error: Paper ID is required")
            return
        
        limit = min(max(int(tool_parameters.get("limit", 20)), 1), 100)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/paper/{paper_id}/citations",
                headers={"Authorization": f"Bearer {api_key}"},
                params={
                    "fields": "paperId,title,authors,year,citationCount,venue",
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
                yield self.create_text_message(f"Error: Paper not found with ID: {paper_id}")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"Error: API returned status {response.status_code}")
                return
            
            data = response.json()
            citations = data.get("data", [])
            
            if not citations:
                yield self.create_text_message(f"No citations found for paper: {paper_id}")
                return
            
            result_lines = [f"# Papers Citing This Paper\n**Paper ID:** {paper_id} | **Showing:** {len(citations)} citations\n"]
            
            for i, item in enumerate(citations, 1):
                paper = item.get("citingPaper", {})
                title = paper.get("title", "N/A")
                authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:3]])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                year = paper.get("year", "N/A")
                cite_count = paper.get("citationCount", 0)
                venue = paper.get("venue", "")
                citing_paper_id = paper.get("paperId", "")
                
                result_lines.append(f"### {i}. {title}")
                result_lines.append(f"**Authors:** {authors}")
                result_lines.append(f"**Year:** {year} | **Citations:** {cite_count}")
                if venue:
                    result_lines.append(f"**Venue:** {venue}")
                result_lines.append(f"**Paper ID:** {citing_paper_id}")
                result_lines.append("")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

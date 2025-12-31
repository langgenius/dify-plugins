from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class PaperRecommendationsTool(Tool):
    """
    Get paper recommendations based on a given paper
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        paper_id = tool_parameters.get("paper_id", "")
        if not paper_id:
            yield self.create_text_message("Error: Paper ID is required")
            return
        
        limit = min(max(int(tool_parameters.get("limit", 10)), 1), 100)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        try:
            # Use the recommendations endpoint
            response = requests.get(
                f"{self.BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                params={
                    "fields": "paperId,title,authors,year,citationCount,venue,abstract,openAccessPdf",
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
                yield self.create_text_message(f"Error: Paper not found or no recommendations available for: {paper_id}")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"Error: API returned status {response.status_code}")
                return
            
            data = response.json()
            papers = data.get("recommendedPapers", [])
            
            if not papers:
                yield self.create_text_message(f"No recommendations found for paper: {paper_id}")
                return
            
            result_lines = [f"# Paper Recommendations\n**Based on:** {paper_id} | **Found:** {len(papers)} recommendations\n"]
            
            for i, paper in enumerate(papers, 1):
                title = paper.get("title", "N/A")
                authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:3]])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                year = paper.get("year", "N/A")
                citations = paper.get("citationCount", 0)
                venue = paper.get("venue", "")
                rec_paper_id = paper.get("paperId", "")
                
                abstract = paper.get("abstract", "")
                if abstract and len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                
                open_access = paper.get("openAccessPdf")
                pdf_url = open_access.get("url", "") if open_access else ""
                
                result_lines.append(f"### {i}. {title}")
                result_lines.append(f"**Authors:** {authors}")
                result_lines.append(f"**Year:** {year} | **Citations:** {citations}")
                if venue:
                    result_lines.append(f"**Venue:** {venue}")
                if abstract:
                    result_lines.append(f"**Abstract:** {abstract}")
                if pdf_url:
                    result_lines.append(f"**PDF:** {pdf_url}")
                result_lines.append(f"**Paper ID:** {rec_paper_id}")
                result_lines.append("")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

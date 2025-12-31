from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class TitleSearchTool(Tool):
    """
    Search for papers by title
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        title = tool_parameters.get("title", "")
        if not title:
            yield self.create_text_message("Error: Paper title is required")
            return
        
        year = tool_parameters.get("year")
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        params = {
            "query": title,
            "limit": 5,
            "fields": "paperId,title,authors,year,abstract,citationCount,openAccessPdf,venue,publicationDate,externalIds"
        }
        
        if year:
            params["year"] = str(int(year))
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/paper/search",
                headers={"Authorization": f"Bearer {api_key}"},
                params=params,
                timeout=30
            )
            
            if response.status_code == 401:
                yield self.create_text_message("Error: Invalid API key")
                return
            elif response.status_code == 402:
                yield self.create_text_message("Error: Insufficient credits. Please recharge at ai4scholar.net")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"Error: API returned status {response.status_code}")
                return
            
            data = response.json()
            papers = data.get("data", [])
            
            if not papers:
                yield self.create_text_message(f"No papers found with title: {title}")
                return
            
            # Find best match by title similarity
            best_match = papers[0]
            
            result_lines = [f"Found paper matching title: \"{title}\"\n"]
            
            paper = best_match
            paper_id = paper.get("paperId", "N/A")
            paper_title = paper.get("title", "N/A")
            authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
            paper_year = paper.get("year", "N/A")
            citations = paper.get("citationCount", 0)
            venue = paper.get("venue", "")
            abstract = paper.get("abstract", "")
            
            external_ids = paper.get("externalIds", {})
            doi = external_ids.get("DOI", "")
            arxiv = external_ids.get("ArXiv", "")
            
            open_access = paper.get("openAccessPdf")
            pdf_url = open_access.get("url", "") if open_access else ""
            
            result_lines.append(f"## {paper_title}")
            result_lines.append(f"**Authors:** {authors}")
            result_lines.append(f"**Year:** {paper_year} | **Citations:** {citations}")
            if venue:
                result_lines.append(f"**Venue:** {venue}")
            if doi:
                result_lines.append(f"**DOI:** {doi}")
            if arxiv:
                result_lines.append(f"**arXiv:** {arxiv}")
            if abstract:
                result_lines.append(f"\n**Abstract:**\n{abstract}")
            if pdf_url:
                result_lines.append(f"\n**PDF:** {pdf_url}")
            result_lines.append(f"\n**Paper ID:** {paper_id}")
            
            # Show other matches if any
            if len(papers) > 1:
                result_lines.append("\n---\n**Other possible matches:**")
                for p in papers[1:]:
                    result_lines.append(f"- {p.get('title', 'N/A')} ({p.get('year', 'N/A')})")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

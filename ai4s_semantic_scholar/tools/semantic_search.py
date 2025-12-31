from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class SemanticSearchTool(Tool):
    """
    Semantic search tool for finding academic papers by relevance
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        query = tool_parameters.get("query", "")
        if not query:
            yield self.create_text_message("Error: Search query is required")
            return
        
        limit = min(max(int(tool_parameters.get("limit", 10)), 1), 100)
        year = tool_parameters.get("year", "")
        fields_of_study = tool_parameters.get("fields_of_study", "")
        open_access_only = tool_parameters.get("open_access_only", False)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        # Build request parameters
        params = {
            "query": query,
            "limit": limit,
            "fields": "paperId,title,authors,year,abstract,citationCount,openAccessPdf,venue,publicationDate,externalIds"
        }
        
        if year:
            params["year"] = year
        if fields_of_study:
            params["fieldsOfStudy"] = fields_of_study
        if open_access_only:
            params["openAccessPdf"] = ""
        
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
            total = data.get("total", 0)
            
            if not papers:
                yield self.create_text_message(f"No papers found for query: {query}")
                return
            
            # Format results
            result_lines = [f"Found {total} papers for query: \"{query}\" (showing {len(papers)})\n"]
            
            for i, paper in enumerate(papers, 1):
                paper_id = paper.get("paperId", "N/A")
                title = paper.get("title", "N/A")
                authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:3]])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                year = paper.get("year", "N/A")
                citations = paper.get("citationCount", 0)
                venue = paper.get("venue", "")
                abstract = paper.get("abstract", "")
                if abstract and len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                
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
                result_lines.append(f"**Paper ID:** {paper_id}")
                result_lines.append("")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

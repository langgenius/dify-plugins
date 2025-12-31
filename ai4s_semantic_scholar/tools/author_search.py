from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class AuthorSearchTool(Tool):
    """
    Search for authors and get their publication information
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        query = tool_parameters.get("query", "")
        if not query:
            yield self.create_text_message("Error: Author name is required")
            return
        
        limit = min(max(int(tool_parameters.get("limit", 5)), 1), 20)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/author/search",
                headers={"Authorization": f"Bearer {api_key}"},
                params={
                    "query": query,
                    "limit": limit,
                    "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex"
                },
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
            authors = data.get("data", [])
            total = data.get("total", 0)
            
            if not authors:
                yield self.create_text_message(f"No authors found for: {query}")
                return
            
            result_lines = [f"# Author Search Results\n**Query:** \"{query}\" | **Found:** {total} authors (showing {len(authors)})\n"]
            
            for i, author in enumerate(authors, 1):
                author_id = author.get("authorId", "N/A")
                name = author.get("name", "N/A")
                affiliations = author.get("affiliations", [])
                affiliation_str = ", ".join(affiliations) if affiliations else "N/A"
                paper_count = author.get("paperCount", 0)
                citation_count = author.get("citationCount", 0)
                h_index = author.get("hIndex", 0)
                
                result_lines.append(f"## {i}. {name}")
                result_lines.append(f"**Affiliations:** {affiliation_str}")
                result_lines.append(f"**Papers:** {paper_count} | **Citations:** {citation_count} | **h-index:** {h_index}")
                result_lines.append(f"**Author ID:** {author_id}")
                result_lines.append("")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

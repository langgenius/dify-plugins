from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class AuthorDetailTool(Tool):
    """
    Get detailed information about a specific author
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        author_id = tool_parameters.get("author_id", "")
        if not author_id:
            yield self.create_text_message("Error: Author ID is required")
            return
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/author/{author_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                params={
                    "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex,homepage,externalIds"
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
            
            author = response.json()
            
            # Format result
            name = author.get("name", "N/A")
            affiliations = author.get("affiliations", [])
            affiliation_str = ", ".join(affiliations) if affiliations else "N/A"
            paper_count = author.get("paperCount", 0)
            citation_count = author.get("citationCount", 0)
            h_index = author.get("hIndex", 0)
            homepage = author.get("homepage", "")
            
            external_ids = author.get("externalIds", {})
            orcid = external_ids.get("ORCID", "")
            dblp = external_ids.get("DBLP", "")
            
            result_lines = [f"# {name}"]
            result_lines.append(f"\n**Affiliations:** {affiliation_str}")
            result_lines.append(f"**Papers:** {paper_count} | **Citations:** {citation_count} | **h-index:** {h_index}")
            
            if homepage:
                result_lines.append(f"**Homepage:** {homepage}")
            if orcid:
                result_lines.append(f"**ORCID:** {orcid}")
            if dblp:
                result_lines.append(f"**DBLP:** {dblp}")
            
            result_lines.append(f"\n**Author ID:** {author.get('authorId', author_id)}")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

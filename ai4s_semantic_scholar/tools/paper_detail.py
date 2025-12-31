from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class PaperDetailTool(Tool):
    """
    Get detailed information about a specific paper
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        paper_id = tool_parameters.get("paper_id", "")
        if not paper_id:
            yield self.create_text_message("Error: Paper ID is required")
            return
        
        include_citations = tool_parameters.get("include_citations", False)
        include_references = tool_parameters.get("include_references", False)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        # Build fields parameter
        fields = [
            "paperId", "title", "authors", "year", "abstract",
            "citationCount", "referenceCount", "openAccessPdf",
            "venue", "publicationDate", "externalIds", "tldr",
            "fieldsOfStudy", "publicationTypes"
        ]
        
        if include_citations:
            fields.append("citations.paperId")
            fields.append("citations.title")
            fields.append("citations.year")
            fields.append("citations.citationCount")
        
        if include_references:
            fields.append("references.paperId")
            fields.append("references.title")
            fields.append("references.year")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/graph/v1/paper/{paper_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"fields": ",".join(fields)},
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
            
            paper = response.json()
            
            # Format result
            title = paper.get("title", "N/A")
            authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
            year = paper.get("year", "N/A")
            citations = paper.get("citationCount", 0)
            ref_count = paper.get("referenceCount", 0)
            venue = paper.get("venue", "")
            abstract = paper.get("abstract", "")
            
            external_ids = paper.get("externalIds", {})
            doi = external_ids.get("DOI", "")
            arxiv = external_ids.get("ArXiv", "")
            
            tldr = paper.get("tldr", {})
            tldr_text = tldr.get("text", "") if tldr else ""
            
            fields_of_study = paper.get("fieldsOfStudy", [])
            pub_types = paper.get("publicationTypes", [])
            
            open_access = paper.get("openAccessPdf")
            pdf_url = open_access.get("url", "") if open_access else ""
            
            result_lines = [f"# {title}"]
            result_lines.append(f"\n**Authors:** {authors}")
            result_lines.append(f"**Year:** {year} | **Citations:** {citations} | **References:** {ref_count}")
            
            if venue:
                result_lines.append(f"**Venue:** {venue}")
            if fields_of_study:
                result_lines.append(f"**Fields:** {', '.join(fields_of_study)}")
            if pub_types:
                result_lines.append(f"**Type:** {', '.join(pub_types)}")
            if doi:
                result_lines.append(f"**DOI:** {doi}")
            if arxiv:
                result_lines.append(f"**arXiv:** {arxiv}")
            
            if tldr_text:
                result_lines.append(f"\n**TL;DR:** {tldr_text}")
            
            if abstract:
                result_lines.append(f"\n**Abstract:**\n{abstract}")
            
            if pdf_url:
                result_lines.append(f"\n**Open Access PDF:** {pdf_url}")
            
            result_lines.append(f"\n**Paper ID:** {paper.get('paperId', paper_id)}")
            
            # Citations
            if include_citations:
                citations_list = paper.get("citations", [])
                if citations_list:
                    result_lines.append(f"\n---\n## Recent Citations ({len(citations_list)} shown)")
                    for c in citations_list[:10]:
                        c_title = c.get("title", "N/A")
                        c_year = c.get("year", "N/A")
                        c_cites = c.get("citationCount", 0)
                        result_lines.append(f"- {c_title} ({c_year}, {c_cites} citations)")
            
            # References
            if include_references:
                references_list = paper.get("references", [])
                if references_list:
                    result_lines.append(f"\n---\n## References ({len(references_list)} shown)")
                    for r in references_list[:10]:
                        r_title = r.get("title", "N/A")
                        r_year = r.get("year", "N/A")
                        result_lines.append(f"- {r_title} ({r_year})")
            
            yield self.create_text_message("\n".join(result_lines))
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error: Network error - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

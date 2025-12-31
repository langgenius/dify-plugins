from typing import Any, Generator
import requests
import re
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class MultiplePapersDetailTool(Tool):
    """
    Get details for multiple papers at once
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        paper_ids_raw = tool_parameters.get("paper_ids", "")
        if not paper_ids_raw:
            yield self.create_text_message("Error: Paper IDs are required")
            return
        
        # Parse paper IDs (split by commas or newlines)
        paper_ids = [p.strip() for p in re.split(r'[,\n]', paper_ids_raw) if p.strip()]
        
        if not paper_ids:
            yield self.create_text_message("Error: No valid paper IDs found")
            return
        
        if len(paper_ids) > 20:
            paper_ids = paper_ids[:20]
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        result_lines = [f"# Multiple Papers Detail\n**Requesting:** {len(paper_ids)} papers\n"]
        
        for i, paper_id in enumerate(paper_ids, 1):
            try:
                response = requests.get(
                    f"{self.BASE_URL}/graph/v1/paper/{paper_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={
                        "fields": "paperId,title,authors,year,abstract,citationCount,openAccessPdf,venue,externalIds,tldr"
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
                    result_lines.append(f"\n## Paper {i}: Not Found")
                    result_lines.append(f"ID: {paper_id}")
                    continue
                elif response.status_code != 200:
                    result_lines.append(f"\n## Paper {i}: Error")
                    result_lines.append(f"API returned status {response.status_code}")
                    continue
                
                paper = response.json()
                
                title = paper.get("title", "N/A")
                authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:5]])
                if len(paper.get("authors", [])) > 5:
                    authors += " et al."
                year = paper.get("year", "N/A")
                citations = paper.get("citationCount", 0)
                venue = paper.get("venue", "")
                
                external_ids = paper.get("externalIds", {})
                doi = external_ids.get("DOI", "")
                
                tldr = paper.get("tldr", {})
                tldr_text = tldr.get("text", "") if tldr else ""
                
                abstract = paper.get("abstract", "")
                if abstract and len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                
                open_access = paper.get("openAccessPdf")
                pdf_url = open_access.get("url", "") if open_access else ""
                
                result_lines.append(f"\n---\n## {i}. {title}")
                result_lines.append(f"**Authors:** {authors}")
                result_lines.append(f"**Year:** {year} | **Citations:** {citations}")
                if venue:
                    result_lines.append(f"**Venue:** {venue}")
                if doi:
                    result_lines.append(f"**DOI:** {doi}")
                if tldr_text:
                    result_lines.append(f"**TL;DR:** {tldr_text}")
                elif abstract:
                    result_lines.append(f"**Abstract:** {abstract}")
                if pdf_url:
                    result_lines.append(f"**PDF:** {pdf_url}")
                result_lines.append(f"**Paper ID:** {paper.get('paperId', paper_id)}")
                
            except requests.exceptions.Timeout:
                result_lines.append(f"\n## Paper {i}: Timeout")
                result_lines.append(f"ID: {paper_id}")
            except Exception as e:
                result_lines.append(f"\n## Paper {i}: Error")
                result_lines.append(f"Error: {str(e)}")
        
        yield self.create_text_message("\n".join(result_lines))

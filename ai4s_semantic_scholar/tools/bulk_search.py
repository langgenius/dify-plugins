from typing import Any, Generator
import requests
import re
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class BulkSearchTool(Tool):
    """
    Execute multiple search queries at once
    """
    
    BASE_URL = "https://ai4scholar.net"
    
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        queries_raw = tool_parameters.get("queries", "")
        if not queries_raw:
            yield self.create_text_message("Error: Search queries are required")
            return
        
        # Parse queries (split by newlines or semicolons)
        queries = [q.strip() for q in re.split(r'[\n;]', queries_raw) if q.strip()]
        
        if not queries:
            yield self.create_text_message("Error: No valid queries found")
            return
        
        if len(queries) > 10:
            queries = queries[:10]
            yield self.create_text_message("Note: Limited to first 10 queries\n")
        
        limit_per_query = min(max(int(tool_parameters.get("limit_per_query", 5)), 1), 20)
        
        api_key = self.runtime.credentials.get("api_key", "")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return
        
        result_lines = [f"# Bulk Search Results\n**Queries:** {len(queries)} | **Results per query:** {limit_per_query}\n"]
        
        for i, query in enumerate(queries, 1):
            try:
                response = requests.get(
                    f"{self.BASE_URL}/graph/v1/paper/search",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={
                        "query": query,
                        "limit": limit_per_query,
                        "fields": "paperId,title,authors,year,citationCount,openAccessPdf"
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
                    result_lines.append(f"\n## Query {i}: \"{query}\"")
                    result_lines.append(f"Error: API returned status {response.status_code}")
                    continue
                
                data = response.json()
                papers = data.get("data", [])
                total = data.get("total", 0)
                
                result_lines.append(f"\n## Query {i}: \"{query}\"")
                result_lines.append(f"Found {total} papers (showing {len(papers)})\n")
                
                if not papers:
                    result_lines.append("No papers found.")
                    continue
                
                for j, paper in enumerate(papers, 1):
                    title = paper.get("title", "N/A")
                    authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:2]])
                    if len(paper.get("authors", [])) > 2:
                        authors += " et al."
                    year = paper.get("year", "N/A")
                    citations = paper.get("citationCount", 0)
                    paper_id = paper.get("paperId", "")
                    
                    open_access = paper.get("openAccessPdf")
                    has_pdf = "📄" if open_access else ""
                    
                    result_lines.append(f"{j}. {has_pdf} **{title}**")
                    result_lines.append(f"   {authors} ({year}) | Citations: {citations}")
                    result_lines.append(f"   ID: {paper_id}")
                    result_lines.append("")
                    
            except requests.exceptions.Timeout:
                result_lines.append(f"\n## Query {i}: \"{query}\"")
                result_lines.append("Error: Request timeout")
            except Exception as e:
                result_lines.append(f"\n## Query {i}: \"{query}\"")
                result_lines.append(f"Error: {str(e)}")
        
        yield self.create_text_message("\n".join(result_lines))

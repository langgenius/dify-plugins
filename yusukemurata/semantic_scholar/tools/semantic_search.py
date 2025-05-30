import requests
import re
from collections.abc import Generator
from typing import Any
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SemanticSearch(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = tool_parameters.get("query", "")
        max_results = min(tool_parameters.get("max_results", 10), 50)  # Cap at 50
        venue = tool_parameters.get("venue", "")
        start_year = tool_parameters.get("start_year")
        end_year = tool_parameters.get("end_year")
        
        if not query:
            yield self.create_text_message("Error: Search query is required")
            return
        
        try:
            # Get API key from credentials (optional)
            api_key = self.runtime.credentials.get("api_key")
            
            # Set up headers
            headers = {
                "User-Agent": "Semantic-Scholar-Plugin/1.0",
                "Accept": "application/json"
            }
            
            if api_key:
                headers["x-api-key"] = api_key
            
            # Search for papers
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            search_params = {
                "query": query,
                "limit": max_results,
                "fields": "title,abstract,authors,year,venue,url,citationCount,openAccessPdf,publicationDate,externalIds,fieldsOfStudy,publicationTypes,tldr"
            }
            
            # Add venue filter if provided
            if venue:
                search_params["venue"] = venue
            
            # Add year range if provided
            if start_year or end_year:
                year_range = ""
                if start_year:
                    year_range += str(start_year)
                year_range += "-"
                if end_year:
                    year_range += str(end_year)
                search_params["year"] = year_range
            
            # Create search description
            search_desc = f"🔍 Searching for papers with query: '{query}'"
            if venue:
                search_desc += f", venue: '{venue}'"
            if start_year or end_year:
                search_desc += f", year range: {search_params.get('year', '')}"
            
            yield self.create_text_message(search_desc)
            
            response = requests.get(search_url, headers=headers, params=search_params, timeout=30)
            
            if response.status_code != 200:
                yield self.create_text_message(f"Error: API request failed with status {response.status_code}")
                return
            
            data = response.json()
            papers = data.get("data", [])
            
            if not papers:
                yield self.create_text_message("No papers found for your query.")
                return
            
            # Process and format results
            results = []
            formatted_output = []
            
            for i, paper in enumerate(papers, 1):
                paper_info = self._format_paper_info(paper)
                results.append(paper_info)
                
                # Create formatted text output
                formatted_paper = f"## {i}. {paper_info.get('title', 'Unknown Title')}\n\n"
                formatted_paper += f"**Title:** {paper_info.get('title', 'Unknown Title')}\n"
                formatted_paper += f"**Author:** {paper_info.get('authors', 'Unknown Authors')}\n"
                
                if paper_info.get('tldr'):
                    formatted_paper += f"**TLDR:** {paper_info['tldr']}\n"
                
                if paper_info.get('abstract'):
                    formatted_paper += f"**Abstract:** {paper_info['abstract']}\n"
                
                formatted_paper += f"**Venue:** {paper_info.get('venue', 'N/A')}\n"
                formatted_paper += f"**Citation:** {paper_info.get('citationCount', 0)} citations\n"
                
                # Add link - try openAccessPdf first, then url
                link_url = paper_info.get('openAccessPdf_url', paper_info.get('url', ''))
                if link_url:
                    formatted_paper += f"**Link:** {link_url}\n"
                else:
                    formatted_paper += f"**Link:** Not Found\n"
                
                formatted_paper += f"**出版年月日:** {paper_info.get('publicationDate', 'N/A')}\n"
                formatted_paper += "\n---\n\n"
                
                formatted_output.append(formatted_paper)
            
            # Create summary and detailed output
            summary = f"📚 Found {len(results)} papers matching your criteria:\n\n"
            summary += "".join(formatted_output)
            
            yield self.create_text_message(summary)
            
            # Yield detailed results
            yield self.create_json_message({
                "query": query,
                "total_results": len(results),
                "papers": results
            })
            
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
    
    def _format_paper_info(self, paper: dict) -> dict:
        """Format paper information for output"""
        # Extract basic info
        paper_info = {
            "paperId": paper.get("paperId", ""),
            "title": paper.get("title", "").strip(),
            "year": paper.get("year"),
            "citationCount": paper.get("citationCount", 0),
            "url": paper.get("url", ""),
            "venue": paper.get("venue", ""),
            "publicationDate": paper.get("publicationDate", ""),
            "externalIds": paper.get("externalIds", {}),
            "fieldsOfStudy": paper.get("fieldsOfStudy", []),
            "publicationTypes": paper.get("publicationTypes", [])
        }
        
        # Format authors
        authors = paper.get("authors", [])
        if authors:
            author_names = [author.get("name", "") for author in authors[:3]]  # Limit to first 3
            if len(authors) > 3:
                author_names.append(f"et al. ({len(authors)} total)")
            paper_info["authors"] = ", ".join(author_names)
        else:
            paper_info["authors"] = "Unknown Authors"
        
        # Add abstract (no truncation)
        abstract = paper.get("abstract", "")
        if abstract:
            paper_info["abstract"] = abstract
        
        # Add TL;DR if available
        tldr = paper.get("tldr")
        if tldr and isinstance(tldr, dict):
            paper_info["tldr"] = tldr.get("text", "")
        
        # Add open access PDF info
        open_access_pdf = paper.get("openAccessPdf")
        if open_access_pdf and isinstance(open_access_pdf, dict):
            paper_info["openAccessPdf_url"] = open_access_pdf.get("url", "")
            paper_info["openAccessPdf_status"] = open_access_pdf.get("status", "")
        
        return paper_info

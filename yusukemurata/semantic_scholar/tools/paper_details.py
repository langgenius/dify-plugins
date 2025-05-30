import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PaperDetails(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        paper_id = tool_parameters.get("paper_id", "")
        include_citations = tool_parameters.get("include_citations", True)
        include_abstract = tool_parameters.get("include_abstract", True)
        
        if not paper_id:
            yield self.create_text_message("Error: Paper ID is required")
            return
        
        try:
            # Get API key from credentials (optional)
            api_key = self.runtime.credentials.get("api_key")
            
            # Set up headers
            headers = {
                "User-Agent": "Dify-Dify-Plugin/1.0",
                "Accept": "application/json"
            }
            
            if api_key:
                headers["x-api-key"] = api_key
            
            # Difyne fields to retrieve
            fields = ["title", "authors", "year", "venue", "publicationDate", "url", "paperId"]
            
            if include_abstract:
                fields.append("abstract")
            
            if include_citations:
                fields.extend(["citationCount", "referenceCount", "citations", "references"])
            
            # Additional useful fields
            fields.extend(["tldr", "fieldsOfStudy", "publicationTypes", "journal"])
            
            # Get paper details
            paper_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
            params = {
                "fields": ",".join(fields)
            }
            
            yield self.create_text_message(f"📄 Retrieving details for paper ID: {paper_id}...")
            
            response = requests.get(paper_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 404:
                yield self.create_text_message(f"Error: Paper with ID '{paper_id}' not found")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"Error: API request failed with status {response.status_code}")
                return
            
            paper = response.json()
            
            # Format paper details
            details = self._format_paper_details(paper, include_citations, include_abstract)
            
            # Create summary message
            title = details.get("title", "Unknown Title")
            authors = details.get("authors", "Unknown Authors")
            year = details.get("year", "Unknown")
            
            summary = f"📚 **Paper Details**\n\n"
            summary += f"**Title:** {title}\n"
            summary += f"**Authors:** {authors}\n"
            summary += f"**Year:** {year}\n"
            
            if details.get("venue"):
                summary += f"**Venue:** {details['venue']}\n"
            
            if include_citations and details.get("citationCount") is not None:
                summary += f"**Citations:** {details['citationCount']}\n"
            
            if details.get("tldr"):
                summary += f"\n**TL;DR:** {details['tldr']}\n"
            
            yield self.create_text_message(summary)
            
            # Yield detailed JSON results
            yield self.create_json_message({
                "paper_id": paper_id,
                "paper_details": details
            })
            
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
    
    def _format_paper_details(self, paper: dict, include_citations: bool, include_abstract: bool) -> dict:
        """Format comprehensive paper details"""
        details = {
            "paperId": paper.get("paperId", ""),
            "title": paper.get("title", "").strip(),
            "year": paper.get("year"),
            "url": paper.get("url", ""),
            "venue": paper.get("venue", ""),
            "publicationDate": paper.get("publicationDate", "")
        }
        
        # Format authors
        authors = paper.get("authors", [])
        if authors:
            author_list = []
            for author in authors:
                name = author.get("name", "")
                author_id = author.get("authorId", "")
                if name:
                    author_list.append(name)
            details["authors"] = ", ".join(author_list) if author_list else "Unknown Authors"
            details["author_count"] = len(authors)
        else:
            details["authors"] = "Unknown Authors"
            details["author_count"] = 0
        
        # Add abstract if requested
        if include_abstract:
            abstract = paper.get("abstract", "")
            if abstract:
                details["abstract"] = abstract
                details["abstract_length"] = len(abstract)
        
        # Add citation information if requested
        if include_citations:
            details["citationCount"] = paper.get("citationCount", 0)
            details["referenceCount"] = paper.get("referenceCount", 0)
            
            # Format recent citations (limit to 5)
            citations = paper.get("citations", [])
            if citations:
                recent_citations = []
                for citation in citations[:5]:
                    citing_paper = {
                        "paperId": citation.get("paperId", ""),
                        "title": citation.get("title", "").strip(),
                        "year": citation.get("year"),
                        "authors": self._format_citation_authors(citation.get("authors", []))
                    }
                    recent_citations.append(citing_paper)
                details["recent_citations"] = recent_citations
            
            # Format key references (limit to 5)
            references = paper.get("references", [])
            if references:
                key_references = []
                for ref in references[:5]:
                    reference = {
                        "paperId": ref.get("paperId", ""),
                        "title": ref.get("title", "").strip(),
                        "year": ref.get("year"),
                        "authors": self._format_citation_authors(ref.get("authors", []))
                    }
                    key_references.append(reference)
                details["key_references"] = key_references
        
        # Add TL;DR if available
        tldr = paper.get("tldr")
        if tldr and isinstance(tldr, dict):
            details["tldr"] = tldr.get("text", "")
        
        # Add fields of study
        fields_of_study = paper.get("fieldsOfStudy", [])
        if fields_of_study:
            details["fields_of_study"] = fields_of_study
        
        # Add publication types
        pub_types = paper.get("publicationTypes", [])
        if pub_types:
            details["publication_types"] = pub_types
        
        # Add journal information
        journal = paper.get("journal")
        if journal:
            details["journal"] = {
                "name": journal.get("name", ""),
                "volume": journal.get("volume", ""),
                "pages": journal.get("pages", "")
            }
        
        return details
    
    def _format_citation_authors(self, authors: list) -> str:
        """Format authors for citations/references"""
        if not authors:
            return "Unknown Authors"
        
        author_names = [author.get("name", "") for author in authors[:2]]  # Limit to first 2
        if len(authors) > 2:
            author_names.append(f"et al.")
        
        return ", ".join(filter(None, author_names))

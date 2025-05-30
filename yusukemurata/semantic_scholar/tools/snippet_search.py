import json
import re
from collections.abc import Generator
from typing import Any, Dict, List, Optional
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests


class SnippetSearch(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Search for specific text snippets within Dify-related academic papers using Semantic Scholar API
        """
        query = tool_parameters.get('query', '')
        limit = min(int(tool_parameters.get('limit', 20)), 100)  # Cap at 100
        snippet_types = tool_parameters.get('snippet_types', 'all')
        min_score = float(tool_parameters.get('min_score', 0.3))
        
        if not query:
            yield self.create_text_message("Error: Search query is required")
            return
        
        try:
            # Use original query without any modification
            
            # Get API credentials
            credentials = self.runtime.credentials or {}
            api_key = credentials.get('api_key')
            
            # Perform snippet search
            snippets_data = self._search_snippets(query, limit, api_key)
            
            if not snippets_data:
                yield self.create_text_message(f"No snippets found for query: {query}")
                return
            
            # Filter and process snippets
            filtered_snippets = self._filter_snippets(
                snippets_data, 
                snippet_types, 
                min_score
            )
            
            # Format results
            formatted_results = self._format_snippet_results(filtered_snippets, query)
            
            yield self.create_text_message(formatted_results)
            
        except Exception as e:
            yield self.create_text_message(f"Error during snippet search: {str(e)}")
    
    def _search_snippets(self, query: str, limit: int, api_key: Optional[str] = None) -> List[Dict]:
        """
        Search for snippets using Semantic Scholar API
        """
        base_url = "https://api.semanticscholar.org/graph/v1/snippet/search"
        
        params = {
            'query': query,
            'limit': limit
        }
        
        headers = {
            'User-Agent': 'Dify-Semantic-Scholar-Plugin/1.0'
        }
        
        if api_key:
            headers['x-api-key'] = api_key
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response: {str(e)}")
    
    def _filter_snippets(self, snippets: List[Dict], snippet_types: str, min_score: float) -> List[Dict]:
        """
        Filter snippets based on type and minimum score
        """
        filtered = []
        
        for item in snippets:
            snippet_info = item.get('snippet', {})
            score = item.get('score', 0.0)
            snippet_kind = snippet_info.get('snippetKind', '')
            
            # Apply score filter
            if score < min_score:
                continue
            
            # Apply type filter
            if snippet_types != 'all':
                if snippet_kind != snippet_types:
                    continue
            
            filtered.append(item)
        
        return filtered
    
    def _format_snippet_results(self, snippets: List[Dict], original_query: str) -> str:
        """
        Format snippet search results for display
        """
        if not snippets:
            return f"No snippets found matching the criteria for query: {original_query}"
        
        result_lines = [
            f"🔍 **Semantic Scholar Snippet Search Results for: '{original_query}'**",
            f"Found {len(snippets)} relevant text snippets:\n"
        ]
        
        for i, item in enumerate(snippets, 1):
            snippet_info = item.get('snippet', {})
            paper_info = item.get('paper', {})
            score = item.get('score', 0.0)
            
            # Extract snippet details
            text = snippet_info.get('text', 'N/A')
            snippet_kind = snippet_info.get('snippetKind', 'unknown')
            section = snippet_info.get('section', 'N/A')
            
            # Extract paper details
            paper_title = paper_info.get('title', 'Unknown Title')
            authors = paper_info.get('authors', [])
            corpus_id = paper_info.get('corpusId', 'N/A')
            
            # Extract URL from openAccessInfo or construct Semantic Scholar URL
            open_access_info = paper_info.get('openAccessInfo', {})
            disclaimer = open_access_info.get('disclaimer', '')
            paper_url = 'N/A'
            
            # Try to extract URL from disclaimer
            if disclaimer and 'https://' in disclaimer:
                import re
                url_match = re.search(r'https://[^\s,]+', disclaimer)
                if url_match:
                    paper_url = url_match.group(0)
            
            # If no URL found, construct Semantic Scholar URL using corpus ID
            if paper_url == 'N/A' and corpus_id != 'N/A':
                paper_url = f"https://www.semanticscholar.org/paper/{corpus_id}"
            
            # Format authors
            author_names = []
            if isinstance(authors, list):
                for author in authors[:3]:  # Limit to first 3 authors
                    if isinstance(author, str):
                        author_names.append(author)
                    elif isinstance(author, dict):
                        author_names.append(author.get('name', 'Unknown'))
            
            authors_str = ', '.join(author_names)
            if len(authors) > 3:
                authors_str += ' et al.'
            
            # Clean snippet text (no truncation)
            clean_text = self._clean_snippet_text(text)
            
            # Format the snippet entry
            result_lines.extend([
                f"## {i}. {snippet_kind.title()} Snippet (Score: {score:.3f})",
                f"**Title:** {paper_title}",
                f"**Authors:** {authors_str}" if authors_str else "**Authors:** Not specified",
                f"**Section:** {section}" if section != 'N/A' else "",
                f"**Corpus ID:** {corpus_id}",
                f"**URL:** {paper_url}" if paper_url != 'N/A' else "",
                "",
                f"**Snippet:**",
                f"_{clean_text}_",
                "",
                "---",
                ""
            ])
        
        # Add summary
        snippet_types_found = set()
        avg_score = sum(item.get('score', 0.0) for item in snippets) / len(snippets)
        
        for item in snippets:
            snippet_kind = item.get('snippet', {}).get('snippetKind', 'unknown')
            snippet_types_found.add(snippet_kind)
        
        result_lines.extend([
            "## 📊 Search Summary",
            f"- **Total snippets found:** {len(snippets)}",
            f"- **Average relevance score:** {avg_score:.3f}",
            f"- **Snippet types:** {', '.join(sorted(snippet_types_found))}",
            f"- **Search query:** {original_query}"
        ])
        
        return '\n'.join(result_lines)
    
    def _clean_snippet_text(self, text: str) -> str:
        """
        Clean and format snippet text for better readability
        """
        if not text:
            return "No text available"
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove or replace problematic characters
        text = text.replace('\r', ' ').replace('\n', ' ')
        
        # Remove citations in brackets [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{3,}', '...', text)
        
        return text

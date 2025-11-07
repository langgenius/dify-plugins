# File: tools/deep_research.py
# This file contains the core Python logic for the main "Deep Research" tool.
# It makes calls to the Tavily API based on the provided parameters.
from collections.abc import Generator
from typing import Any, Mapping

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tavily import TavilyClient


class DeepResearchTool(Tool):
    """
    A Dify Tool Plugin to perform web searches using the Tavily API,
    serving as the core search capability for the "Deep Research" plugin.
    It can return search snippets and optionally the full content of web pages.
    """


    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Parses the raw response from the Tavily API and organizes it into a cleaner format.

        Args:
            response (Dict[str, Any]): The raw dictionary response from the Tavily API.

        Returns:
            Dict[str, Any]: A dictionary containing a list of organized search results.
                            Each result includes title, URL, and snippet.
        """
        organized_results = []
        # Iterate through each search result in the 'results' list from Tavily's response
        for result in response.get("results", []):
            item = {
                "title": result.get("title", "Your search results"), # Provide default if title is missing
                "url": result.get("url", "No URL Available"),       # Provide default if URL is missing
                "snippet": result.get("content") # Tavily uses 'content' for snippets
            }
            organized_results.append(item)

        # The final returned response structure will be here
        return {"search_results": organized_results}




    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        


        """
        Invokes the Tavily API to perform a web search for deep research purposes.

        Args:
            tool_parameters (Mapping[str, Any]): A dictionary containing the tool's input parameters.
                Expected keys:
                - "query" (str): The search query. (required)

        Yields:
            ToolInvokeMessage: A JSON message containing the search results.
        """
    
        tavily_api_key = self.runtime.credentials.get("tavily_api_key")

        # Initialize Tavily client with the API key
        client = TavilyClient(api_key=tavily_api_key)

        # Extract parameters from tool_parameters with default values
        query = tool_parameters.get("query")

        max_results = tool_parameters.get("max_results", 5) 


        
        # Perform the search using Tavily API
        response = client.search(query=query)

        # Process the search results
        results = []
        for result in response.get("results", []):
            item = {
                "title": result.get("title"),
                "url": result.get("url"),
                "snippet": result.get("content")
            }
            results.append(item)

        # Yield the results as a JSON message.
        yield self.create_json_message({"search_results": results})


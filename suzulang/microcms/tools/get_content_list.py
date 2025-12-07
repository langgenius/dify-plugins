from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetContentListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get credentials
        service_domain = self.runtime.credentials.get("service_domain", "").strip()
        api_key = self.runtime.credentials.get("api_key", "").strip()

        if not service_domain:
            yield self.create_text_message("Service domain is required")
            return
        if not api_key:
            yield self.create_text_message("API key is required")
            return

    
        # Get required parameters
        endpoint = tool_parameters.get("endpoint", "").strip()
        if not endpoint:
            yield self.create_text_message("Endpoint is required")
            return

        try:
            # Build query parameters
            params = {}

            # Handle limit
            limit = tool_parameters.get("limit", 10)
            if limit is not None:
                limit = int(limit)
                if limit < 1:
                    limit = 1
                elif limit > 100:
                    limit = 100
                params["limit"] = limit

            # Handle offset
            offset = tool_parameters.get("offset", 0)
            if offset is not None:
                offset = int(offset)
                if offset < 0:
                    offset = 0
                params["offset"] = offset

            # Handle orders
            orders = tool_parameters.get("orders", "").strip()
            if orders:
                params["orders"] = orders

            # Handle search query
            q = tool_parameters.get("q", "").strip()
            if q:
                params["q"] = q

            # Handle filters
            filters = tool_parameters.get("filters", "").strip()
            if filters:
                params["filters"] = filters

            # Handle fields
            fields = tool_parameters.get("fields", "").strip()
            if fields:
                params["fields"] = fields

            # Handle IDs
            ids = tool_parameters.get("ids", "").strip()
            if ids:
                params["ids"] = ids

            # Handle depth
            depth = tool_parameters.get("depth", 1)
            if depth is not None:
                depth = int(depth)
                if depth < 0:
                    depth = 0
                elif depth > 3:
                    depth = 3
                params["depth"] = depth

            # Handle draft key
            draft_key = tool_parameters.get("draftKey", "").strip()
            if draft_key:
                params["draftKey"] = draft_key

            # Handle rich editor format
            rich_editor_format = tool_parameters.get("richEditorFormat", "object")
            if rich_editor_format:
                params["richEditorFormat"] = rich_editor_format

            # Make API request
            url = f"https://{service_domain}.microcms.io/api/v1/{endpoint}"
            headers = {"X-MICROCMS-API-KEY": api_key}

            response = requests.get(url, headers=headers, params=params, timeout=30)

            # Handle response
            if response.status_code == 401:
                yield self.create_text_message("Invalid API key")
                return
            elif response.status_code == 404:
                yield self.create_text_message("Endpoint not found or service domain is invalid")
                return
            elif response.status_code == 429:
                yield self.create_text_message("Too many requests. Please try again later")
                return
            elif response.status_code >= 500:
                yield self.create_text_message(f"Server error: {response.status_code}")
                return
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", f"HTTP {response.status_code}")
                    yield self.create_text_message(f"API error: {error_msg}")
                except:
                    yield self.create_text_message(f"HTTP error: {response.status_code}")
                return

            # Parse and return successful response
            try:
                data = response.json()

                # Success message
                total_count = data.get("totalCount", 0)
                current_limit = data.get("limit", 0)
                current_offset = data.get("offset", 0)
                content_count = len(data.get("contents", []))

                yield self.create_text_message(
                    f"Successfully retrieved {content_count} items from endpoint '{endpoint}' "
                    f"(total: {total_count} items, limit: {current_limit}, offset: {current_offset})"
                )

                # Return the data
                yield self.create_json_message(data)

            except Exception as e:
                yield self.create_text_message(f"Failed to parse response: {str(e)}")

        except requests.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
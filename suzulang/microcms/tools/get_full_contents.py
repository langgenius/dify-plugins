from collections.abc import Generator
from typing import Any
import requests
import concurrent.futures
import threading

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetFullContentsTool(Tool):
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
            # Step 1: Get content list (only IDs)
            yield self.create_text_message("Step 1: Retrieving content list...")

            # Build list parameters
            list_params = {}

            # Handle pagination and filtering for list request
            limit = tool_parameters.get("limit", 10)
            if limit is not None:
                limit = int(limit)
                if limit < 1:
                    limit = 1
                elif limit > 100:
                    limit = 100
                list_params["limit"] = limit

            offset = tool_parameters.get("offset", 0)
            if offset is not None:
                offset = int(offset)
                if offset < 0:
                    offset = 0
                list_params["offset"] = offset

            orders = tool_parameters.get("orders", "").strip()
            if orders:
                list_params["orders"] = orders

            q = tool_parameters.get("q", "").strip()
            if q:
                list_params["q"] = q

            filters = tool_parameters.get("filters", "").strip()
            if filters:
                list_params["filters"] = filters

            # Only request IDs in list request to minimize data transfer
            list_params["fields"] = "id"

            # Make list request
            list_url = f"https://{service_domain}.microcms.io/api/v1/{endpoint}"
            headers = {"X-MICROCMS-API-KEY": api_key}

            list_response = requests.get(list_url, headers=headers, params=list_params, timeout=30)

            if list_response.status_code == 401:
                yield self.create_text_message("Invalid API key")
                return
            elif list_response.status_code == 404:
                yield self.create_text_message("Endpoint not found or service domain is invalid")
                return
            elif list_response.status_code == 429:
                yield self.create_text_message("Too many requests. Please try again later")
                return
            elif list_response.status_code >= 400:
                try:
                    error_data = list_response.json()
                    error_msg = error_data.get("message", f"HTTP {list_response.status_code}")
                    yield self.create_text_message(f"API error: {error_msg}")
                except:
                    yield self.create_text_message(f"HTTP error: {list_response.status_code}")
                return

            # Parse list response
            list_data = list_response.json()
            content_ids = [item["id"] for item in list_data.get("contents", [])]
            total_count = list_data.get("totalCount", 0)
            current_limit = list_data.get("limit", 0)
            current_offset = list_data.get("offset", 0)

            if not content_ids:
                yield self.create_text_message("No content found matching the criteria")
                yield self.create_json_message({
                    "totalCount": total_count,
                    "limit": current_limit,
                    "offset": current_offset,
                    "contents": []
                })
                return

            yield self.create_text_message(f"Found {len(content_ids)} content items. Step 2: Fetching full details...")

            # Step 2: Prepare detail parameters
            detail_params = {}

            fields = tool_parameters.get("fields", "").strip()
            if fields:
                detail_params["fields"] = fields

            depth = tool_parameters.get("depth", 1)
            if depth is not None:
                depth = int(depth)
                if depth < 0:
                    depth = 0
                elif depth > 3:
                    depth = 3
                detail_params["depth"] = depth

            draft_key = tool_parameters.get("draftKey", "").strip()
            if draft_key:
                detail_params["draftKey"] = draft_key

            rich_editor_format = tool_parameters.get("richEditorFormat", "object")
            if rich_editor_format:
                detail_params["richEditorFormat"] = rich_editor_format

            # Step 3: Concurrent detail requests
            max_concurrent = tool_parameters.get("max_concurrent", 5)
            if max_concurrent is not None:
                max_concurrent = int(max_concurrent)
                if max_concurrent < 1:
                    max_concurrent = 1
                elif max_concurrent > 10:
                    max_concurrent = 10

            # Thread-safe containers
            results = []
            errors = []
            lock = threading.Lock()

            def fetch_content_detail(content_id: str):
                try:
                    detail_url = f"https://{service_domain}.microcms.io/api/v1/{endpoint}/{content_id}"
                    detail_response = requests.get(detail_url, headers=headers, params=detail_params, timeout=30)

                    if detail_response.status_code == 200:
                        content_data = detail_response.json()
                        with lock:
                            results.append(content_data)
                    else:
                        with lock:
                            errors.append({
                                "content_id": content_id,
                                "error": f"HTTP {detail_response.status_code}"
                            })

                except Exception as e:
                    with lock:
                        errors.append({
                            "content_id": content_id,
                            "error": str(e)
                        })

            # Use ThreadPoolExecutor for concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit all tasks
                future_to_id = {executor.submit(fetch_content_detail, cid): cid for cid in content_ids}

                # Wait for all to complete with progress
                completed = 0
                for future in concurrent.futures.as_completed(future_to_id):
                    completed += 1
                    if completed % 5 == 0 or completed == len(content_ids):
                        yield self.create_text_message(f"Progress: {completed}/{len(content_ids)} items fetched...")

            # Step 4: Combine and return results
            yield self.create_text_message(
                f"Completed! Retrieved {len(results)} full content details from endpoint '{endpoint}' "
                f"(total available: {total_count})"
            )

            # Prepare final response
            final_response = {
                "totalCount": total_count,
                "limit": current_limit,
                "offset": current_offset,
                "contents": results
            }

            # Add errors if any
            if errors:
                final_response["errors"] = errors
                yield self.create_text_message(f"Warning: {len(errors)} items failed to retrieve")

            yield self.create_json_message(final_response)

        except requests.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
import time
from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://api.anakin.io/v1"
MAX_POLL_ATTEMPTS = 90
POLL_INTERVAL = 5


class BatchScraperTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")

        urls_str = tool_parameters.get("urls")
        if not urls_str:
            yield self.create_text_message("Error: URLs are required")
            return

        # Parse comma-separated URLs
        urls = [url.strip() for url in urls_str.split(",") if url.strip()]

        if not urls:
            yield self.create_text_message("Error: No valid URLs provided")
            return

        if len(urls) > 10:
            yield self.create_text_message("Error: Maximum 10 URLs allowed per batch")
            return

        country = tool_parameters.get("country", "us")
        use_browser = tool_parameters.get("use_browser", False)
        generate_json = tool_parameters.get("generate_json", False)

        payload = {
            "urls": urls,
            "country": country,
            "useBrowser": use_browser,
            "generateJson": generate_json
        }

        try:
            with httpx.Client(timeout=30) as client:
                # Submit batch job
                response = client.post(
                    f"{BASE_URL}/url-scraper/batch",
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code == 401:
                    yield self.create_text_message("Error: Invalid API Key")
                    return
                elif response.status_code == 402:
                    yield self.create_text_message("Error: Plan upgrade required")
                    return
                elif response.status_code not in [200, 202]:
                    yield self.create_text_message(f"Error: {response.text}")
                    return

                job_data = response.json()
                job_id = job_data.get("jobId")

                if not job_id:
                    yield self.create_json_message(job_data)
                    return

                # Poll for results
                for _ in range(MAX_POLL_ATTEMPTS):
                    time.sleep(POLL_INTERVAL)

                    result_response = client.get(
                        f"{BASE_URL}/url-scraper/{job_id}",
                        headers={"X-API-Key": api_key}
                    )

                    if result_response.status_code != 200:
                        continue

                    result = result_response.json()
                    status = result.get("status")

                    if status == "completed":
                        yield self.create_json_message(result)
                        return
                    elif status == "failed":
                        error = result.get("error", "Unknown error")
                        yield self.create_text_message(f"Batch scraping failed: {error}")
                        return

                yield self.create_text_message("Error: Batch job timed out. Please try again.")

        except httpx.TimeoutException:
            yield self.create_text_message("Error: Request timeout")
        except httpx.RequestError as e:
            yield self.create_text_message(f"Error: {str(e)}")

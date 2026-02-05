import json
import time
from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://api.anakin.io/v1"
MAX_POLL_ATTEMPTS = 60
POLL_INTERVAL = 3


class WebScraperTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")

        url = tool_parameters.get("url")
        if not url:
            yield self.create_text_message("Error: URL is required")
            return

        scraper_code = tool_parameters.get("scraper_code")
        if not scraper_code:
            yield self.create_text_message("Error: Scraper code is required")
            return

        # Parse optional scraper params
        scraper_params_str = tool_parameters.get("scraper_params", "{}")
        try:
            scraper_params = json.loads(scraper_params_str) if scraper_params_str else {}
        except json.JSONDecodeError:
            yield self.create_text_message("Error: Invalid JSON in scraper_params")
            return

        payload = {
            "url": url,
            "scraper_code": scraper_code,
            "scraper_scope": "GLOBAL",
            "scraper_params": scraper_params,
            "action_type": "scrape_data"
        }

        try:
            with httpx.Client(timeout=30) as client:
                # Submit web scraper job
                response = client.post(
                    f"{BASE_URL}/web-scraper",
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
                        f"{BASE_URL}/web-scraper/{job_id}",
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
                        yield self.create_text_message(f"Web scraping failed: {error}")
                        return

                yield self.create_text_message("Error: Job timed out. Please try again.")

        except httpx.TimeoutException:
            yield self.create_text_message("Error: Request timeout")
        except httpx.RequestError as e:
            yield self.create_text_message(f"Error: {str(e)}")

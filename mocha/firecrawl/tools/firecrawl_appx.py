import json
import logging
import time
from collections.abc import Mapping
from typing import Any

import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class FirecrawlApp:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.firecrawl.dev"
        if not self.api_key:
            raise ValueError("API key is required")

    def _prepare_headers(self, idempotency_key: str | None = None):
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _request(
        self,
        method: str,
        url: str,
        data: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> Mapping[str, Any] | None:
        if not headers:
            headers = self._prepare_headers()
        for i in range(retries):
            try:
                logger.debug(f"Making {method} request to {url} with data: {data}")
                response = requests.request(method, url, json=data, headers=headers)
                logger.debug(f"Response status: {response.status_code}")
                if not response.ok:
                    logger.error(f"Request failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception on attempt {i+1}/{retries}: {e}")
                if i < retries - 1:
                    time.sleep(backoff_factor * (2**i))
                else:
                    raise
        return None

    def scrape_url(self, url: str, **kwargs):
        endpoint = f"{self.base_url}/v2/scrape"
        data = {"url": url, **kwargs}
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = self._request("POST", endpoint, data)
        if response is None:
            raise HTTPError("Failed to scrape URL after multiple retries")
        return response

    def map(self, url: str, **kwargs):
        endpoint = f"{self.base_url}/v2/map"
        data = {"url": url, **kwargs}
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = self._request("POST", endpoint, data)
        if response is None:
            raise HTTPError("Failed to perform map after multiple retries")
        return response

    def crawl_url(
        self, url: str, wait: bool = True, poll_interval: int = 5, idempotency_key: str | None = None, **kwargs
    ):
        endpoint = f"{self.base_url}/v2/crawl"
        headers = self._prepare_headers(idempotency_key)
        data = {"url": url, **kwargs}
        logger.debug(f"Sent request to {endpoint=} body={data}")
        response = self._request("POST", endpoint, data, headers)
        if response is None:
            raise HTTPError("Failed to initiate crawl after multiple retries")
        elif response.get("success") == False:
            raise HTTPError(f'Failed to crawl: {response.get("error")}')
        job_id: str = response["id"]
        if wait:
            return self._monitor_job_status(job_id=job_id, poll_interval=poll_interval)
        return response

    def check_crawl_status(self, job_id: str):
        endpoint = f"{self.base_url}/v2/crawl/{job_id}"
        response = self._request("GET", endpoint)
        if response is None:
            raise HTTPError(f"Failed to check status for job {job_id} after multiple retries")
        return response

    def cancel_crawl_job(self, job_id: str):
        endpoint = f"{self.base_url}/v2/crawl/{job_id}"
        response = self._request("DELETE", endpoint)
        if response is None:
            raise HTTPError(f"Failed to cancel job {job_id} after multiple retries")
        return response

    def _monitor_job_status(self, job_id: str, poll_interval: int):
        while True:
            status = self.check_crawl_status(job_id)
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise HTTPError(f'Job {job_id} failed: {status["error"]}')
            time.sleep(poll_interval)


def get_array_params(tool_parameters: dict[str, Any], key):
    param = tool_parameters.get(key)
    if param:
        return param.split(",")


def get_json_params(tool_parameters: dict[str, Any], key):
    param = tool_parameters.get(key)
    if param:
        try:
            # support both single quotes and double quotes
            param = param.replace("'", '"')
            param = json.loads(param)
        except Exception:
            raise ValueError(f"Invalid {key} format.")
        return param


def process_formats_v2(tool_parameters: dict[str, Any]):
    """Process formats parameter for Firecrawl v2 API"""
    formats = get_array_params(tool_parameters, "formats")
    if not formats:
        return None
    
    processed_formats = []
    for format_item in formats:
        format_item = format_item.strip()
        # Handle basic string formats
        if format_item in ["markdown", "html", "rawHtml", "links", "summary"]:
            processed_formats.append(format_item)
        # Handle extract format (renamed to json in v2)
        elif format_item == "extract":
            # Convert to v2 json format object
            json_format = {"type": "json"}
            # Add schema and prompt if available
            schema = get_json_params(tool_parameters, "schema")
            prompt = tool_parameters.get("prompt")
            system_prompt = tool_parameters.get("systemPrompt")
            
            if schema:
                json_format["schema"] = schema
            if prompt:
                json_format["prompt"] = prompt
            if system_prompt:
                json_format["systemPrompt"] = system_prompt
                
            processed_formats.append(json_format)
        # Handle screenshot formats
        elif format_item.startswith("screenshot"):
            if format_item == "screenshot@fullPage":
                processed_formats.append({"type": "screenshot", "fullPage": True})
            else:
                processed_formats.append({"type": "screenshot"})
    
    return processed_formats
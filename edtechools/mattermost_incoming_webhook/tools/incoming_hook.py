from collections.abc import Generator
from typing import Dict, Any, Optional, Union

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests
import json


class WebhookClient:
    """A client for interacting with webhooks with extensibility in mind."""

    def __init__(
        self, base_url: str = None, default_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the webhook client.

        Args:
            base_url: Optional base URL for all requests
            default_headers: Optional default headers to include in all requests
        """
        self.base_url = base_url
        self.default_headers = default_headers or {"Content-Type": "application/json"}

    def post(
        self,
        url: str,
        data: Union[Dict[str, Any], str],
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> requests.Response:
        """
        Send a POST request to the specified webhook URL.

        Args:
            url: The webhook URL or endpoint (if base_url is defined)
            data: The data to send in the request body
            headers: Optional additional headers
            params: Optional query parameters
            timeout: Request timeout in seconds

        Returns:
            Response object from the requests library
        """
        # Combine default headers with any passed headers
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)

        # Build full URL if base_url is provided
        full_url = f"{self.base_url}{url}" if self.base_url else url

        # Ensure data is properly formatted
        if isinstance(data, dict):
            payload = json.dumps(data)
        else:
            payload = data

        try:
            response = requests.post(
                full_url,
                data=payload,
                headers=request_headers,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()

            return response
        except requests.exceptions.RequestException:
            pass

    def send_text_message(self, url: str, text: str) -> requests.Response:
        """
        Helper method to send a text message to a webhook.

        Args:
            url: The webhook URL
            text: The text content to send

        Returns:
            Response object from the requests library
        """
        return self.post(url, {"text": text})


class MattermostTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        llm_content = tool_parameters["message"]
        webhook_url = tool_parameters["webhook_url"]

        client = WebhookClient()
        client.send_text_message(webhook_url, llm_content)

        yield self.create_text_message(llm_content)

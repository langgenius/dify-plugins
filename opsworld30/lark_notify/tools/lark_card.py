from collections.abc import Generator
from typing import Any, Dict
import json
import os
import time
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tenacity import retry, stop_after_attempt, wait_exponential


class LarkCardTool(Tool):
    WEBHOOK_BASE_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/"
    RETRY_ATTEMPTS = 3
    RETRY_MULTIPLIER = 1
    RETRY_MIN_WAIT = 4
    RETRY_MAX_WAIT = 10

    # Color mapping for card types
    COLOR_MAP = {
        "info": "blue",
        "warning": "orange",
        "success": "green",
        "error": "red"
    }

    def _get_env_var(self, env_var_name: str) -> str:
        """Get value from environment variable"""
        value = os.getenv(env_var_name, '')
        if not value:
            raise ValueError(f"Environment variable {env_var_name} is not set")
        return value

    def _get_webhook_url(self, webhook: str) -> str:
        """Get full webhook URL from either full URL or key-only format."""
        # Handle environment variable
        if webhook.startswith('${') and webhook.endswith('}'):
            env_var = webhook[2:-1]
            webhook = self._get_env_var(env_var)

        # Return if it's already a full URL
        if webhook.startswith('http'):
            return webhook

        # Extract webhook key and ensure it's not empty
        webhook_key = webhook.split('/hook/')[-1].strip('/')
        if not webhook_key:
            raise ValueError("Webhook key cannot be empty")
            
        return f"{self.WEBHOOK_BASE_URL}{webhook_key}"

    def _send_request(self, webhook: str, payload: dict) -> tuple[bool, str]:
        """Send request to Lark bot"""
        try:
            webhook_url = self._get_webhook_url(webhook)
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            result = response.json()
            
            # Check HTTP status code
            if response.status_code != 200:
                return False, f"HTTP error: {response.status_code}, URL: {webhook_url}"
                
            # Check business status code
            if result.get('code') != 0:
                error_msg = result.get('msg', 'Unknown error')
                if error_msg == 'Key Words Not Found':
                    return False, (
                        "Invalid webhook URL or format. Please check:\n"
                        "1. Full URL format should be: https://open.feishu.cn/open-apis/bot/v2/hook/xxx\n"
                        "2. If using key only, make sure it's the part after /hook/\n"
                        "3. If using environment variable, make sure it's properly set\n"
                        f"Current URL: {webhook_url}"
                    )
                return False, f"API error: {error_msg}"
                
            return True, ''
        except requests.RequestException as e:
            return False, f"Request failed: {str(e)}, URL: {webhook_url}"
        except ValueError as e:
            return False, f"Response parsing failed: {str(e)}"

    def _build_card_payload(
            self, 
            card_content: str, 
            title: str = "", 
            card_type: str = "info",
            show_time: bool = True
    ) -> dict:
        """Build card message payload"""
        # Build basic card structure
        card = {
            "header": {
                "template": self.COLOR_MAP.get(card_type, "blue"),
                "title": {
                    "content": title or "",
                    "tag": "plain_text"
                }
            },
            "elements": [],
            "config": {
                "wide_screen_mode": True
            }
        }

        # Split content by lines and create elements
        lines = card_content.split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                if line.startswith('- '):
                    # Handle list item with indentation
                    card["elements"].append({
                        "tag": "div",
                        "text": {
                            "content": "  • " + line[2:],  # Replace "- " with "  • "
                            "tag": "lark_md"
                        }
                    })
                else:
                    # Normal line
                    card["elements"].append({
                        "tag": "div",
                        "text": {
                            "content": line,
                            "tag": "lark_md"
                        }
                    })
        
        # Add timestamp if requested
        if show_time:
            # Add a divider line
            card["elements"].append({
                "tag": "hr"
            })
            
            # Add timestamp
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            card["elements"].append({
                "tag": "note",
                "elements": [{
                    "tag": "plain_text",
                    "content": current_time
                }]
            })
            
        return {
            "msg_type": "interactive",
            "card": card
        }

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=RETRY_MULTIPLIER,
            min=RETRY_MIN_WAIT,
            max=RETRY_MAX_WAIT
        )
    )
    def _send_card_message(self, webhook: str, payload: dict) -> Generator[ToolInvokeMessage, None, None]:
        """Send card message with retry mechanism"""
        try:
            success, error = self._send_request(webhook, payload)
            if not success:
                yield self.create_text_message(text=f"Message sending failed: {error}")
                return
            
            yield self.create_text_message(text="Card message delivered ")
        except Exception as e:
            yield self.create_text_message(text=f"Message sending failed: {str(e)}")

    def _validate_parameter(self, name: str, value: str | None) -> None:
        """Validate a required parameter"""
        if not value or not str(value).strip():
            raise ValueError(f"Run failed: tool parameter {name} not found in tool config")

    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Invoke the tool with the given parameters."""
        try:
            # Get and validate required parameters
            webhook = tool_parameters.get('webhook')
            card_content = tool_parameters.get('card_content')
            title = tool_parameters.get('title', '')
            card_type = tool_parameters.get('card_type', 'info')
            show_time = tool_parameters.get('show_time', True)
            
            for param_name, param_value in [('webhook', webhook), ('card_content', card_content)]:
                self._validate_parameter(param_name, param_value)

            # Build and send card message
            payload = self._build_card_payload(
                card_content=card_content,
                title=title,
                card_type=card_type,
                show_time=show_time
            )

            success, error = self._send_request(webhook, payload)
            if not success:
                yield self.create_text_message(text=f"Card message sending failed: {error}")
                return

            yield self.create_text_message(text="Card message delivered")
        except ValueError as e:
            raise

from collections.abc import Generator
from typing import Any, Dict
import os
import time
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tenacity import retry, stop_after_attempt, wait_exponential


class LarkTextTool(Tool):
    WEBHOOK_BASE_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/"
    MAX_MESSAGE_LENGTH = 500
    RETRY_ATTEMPTS = 3
    RETRY_MIN_WAIT = 4
    RETRY_MAX_WAIT = 10
    RETRY_MULTIPLIER = 1

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

    def _split_message(self, message: str) -> list[str]:
        """Split long message into chunks"""
        if len(message) <= self.MAX_MESSAGE_LENGTH:
            return [message]
        
        chunks = []
        current_chunk = ""
        
        for line in message.split('\n'):
            if len(current_chunk) + len(line) + 1 <= self.MAX_MESSAGE_LENGTH:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = line + '\n'
                
        if current_chunk:
            chunks.append(current_chunk.rstrip())
            
        return chunks

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=RETRY_MULTIPLIER,
            min=RETRY_MIN_WAIT,
            max=RETRY_MAX_WAIT
        )
    )
    def _send_text_message(self, webhook: str, message: str) -> Generator[ToolInvokeMessage, None, None]:
        """Send text message with support for long text splitting and retry mechanism"""
        message_chunks = self._split_message(message)
        total_chunks = len(message_chunks)
        
        for index, chunk in enumerate(message_chunks, 1):
            sequence_text = f"[{index}/{total_chunks}] " if total_chunks > 1 else ""
            chunk_text = sequence_text + chunk

            payload = {
                "msg_type": "text",
                "content": {
                    "text": chunk_text
                }
            }

            success, error = self._send_request(webhook, payload)
            if not success:
                yield self.create_text_message(text=f"Message sending failed: {error}")
                return

            if index < total_chunks:
                time.sleep(1)  # Avoid rate limiting
        
        sent_msg = "Message sent in {num} parts " if total_chunks > 1 else "Message delivered "
        yield self.create_text_message(text=sent_msg.format(num=total_chunks))

    def _validate_parameter(self, name: str, value: str | None) -> None:
        """Validate a required parameter"""
        if not value or not str(value).strip():
            raise ValueError(f"Run failed: tool parameter {name} not found in tool config")

    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # Get and validate required parameters
            webhook = tool_parameters.get('webhook')
            message = tool_parameters.get('message')
            
            for param_name, param_value in [('webhook', webhook), ('message', message)]:
                self._validate_parameter(param_name, param_value)

            yield from self._send_text_message(webhook, message)
        except ValueError as e:
            raise

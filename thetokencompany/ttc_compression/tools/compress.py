import logging
from typing import Any, Generator

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class CompressInputTool(Tool):
    """
    TTC Compression Tool.

    Compresses input text using The Token Company API to reduce
    token usage before sending to any LLM.
    """

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Compress the input text using TTC API.

        Args:
            tool_parameters: Dictionary containing:
                - text: The text to compress
                - aggressiveness: Compression level (0.1-0.9)
                - max_output_tokens: Maximum tokens in output
                - min_output_tokens: Minimum tokens in output
                - protect_json: Whether to preserve JSON structures

        Yields:
            ToolInvokeMessage with compressed text or error
        """
        # Log incoming parameters for debugging
        logger.info(f"TTC Compress tool invoked with parameters: {tool_parameters}")

        # Get text parameter
        text = tool_parameters.get("text") or ""

        # Get aggressiveness with default
        aggressiveness_val = tool_parameters.get("aggressiveness")
        if aggressiveness_val is None:
            aggressiveness = 0.6
        else:
            try:
                aggressiveness = float(aggressiveness_val)
                # Clamp to valid range
                aggressiveness = max(0.1, min(0.9, aggressiveness))
            except (ValueError, TypeError):
                aggressiveness = 0.5

        # Get max_output_tokens (can be None)
        max_output_tokens = tool_parameters.get("max_output_tokens")
        if max_output_tokens is not None:
            try:
                max_output_tokens = int(max_output_tokens)
            except (ValueError, TypeError):
                max_output_tokens = None

        # Get min_output_tokens (can be None)
        min_output_tokens = tool_parameters.get("min_output_tokens")
        if min_output_tokens is not None:
            try:
                min_output_tokens = int(min_output_tokens)
            except (ValueError, TypeError):
                min_output_tokens = None

        # Get protect_json with default False
        protect_json_val = tool_parameters.get("protect_json")
        if protect_json_val is None:
            protect_json = False
        else:
            protect_json = bool(protect_json_val)

        # Validate input
        if not text or not str(text).strip():
            yield self.create_text_message("Error: No text provided to compress.")
            yield self.create_json_message({"error": "No text provided", "parameters_received": tool_parameters})
            return

        text = str(text).strip()

        # Get API key from credentials
        api_key = self.runtime.credentials.get("ttc_api_key")
        if not api_key:
            yield self.create_text_message(
                "Error: TTC API key not configured. Please add your API key in the tool settings."
            )
            return

        # Build compression_settings
        compression_settings = {
            "aggressiveness": aggressiveness,
            "protect_json": protect_json,
        }

        # Add optional parameters if set
        if max_output_tokens is not None:
            compression_settings["max_output_tokens"] = max_output_tokens
        if min_output_tokens is not None:
            compression_settings["min_output_tokens"] = min_output_tokens

        # Build request payload
        payload = {
            "model": "bear-1",
            "input": text,
            "compression_settings": compression_settings,
        }

        logger.info(f"TTC API request payload: {payload}")

        # Call TTC API
        try:
            response = requests.post(
                "https://api.thetokencompany.com/v1/compress",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )

            if response.status_code == 401:
                yield self.create_text_message(
                    "Error: Invalid TTC API key. Please check your credentials."
                )
                return

            if response.status_code == 429:
                yield self.create_text_message(
                    "Error: TTC API rate limit exceeded. Please try again later."
                )
                return

            if response.status_code != 200:
                logger.warning(f"TTC API error: {response.status_code} - {response.text}")
                yield self.create_text_message(
                    f"Error: TTC API returned status {response.status_code}. Returning original text."
                )
                yield self.create_text_message(text)
                return

            result = response.json()
            compressed_text = result.get("output", text)
            original_tokens = result.get("original_input_tokens", 0)
            output_tokens = result.get("output_tokens", 0)
            compression_time = result.get("compression_time", 0)

            # Log compression stats
            if original_tokens > 0:
                savings_pct = ((original_tokens - output_tokens) / original_tokens) * 100
                logger.info(
                    f"TTC Compression: {original_tokens} -> {output_tokens} tokens "
                    f"({savings_pct:.1f}% reduction) in {compression_time:.2f}s"
                )

            # Return compressed text
            yield self.create_text_message(compressed_text)

            # Also return stats as JSON for workflows that want them
            yield self.create_json_message({
                "compressed_text": compressed_text,
                "original_tokens": original_tokens,
                "output_tokens": output_tokens,
                "tokens_saved": original_tokens - output_tokens,
                "compression_ratio": round(output_tokens / original_tokens, 3) if original_tokens > 0 else 1.0,
                "compression_time_seconds": compression_time,
            })

        except requests.exceptions.Timeout:
            yield self.create_text_message(
                "Error: TTC API request timed out. Returning original text."
            )
            yield self.create_text_message(text)

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"TTC API connection error: {e}")
            yield self.create_text_message(
                "Error: Could not connect to TTC API. Returning original text."
            )
            yield self.create_text_message(text)

        except Exception as e:
            logger.exception("Unexpected error in TTC compression")
            yield self.create_text_message(f"Error: {str(e)}. Returning original text.")
            yield self.create_text_message(text)

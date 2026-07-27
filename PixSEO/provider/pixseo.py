import json
from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.get_usage import GetUsageTool


class PixseoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for msg in GetUsageTool.from_credentials(credentials).invoke(
                tool_parameters={},
            ):
                # Dify SDK stores JSON data in the 'message' attribute as a string
                raw = getattr(msg, "message", None) or getattr(msg, "data", None)
                if raw is None:
                    continue
                if isinstance(raw, str):
                    try:
                        raw = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        pass
                if isinstance(raw, dict) and "error" in raw:
                    raise ToolProviderCredentialValidationError(
                        raw.get("error", "Invalid API key")
                    )
                break
        except ToolProviderCredentialValidationError:
            raise
        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError(
                "Connection timed out while validating the API key. "
                "Please check your network and try again."
            )
        except requests.exceptions.ConnectionError:
            raise ToolProviderCredentialValidationError(
                "Unable to connect to the PixSEO API service. "
                "Please check your network connection and try again."
            )
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(
                f"Network error while validating the API key: {e}"
            )
        except Exception as e:
            # Avoid mapping all exceptions to "Invalid API key".
            # If the response explicitly indicated an authentication error,
            # it would have been raised above.
            raise ToolProviderCredentialValidationError(
                f"Failed to validate API key: {e}"
            )

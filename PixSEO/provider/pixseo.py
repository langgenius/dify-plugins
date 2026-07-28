from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from _config import API_BASE


class PixseoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("pixseo_api_key", "")
        headers = {"X-API-Key": api_key}

        try:
            resp = requests.request(
                "GET",
                f"{API_BASE}/api/v1/usage",
                headers=headers,
                timeout=10,
            )
            if resp.status_code in (401, 403):
                raise ToolProviderCredentialValidationError("Invalid API key")
            resp.raise_for_status()
            try:
                body = resp.json()
            except Exception:
                body = {}
            # 后端统一错误格式: {"error": {"code": ..., "message": ..., "user_tip": ...}}
            err = body.get("error") if isinstance(body, dict) else None
            if isinstance(err, dict):
                raise ToolProviderCredentialValidationError(
                    err.get("user_tip", "Invalid API key")
                )
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
            raise ToolProviderCredentialValidationError(
                f"Failed to validate API key: {e}"
            )

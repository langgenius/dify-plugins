from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import requests

API_BASE = "https://wwwvibo.com"


class ViBoProvider(ToolProvider):
    """Validates the ViBo license key via /status."""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("vibo_key")
        if not api_key or not str(api_key).strip():
            raise ToolProviderCredentialValidationError(
                "ViBo license key is missing. Get a free trial at https://wwwvibo.com"
            )
        try:
            resp = requests.post(
                f"{API_BASE}/status",
                json={"key": str(api_key).strip()},
                timeout=10,
            )
            data = resp.json()
            if not data.get("ok"):
                raise ToolProviderCredentialValidationError(
                    f"ViBo key rejected: {data.get('message', 'invalid key')}"
                )
        except requests.RequestException as exc:
            raise ToolProviderCredentialValidationError(
                f"Could not reach ViBo API to validate the key: {exc}"
            ) from None
        except Exception as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from None

from __future__ import annotations

from typing import Any

from tools._client import E2AClient


def e2a_client(tool: Any) -> E2AClient:
    return E2AClient(tool.runtime.credentials.get("e2a_api_key", ""))

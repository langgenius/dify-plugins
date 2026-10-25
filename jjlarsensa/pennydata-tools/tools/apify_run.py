import re
from typing import Any

import requests

API = "https://api.apify.com/v2"
MAX_ITEMS = 100
MAX_COST_USD = 1.0
SYNC_TIMEOUT_SECS = 300


def split_list(value: Any, limit: int = MAX_ITEMS) -> list[str]:
    """Split a comma/newline/semicolon/space separated string into unique items."""
    seen: dict[str, None] = {}
    for part in re.split(r"[\s,;]+", str(value or "")):
        part = part.strip()
        if part:
            seen.setdefault(part)
    return list(seen)[:limit]


def run_actor(token: str, actor: str, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Run a public pennydata actor synchronously with the caller's own token."""
    resp = requests.post(
        f"{API}/acts/pennydata~{actor}/run-sync-get-dataset-items",
        params={"maxTotalChargeUsd": MAX_COST_USD, "format": "json", "clean": "true"},
        headers={"Authorization": f"Bearer {token}"},
        json=run_input,
        timeout=SYNC_TIMEOUT_SECS + 15,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        return data if isinstance(data, list) else [data]
    if resp.status_code in (401, 403):
        raise ValueError("Apify rejected the API token (check it in the PennyData Tools credentials).")
    if resp.status_code == 402:
        raise ValueError("Apify account has insufficient prepaid usage or hit a spending limit.")
    if resp.status_code == 408:
        raise ValueError("The Apify run took longer than 5 minutes; send fewer items.")
    raise ValueError(f"Apify returned HTTP {resp.status_code}: {resp.text[:300]}")

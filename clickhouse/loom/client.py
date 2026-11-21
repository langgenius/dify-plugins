"""Scoped SDK requests run in native threads; credentials stay in provider settings."""

from typing import Any
from urllib.parse import urlsplit

from gevent import get_hub
from loom import SyncAgent


def request(
    credentials: dict[str, Any], op: str, body: dict[str, Any], **identity: Any
) -> dict[str, Any]:
    fields = {}
    for name in ("base_url", "api_key", "org", "namespace", "agent"):
        value = credentials.get(name)
        if not isinstance(value, str) or not value.strip() or value.strip() in ("-", "*"):
            raise ValueError(f"Configure {name} in the Loom provider")
        fields[name] = value.strip()
    url = urlsplit(fields["base_url"])
    if (
        url.scheme not in ("http", "https")
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
    ):
        raise ValueError(
            "Loom URL must be an HTTP(S) endpoint without embedded credentials or query"
        )

    def call() -> dict[str, Any] | Exception:
        try:
            with SyncAgent(
                **fields,
                timeout_s=15,
                call_timeout_s=30,
                retry={"max_attempts": 1},
                pacing=False,
                consumer="dify-plugin",
            ) as agent:
                return agent.call(op, body, **identity)
        except Exception as error:  # noqa: BLE001 — Return failures without hub credential logging.
            return error

    result = get_hub().threadpool.apply(call)
    if isinstance(result, Exception):
        raise result
    return result


def user(parameters: dict[str, Any]) -> str:
    value = parameters.get("user_id")
    if not isinstance(value, str) or not value.strip() or value.strip() in ("-", "*"):
        raise ValueError("Bind User ID to an application-controlled end-user identifier")
    return value.strip()


def text(parameters: dict[str, Any], name: str) -> str:
    value = parameters.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value


def limit(parameters: dict[str, Any], maximum: int = 500) -> int:
    value = parameters.get("top_k", 5)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 1 <= value <= maximum
        or int(value) != value
    ):
        raise ValueError(f"top_k must be an integer from 1 to {maximum}")
    return int(value)

from typing import Any

from dify_plugin import ToolProvider


class X402PayPerCallProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # This provider requires no account or API key: each call carries its
        # own payment proof (a settled Nano block hash or prepaid balance
        # account), supplied per-invocation as tool parameters rather than as
        # provider credentials. Nothing to validate here.
        return

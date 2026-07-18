from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from scrapeunblocker_client import ScrapeUnblockerClient, ScrapeUnblockerError


class ScrapeUnblockerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            client = ScrapeUnblockerClient.from_credentials(credentials)
            client.validate_credentials()
        except ScrapeUnblockerError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

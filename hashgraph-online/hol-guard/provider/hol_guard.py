from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class HolGuardProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            from codex_plugin_scanner.guard.runtime.command_inspection import inspect_command

            if not callable(inspect_command):
                raise TypeError("HOL Guard command inspection API is unavailable")
        except Exception as exc:  # noqa: BLE001
            raise ToolProviderCredentialValidationError(
                f"HOL Guard failed to load: {exc}"
            ) from exc

"""Prompt Shield tool provider for Dify."""

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class PromptShieldProvider(ToolProvider):
    """Provider that validates prompt-shield is installed and functional."""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate that prompt-shield is installed by running a quick test scan."""
        try:
            from prompt_shield import PromptShieldEngine

            engine = PromptShieldEngine()
            report = engine.scan("test validation input")
            if report.scan_id is None:
                raise ToolProviderCredentialValidationError(
                    "prompt-shield scan returned invalid result"
                )
        except ImportError as e:
            raise ToolProviderCredentialValidationError(
                "prompt-shield is not installed. "
                "Install it with: pip install prompt-shield-ai"
            ) from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to initialize prompt-shield: {e}"
            ) from e

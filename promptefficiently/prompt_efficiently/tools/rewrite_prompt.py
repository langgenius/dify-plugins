from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._auth import drop_token, ensure_token
from .pe_api import PEError, SessionExpired, ai_rewrite


class RewritePromptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        creds = self.runtime.credentials or {}
        if creds.get("confirm_adult_consent") not in (True, "true", "True", "1", 1):
            raise PEError(
                "AI rewrite is off for this account. In the plugin settings, tick the 18+ consent agreeing that text sent to this tool is processed by Prompt Efficiently and its AI provider, then save."
            )
        text = (tool_parameters.get("text") or "").strip()
        if not text:
            raise PEError("Pass the prompt text to rewrite.")
        if len(text) > 32000:
            raise PEError("That prompt is too long to rewrite (over 32,000 characters).")
        mode = (tool_parameters.get("mode") or "shorter").strip().lower()
        if mode not in ("shorter", "clearer", "more_specific"):
            mode = "shorter"

        token = ensure_token(self)
        try:
            result = ai_rewrite(token, text, mode)
        except SessionExpired:
            drop_token(self)
            token = ensure_token(self, force_refresh=True)
            result = ai_rewrite(token, text, mode)

        rewrite = result.get("rewrite", "")
        warning = result.get("warning") or "Review the rewrite against your original before using it."
        yield self.create_json_message(
            {
                "mode": mode,
                "rewrite": rewrite,
                "unchanged": bool(result.get("unchanged")),
                "warning": warning,
                "source": "promptefficiently.com",
            }
        )
        yield self.create_text_message(rewrite_card(mode, rewrite, bool(result.get("unchanged")), warning))


def rewrite_card(mode, rewrite, unchanged, warning):
    """Markdown card mirroring the extension's rewrite panel."""
    mode_label = {"shorter": "Shorter", "clearer": "Clearer", "more_specific": "More specific"}.get(mode, mode)
    if unchanged or not rewrite:
        body = "No safer version returned. Your original prompt is unchanged."
    else:
        body = "> " + rewrite.replace("\n", "\n> ")
    return (
        "### Prompt Efficiently rewrite \u00b7 %s\n\n"
        "%s\n\n"
        "_%s Lower costs are not guaranteed. promptefficiently.com_"
    ) % (mode_label, body, warning)

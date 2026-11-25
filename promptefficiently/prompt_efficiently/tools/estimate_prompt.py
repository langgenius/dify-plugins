from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._auth import drop_token, ensure_token
from .pe_api import PEError, SessionExpired, consume_usage, full_estimate, platform_by_id


class EstimatePromptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        text = (tool_parameters.get("prompt") or "").strip()
        if not text:
            raise PEError("Pass the prompt text to estimate.")
        if len(text) > 100000:
            raise PEError("That prompt is too long to estimate (over 100,000 characters).")
        platform_id = (tool_parameters.get("platform") or "").strip().lower()
        platform = platform_by_id(platform_id)
        if not platform:
            raise PEError("Choose one of: chatgpt, claude, gemini, grok, town, manus, lovable, bolt, replit, openai_api, anthropic_api, gemini_api, deepseek, xai_api, mistral, groq, together, fireworks, openrouter, qwen, zhipu, moonshot, cohere, ollama.")
        size = (tool_parameters.get("size") or "medium").strip().lower()
        if size not in ("small", "medium", "big"):
            size = "medium"
        plan_id = (tool_parameters.get("plan") or "").strip().lower() or None

        token = ensure_token(self)
        try:
            pro, remaining = consume_usage(token)
        except SessionExpired:
            drop_token(self)
            token = ensure_token(self, force_refresh=True)
            pro, remaining = consume_usage(token)

        result = full_estimate(text, platform_id, size, plan_id)
        result["account"] = {"plan": "Pro" if pro else "Free"}
        if remaining is not None and not pro:
            result["account"]["freeEstimatesLeftToday"] = remaining
        result["disclaimer"] = "Rough guide, not a quote or a reading of your balance. promptefficiently.com"
        yield self.create_json_message(result)
        yield self.create_text_message(estimate_card(result, pro, remaining))


def estimate_card(result, pro, remaining):
    """Markdown card mirroring the extension's cost bubble."""
    fit = result.get("cheapestFreeFit")
    if result.get("plan") == "Pay per use":
        fit_line = "Pay-per-use API, billed per token. No free tier tracked."
    elif fit and fit["platform"] != result["platform"] and fit.get("headroom", 0) >= 1:
        fit_line = (
            "Rough guide: this fits in %s's free tier (about %s). "
            "Check their current limits first." % (fit["platform"], fit["rangeText"])
        )
    else:
        fit_line = "Rough guide: this is likely beyond the free tiers we track."
    if pro:
        plan_line = "**Pro plan** \u00b7 unlimited estimates."
    elif remaining is not None:
        plan_line = (
            "**Free plan** \u00b7 %s of 5 free estimates left today. "
            "[Upgrade to Pro](https://promptefficiently.com/app) for unlimited estimates." % remaining
        )
    else:
        plan_line = "[Upgrade to Pro](https://promptefficiently.com/app) for unlimited estimates."
    return (
        "### About %s on %s\n\n"
        "**Plan:** %s \u00b7 **Task size:** %s \u00b7 **Input:** ~%s tokens\n\n"
        "%s\n\n"
        "%s\n\n"
        "%s\n\n"
        "Want it cheaper? Run the **Prompt Efficiently rewrite** tool on this prompt "
        "for a shorter version.\n\n"
        "_Rough guide, not a quote or a reading of your balance. promptefficiently.com_"
    ) % (
        result["estimate"],
        result["platform"],
        result["plan"],
        result["size"].capitalize(),
        result["roughInputTokens"],
        result["verdictText"],
        fit_line,
        plan_line,
    )

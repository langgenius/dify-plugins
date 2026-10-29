"""Router /v1/models 里的一条模型 → Dify 模型 YAML。打包时（sync_models.py）和运行时（新模型）共用。"""

from __future__ import annotations

CURRENCY = {"cn": "RMB", "intl": "USD"}
MAX_OUTPUT = 65536
# 国际站的 GPT / Claude / Gemini 经 LiteLLM 转给原厂，原厂不收的参数直接 400 而不是忽略：
# GPT-5 起不收 temperature / top_p / penalty，Claude、Gemini 不收 penalty，新版 Claude 的 temperature 和 top_p 不能同传。
# 参数表仍给每个模型列全 —— Dify 切换模型时会把新模型没列的参数删掉并弹「部分参数无效，已移除」，
# 所以不收的参数照列、说明里写明不生效，调用前由 upstream_params 去掉。
IGNORED_BY_OWNER = {
    "OpenAI": ("temperature", "top_p", "presence_penalty", "frequency_penalty"),
    "Anthropic": ("presence_penalty", "frequency_penalty"),
    "Google": ("presence_penalty", "frequency_penalty"),
}
IGNORED_HELP = {
    "zh_Hans": "该模型不支持此参数，开启了也不生效，不影响正常调用",
    "en_US": "Not supported by this model. Ignored if set; calls still work.",
}
CLAUDE_TOP_P_HELP = {
    "zh_Hans": "Claude 不能同时用温度和 Top P，两项都开时只按温度生效",
    "en_US": "Claude can't take temperature and top_p together; temperature wins if both are set.",
}
ALL_PARAMS = ("temperature", "top_p", "max_tokens", "presence_penalty", "frequency_penalty")


def model_filename(model_id: str) -> str:
    return model_id.replace("/", "--") + ".yaml"


def display_label(model_id: str, owner: str) -> str:
    """GPT / Claude / Gemini 按官方写法显示（GPT-6.1 Sol、Claude Opus 5.5），国内模型保持 id。"""
    parts = model_id.split("-")
    if owner == "OpenAI" and len(parts) > 1:
        return " ".join([f"GPT-{parts[1]}", *(p.capitalize() for p in parts[2:])])
    if owner == "Anthropic":
        nums = ".".join(p for p in parts if p.isdigit())
        return " ".join([*(p.capitalize() for p in parts if not p.isdigit()), nums]).strip()
    if owner == "Google":
        return " ".join(p.capitalize() for p in parts)
    return model_id


def upstream_params(owner: str, params: dict) -> dict:
    """去掉上游不收的参数（Dify 应用里开了也照样能调通）。"""
    ignored = IGNORED_BY_OWNER.get(owner, ())
    out = {k: v for k, v in params.items() if k not in ignored}
    if owner == "Anthropic" and "temperature" in out:
        out.pop("top_p", None)
    return out


def param_rule(p: str, owner: str, context: int) -> dict:
    rule = {"name": p, "use_template": p}
    if p == "max_tokens":
        rule |= {"default": 4096, "min": 1, "max": min(context, MAX_OUTPUT)}
    if p in IGNORED_BY_OWNER.get(owner, ()):
        rule["help"] = dict(IGNORED_HELP)  # 拷一份，否则 YAML 里会生成锚点引用
    elif owner == "Anthropic" and p == "top_p":
        rule["help"] = dict(CLAUDE_TOP_P_HELP)
    return rule


def features_of(capabilities: list[str]) -> list[str]:
    feats = []
    if "tools" in capabilities:
        feats += ["agent-thought", "tool-call", "multi-tool-call", "stream-tool-call"]
    if "vision" in capabilities:
        feats.append("vision")
    return feats


def model_yaml(m: dict, site: str) -> dict:
    context = int(m.get("context_length") or 32768)
    owner = m.get("owned_by", "")
    doc = {
        "model": m["id"],
        "label": {"en_US": display_label(m["id"], owner)},
        "model_type": "llm",
        "features": features_of(m.get("capabilities") or []),
        "model_properties": {"mode": "chat", "context_size": context},
        "parameter_rules": [param_rule(p, owner, context) for p in ALL_PARAMS],
    }
    if not doc["features"]:
        del doc["features"]
    price = m.get("pricing") or {}
    if price.get("unit") == "/MTok" and "input" in price and "output" in price:
        doc["pricing"] = {
            "input": str(price["input"]),
            "output": str(price["output"]),
            "unit": "0.000001",
            "currency": CURRENCY[site],
        }
    return doc

"""
Bumo Router 连接细节：站点识别、模型目录、请求标识、报错翻译。

Router 有两个站点，Key 和模型都不互通：
  - 国内站 router.bumo.cc：DeepSeek / Kimi / Qwen / GLM / MiniMax ...
  - 国际站 router.bumo.ai：Claude / GPT / Gemini ...
用户在 Dify 里只填一个 Key，插件自己探测 Key 属于哪个站（不让用户选站点）。

探测不花钱：Router 先验 Key、再查余额、最后才解析模型（lib/v1/proxy/index.ts），
拿一个不存在的模型名发请求，401 = 不是这个站的 Key，402 = Key 对但没余额，404 = Key 对且有余额。
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Optional

import requests

PLUGIN_VERSION = "0.0.3"

SITES = {
    "cn": "https://router.bumo.cc/v1",
    "intl": "https://router.bumo.ai/v1",
}
SITE_CONSOLE = {
    "cn": "https://router.bumo.cc",
    "intl": "https://router.bumo.ai",
}
# Router 按 X-Title / HTTP-Referer 认调用方（utils/client-detect.ts），用量页据此按客户端分行
CLIENT_HEADERS = {
    "X-Title": "Dify",
    "HTTP-Referer": "https://dify.ai/",
    "User-Agent": f"bumo-router-dify-plugin/{PLUGIN_VERSION}",
}
PROBE_MODEL = "__bumo_dify_key_probe__"
CATALOG_PATH = Path(__file__).with_name("catalog.json")
LIVE_TTL = 600

_site_cache: dict[str, str] = {}
_live_cache: dict[str, tuple[float, dict]] = {}
_lock = threading.Lock()


class RouterKeyError(Exception):
    """Key 无效 / 没余额：给用户看的报错，中英双语。"""


def _key_hash(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def normalize_endpoint(url: str) -> str:
    """接受 https://router.bumo.cc、.../v1、.../v1/、.../v1/chat/completions 这几种写法。"""
    url = (url or "").strip().rstrip("/")
    if url.endswith("/chat/completions"):
        url = url[: -len("/chat/completions")]
    if not url.endswith("/v1"):
        url += "/v1"
    return url


def load_catalog() -> dict:
    """打包时由 scripts/sync_models.py 生成的模型目录：{model_id: {site, context_length, capabilities, ...}}"""
    with CATALOG_PATH.open(encoding="utf-8") as f:
        return json.load(f)["models"]


def probe(endpoint: str, api_key: str, timeout: float = 15) -> int:
    resp = requests.post(
        f"{endpoint}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", **CLIENT_HEADERS},
        json={"model": PROBE_MODEL, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
        timeout=timeout,
    )
    resp.close()
    return resp.status_code


def check_key(api_key: str, endpoint: Optional[str] = None) -> str:
    """
    校验 Key 并返回它所在站点的 API 地址。填了自定义地址就只验那一个地址。
    Key 无效、没余额都抛 RouterKeyError（文案直接给用户看）。
    """
    api_key = (api_key or "").strip()
    if not api_key:
        raise RouterKeyError("请填写 API Key / API Key is required")

    candidates = [normalize_endpoint(endpoint)] if endpoint else list(SITES.values())
    # 自动识别时一个站连不上 / 5xx 不能挡住另一个站：记下来接着探，全部不行再报
    unreachable = []
    for url in candidates:
        try:
            status = probe(url, api_key)
        except requests.RequestException as e:
            if endpoint:
                raise
            unreachable.append(f"{url}（{type(e).__name__}）")
            continue
        if status == 401:
            continue
        if status == 402:
            site = _site_of(url)
            console = SITE_CONSOLE.get(site, url)
            raise RouterKeyError(
                f"Key 有效，但账户余额为 0，请到 {console} 充值后再保存。"
                f" / The key is valid but the balance is 0. Top up at {console} and save again."
            )
        if status in (400, 404):
            return url
        if endpoint:
            raise RouterKeyError(f"连接 {url} 失败（HTTP {status}），请稍后重试 / Failed to reach {url} (HTTP {status})")
        unreachable.append(f"{url}（HTTP {status}）")

    if unreachable:
        failed = "、".join(unreachable)
        raise RouterKeyError(f"连接 {failed} 失败，请稍后重试 / Failed to reach {failed}")
    where = candidates[0] if endpoint else "router.bumo.cc / router.bumo.ai"
    raise RouterKeyError(
        f"API Key 无效：在 {where} 都验证不通过，请到 Router 控制台「API Keys」重新复制。"
        f" / Invalid API key for {where}. Copy it again from the Router console (API Keys)."
    )


def _site_of(url: str) -> str:
    for site, base in SITES.items():
        if base == url:
            return site
    return "custom"


def resolve_endpoint(credentials: dict) -> str:
    """调用模型时用：自定义地址优先，否则按 Key 探测站点（进程内缓存，只探一次）。"""
    custom = (credentials.get("endpoint_url") or "").strip()
    if custom:
        return normalize_endpoint(custom)
    key = _key_hash(credentials.get("api_key", ""))
    with _lock:
        cached = _site_cache.get(key)
    if cached:
        return cached
    url = check_key(credentials.get("api_key", ""))
    with _lock:
        _site_cache[key] = url
    return url


def live_models(endpoint: str) -> dict:
    """Router 的 /v1/models（免鉴权），10 分钟缓存。用于目录里还没有的新模型。"""
    now = time.time()
    with _lock:
        hit = _live_cache.get(endpoint)
    if hit and now - hit[0] < LIVE_TTL:
        return hit[1]
    resp = requests.get(f"{endpoint}/models", headers=CLIENT_HEADERS, timeout=15)
    resp.raise_for_status()
    models = {m["id"]: m for m in resp.json().get("data", []) if m.get("category", "chat") == "chat"}
    with _lock:
        _live_cache[endpoint] = (now, models)
    return models


def site_mismatch_message(model: str, model_site: str, key_site: str) -> str:
    want = SITE_CONSOLE[model_site]
    have = SITE_CONSOLE[key_site]
    return (
        f"模型 {model} 在 {want} 提供，当前 Key 属于 {have}。请换用 {have} 的模型，或到 {want} 创建 Key。"
        f" / {model} is served by {want}, but this key belongs to {have}. "
        f"Pick a model from {have}, or create a key at {want}."
    )


def explain_http_error(status: int, body: str) -> Optional[str]:
    """把 Router 的常见错误翻成用户能照做的话；认不出返回 None，保留原始报错。"""
    if status == 401:
        return "API Key 无效或已删除，请到 Router 控制台重新复制 / Invalid or deleted API key"
    if status == 402:
        return "账户余额不足，请到 Router 控制台充值 / Insufficient balance, please top up in the Router console"
    if status == 404 and "No provider for model" in body:
        return "这个模型当前站点不提供或已下线，请换一个模型 / This model is not available on this site"
    return None

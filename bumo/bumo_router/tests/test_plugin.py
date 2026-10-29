"""
单测：不连网，requests 全部打桩。

    cd integrations/dify-plugin && pip install -r requirements.txt pytest && pytest tests/test_plugin.py
"""

import json
from pathlib import Path

import pytest
import yaml

from dify_plugin.entities.model import AIModelEntity, ModelFeature, ModelPropertyKey
from dify_plugin.entities.model.message import UserPromptMessage
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
)

import models.router_client as rc
from models.llm.llm import BumoRouterLargeLanguageModel
from models.schema import ALL_PARAMS, IGNORED_HELP, display_label, model_filename, model_yaml, upstream_params
from provider.bumo_router import BumoRouterProvider
from scripts import sync_models

ROOT = Path(__file__).resolve().parent.parent
CN, INTL = rc.SITES["cn"], rc.SITES["intl"]


class FakeResp:
    def __init__(self, status=200, body=None, lines=None):
        self.status_code = status
        self._body = body if body is not None else {}
        self._lines = lines or []
        self.text = json.dumps(self._body)
        self.encoding = "utf-8"
        self.headers = {}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def iter_lines(self, *a, **k):
        yield from self._lines

    def close(self):
        pass


@pytest.fixture(autouse=True)
def clean_cache():
    rc._site_cache.clear()
    rc._live_cache.clear()
    yield


def fake_probe(monkeypatch, status_by_site):
    calls = []

    def post(url, **kw):
        calls.append((url, kw))
        base = url.rsplit("/chat/completions", 1)[0]
        return FakeResp(status_by_site.get(base, 401), {"error": {"message": "x"}})

    monkeypatch.setattr(rc.requests, "post", post)
    return calls


# ---------- 凭证校验 ----------


def test_cn_key_detected(monkeypatch):
    calls = fake_probe(monkeypatch, {CN: 404})
    assert rc.check_key("sk-cn") == CN
    assert len(calls) == 1
    # 探测请求带来源标识，且用不存在的模型名（Router 在解析模型前就返回，不扣费）
    _, kw = calls[0]
    assert kw["headers"]["X-Title"] == "Dify"
    assert kw["json"]["model"] == rc.PROBE_MODEL


def test_intl_key_detected(monkeypatch):
    calls = fake_probe(monkeypatch, {CN: 401, INTL: 404})
    assert rc.check_key("sk-intl") == INTL
    assert [u for u, _ in calls] == [f"{CN}/chat/completions", f"{INTL}/chat/completions"]


def test_wrong_key_has_clear_message(monkeypatch):
    fake_probe(monkeypatch, {CN: 401, INTL: 401})
    with pytest.raises(rc.RouterKeyError, match="API Key 无效.*Invalid API key"):
        rc.check_key("sk-wrong")


def test_empty_key(monkeypatch):
    calls = fake_probe(monkeypatch, {})
    with pytest.raises(rc.RouterKeyError, match="请填写"):
        rc.check_key("  ")
    assert calls == []


def test_zero_balance_points_to_topup(monkeypatch):
    fake_probe(monkeypatch, {CN: 402})
    with pytest.raises(rc.RouterKeyError, match="余额为 0.*router.bumo.cc"):
        rc.check_key("sk-poor")


def test_cn_down_still_detects_intl_key(monkeypatch):
    # 国内站 5xx / 连不上时不能挡住有效的国际站 Key
    calls = fake_probe(monkeypatch, {CN: 503, INTL: 404})
    assert rc.check_key("sk-intl") == INTL
    assert len(calls) == 2

    def post(url, **kw):
        if url.startswith(CN):
            raise rc.requests.ConnectionError("down")
        return FakeResp(404)

    monkeypatch.setattr(rc.requests, "post", post)
    assert rc.check_key("sk-intl") == INTL


def test_all_sites_down_reports_connection_failure(monkeypatch):
    fake_probe(monkeypatch, {CN: 503, INTL: 401})
    with pytest.raises(rc.RouterKeyError, match="连接 .*router.bumo.cc.*失败"):
        rc.check_key("sk-intl")


def test_custom_endpoint_5xx_fails_fast(monkeypatch):
    calls = fake_probe(monkeypatch, {"https://my.proxy/v1": 502})
    with pytest.raises(rc.RouterKeyError, match="HTTP 502"):
        rc.check_key("sk", "https://my.proxy/v1")
    assert len(calls) == 1


def test_custom_endpoint_only_probes_it(monkeypatch):
    calls = fake_probe(monkeypatch, {"https://my.proxy/v1": 404})
    assert rc.check_key("sk", "https://my.proxy/v1/chat/completions") == "https://my.proxy/v1"
    assert len(calls) == 1


@pytest.mark.parametrize(
    "raw",
    ["https://router.bumo.cc", "https://router.bumo.cc/", "https://router.bumo.cc/v1", "https://router.bumo.cc/v1/chat/completions"],
)
def test_normalize_endpoint(raw):
    assert rc.normalize_endpoint(raw) == CN


def test_provider_validate_wraps_error(monkeypatch):
    fake_probe(monkeypatch, {CN: 401, INTL: 401})
    with pytest.raises(CredentialsValidateFailedError, match="API Key 无效"):
        BumoRouterProvider.validate_provider_credentials(None, {"api_key": "sk-wrong"})


def test_provider_validate_ok(monkeypatch):
    fake_probe(monkeypatch, {CN: 404})
    BumoRouterProvider.validate_provider_credentials(None, {"api_key": "sk-ok"})


def test_site_detected_once_per_key(monkeypatch):
    calls = fake_probe(monkeypatch, {CN: 401, INTL: 404})
    for _ in range(3):
        assert rc.resolve_endpoint({"api_key": "sk-intl"}) == INTL
    assert len(calls) == 2


# ---------- 模型清单 ----------

SAMPLE = {
    "cn": [
        {"id": "deepseek/deepseek-flash", "category": "chat", "featured": True, "context_length": 1000000,
         "capabilities": ["tools", "reasoning"], "pricing": {"input": 1, "output": 2, "unit": "/MTok"}},
        {"id": "kimi/kimi-k3", "category": "chat", "context_length": 1048576,
         "capabilities": ["tools", "vision"], "pricing": {"input": 20, "output": 100, "unit": "/MTok"}},
    ],
    "intl": [
        {"id": "gpt-6-astra", "category": "chat", "featured": True, "context_length": 1050000, "owned_by": "OpenAI",
         "capabilities": ["tools", "vision"], "pricing": {"input": 5, "output": 30, "unit": "/MTok"}},
        {"id": "plain-model", "category": "chat", "context_length": 8000, "capabilities": []},
    ],
}


def test_model_yaml_features_and_pricing():
    doc = model_yaml(SAMPLE["cn"][1], "cn")
    assert doc["model"] == "kimi/kimi-k3"
    assert doc["model_properties"] == {"mode": "chat", "context_size": 1048576}
    assert "vision" in doc["features"] and "multi-tool-call" in doc["features"]
    assert doc["pricing"]["currency"] == "RMB"
    assert model_yaml(SAMPLE["intl"][0], "intl")["pricing"]["currency"] == "USD"
    plain = model_yaml(SAMPLE["intl"][1], "intl")
    assert "features" not in plain and "pricing" not in plain
    # max_tokens 上限不超过上下文
    assert next(r for r in plain["parameter_rules"] if r["name"] == "max_tokens")["max"] == 8000
    # 生成的 YAML 能被 SDK 解析
    AIModelEntity(**doc)


def test_every_model_lists_all_params():
    """参数表一致，Dify 切换模型时才不会弹「部分参数无效，已移除」；上游不收的写明不生效。"""
    rules = lambda doc: {r["name"]: r for r in doc["parameter_rules"]}
    gpt = rules(model_yaml(SAMPLE["intl"][0], "intl"))
    claude = rules(model_yaml({"id": "claude-opus-5-5", "owned_by": "Anthropic"}, "intl"))
    cn = rules(model_yaml(SAMPLE["cn"][0], "cn"))
    assert list(gpt) == list(claude) == list(cn) == list(ALL_PARAMS)
    assert gpt["temperature"]["help"] == IGNORED_HELP and "help" not in gpt["max_tokens"]
    assert claude["presence_penalty"]["help"] == IGNORED_HELP and "help" not in claude["temperature"]
    assert not any("help" in r for r in cn.values())
    AIModelEntity(**model_yaml(SAMPLE["intl"][0], "intl"))


def test_upstream_params():
    params = {"temperature": 0.7, "top_p": 0.9, "presence_penalty": 0.1, "frequency_penalty": 0.1, "max_tokens": 100}
    assert upstream_params("OpenAI", params) == {"max_tokens": 100}
    assert upstream_params("Anthropic", params) == {"temperature": 0.7, "max_tokens": 100}
    assert upstream_params("Anthropic", {"top_p": 0.9}) == {"top_p": 0.9}
    assert upstream_params("Google", params) == {"temperature": 0.7, "top_p": 0.9, "max_tokens": 100}
    assert upstream_params("", params) == params


@pytest.mark.parametrize("model_id,owner,label", [
    ("gpt-6-astra", "OpenAI", "GPT-6 Astra"),
    ("gpt-6.1-sol", "OpenAI", "GPT-6.1 Sol"),
    ("gpt-5.3-codex", "OpenAI", "GPT-5.3 Codex"),
    ("claude-opus-5-5", "Anthropic", "Claude Opus 5.5"),
    ("claude-fable-5", "Anthropic", "Claude Fable 5"),
    ("gemini-3.1-pro-preview", "Google", "Gemini 3.1 Pro Preview"),
    ("kimi/kimi-k3", "Moonshot", "kimi/kimi-k3"),
])
def test_display_label(model_id, owner, label):
    assert display_label(model_id, owner) == label


def test_build_orders_featured_first_and_records_site():
    files, order, catalog = sync_models.build(SAMPLE)
    assert order == ["deepseek/deepseek-flash", "gpt-6-astra", "kimi/kimi-k3", "plain-model"]
    assert catalog["models"]["gpt-6-astra"]["site"] == "intl"
    assert model_filename("kimi/kimi-k3") in files
    assert yaml.safe_load(files["_position.yaml"]) == order


def test_fetch_skips_image_models(monkeypatch):
    body = {"data": [{"id": "a", "category": "chat"}, {"id": "gpt-image-2", "category": "image"}]}
    monkeypatch.setattr(sync_models.requests, "get", lambda *a, **k: FakeResp(200, body))
    assert [m["id"] for m in sync_models.fetch("intl")] == ["a"]


def test_packaged_list_is_consistent():
    """打进包里的 YAML、_position.yaml、catalog.json 三者一致，且每个 YAML 都能被 SDK 解析。"""
    llm_dir = ROOT / "models" / "llm"
    order = yaml.safe_load((llm_dir / "_position.yaml").read_text())
    catalog = json.loads((ROOT / "models" / "catalog.json").read_text())["models"]
    files = {p.name for p in llm_dir.glob("*.yaml")} - {"_position.yaml"}
    assert set(order) == set(catalog)
    assert files == {model_filename(m) for m in order}
    for f in files:
        AIModelEntity(**yaml.safe_load((llm_dir / f).read_text()))
    assert {m["site"] for m in catalog.values()} == {"cn", "intl"}


# ---------- 调用 ----------


def make_llm():
    schemas = [AIModelEntity(**model_yaml(m, s)) for s, ms in SAMPLE.items() for m in ms]
    return BumoRouterLargeLanguageModel(schemas)


def sse(*events):
    return [f"data: {json.dumps(e)}" for e in events] + ["data: [DONE]"]


def chunk(text, finish=None):
    return {"id": "1", "object": "chat.completion.chunk", "model": "m",
            "choices": [{"index": 0, "delta": {"content": text} if text else {}, "finish_reason": finish}]}


def test_stream_output_is_concatenated(monkeypatch):
    llm = make_llm()
    monkeypatch.setattr(rc, "load_catalog", lambda: {"deepseek/deepseek-flash": {"site": "cn"}})
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {"deepseek/deepseek-flash": {"site": "cn"}})
    rc._site_cache[rc._key_hash("sk-cn")] = CN

    sent = {}

    def post(url, **kw):
        sent["url"], sent["headers"] = url, kw["headers"]
        sent["body"] = json.loads(kw["data"])
        return FakeResp(200, lines=sse(chunk("Hel"), chunk("lo "), chunk("world"), chunk("", "stop")))

    import dify_plugin.interfaces.model.openai_compatible.llm as oai
    monkeypatch.setattr(oai.requests, "post", post)

    result = llm._invoke(
        "deepseek/deepseek-flash", {"api_key": "sk-cn"}, [UserPromptMessage(content="hi")], {}, stream=True
    )
    text = "".join(c.delta.message.content or "" for c in result)
    assert text == "Hello world"
    assert sent["url"] == f"{CN}/chat/completions"
    assert sent["headers"]["X-Title"] == "Dify"
    assert sent["headers"]["Authorization"] == "Bearer sk-cn"
    assert sent["body"]["model"] == "deepseek/deepseek-flash" and sent["body"]["stream"] is True


def test_unsupported_params_dropped_at_invoke(monkeypatch):
    """应用里开着上游不收的参数（GPT 的温度 / penalty），调用前去掉，不 400。"""
    llm = make_llm()
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {"gpt-6-astra": {"site": "intl", "owned_by": "OpenAI"}})
    rc._site_cache[rc._key_hash("sk-intl")] = INTL
    sent = {}

    def post(url, **kw):
        sent["body"] = json.loads(kw["data"])
        return FakeResp(200, lines=sse(chunk("ok", "stop")))

    import dify_plugin.interfaces.model.openai_compatible.llm as oai
    monkeypatch.setattr(oai.requests, "post", post)
    params = {"presence_penalty": 0.1, "frequency_penalty": 0.1, "temperature": 0.7, "max_tokens": 100}
    list(llm._invoke("gpt-6-astra", {"api_key": "sk-intl"}, [UserPromptMessage(content="hi")], params))
    assert "presence_penalty" not in sent["body"] and "temperature" not in sent["body"]
    assert sent["body"]["max_tokens"] == 100


def test_cn_key_with_intl_model_is_explained(monkeypatch):
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {"gpt-6-astra": {"site": "intl", "owned_by": "OpenAI"}})
    rc._site_cache[rc._key_hash("sk-cn")] = CN
    with pytest.raises(InvokeBadRequestError, match="router.bumo.ai.*router.bumo.cc"):
        make_llm()._invoke("gpt-6-astra", {"api_key": "sk-cn"}, [UserPromptMessage(content="hi")], {})


def test_invalid_key_at_invoke(monkeypatch):
    fake_probe(monkeypatch, {CN: 401, INTL: 401})
    with pytest.raises(InvokeAuthorizationError, match="API Key 无效"):
        make_llm()._invoke("deepseek/deepseek-flash", {"api_key": "sk-x"}, [UserPromptMessage(content="hi")], {})


def test_balance_error_at_invoke_is_translated(monkeypatch):
    import models.llm.llm as llm_mod
    import dify_plugin.interfaces.model.openai_compatible.llm as oai
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {})
    rc._site_cache[rc._key_hash("sk-cn")] = CN
    monkeypatch.setattr(oai.requests, "post", lambda *a, **k: FakeResp(402, {"error": {"message": "Insufficient balance"}}))
    with pytest.raises(InvokeBadRequestError, match="余额不足"):
        make_llm()._invoke("deepseek/deepseek-flash", {"api_key": "sk-cn"}, [UserPromptMessage(content="hi")], {}, stream=False)


# ---------- 新模型（目录里没有）：只填模型名，能力自动查 ----------


def test_customizable_schema_from_live_models(monkeypatch):
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {})
    rc._site_cache[rc._key_hash("sk-cn")] = CN
    live = {"data": [{"id": "glm/glm-9", "category": "chat", "context_length": 500000, "capabilities": ["tools", "vision"]}]}
    monkeypatch.setattr(rc.requests, "get", lambda *a, **k: FakeResp(200, live))
    schema = make_llm().get_customizable_model_schema("glm/glm-9", {"api_key": "sk-cn"})
    assert schema.model_properties[ModelPropertyKey.CONTEXT_SIZE] == 500000
    assert ModelFeature.VISION in schema.features and ModelFeature.MULTI_TOOL_CALL in schema.features


def test_add_unknown_model_is_rejected(monkeypatch):
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {})
    fake_probe(monkeypatch, {CN: 404})
    monkeypatch.setattr(rc.requests, "get", lambda *a, **k: FakeResp(200, {"data": []}))
    with pytest.raises(CredentialsValidateFailedError, match="没有模型 nope"):
        make_llm().validate_credentials("nope", {"api_key": "sk-cn"})


def test_add_catalog_model_with_wrong_site_key_is_rejected(monkeypatch):
    # 国内站 Key + 国际站预置模型：保存时就拦下，别等调用时才报
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {"gpt-6-astra": {"site": "intl"}})
    fake_probe(monkeypatch, {CN: 404})
    with pytest.raises(CredentialsValidateFailedError, match="router.bumo.ai.*router.bumo.cc"):
        make_llm().validate_credentials("gpt-6-astra", {"api_key": "sk-cn"})


def test_add_catalog_model_same_site_ok(monkeypatch):
    import models.llm.llm as llm_mod
    monkeypatch.setattr(llm_mod, "load_catalog", lambda: {"deepseek/deepseek-flash": {"site": "cn"}})
    fake_probe(monkeypatch, {CN: 404})
    make_llm().validate_credentials("deepseek/deepseek-flash", {"api_key": "sk-cn"})

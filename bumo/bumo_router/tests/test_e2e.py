"""
端到端：dify CLI 按 Dify 的方式跑插件包（`dify plugin run`），用真 Key 调真 Router。会产生几分钱的模型费用。

    BUMO_ROUTER_API_KEY=sk-... pytest tests/test_e2e.py -s
    # 可选：BUMO_ROUTER_E2E_MODELS=deepseek/deepseek-flash,kimi/kimi-k3（默认取国内站这两个）
    # 可选：BUMO_ROUTER_ENDPOINT=http://127.0.0.1:8946/v1（连本机 Router，见 tests/integrations-e2e；不填按 Key 自动识别线上站点）
    # 可选：BUMO_ROUTER_POOR_KEY=<余额为 0 的 Key>（验证「余额为 0」的提示）

没设 Key 就跳过。dify CLI 从 https://github.com/langgenius/dify-plugin-daemon/releases 下，放进 PATH 或设 DIFY_CLI_PATH。
"""

import os
from pathlib import Path

import pytest
from pydantic import BaseModel

from dify_plugin.config.integration_config import IntegrationConfig
from dify_plugin.core.entities.plugin.request import (
    ModelActions,
    ModelInvokeLLMRequest,
    ModelValidateProviderCredentialsRequest,
    PluginInvokeType,
)
from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.llm import LLMResultChunk
from dify_plugin.integration.run import PluginRunner

KEY = os.getenv("BUMO_ROUTER_API_KEY", "")
MODELS = os.getenv("BUMO_ROUTER_E2E_MODELS", "deepseek/deepseek-flash,kimi/kimi-k3").split(",")
ENDPOINT = os.getenv("BUMO_ROUTER_ENDPOINT", "")
POOR_KEY = os.getenv("BUMO_ROUTER_POOR_KEY", "")
PLUGIN = str(Path(__file__).resolve().parent.parent)

pytestmark = pytest.mark.skipif(not KEY, reason="BUMO_ROUTER_API_KEY 未设置")


@pytest.fixture(scope="module")
def runner():
    with PluginRunner(config=IntegrationConfig(), plugin_package_path=PLUGIN) as r:
        yield r


class ValidateResult(BaseModel):
    result: bool


def _creds(key):
    return {"api_key": key, "endpoint_url": ENDPOINT} if ENDPOINT else {"api_key": key}


def _validate(runner, key):
    payload = ModelValidateProviderCredentialsRequest(user_id="e2e", provider="bumo_router", credentials=_creds(key))
    return list(
        runner.invoke(
            access_type=PluginInvokeType.Model,
            access_action=ModelActions.ValidateProviderCredentials,
            payload=payload,
            response_type=ValidateResult,
        )
    )


def test_wrong_key_rejected(runner):
    with pytest.raises(Exception, match="API Key 无效"):
        _validate(runner, "sk-definitely-wrong")


@pytest.mark.skipif(not POOR_KEY, reason="BUMO_ROUTER_POOR_KEY 未设置")
def test_zero_balance_key_explained(runner):
    with pytest.raises(Exception, match="余额为 0"):
        _validate(runner, POOR_KEY)


def test_right_key_accepted(runner):
    out = _validate(runner, KEY)
    assert out and out[-1].result is True


def _chat(runner, model, content, tools=None):
    payload = ModelInvokeLLMRequest(
        user_id="e2e",
        provider="bumo_router",
        model_type=ModelType.LLM,
        model=model,
        credentials=_creds(KEY),
        prompt_messages=[{"role": "user", "content": content}],
        stop=None,
        tools=tools,
        stream=True,
        model_parameters={"max_tokens": 1024},
    )
    return list(
        runner.invoke(
            access_type=PluginInvokeType.Model,
            access_action=ModelActions.InvokeLLM,
            payload=payload,
            response_type=LLMResultChunk,
        )
    )


@pytest.mark.parametrize("model", MODELS)
def test_stream_chat(runner, model):
    chunks: list[LLMResultChunk] = _chat(runner, model, "只回复两个字：你好")
    text = "".join(c.delta.message.content or "" for c in chunks if isinstance(c.delta.message.content, str))
    print(f"\n[{model}] {len(chunks)} chunks → {text!r}")
    assert len(chunks) > 1 and text.strip()


def test_tool_call(runner):
    """Dify Agent / 工作流里的工具调用：模型要能回出结构化的 tool_calls。"""
    weather = {
        "name": "get_weather",
        "description": "查询城市天气",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    }
    chunks = _chat(runner, MODELS[0], "北京今天天气怎么样？请调用工具查询。", tools=[weather])
    calls = [t for c in chunks for t in (c.delta.message.tool_calls or [])]
    print(f"\n[{MODELS[0]}] tool_calls → {[(t.function.name, t.function.arguments) for t in calls]}")
    assert any(t.function.name == "get_weather" for t in calls)

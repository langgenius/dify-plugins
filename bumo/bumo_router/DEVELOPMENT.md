# 开发、测试、打包

插件市场展示的是 README.md / readme/README_zh_Hans.md，本文件只给开发者看，打包时由 .difyignore 排除。

## 结构

| 文件 | 作用 |
| --- | --- |
| `provider/bumo_router.yaml` | 凭证表单：只有 API Key 必填，自定义地址可选 |
| `provider/bumo_router.py` | 保存 Key 时校验（按 Key 自动识别国内站 / 国际站，不发真实对话） |
| `models/llm/llm.py` | 调用：继承 Dify 的 OpenAI 兼容实现，补站点地址、来源标识、报错翻译 |
| `models/router_client.py` | 站点识别、`/v1/models` 查询、报错文案 |
| `models/llm/*.yaml`、`models/catalog.json` | 预置模型清单，**由脚本生成，不要手改** |

## 模型清单

Dify 只认插件包里的 YAML 作为预置模型，安装时就定死，所以清单在打包前从 Router 两个站点的 `/v1/models` 生成：

```bash
python scripts/sync_models.py          # 重写清单
python scripts/sync_models.py --check  # 只比对，过期 exit 1
```

包发出去之后 Router 再上新模型，用户在 Dify「添加模型」只填模型名，能力由插件运行时查 `/v1/models` 补齐。

## 测试

```bash
pip install -r requirements.txt pytest
pytest tests/test_plugin.py            # 单测，不连网
```

端到端（`dify plugin run` 按 Dify 的方式跑插件，真调 Router）：

```bash
# 连本机 Router（mock 计费中心，不碰线上，起法见仓库 tests/integrations-e2e/run.mjs）
BUMO_ROUTER_ENDPOINT=http://127.0.0.1:8946/v1 BUMO_ROUTER_API_KEY=sk-... \
BUMO_ROUTER_POOR_KEY=sk-...  BUMO_ROUTER_E2E_MODELS=deepseek/deepseek-flash,qwen/qwen3.8-flash \
pytest tests/test_e2e.py -s
```

`dify plugin run` 会清空环境变量、用全新 uv 缓存直连 pypi.org 装依赖，国内网络常超过 120 秒被杀。
写一个 uv 包装脚本补镜像，再用 `UV_PATH` 指给它：

```sh
#!/bin/sh
export UV_CACHE_DIR=$HOME/.cache/uv UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
exec uv "$@"
```

## 打包

```bash
python scripts/sync_models.py --check && dify plugin package . -o bumo_router-0.0.3.difypkg
```

`dify` CLI 从 https://github.com/langgenius/dify-plugin-daemon/releases 下载。发新版先改 `manifest.yaml` 的 `version` 和 `meta.version`。

# 不墨 Router（Dify 插件）

**一个 Key，用上所有模型。** 通过[不墨 Router](https://router.bumo.cc) 在 Dify 里使用 DeepSeek、Kimi、通义千问、GLM、MiniMax，以及 Claude、GPT、Gemini 等模型——不用逐家装供应商插件、逐家充值，也不用手敲模型名和上下文长度。

## 三步接入

1. 在 Dify 插件市场安装 **不墨 Router**。
2. 到 [router.bumo.cc](https://router.bumo.cc/user/api-keys)（国内站）或 [router.bumo.ai](https://router.bumo.ai/user/api-keys)（国际站）创建 API Key。
3. Dify **设置 → 模型供应商 → 不墨 Router**，粘贴 Key，保存。

完成。插件会自动识别 Key 属于国内站还是国际站，模型直接出现在 Dify 里，上下文长度、工具调用、视觉能力都已填好，不用手敲。

## 模型

| 站点 | 模型 |
| --- | --- |
| 国内站 router.bumo.cc | DeepSeek、Kimi、通义千问、GLM、MiniMax、阶跃星辰、小米 MiMo、腾讯混元 |
| 国际站 router.bumo.ai | Claude、GPT、Gemini |

实时清单见 `https://router.bumo.cc/v1/models` 和 `https://router.bumo.ai/v1/models`。两个站点的 Key 和余额互不通用；选了另一个站点的模型，会提示你去哪个站点创建 Key。

**插件发布之后才上线的新模型？** 点「添加模型」，填模型名（如 `deepseek/deepseek-flash`）和 Key 即可，上下文长度、工具调用、视觉能力会自动从不墨 Router 查询。

## 功能

- 流式输出、工具调用（Agent / 工作流）、支持视觉的模型可直接传图
- 保存时校验 Key，不发真实对话、不扣费
- Key 无效、余额为 0、模型不在当前站点，都有明确的中文提示
- 可选自定义 API 地址（绝大多数情况留空）

## 帮助

- 文档：https://bumo.cc/docs/api
- 控制台与联系方式：https://router.bumo.cc · https://router.bumo.ai
- 源码：https://github.com/langgenius/dify-plugins/tree/main/bumo/bumo_router

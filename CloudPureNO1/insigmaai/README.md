# InsigmaAI 插件（InsigmaAI Plugin for Dify）

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

本插件为 [Dify](https://github.com/langgenius/dify) 平台提供 AI 功能扩展，支持通过本地或自定义模型服务（如 `InsigmaAI`）实现智能推理、文本生成、语音识别、文本嵌入等多种能力。

## 📌 插件信息

- **名称**：insigmaai
- **显示名**：InsigmaAI
- **作者**：[CloudPureNO1](https://github.com/CloudPureNO1)
- **版本**：0.0.1
- **语言**：Python 3.12
- **架构**：amd64 / arm64
- **类型**：Dify Plugin
- **隐私政策**：[查看 PRIVACY.md](./PRIVACY.md)

## 🧩 功能特性

- 支持调用自定义 LLM、TTS、语音识别、文本嵌入等模型服务；
- 集成 `InsigmaAI` 模型接口；
- 支持以下能力：
  - ✅ 大语言模型（LLM）
  - ✅ 文本嵌入（Text Embedding）
  - ✅ 语音转文本（Speech2Text）
  - ✅ 文本转语音（TTS）
  - ✅ 重排序（Rerank）

> ⚠️ 本插件不收集、存储或传输任何用户数据，所有处理均在用户本地或授权服务中完成。

## 📦 使用方式

1. 在 Dify 平台中安装本插件（通过 Dify Marketplace 或手动导入 `.pkg` 文件）；
2. 在工作流中添加 `InsigmaAI` 节点；
3. 配置所需参数（如模型地址、API Key 等）；
4. 连接前后节点，运行流程。

## 📁 目录结构
```
insigma_ai/
├── manifest.yaml              # 插件元数据（必选）
├── privacy.md                 # 隐私政策（必选）
├── README.md                  # 插件说明（推荐）
├── icon.png                   # 图标文件（建议使用 PNG 格式）
├── main.py                    # 插件入口文件（entrypoint: main）
├── models/
│   └── llm/
│       └── llm.py             # LLM 核心逻辑
└── provider/
    ├── insigma_ai.py           # 模型提供方实现类
    └── insigma_ai.yaml         # 模型配置定义（供 Dify 加载）
```

## 🔐 隐私与安全

本插件严格遵守 Dify 插件隐私准则：

- ❌ 不收集用户个人信息；
- 🚫 不包含追踪或遥测代码；
- 🔑 API 密钥由用户在 Dify 中配置，插件无法读取；
- 🌐 所有数据处理在用户控制的环境中进行。

详情请参阅：[PRIVACY.md](./PRIVACY.md)

## 📎 开发与打包

如需修改本插件，请使用 参考 [Dify插件开发：HelloWord 指南](https://docs.dify.ai/plugin-dev-zh/0211-getting-started-dify-tool) 中的【**7.打包插件**】

## 📬 联系方式
GitHub: [CloudPureNO1](https://github.com/CloudPureNO1)

Email: [CloudPure@163.com](CloudPure@163.com)

欢迎提交 Issue 或 PR！

## 许可证
本插件开源，遵循 MIT License（如适用）。


 
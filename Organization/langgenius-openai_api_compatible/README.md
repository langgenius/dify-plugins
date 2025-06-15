# OpenAI-API-compatible 插件增强版

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dify](https://img.shields.io/badge/Dify-Plugin-brightgreen)](https://dify.ai/)
[![Base Version](https://img.shields.io/badge/Base%20Version-0.0.16-blue)](https://github.com/langgenius/dify-plugins)

> 基于官方 0.0.16 版本增强，添加 `thinking_budget` 参数支持，优化通义千问等支持思考模式的大语言模型体验。

## 🚀 功能特性

- ✅ 完全兼容官方 0.0.16 版本所有功能
- ✨ 新增 `thinking_budget` 参数支持，控制思考过程的最大 token 数
- 🔧 增强 `enable_thinking` 参数，优化思考模式体验
- 🎯 特别适配通义千问(Qwen)等支持思考模式的大语言模型
- 🛠️ 支持通过 Dify 界面直观配置参数

## 🔧 安装方法

### 通过 GitHub 仓库安装

1. 在 Dify 中进入「插件」页面
2. 点击「安装插件」
3. 选择「通过 GitHub 仓库安装」
4. 输入仓库地址：
   ```
   https://github.com/你的用户名/langgenius-openai_api_compatible_0.0.16_fix
   ```
5. 点击「安装」

### 通过本地文件安装

1. 克隆本仓库：
   ```bash
   git clone https://github.com/你的用户名/langgenius-openai_api_compatible_0.0.16_fix.git
   cd langgenius-openai_api_compatible_0.0.16_fix
   ```
2. 打包插件：
   ```bash
   dify plugin package .
   ```
3. 在 Dify 中通过「上传插件」安装生成的 `.difypkg` 文件

## ⚙️ 参数说明

### 基础参数

- **API Key**: 您的 OpenAI 兼容 API 密钥
- **API Base URL**: API 基础地址（例如：`https://api.openai.com/v1`）
- **Model Name**: 模型名称

### 高级参数

- **Enable Thinking Mode** (`enable_thinking`): 
  - 类型: 布尔值
  - 默认值: 关闭
  - 说明: 是否启用思考模式，适用于支持思考模式的模型（如 Qwen3）

- **Thinking Budget** (`thinking_budget`):
  - 类型: 整数
  - 范围: 0-1000
  - 默认值: 200
  - 说明: 思考过程使用的最大 token 数，控制思考深度

## 🎯 使用示例

### 1. 在 Dify 中配置

1. 创建新的模型提供者，选择 "OpenAI-API-compatible"
2. 填写 API 密钥和基础 URL
3. 在高级参数中：
   - 启用 "Thinking mode"
   - 设置 "Thinking Budget" 为期望的值（如 300）
4. 保存配置

### 2. 在应用中使用

在 Dify 应用中，选择你刚刚配置的模型，即可享受增强的思考模式功能。

## 🔄 更新日志

### v0.0.17 (2025-06-15)
- 新增 `thinking_budget` 参数支持
- 优化 `enable_thinking` 参数处理
- 更新文档和说明

## 📝 注意事项

1. 本插件需要后端模型支持思考模式功能
2. 较大的 `thinking_budget` 值会增加响应时间和 token 消耗
3. 建议根据实际需求调整 `thinking_budget` 值

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

## 📜 许可证

MIT License

## 🙏 致谢

- 基于 [langgenius/openai_api_compatible](https://github.com/langgenius/dify-plugins) 0.0.16 版本开发
- 特别感谢 Dify 团队提供优秀的 AI 应用开发平台

---

<p align="center">
  <a href="https://dify.ai/" target="_blank">
    <img src="https://dify.ai/favicon.ico" alt="Dify" width="30">
  </a>
  <br>
  <sub>Built with ❤️ for Dify</sub>
</p>

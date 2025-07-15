# smartsearch

## 基本信息
- **作者 (Author):** cloudswayai  
- **版本 (Version):** 0.0.1  
- **类型 (Type):** tool  

## 插件描述 (Description)
`smartsearch` 是一款基于 Dify 生态的智能搜索工具，通过集成 Cloudsway 搜索 API，为大模型应用提供高效、可控的网页全文检索能力。支持多语言过滤、内容安全级别调整及结构化结果返回，适用于深度内容分析、事实核查、多源信息聚合等场景。

## 核心功能 (Key Features)
- 精准网页搜索：支持关键词检索，可配置结果数量、分页偏移、语言过滤及安全级别
- 全文内容提取：返回完整页面内容（支持 HTML/MARKDOWN 格式），满足深度分析需求
- 结构化输出：结果以 JSON 格式返回，包含标题、URL、发布时间、摘要及全文内容，便于解析和下游处理
- Dify 无缝集成：符合 Dify 插件规范，可直接在 Dify 应用、工作流中调用

## 使用指南 (Usage Guide)

### 1. 前置准备 (Prerequisites)
- 需获取 Cloudsway 搜索 API 密钥（`SERVER_KEY`），格式为 `endpoint-accesskey`
- 获取方式：登录 [Cloudsway 控制台](https://www.cloudsway.ai) 或联系 `info@cloudsway.ai` 申请

### 2. 配置步骤 (Configuration Steps)
在 Dify 中安装插件后，在「插件设置」中配置环境变量：  
```bash
SERVER_KEY=你的密钥 
```

### 3. 工具调用参数 (Tool Parameters)
| 参数名        | 类型   | 是否必填 | 默认值     | 说明                                                                 |  
|---------------|--------|----------|------------|----------------------------------------------------------------------|  
| `query`       | string | 是       | -          | 搜索关键词或问题（如："2024 年机器学习最新进展"）                     |  
| `count`       | number | 否       | 10         | 返回结果数量（1-50，建议 3-10）                                      |  
| `offset`      | number | 否       | 0          | 分页偏移量（如：offset=10 表示从第 11 条结果开始）                   |  
| `setLang`     | string | 否       | "en"       | 语言过滤（如 `zh-CN`、`en`、`ja` 等）                                |  
| `safeSearch`  | string | 否       | "Strict"   | 内容安全级别：`Strict`、`Moderate`、`Off`                            |  

### 4. 调用示例 (Example)
输入参数：  
```json
{
  "query": "2024 全球人工智能峰会成果",
  "count": 5,
  "setLang": "zh-CN",
  "contentType": "MARKDOWN"
}
```
返回结果（简化版）：
```json
{
  "results": [
    {
      "title": "2024 人工智能峰会总结",
      "url": "https://example.com/summit-2024",
      "content": "# 2024 人工智能峰会...",
      "dateLastCrawled": "2025-07-01T08:00:00Z"
    }
  ]
}
```

## 隐私政策 (Privacy Policy)
- **收集的数据类型**：本插件仅收集用户输入的搜索关键词（`query`），用于实时调用 Cloudsway 搜索 API。插件不收集姓名、邮箱、设备信息等任何可识别个人身份的数据。
- **数据用途**：所有输入仅用于即时搜索请求，不做持久化存储、分析或其他用途。
- **第三方处理**：搜索请求由 Cloudsway API 实时处理，数据仅在请求过程中传递给 Cloudsway，不与其他第三方共享。
- **安全措施**：API 密钥仅用于身份验证，不会被插件存储或泄露。所有数据传输均通过 HTTPS 加密。
- **用户权利**：用户可随时删除或更换 API 密钥，插件不保存任何历史数据。
- **支持与反馈**：如有隐私相关问题，可通过 support@cloudsway.ai 联系我们。

## 许可证 (License)
本项目基于 MIT 许可证开源，详见 LICENSE。

## 常见问题 (FAQ)
**Q：调用失败？**  
A：检查 SERVER_KEY 格式（需包含 endpoint 和 accesskey），或确认密钥有效（登录 Cloudsway 控制台验证）。

**Q：结果为空？**  
A：尝试调整 safeSearch 为 Moderate，或优化 query 关键词。

**Q：支持哪些语言？**  
A：覆盖 zh-CN（中文）、en（英文）、ja（日文）、ko（韩文）、fr（法文）等 20+ 语言，具体见参数 setLang 说明。

如需更多支持，可提交 Issue 至 GitHub 仓库 或联系 support@cloudsway.ai。
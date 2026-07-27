# PixSEO - AI 商品图片SEO优化

PixSEO 是一个 AI 驱动的跨境电商图片 SEO 优化引擎。外部 API 负责去背景和 WebP 压缩，Alt 文本、Schema 和 Listing 由 Agent 本地 LLM 生成。

## 功能

- **AI 去背景** - 智能识别并移除商品图片背景（通过 Photoroom API）
- **WebP 压缩** - 自动压缩为 WebP 格式（减少 30-80% 文件体积）
- **本地 Alt 文本评分** - 四维度评估 Alt 文本 SEO 质量（长度、关键词、自然语言、描述性）
- **隐私透明** - 外部 API 仅处理图片去背景和压缩，不上传任何商品文字信息

## 工具

| 工具 | 说明 |
|------|------|
| **商品图片处理** | 单张商品图片的去背景 + WebP 压缩 |
| **批量处理图片** | 批量处理多张商品图片，支持 URL 或 Base64 输入 |
| **查询 API 用量** | 查看当前 API Key 使用统计和剩余配额 |

## 安装

### 前置条件

- Python 3.12+
- PixSEO API Key（在 [https://api.hzhdmn.icu](https://api.hzhdmn.icu) 注册获取）

### 设置

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 Dify 调试凭据
python -m main
```

## 配置

需要 PixSEO API Key。在 [https://api.hzhdmn.icu](https://api.hzhdmn.icu) 注册获取。

## 定价

PixSEO 提供 7 档方案，从免费到企业级。详见 [定价页面](https://api.hzhdmn.icu)。

## 支持

- 文档: [https://api.hzhdmn.icu/api-docs](https://api.hzhdmn.icu/api-docs)
- 邮箱: 15997885002@163.com
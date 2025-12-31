# AI4S Semantic Scholar

基于 [ai4scholar.net](https://ai4scholar.net) API 的学术论文搜索插件，为 Dify 平台提供强大的学术搜索能力。

**作者**: [ai4scholar](https://ai4scholar.net)  
**项目地址**: [dify-plugin-ai4s-semantic-scholar](https://github.com/literaf/dify-plugin-ai4s-semantic-scholar)

[English Documentation](./README.md) | [中文文档](./README_ZH.md)

---

## 概述

- **插件类型**: 工具插件 (Python)
- **包含工具**: 11 个 (论文搜索 / 论文详情 / 论文分析 / 作者搜索)
- **输出**: text (Markdown 格式)

本插件是 Semantic Scholar API 的包装层，通过 ai4scholar.net 代理访问，提供更稳定的服务和统一的积分计费。

---

## 配置 (Provider Credentials)

在 Dify 中安装插件后，配置以下凭证：

| 凭证 | 必填 | 说明 |
|-----|------|------|
| `api_key` | ✅ 是 | 你的 ai4scholar.net API Key |

**获取 API Key**: 访问 [ai4scholar.net](https://ai4scholar.net) 注册并获取

---

## 工具

### 论文搜索

| 工具名称 | 接口 | 说明 |
|---------|------|------|
| **语义搜索** (`semantic_search`) | `GET /graph/v1/paper/search` | 使用自然语言按相关性搜索论文 |
| **标题搜索** (`title_search`) | `GET /graph/v1/paper/search/match` | 通过精确或部分标题搜索论文 |
| **批量搜索** (`bulk_search`) | `GET /graph/v1/paper/search/bulk` | 一次执行多个搜索查询 |

### 论文详情

| 工具名称 | 接口 | 说明 |
|---------|------|------|
| **论文详情** (`paper_detail`) | `GET /graph/v1/paper/{paper_id}` | 获取单篇论文详细信息 |
| **多篇论文详情** (`multiple_papers_detail`) | `POST /graph/v1/paper/batch` | 批量获取多篇论文信息 |

### 论文分析

| 工具名称 | 接口 | 说明 |
|---------|------|------|
| **论文推荐** (`paper_recommendations`) | `GET /recommendations/v1/papers` | 基于给定论文获取推荐论文 |
| **论文引用** (`paper_citations`) | `GET /graph/v1/paper/{paper_id}/citations` | 获取引用该论文的论文列表 |
| **论文参考文献** (`paper_references`) | `GET /graph/v1/paper/{paper_id}/references` | 获取论文的参考文献列表 |

### 作者搜索

| 工具名称 | 接口 | 说明 |
|---------|------|------|
| **作者搜索** (`author_search`) | `GET /graph/v1/author/search` | 搜索作者并获取发表统计 |
| **作者详情** (`author_detail`) | `GET /graph/v1/author/{author_id}` | 获取作者详细信息（h-index、引用数等） |
| **作者论文** (`author_papers`) | `GET /graph/v1/author/{author_id}/papers` | 获取作者发表的论文列表 |

---

## 参数说明

### 语义搜索 (semantic_search)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 自然语言搜索查询 |
| `limit` | number | ❌ | 返回数量 (1-100, 默认 10) |
| `year` | string | ❌ | 年份筛选 (如 "2020", "2020-2024") |
| `fields_of_study` | string | ❌ | 研究领域筛选 |
| `open_access_only` | boolean | ❌ | 仅返回开放获取论文 |

### 论文详情 (paper_detail)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `paper_id` | string | ✅ | 论文 ID (支持 S2 ID, DOI, arXiv ID) |
| `include_citations` | boolean | ❌ | 包含引用论文 |
| `include_references` | boolean | ❌ | 包含参考文献 |

### 论文推荐 / 引用 / 参考文献

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `paper_id` | string | ✅ | 论文 ID (支持 S2 ID, DOI, arXiv ID) |
| `limit` | number | ❌ | 返回数量 (默认 10-20) |

### 作者搜索 (author_search)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 作者姓名 |
| `limit` | number | ❌ | 返回数量 (1-20, 默认 5) |

### 作者详情 / 作者论文

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `author_id` | string | ✅ | Semantic Scholar 作者 ID |
| `limit` | number | ❌ | 返回数量 (仅 author_papers) |

---

## 积分消耗

每次 API 调用消耗 1 积分，批量操作按实际调用次数计算。

如需更多积分，请访问 [ai4scholar.net](https://ai4scholar.net) 充值。

---

## 相关链接

- [ai4scholar.net](https://ai4scholar.net) - API 服务
- [Semantic Scholar API 文档](https://api.semanticscholar.org/api-docs/)
- [Dify 插件开发文档](https://docs.dify.ai/zh/use-dify/workspace/plugins)

---

## 联系支持

- **GitHub Issues**: [提交问题或建议](https://github.com/literaf/dify-plugin-ai4s-semantic-scholar/issues)
- **微信**: literaf
- **网站**: [ai4scholar.net](https://ai4scholar.net)

---

## 许可证

MIT License

# AI4S Semantic Scholar

Academic paper search plugin powered by [ai4scholar.net](https://ai4scholar.net) API for Dify platform.

**Author**: [ai4scholar](https://ai4scholar.net)  
**Repository**: [dify-plugin-ai4s-semantic-scholar](https://github.com/literaf/dify-plugin-ai4s-semantic-scholar)

[English Documentation](./README.md) | [中文文档](./README_ZH.md)

---

## Overview

- **Plugin Type**: Tool Plugin (Python)
- **Tools**: 11 tools (Paper Search / Paper Details / Paper Analysis / Author Search)
- **Output**: text (Markdown format)

This plugin wraps the Semantic Scholar API via ai4scholar.net proxy, providing stable service with unified credit billing.

---

## Configuration (Provider Credentials)

After installing the plugin in Dify, configure the following credentials:

| Credential | Required | Description |
|-----------|----------|-------------|
| `api_key` | ✅ Yes | Your ai4scholar.net API Key |

**Get API Key**: Visit [ai4scholar.net](https://ai4scholar.net) to register and obtain your API key.

---

## Tools

### Paper Search

| Tool | API Endpoint | Description |
|------|-------------|-------------|
| **Semantic Search** (`semantic_search`) | `GET /graph/v1/paper/search` | Search papers by relevance using natural language |
| **Title Search** (`title_search`) | `GET /graph/v1/paper/search/match` | Search papers by exact or partial title |
| **Bulk Search** (`bulk_search`) | `GET /graph/v1/paper/search/bulk` | Execute multiple search queries at once |

### Paper Details

| Tool | API Endpoint | Description |
|------|-------------|-------------|
| **Paper Detail** (`paper_detail`) | `GET /graph/v1/paper/{paper_id}` | Get detailed information for a single paper |
| **Multiple Papers Detail** (`multiple_papers_detail`) | `POST /graph/v1/paper/batch` | Get details for multiple papers at once |

### Paper Analysis

| Tool | API Endpoint | Description |
|------|-------------|-------------|
| **Paper Recommendations** (`paper_recommendations`) | `GET /recommendations/v1/papers` | Get recommended papers based on a given paper |
| **Paper Citations** (`paper_citations`) | `GET /graph/v1/paper/{paper_id}/citations` | Get papers that cite the given paper |
| **Paper References** (`paper_references`) | `GET /graph/v1/paper/{paper_id}/references` | Get reference papers of the given paper |

### Author Search

| Tool | API Endpoint | Description |
|------|-------------|-------------|
| **Author Search** (`author_search`) | `GET /graph/v1/author/search` | Search authors and get publication statistics |
| **Author Detail** (`author_detail`) | `GET /graph/v1/author/{author_id}` | Get author details (h-index, citation count, etc.) |
| **Author Papers** (`author_papers`) | `GET /graph/v1/author/{author_id}/papers` | Get papers published by an author |

---

## Parameters

### Semantic Search

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Natural language search query |
| `limit` | number | ❌ | Number of results (1-100, default 10) |
| `year` | string | ❌ | Year filter (e.g., "2020", "2020-2024") |
| `fields_of_study` | string | ❌ | Field of study filter |
| `open_access_only` | boolean | ❌ | Only return open access papers |

### Paper Detail

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paper_id` | string | ✅ | Paper ID (supports S2 ID, DOI, arXiv ID) |
| `include_citations` | boolean | ❌ | Include citing papers |
| `include_references` | boolean | ❌ | Include reference papers |

### Paper Recommendations / Citations / References

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paper_id` | string | ✅ | Paper ID (supports S2 ID, DOI, arXiv ID) |
| `limit` | number | ❌ | Number of results (default 10-20) |

### Author Search

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Author name |
| `limit` | number | ❌ | Number of results (1-20, default 5) |

### Author Detail / Author Papers

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `author_id` | string | ✅ | Semantic Scholar author ID |
| `limit` | number | ❌ | Number of results (for author_papers only) |

---

## Credits

Each API call consumes 1 credit. Batch operations are charged per actual API call.

To get more credits, visit [ai4scholar.net](https://ai4scholar.net).

---

## Links

- [ai4scholar.net](https://ai4scholar.net) - API Service
- [Semantic Scholar API Docs](https://api.semanticscholar.org/api-docs/)
- [Dify Plugin Documentation](https://docs.dify.ai/)

---

## Support

- **GitHub Issues**: [Report a bug or request a feature](https://github.com/literaf/dify-plugin-ai4s-semantic-scholar/issues)
- **WeChat**: literaf
- **Website**: [ai4scholar.net](https://ai4scholar.net)

---

## License

MIT License

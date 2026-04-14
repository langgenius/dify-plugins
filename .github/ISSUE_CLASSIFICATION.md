# Issue Classification — dify-plugins

> **Purpose:** Categorize and deduplicate existing open issues to improve triage and prioritization.
>
> **Date:** 2026-04-14

---

## Duplicate Groups

The following issues are duplicates. The **newest** issue in each group should remain open; all others should be closed with a comment linking to the kept issue.

| Group | Keep Open | Close as Duplicate |
|---|---|---|
| Parse Document OCR | #2102 | #2035 |
| Security Scanning for Plugins | #2163 | #2160 |
| BookStack Integration | #1322 | #693 |
| vLLM Plugin Improvements | #893 | #766 |

---

## Categories

### 🔌 Plugin Requests — New Model Providers

| Issue | Title |
|---|---|
| #2265 | openclaw (OpenAI-compatible) |
| #1966 | z.ai LLM |
| #914 | GitHub Copilot Model Provider |
| #860 | Perplexity Model Provider |
| #834 | Compshare (UCloud GPU) |
| #656 | Gemini Audio Generation (TTS/STT) |
| #632 | Black Forest Labs (Flux image gen) |

### 🔧 Plugin Requests — New Tools / Integrations

| Issue | Title |
|---|---|
| #2225 | db_tools |
| #2185 | mcp-playwright |
| #2182 | API OTA |
| #2159 | Streaming Agent Strategy with MCP |
| #2158 | Pangolin Amazon Keyword Scraper |
| #2042 | Long-term Memory Assistant |
| #1995 | Pinchwork (agent marketplace) |
| #1820 | Jira Plugin |
| #1781 | GPTProto Tools (multi-model) |
| #1747 | Chatwoot messaging plugin |
| #1691 | File Upload (SFTP) |
| #1619 | TOON format converter |
| #1468 | Long Text Content Extractor |
| #1460 | MCP DataSource Plugin |
| #1322 | BookStack Workflow Automation |
| #1320 | Eunoia Platform |
| #1209 | xgboost and SHAP |
| #1206 | Google Sheets & Google Docs |
| #1201 | Pipedream |
| #994 | LLM Memory Modification |
| #947 | Kling video generation |
| #890 | Google Map (Places API) |
| #883 | Feishu feature parity with Coze |
| #690 | LINEWORKS messaging |
| #684 | Brighton Plugin |
| #645 | gitea plugin |
| #628 | Google Cloud Storage / AWS S3 |
| #599 | minimax TTS (or generic TTS) |
| #560 | Pagerduty |
| #547 | Docling Document Processing |
| #546 | GLPI ServiceDesk |

### 📄 Plugin Requests — Document / OCR

| Issue | Title | Note |
|---|---|---|
| #2102 | parse document OCR | keep |
| #2035 | parse document OCR | **duplicate of #2102** |

### 🛡️ Security Scanning

| Issue | Title | Note |
|---|---|---|
| #2163 | Security scanning suggestion | keep |
| #2160 | Security scanning proposal | **duplicate of #2163** |

### 🐛 Bug Reports

| Issue | Title |
|---|---|
| #1980 | volcengine embedding model 500 error |
| #1969 | GPT-4.1-mini missing "Streaming" feature toggle |
| #1960 | xAI Grok web search deprecated API |
| #1931 | slack bot plugin install failure |
| #1391 | feishu_base plugin bug |
| #1252 | neo4j_query DateTime type error |
| #1216 | Mistral OCR URL error |
| #757 | Confluence plugin missing username field (self-hosted) |
| #730 | GPUSTACK qwen3-235B thinking switch bug |
| #679 | Firecrawl extract tool agent node issue |
| #660 | Agora plugin 404 error |
| #631 | Tags not displaying in manifest |
| #624 | Anthropic plugin reinstall error |
| #623 | OpenAI-API-compatible Qwen3 credential validation error |
| #502 | agent strategy parse error |
| #501 | alicloud connection error |
| #471 | VLLM/Xinference GPU memory overflow (multi-image) |
| #355 | OpenAI gpt-4.1 error |
| #312 | Gemini 0.1.3 video timeout |
| #293 | dify plugin packaging failure |
| #96 | Model Factory display issue |

### ✨ Feature Requests / Improvements on Existing Plugins

| Issue | Title |
|---|---|
| #2063 | gitlab plugin — add issue management features |
| #1857 | Tongyi plugin — custom input header |
| #1010 | OpenAI-API-compatible — custom per-token pricing |
| #893 | vLLM plugin — multi-model on separate GPUs |
| #315 | google_sheets — batchInsert mode |
| #265 | Xinference — add lora_name parameter |

### ❓ Other / Unclear

| Issue | Title | Note |
|---|---|---|
| #2180 | Dog Check Pixel | appears to be a test/spam issue |
| #2053 | Tavily | **⚠️ may contain an API key in the title — consider closing and rotating the key** |
| #1236 | WaterCrawl data source v2 support | |
| #959 | Dropbox access token format | support question |
| #721 | aippt privatization deployment | |
| #425 | Licensing clarification for contributor plugins | |

---

## Recommended Labels

| Label | Color | Issues |
|---|---|---|
| `plugin-request` | `#0075ca` | All issues in "New Model Providers", "New Tools / Integrations", "Document / OCR" sections |
| `bug` | `#d73a4a` | All issues in "Bug Reports" section |
| `feature-request` | `#a2eeef` | All issues in "Feature Requests / Improvements" section |
| `duplicate` | `#cfd3d7` | #2035, #2160, #693, #766 |
| `security` | `#e4e669` | #2163, #2160 |
| `question` | `#d876e3` | #959, #425 |

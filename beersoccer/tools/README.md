# Mem0 Dify Plugin v0.1.3

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://dify.ai)
[![Mem0 AI](https://img.shields.io/badge/Mem0-AI-green)](https://mem0.ai)

A comprehensive Dify plugin that integrates [Mem0 AI](https://mem0.ai)'s intelligent memory layer, providing **Local-only** tools with a unified client for self-hosted setups.

---

## 🌟 Features

### Complete Memory Management (8 Tools)
- ✅ **Add Memory** - Intelligently add, update, or delete memories based on user interactions
- ✅ **Search Memory** - Search with advanced filters (AND/OR logic) and top_k limiting
- ✅ **Get All Memories** - List memories with pagination
- ✅ **Get Memory** - Fetch specific memory details
- ✅ **Update Memory** - Modify existing memories
- ✅ **Delete Memory** - Remove individual memories
- ✅ **Delete All Memories** - Batch delete with filters
- ✅ **Get Memory History** - View change history

### Advanced Capabilities
- 🖥️ **Local Mode Only** - Run with Local Mem0 (JSON-based config)
- 🧱 **Simplified Local Config** - 5 JSON blocks: LLM, Embedder, Vector DB, Graph DB (optional), Reranker (optional)
- 🎯 **Entity Scoping** - user_id (required for add), agent_id, run_id
- 📊 **Metadata System** - Custom JSON metadata for rich context
- 🔍 **Filters** - JSON filters supported by Mem0 local mode
- 🌍 **Internationalized** - 4 languages (en/zh/pt/ja)
- ⚙️ **Async Mode Switch** - `async_mode` is enabled by default; Write ops (Add/Update/Delete) are non-blocking in async mode, Read ops (Search/Get) always wait; in sync mode all operations block until completion.

### What's New (v0.1.3)
- **Unified Logging Configuration**: Implemented centralized logging using Dify's official plugin logger handler to ensure all logs are properly output to the Dify plugin container for better debugging and monitoring.
- **Database Connection Pool Optimization**: Added automatic connection pool settings for pgvector (min: 10, max: 40) to align with concurrent operation limits, ensuring sufficient database connections for high-concurrency scenarios.
- **PGVector Configuration Enhancement**: Optimized pgvector configuration handling according to Mem0 official documentation, properly supporting parameter priority (connection_pool > connection_string > individual parameters) and automatically building connection strings from discrete parameters.
- **Constant Naming Optimization**: Renamed `MAX_CONCURRENT_MEM_ADDS` to `MAX_CONCURRENT_MEMORY_OPERATIONS` (default: 40) to accurately reflect that it controls concurrency for all async memory operations, not just add operations.

### Previous Updates (v0.1.2)
- **Configurable Timeout Parameters**: All read operations (Search/Get/Get_All/History) now support user-configurable timeout values through the Dify plugin configuration interface. Timeout parameters are set as manual input fields (not exposed to LLM), allowing users to customize timeout behavior per tool based on their specific needs.
- **Optimized Default Timeouts**: Reduced default timeout values for better responsiveness - all read operations now default to 30 seconds (previously 60s for Search/Get_All), and `MAX_REQUEST_TIMEOUT` reduced to 60 seconds (from 120s).
- **Code Quality**: Added missing module and class docstrings, fixed formatting issues to comply with Python best practices.

### Previous Updates (v0.1.1)
- **Timeout & Service Degradation**: Added comprehensive timeout mechanisms for all async read operations (Search/Get/Get_All/History) with graceful service degradation. When operations timeout or encounter errors, the plugin logs the event and returns default/empty results to ensure Dify workflow continuity.
- **Robust Error Handling**: Enhanced exception handling across all tools to catch all error types (network errors, connection failures, etc.), ensuring workflows continue even when individual tools fail.
- **Resource Management**: Improved background task cancellation on timeout to prevent resource leaks and hanging tasks.
- **Production Stability**: Fixed production issues where tools would hang indefinitely, ensuring reliable operation in production environments.

### Previous Updates (v0.1.0)
- **Smart Memory Management**: `add_memory` tool description updated to reflect its ability to intelligently add, update, or delete memories based on context.
- **Robust Error Handling**: Enhanced `get_memory`, `update_memory`, and `delete_memory` to gracefully handle non-existent memories and race conditions with clear error messages instead of crashes.
- **Bug Fixes**: Fixed `get_all_memories` returning empty results by correctly parsing Mem0's dictionary response format.
- **Documentation**: Added important notes about `delete_all` index reset warnings and vector store connection details.

---

## 🚀 Quick Start

### Installation

Follow the official Dify plugin installation guide:
1. **In Dify Dashboard**
   - Go to `Settings` → `Plugins`
   - Click `Install from GitHub` or upload the plugin package
   - Enter your repository URL or select the `.difypkg` file
   - Click `Install`

### Configuration

After installation, configure the plugin in the following order:

#### Step 1: Choose Operation Mode

First, select the operation mode:

- **Async Mode** (Recommended for Production)
  - Set `async_mode` to `true`
  - Supports high concurrency
  - Write operations (Add/Update/Delete) are non-blocking and return immediately
  - Read operations (Search/Get) wait for results with timeout protection
  - Best for production environments with high traffic

- **Sync Mode** (Recommended for Testing)
  - Set `async_mode` to `false`
  - All operations block until completion
  - You can see the actual results of each memory operation immediately
  - Best for testing and debugging
  - **Note**: Sync mode has no timeout protection. If timeout protection is needed, use `async_mode=true`

#### Step 2: Configure Models and Databases

Configure the following JSON blocks in plugin settings. For detailed configuration options and supported providers, refer to the [Mem0 Official Configuration Documentation](https://docs.mem0.ai/open-source/configuration).

**Required:**
- `local_llm_json` - LLM provider configuration
- `local_embedder_json` - Embedding model configuration
- `local_vector_db_json` - Vector database configuration

**Optional:**
- `local_graph_db_json` - Graph database configuration (e.g., Neo4j)
- `local_reranker_json` - Reranker configuration

See the [Configuration Examples](#-configuration-examples) section below for basic JSON examples.

### Start Using

Once configured, all 8 tools are available in your workflows!

---

## 📖 Usage Examples

### Basic Usage

#### Add a Memory (user_id required)
```json
{
  "user": "I love Italian food",
  "assistant": "Great! I'll remember that.",
  "user_id": "alex"
}
```

#### Search Memories
```json
{
  "query": "What food does alex like?",
  "user_id": "alex",
  "top_k": 5
}
```

### Add Memory with Metadata
```json
{
  "user": "I prefer morning meetings",
  "assistant": "Noted!",
  "user_id": "alex",
  "agent_id": "scheduler",
  "metadata": "{\"type\": \"preference\", \"priority\": \"high\"}"
}
```

### Search with Filters (local mode)
```json
{
  "query": "user preferences",
  "filters": "{\"AND\": [{\"user_id\": \"alex\"}, {\"agent_id\": \"scheduler\"}]}"
}
```

#### Get All Memories for an Agent
```json
{
  "agent_id": "travel_assistant",
  "limit": 50
}
```

---

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `add_memory` | Add new memories (user_id required) |
| `search_memory` | Search with filters and top_k |
| `get_all_memories` | List all memories |
| `get_memory` | Get specific memory |
| `update_memory` | Update memory content |
| `delete_memory` | Delete single memory |
| `delete_all_memories` | Batch delete memories |
| `get_memory_history` | View change history |

---

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Detailed changelog and examples
- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[BUGFIX.md](BUGFIX.md)** - Known issues and fixes
- **[Mem0 Official Docs](https://docs.mem0.ai)** - Full API documentation

---

## 🎯 Use Cases

### Personal Assistant
```python
# Remember user preferences
add_memory("I prefer morning meetings", user_id="john")
add_memory("I'm vegetarian", user_id="john")

# Query preferences
search("when does john prefer meetings?", user_id="john")
```

### Customer Support
```python
# Track interactions
add_memory("Customer reported login issue", user_id="customer_123")

# Retrieve context
search("previous issues", user_id="customer_123")
```

### Multi-Agent Systems
```python
# Agent-specific memories
add_memory("User likes Italian food", agent_id="food_agent")
add_memory("User prefers Rome", agent_id="travel_agent")

# Search across agents
search(
    "user preferences",
    filters='{"OR": [{"agent_id": "food_agent"}, {"agent_id": "travel_agent"}]}'
)
```

---

## 🔧 Configuration Examples

> **📚 Reference**: For detailed configuration options and supported providers, please refer to the [Mem0 Official Configuration Documentation](https://docs.mem0.ai/open-source/configuration).

### Operation Mode

Set `async_mode` in plugin credentials:
- `true` (default) - Async mode, recommended for production
- `false` - Sync mode, recommended for testing

### LLM Configuration (`local_llm_json`)

```json
{
  "provider": "azure_openai",
  "config": {
    "model": "your-deployment-name",
    "temperature": 0.1,
    "max_tokens": 256,
    "azure_kwargs": {
      "azure_deployment": "your-deployment-name",
      "api_version": "version-to-use",
      "azure_endpoint": "your-api-base-url",
      "api_key": "your-api-key",
      "default_headers": {
        "CustomHeader": "your-custom-header"
      }
    }
  }
}
```

### Embedder Configuration (`local_embedder_json`)

```json
{
  "provider": "azure_openai",
  "config": {
    "model": "your-deployment-name",
    "azure_kwargs": {
      "api_version": "version-to-use",
      "azure_deployment": "your-deployment-name",
      "azure_endpoint": "your-api-base-url",
      "api_key": "your-api-key",
      "default_headers": {
        "CustomHeader": "your-custom-header"
      }
    }
  }
}
```

### Vector Store Configuration (`local_vector_db_json`)

```json
{
  "provider": "pgvector",
  "config": {
    "dbname": "your-vector-db-name",
    "user": "your-vector-db-user",
    "password": "your-vector-db-password",
    "host": "your-vector-db-host",
    "port": "your-vector-db-port",
    "sslmode": "require or disable"
  }
}
```

### Graph Store Configuration (`local_graph_db_json`) - Optional

```json
{
  "provider": "neo4j",
  "config": {
    "url": "neo4j+s://<HOST>",
    "username": "your-graph-db-user",
    "password": "your-graph-db-password"
  }
}
```

### Reranker Configuration (`local_reranker_json`) - Optional

```json
{
  "provider": "cohere",
  "config": {
    "model": "your-model-name",
    "api_key": "your-cohere-api-key",
    "top_k": 5
  }
}
```

### Configurable Timeout (v0.1.2+)

All read operations (Search/Get/Get_All/History) support user-configurable timeout values:
- Timeout parameters are available in the Dify plugin configuration interface as manual input fields
- If not specified, tools use default values (30 seconds for all read operations)
- Allows customization per tool based on specific use case requirements

---

## 📌 Important Notes

### Delete All Memories Operation

> **Note**: When using the `delete_all_memories` tool to delete memories in batch, Mem0 will automatically reset the vector index to optimize performance and reclaim space. You may see a log message like `WARNING: Resetting index mem0...` during this operation. This is a **normal and expected behavior** — the warning indicates that the vector store table is being dropped and recreated to ensure optimal query performance after bulk deletion. No action is needed from your side.

### Operation Mode Behavior

- **Async Mode** (`async_mode=true`, default):
  - Write operations (Add/Update/Delete/Delete_All): Non-blocking, return ACCEPT status immediately
  - Read operations (Search/Get/Get_All/History): Wait for results with timeout protection (default: 30s, configurable)
  - On timeout or error: Logs event, cancels background tasks, returns default/empty results
  - Best for production environments with high traffic

- **Sync Mode** (`async_mode=false`):
  - All operations block until completion
  - You can see the actual results of each operation immediately
  - Best for testing and debugging
  - **Note**: No timeout protection. If timeout protection is needed, use `async_mode=true`

### Service Degradation

When operations timeout or encounter errors:
- The event is logged with full exception details
- Background tasks are cancelled to prevent resource leaks (async mode only)
- Default/empty results are returned (empty list `[]` for Search/Get_All/History, `None` for Get)
- Dify workflow continues execution without interruption

---

## 🚀 Development

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/beersoccer/mem0_dify_plugin.git
   cd mem0_dify_plugin
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**
   ```bash
   python -m main
   ```

### Testing

Run YAML validation:
```bash
for file in tools/*.yaml; do 
  python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✅ $(basename $file)"
done
```

---

## 📊 Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1.3 | 2025-11-22 | Unified logging configuration, database connection pool optimization, pgvector config enhancement, constant naming optimization |
| v0.1.2 | 2025-11-21 | Configurable timeout parameters, optimized default timeouts (30s for all read ops), code quality improvements |
| v0.1.1 | 2025-11-20 | Timeout & service degradation for async operations, robust error handling, resource management improvements, production stability fixes |
| v0.1.0 | 2025-11-19 | Smart memory management, robust error handling for non-existent memories, race condition protection, bug fixes |
| v0.0.9 | 2025-11-17 | Unified return format, enhanced async operations (Update/Delete/Delete_All non-blocking), standardized fields, extended constants, complete documentation |
| v0.0.8 | 2025-11-11 | async_mode credential (default true), sync/async tool routing, provider validation aligned, docs updated |
| v0.0.7 | 2025-11-08 | Local-only refactor, centralized constants, background event loop with graceful shutdown, non-blocking add (queued), search via background loop, normalized outputs |
| v0.0.4 | 2025-10-29 | Dual-mode (SaaS/Local), unified client, simplified Local JSON config, search top_k, add requires user_id, HTTP→SDK refactor |
| v0.0.3 | 2025-10-06 | Added 6 new tools, v2 API support, metadata, multi-entity |
| v0.0.2 | 2025-02-24 | Basic add and retrieve functionality |
| v0.0.1 | Initial | First release |

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Dify](https://dify.ai) - AI application development platform
- [Mem0 AI](https://mem0.ai) - Intelligent memory layer for AI
- Built with ❤️ using Dify Plugin SDK

---

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: [Mem0 Docs](https://docs.mem0.ai)
- **Dify Docs**: [Plugin Development](https://docs.dify.ai/docs/plugins)

---

## ⭐ Show Your Support

If you find this plugin useful, please give it a ⭐ on GitHub!

---

### 🌟 Acknowledgments and Origin

This project is a **deeply modified and enhanced** version of the excellent [dify-plugin-mem0](https://github.com/Feversun/dify-plugin-mem0) project by **yevanchen**.

I sincerely appreciate the foundational work and outstanding contribution of the original author, yevanchen. The project provided a solid foundation for my localized, high-performance, and asynchronous plugin.

**Key Differences from the Original Project:**

The original project primarily supported Mem0 platform (SaaS mode) and synchronous request handling. This project has been fully refactored to include:
* **Local Mode**: Supports configuring and running the user's own LLM, embedding models, vector databases (e.g., pgvector/Milvus), graph databases, and more.
* **Asynchronous Support**: Utilizes asynchronous request handling, significantly improving performance and concurrency.

[Original Project Repository Link](https://github.com/Feversun/dify-plugin-mem0)

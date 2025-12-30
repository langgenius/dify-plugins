# Huoban API Suite - Dify Plugin

[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://dify.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.2.0-green)](https://github.com/purexiao/huoban-plugin-dify)

A comprehensive Huoban API plugin for Dify AI platform that provides full CRUD operations, workspace management, and data automation capabilities. This plugin enables Dify AI agents to interact with Huoban (伙伴云) platform for intelligent business automation.

## 🚀 Features

### Workspace & Data Management
- **Workspace Discovery**: List all accessible workspaces (spaces)
- **Table Exploration**: Explore tables within workspaces with detailed field configurations
- **Intelligent Data Operations**: Create, read, update, and delete records in Huoban tables
- **Advanced Querying**: Complex filtering with AND/OR logical operations
- **Member Management**: Retrieve workspace member information for user assignments

### AI-Powered Automation
- **Autonomous Exploration**: Step-by-step workflow for AI agents to discover data structures
- **Smart Field Mapping**: Automatic field ID detection and validation

## 📦 Installation

### Dify Marketplace Installation (Recommended)
1. Navigate to **Dify Marketplace** in your Dify instance
2. Search for **"Huoban API Suite"**
3. Click **"Install"** and follow the setup wizard
4. Configure authentication with your Huoban API key

## 🔐 Authentication Configuration

This plugin uses secure API key authentication:

1. **Obtain API Key**: Get your API key from [Huoban Platform](https://www.huoban.com)
2. **Configure in Dify**: When adding the plugin, enter your API key in the format:

```
Bearer {YOUR_API_KEY}
```

## 🛠️ Available Tools

1. **get_workspace_list**: Lists all workspaces accessible to the current user.
2. **get_table_list**: Retrieves all tables within a specified workspace.
3. **get_table_config**: Gets detailed field configuration for a specific table. **Critical for field mapping.**
4. **create_record**: Creates a new record in the specified table.
5. **query_table_data**: Queries table data with complex filtering conditions.
6. **get_item_detail**: Gets complete details of a specific record.
7. **update_record**: Updates an existing record.
8. **delete_record**: Deletes a specific record.
9. **get_space_members**: Retrieves member information within a workspace.

## ⚠️ Error Handling & Troubleshooting

| Error Type | Solution |
|------------|----------|
| Authentication Error | Regenerate API key in Huoban platform |
| Permission Denied | Check user permissions in Huoban |
| Invalid Field ID | Call `get_table_config` to get correct IDs |

## 📄 License

This plugin is licensed under the **MIT License**.
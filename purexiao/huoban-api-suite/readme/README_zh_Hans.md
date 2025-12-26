# 伙伴云全能工具箱 (Huoban API Suite)

[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://dify.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dify AI平台的伙伴云全能工具箱。包含自主探索数据结构、增删改查数据、以及获取成员列表的能力。

## 🚀 功能特性

### 工作区与数据管理
- **工作区发现**: 列出当前用户可访问的所有工作区
- **表格探索**: 获取表格详细字段配置，帮助 AI 理解数据结构
- **智能数据操作**: 支持增、删、改、查 (CRUD) 全套操作
- **高级查询**: 支持 AND/OR 逻辑嵌套的复杂筛选
- **成员管理**: 获取工作区成员列表，便于指派任务

## 📦 安装与配置

### 认证配置
本插件使用 Bearer Token 认证：
1. 从 [伙伴云平台](https://www.huoban.com) 获取 API Key
2. 在 Dify 插件配置中输入：`Bearer {YOUR_API_KEY}`

## 🛠️ 工具列表

1. **get_workspace_list (获取工作区列表)**: 第一步，获取所有可用的工作区。
2. **get_table_list (获取表格列表)**: 获取指定工作区下的所有表格。
3. **get_table_config (获取表格配置)**: **核心接口**，获取表格的字段 ID 映射关系，写入数据前必用。
4. **create_record (创建记录)**: 向表格添加新数据。
5. **query_table_data (查询表格数据)**: 支持复杂筛选条件的查询。
6. **get_item_detail (获取记录详情)**: 获取单条数据的完整信息。
7. **update_record (更新记录)**: 修改现有数据。
8. **delete_record (删除记录)**: 删除数据。
9. **get_space_members (获取空间成员)**: 获取成员 User ID，用于人员字段赋值。

## 📄 许可证
本项目采用 MIT 许可证。
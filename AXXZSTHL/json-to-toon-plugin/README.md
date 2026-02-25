# JSON to TOON Converter Plugin

## 简介

JSON to TOON Converter 是一个 Dify 插件，用于将 JSON 内容转换为 TOON（Token-Oriented Object Notation）格式，从而大幅降低 token 使用量。

TOON 格式通过移除 JSON 中的冗余符号（如大括号、中括号和引号），同时保持数据结构的清晰度，可以平均减少 30-60% 的 token 消耗。

## 功能特性

- ✅ 将 JSON 数据转换为 TOON 格式
- ✅ 支持嵌套对象和数组
- ✅ 保持数据结构清晰可读
- ✅ 显著减少 token 使用量（平均 30-60%）
- ✅ 错误处理和验证

## 安装

1. 在 Dify 插件市场中搜索 "JSON to TOON Converter"
2. 点击安装按钮
3. 插件将自动配置并可用

## 使用方法

### 在 Dify 工作流中使用

1. 在工作流中添加 "JSON to TOON Converter" 工具节点
2. 将需要转换的 JSON 内容作为输入
3. 工具将返回 TOON 格式的字符串

### API 调用示例

```python
import requests

url = "http://your-dify-instance/api/plugins/json_to_toon/convert"
payload = {
    "json_content": '{"users": [{"id": 1, "name": "Alice", "role": "admin"}, {"id": 2, "name": "Bob", "role": "user"}]}'
}

response = requests.post(url, json=payload)
print(response.text)
```

### 输入示例

**JSON 输入：**
```json
{
  "users": [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
  ],
  "settings": {
    "theme": "dark",
    "notifications": true
  }
}
```

**TOON 输出：**
```
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
settings:
  theme: dark
  notifications: true
```

## TOON 格式说明

TOON 格式的特点：

1. **数组表示**：`key[length]{columns}:` 表示数组，其中 `length` 是数组长度，`columns` 是对象数组的键名
2. **对象表示**：使用缩进表示嵌套关系
3. **值表示**：`key: value` 格式表示键值对
4. **无冗余符号**：移除了 JSON 中的 `{}`, `[]`, `"` 等符号

## 配置

本插件无需额外配置，安装后即可使用。

## 隐私政策

本插件不会收集、存储或传输任何用户数据。所有数据处理都在本地完成，不会发送到外部服务器。

详细的隐私政策请参阅 [PRIVACY_POLICY.md](./PRIVACY_POLICY.md)

## 开发

### 本地开发

1. 克隆仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行服务：
   ```bash
   python app.py
   ```
4. 测试 API：
   ```bash
   curl -X POST http://localhost:5001/convert \
     -H "Content-Type: application/json" \
     -d '{"json_content": "{\"test\": \"value\"}"}'
   ```

## 许可证

MIT License

## 支持

如有问题或建议，请提交 Issue 或 Pull Request。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 JSON 到 TOON 格式转换
- 支持嵌套对象和数组


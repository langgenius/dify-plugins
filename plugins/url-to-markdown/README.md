# URL to Markdown 插件

**作者:** siwei
**版本:** 0.0.1
**类型:** tool

## 功能描述
这是一个强大的网页内容抓取工具，可以将任何网页内容转换为整洁的Markdown格式。主要特点：
- 支持多种网页格式的解析
- 智能提取主要内容
- 保留文章结构和格式
- 支持图片链接转换
- 自动生成目录

## 安装要求
- Python 3.12+
- 依赖包：见 requirements.txt

## 快速开始
1. 安装插件
2. 配置环境变量（如需要）
3. 在Dify中调用工具，传入URL即可获取Markdown内容

## 使用示例
```python
url = "https://example.com"
result = await tool.invoke({"url": url})
print(result)  # 输出转换后的Markdown内容
```

## 注意事项
- 请遵守目标网站的robots.txt规则
- 建议添加适当的请求延迟
- 部分网站可能需要配置User-Agent

## 更新日志
### v0.0.1 (2024-03-06)
- 初始版本发布
- 基础网页抓取功能
- Markdown转换支持

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证
MIT License




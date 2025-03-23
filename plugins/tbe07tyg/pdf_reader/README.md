# PDF Reader Plugin for Dify

一个用于读取和处理PDF文件的Dify插件。

## 功能特点

- 支持从URL或本地路径读取PDF文件
- 将PDF转换为文本内容
- 提取PDF元数据信息
- 支持中英文界面

## 安装要求

- Python 3.10 或更高版本
- 依赖包：
  - PyPDF2
  - requests
  - python-magic

## 快速开始

1. 在Dify平台安装插件
2. 在应用中启用PDF Reader工具
3. 使用以下方式调用插件：
   - 提供PDF文件的URL
   - 或提供本地PDF文件路径

## 使用示例

```python
# 从URL读取PDF
response = pdf_to_text(url="https://example.com/sample.pdf")

# 从本地文件读取PDF
response = pdf_to_text(file_path="/path/to/local/file.pdf")
```

## API参数说明

### pdf_to_text

将PDF文件转换为文本。

**参数：**
- `url` (string, 可选): PDF文件的URL地址
- `file_path` (string, 可选): PDF文件的本地路径

**返回值：**
- `success` (boolean): 操作是否成功
- `content` (string): 提取的文本内容
- `metadata` (object): PDF文件的元数据

## 隐私说明

本插件不会收集或存储任何个人信息。所有PDF处理都在本地完成，不会上传到第三方服务器。

## 许可证

MIT License

## 作者

作者：DrYang
联系方式：383441523@qq.com
GitHub：tbe07tyg 
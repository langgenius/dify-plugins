# 安装指南

## 使用dify安装

### 1. 安装dify工具

```bash
brew install dify
```

### 2. 验证插件

```bash
cd tencent_cloud_search_plugin
dify plugin validate
```

### 3. 打包插件

```bash
dify plugin package
```

这将生成一个 `.difypkg` 文件。

### 4. 安装到Dify

#### 方法一：通过Dify界面
1. 登录Dify工作台
2. 进入"工具"页面
3. 点击"上传自定义工具"
4. 选择生成的 `.difypkg` 文件
5. 配置API密钥

#### 方法二：通过CLI
```bash
dify plugin install tencent_cloud_search-0.0.1.difypkg
```

## 配置API密钥

1. 在Dify工具配置页面找到"腾讯云搜索"
2. 填入您的腾讯云API密钥：
   - Secret ID: 您的腾讯云SecretId
   - Secret Key: 您的腾讯云SecretKey
3. 点击"测试连接"验证
4. 保存配置

## 开始使用

配置完成后，您就可以在Dify工作流中使用腾讯云联网搜索功能了！

### 基础搜索示例

```json
{
    "query": "人工智能发展趋势"
}
```

### 高级搜索示例

```json
{
    "query": "机器学习",
    "site": "github.com",
    "mode": "2",
    "count": 20
}
```

更多使用示例请参考 `examples/usage_examples.py` 文件。
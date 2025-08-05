# Dify插件构建指南

## 使用dify-cli打包插件

### 1. 安装dify

```bash
# 使用brew安装dify工具
brew install dify
```

### 2. 验证插件结构

```bash
# 进入插件目录
cd tencent_cloud_search_plugin

# 验证插件结构
dify plugin validate
```

### 3. 打包插件

```bash
# 打包插件
dify plugin package

# 这将生成一个 .difypkg 文件
```

### 4. 安装到Dify

```bash
# 方法1: 通过CLI安装
dify plugin install tencent_cloud_search-0.0.1.difypkg

# 方法2: 在Dify界面上传.difypkg文件
```

## 插件目录结构

```
tencent_cloud_search_plugin/
├── manifest.yaml                 # 插件清单
├── dify_plugin_package.yaml     # 包配置文件
├── _assets/
│   └── icon.svg                 # 插件图标
├── provider/
│   ├── __init__.py             # 提供商入口
│   ├── provider.yaml           # 提供商配置
│   └── tools/
│       ├── __init__.py         # 工具模块入口
│       ├── search.yaml         # 搜索工具配置
│       └── search.py           # 搜索工具实现
├── README.md                   # 说明文档
├── DEPLOYMENT.md              # 部署指南
├── requirements.txt           # 依赖包
├── test_plugin.py            # 测试脚本
└── examples/
    └── usage_examples.py     # 使用示例
```

## 常见问题

### 1. 验证失败
- 检查yaml文件格式是否正确
- 确认所有必需文件是否存在
- 验证图标文件路径是否正确

### 2. 打包失败
- 确认dify-cli版本是否最新
- 检查依赖包是否正确安装
- 验证Python代码语法是否正确

### 3. 安装失败
- 确认Dify版本兼容性
- 检查插件权限设置
- 验证API密钥配置

## 开发调试

### 本地测试
```bash
# 运行测试脚本
python test_plugin.py
```

### 日志调试
```bash
# 启用详细日志
dify plugin validate --verbose
dify plugin package --verbose
```

## 发布流程

1. 更新版本号（manifest.yaml 和 dify_plugin_package.yaml）
2. 运行测试确保功能正常
3. 使用dify验证和打包
4. 上传到Dify插件市场或私有部署
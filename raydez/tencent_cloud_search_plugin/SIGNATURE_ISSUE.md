# 插件签名验证问题解决方案

## 问题描述
上传插件时遇到错误：`plugin verification has been enabled, and the plugin you want to install has a bad signature`

这表明 Dify 启用了插件签名验证，只允许安装经过官方签名的插件。

## 解决方案

### 方案1：禁用插件验证（推荐用于开发环境）

如果您有 Dify 的管理权限，可以尝试禁用插件验证：

1. **检查 Dify 配置**
   ```bash
   # 查找 Dify 配置文件
   find ~ -name "*.yaml" -o -name "*.yml" | grep -i dify
   ```

2. **修改配置文件**
   在 Dify 配置中添加或修改：
   ```yaml
   plugin:
     verification:
       enabled: false
   ```

3. **重启 Dify 服务**

### 方案2：使用开发模式

1. **检查是否有开发模式选项**
   - 在 Dify 界面查找"开发者模式"或"调试模式"
   - 启用后可能允许安装未签名的插件

### 方案3：本地开发模式

1. **直接集成到 Dify 源码**
   ```bash
   # 将插件代码直接放到 Dify 的插件目录
   cp -r tencent_cloud_search_plugin /path/to/dify/plugins/
   ```

### 方案4：申请官方签名

1. **联系 Dify 官方**
   - 提交插件到 Dify 官方仓库
   - 申请官方签名和发布

### 方案5：环境变量配置

尝试设置环境变量禁用验证：
```bash
export DIFY_PLUGIN_VERIFICATION_ENABLED=false
export DIFY_PLUGIN_SIGNATURE_CHECK=false
```

## 临时解决方案

### 直接使用 Python 代码

如果无法安装插件，可以直接在 Dify 工作流中使用 Python 代码节点：

```python
import json
import time
import hmac
import hashlib
import requests
from typing import Dict, Any

def tencent_cloud_search(query: str, secret_id: str, secret_key: str, mode: int = 0):
    """腾讯云联网搜索API调用"""
    
    # API配置
    service = "wsa"
    version = "2025-05-08"
    action = "SearchPro"
    endpoint = "wsa.tencentcloudapi.com"
    
    # 构建请求参数
    params = {"Query": query, "Mode": mode}
    payload = json.dumps(params, separators=(',', ':'))
    
    # 构建签名（简化版）
    timestamp = int(time.time())
    date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
    
    # 这里需要完整的签名算法实现...
    # [签名代码省略，可参考插件中的完整实现]
    
    # 发送请求
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Host': endpoint,
        'X-TC-Action': action,
        'X-TC-Timestamp': str(timestamp),
        'X-TC-Version': version,
    }
    
    url = f"https://{endpoint}"
    response = requests.post(url, headers=headers, data=payload)
    
    return response.json()

# 使用示例
result = tencent_cloud_search("人工智能", "your_secret_id", "your_secret_key")
print(result)
```

## 建议

1. **开发环境**：尝试方案1禁用验证
2. **生产环境**：考虑方案4申请官方签名
3. **临时使用**：使用方案5的Python代码节点

## 技术支持

如需进一步帮助，请：
1. 检查 Dify 官方文档关于插件开发的说明
2. 联系 Dify 社区或技术支持
3. 查看 Dify GitHub 仓库的 Issues
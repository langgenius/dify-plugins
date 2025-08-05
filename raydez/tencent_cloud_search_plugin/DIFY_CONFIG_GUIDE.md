# Dify 插件签名验证禁用配置指导

## 🔍 步骤1：确定 Dify 部署方式

首先需要确定您的 Dify 是如何部署的：

### 检查部署方式
```bash
# 检查是否是 Docker 部署
docker ps | grep dify

# 检查是否有 Docker Compose
find . -name "docker-compose*.yml" -o -name "compose*.yml" 2>/dev/null

# 检查是否是源码部署
find /opt /usr/local /home -name "dify" -type d 2>/dev/null

# 检查进程
ps aux | grep dify
```

## 🐳 方案A：Docker/Docker Compose 部署

### A1. 找到 Docker Compose 文件
```bash
# 常见位置
ls -la docker-compose.yml
ls -la docker-compose.yaml
ls -la compose.yml
ls -la dify/docker-compose.yml
```

### A2. 修改环境变量
在 `docker-compose.yml` 文件中找到 `api` 服务，添加环境变量：

```yaml
services:
  api:
    image: langgenius/dify-api:latest
    environment:
      # 添加以下环境变量
      - PLUGIN_VERIFICATION_ENABLED=false
      - PLUGIN_SIGNATURE_CHECK=false
      - DISABLE_PLUGIN_VERIFICATION=true
      # 其他现有环境变量...
```

### A3. 重启服务
```bash
docker-compose down
docker-compose up -d
```

## 📁 方案B：源码部署

### B1. 找到配置文件
```bash
# 查找配置文件
find . -name "config.py" -o -name "settings.py" -o -name "*.env" | grep -i dify

# 常见位置
ls -la .env
ls -la .env.local
ls -la config/config.py
ls -la api/config.py
```

### B2. 修改 .env 文件
在 `.env` 或 `.env.local` 文件中添加：

```bash
# 禁用插件验证
PLUGIN_VERIFICATION_ENABLED=false
PLUGIN_SIGNATURE_CHECK=false
DISABLE_PLUGIN_VERIFICATION=true
```

### B3. 修改 Python 配置文件
如果有 `config.py` 文件，添加：

```python
# 插件配置
PLUGIN_VERIFICATION_ENABLED = False
PLUGIN_SIGNATURE_CHECK = False
DISABLE_PLUGIN_VERIFICATION = True
```

### B4. 重启服务
```bash
# 如果使用 systemd
sudo systemctl restart dify

# 如果是手动启动
pkill -f dify
# 然后重新启动 Dify
```

## ⚙️ 方案C：Kubernetes 部署

### C1. 修改 ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dify-config
data:
  PLUGIN_VERIFICATION_ENABLED: "false"
  PLUGIN_SIGNATURE_CHECK: "false"
  DISABLE_PLUGIN_VERIFICATION: "true"
```

### C2. 更新部署
```bash
kubectl apply -f dify-configmap.yaml
kubectl rollout restart deployment/dify-api
```

## 🔧 方案D：通过 API 配置（如果支持）

### D1. 检查管理 API
```bash
# 尝试访问管理接口
curl -X GET http://localhost:5001/console/api/setup
curl -X GET http://localhost:5001/console/api/config
```

### D2. 修改配置（如果有管理接口）
```bash
curl -X POST http://localhost:5001/console/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "plugin_verification_enabled": false,
    "plugin_signature_check": false
  }'
```

## 🌐 方案E：Nginx/反向代理配置

如果通过反向代理访问，可能需要修改代理配置：

```nginx
# nginx.conf
location /console/api/ {
    proxy_pass http://dify-api:5001;
    proxy_set_header X-Plugin-Verification-Disabled true;
}
```

## 📋 验证配置是否生效

### 检查环境变量
```bash
# Docker 部署
docker exec -it dify-api env | grep -i plugin

# 源码部署
ps aux | grep dify
cat /proc/$(pgrep -f dify)/environ | tr '\0' '\n' | grep -i plugin
```

### 检查日志
```bash
# Docker 日志
docker logs dify-api | grep -i plugin

# 源码部署日志
tail -f /var/log/dify/api.log | grep -i plugin
```

### 测试上传
配置修改后，重新尝试上传插件。

## 🚨 常见问题排查

### 问题1：找不到配置文件
```bash
# 全局搜索 Dify 相关文件
find / -name "*dify*" -type f 2>/dev/null | head -20
find / -name "docker-compose*" -exec grep -l "dify" {} \; 2>/dev/null
```

### 问题2：权限不足
```bash
# 使用 sudo 修改配置
sudo find /etc -name "*dify*" -type f
sudo find /opt -name "*dify*" -type f
```

### 问题3：配置不生效
```bash
# 确保完全重启
docker-compose down && docker-compose up -d
# 或
sudo systemctl stop dify && sudo systemctl start dify
```

## 🔍 具体操作步骤

### 第一步：确定部署方式
运行以下命令确定您的部署方式：
```bash
echo "=== 检查 Docker 部署 ==="
docker ps | grep dify
echo "=== 检查 Docker Compose ==="
find . -maxdepth 3 -name "*compose*.yml" -exec ls -la {} \;
echo "=== 检查源码部署 ==="
find /opt /usr/local /home -maxdepth 3 -name "dify" -type d 2>/dev/null
```

### 第二步：根据结果选择方案
- 如果有 Docker 容器 → 使用方案A
- 如果有源码目录 → 使用方案B
- 如果是 K8s 环境 → 使用方案C

### 第三步：验证修改
重启服务后，尝试重新上传插件。

## 📞 需要帮助？

如果按照以上步骤仍然无法解决，请提供：
1. 您的 Dify 部署方式
2. 配置文件位置
3. 错误日志信息

我会提供更具体的解决方案！
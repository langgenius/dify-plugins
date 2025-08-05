# 部署指南 / Deployment Guide

## 快速部署

### 1. 准备工作

#### 获取腾讯云API密钥
1. 登录 [腾讯云控制台](https://cloud.tencent.com/)
2. 进入 [访问管理 > API密钥管理](https://console.cloud.tencent.com/cam/capi)
3. 点击"新建密钥"获取 SecretId 和 SecretKey
4. 妥善保存密钥信息

#### 开通联网搜索服务
1. 在腾讯云控制台搜索"联网搜索API"
2. 点击进入产品页面
3. 点击"立即使用"开通服务
4. 完成实名认证（企业认证推荐）
5. 选择计费版本：
   - 标准版：千次46元
   - 尊享版：千次80元（支持更多功能）

### 2. 在Dify中安装插件

#### 方法一：通过Dify插件市场（推荐）
1. 登录Dify工作台
2. 进入"工具"页面
3. 搜索"腾讯云联网搜索"
4. 点击安装

#### 方法二：手动安装
1. 下载插件代码到本地
2. 在Dify中选择"自定义工具"
3. 上传插件文件夹
4. 配置插件参数

### 3. 配置插件

1. 在Dify工具配置页面找到"腾讯云联网搜索"
2. 点击"配置"
3. 填入API密钥：
   - **Secret ID**: 您的腾讯云SecretId
   - **Secret Key**: 您的腾讯云SecretKey
4. 点击"测试连接"验证配置
5. 保存配置

## 高级配置

### 环境变量配置（可选）

为了更安全地管理密钥，可以使用环境变量：

```bash
# 设置环境变量
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"
```

### 子账号配置（企业用户推荐）

1. **创建子账号**
   - 在腾讯云控制台创建子账号
   - 为子账号分配最小权限原则

2. **权限配置**
   - 搜索"联网搜索API"
   - 勾选以下权限：
     - `wsa:SearchPro`
     - `wsa:DescribeInstances`

3. **使用子账号密钥**
   - 使用子账号的SecretId和SecretKey配置插件

## 测试验证

### 1. 基础功能测试

```python
# 在Dify工作流中测试
{
    "query": "人工智能",
    "mode": "0"
}
```

### 2. 高级功能测试

```python
# 测试VR卡功能
{
    "query": "北京天气",
    "mode": "1"
}

# 测试网站筛选
{
    "query": "开源项目",
    "site": "github.com"
}
```

### 3. 使用测试脚本

```bash
# 设置环境变量
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"

# 运行测试
python test_plugin.py
```

## 故障排除

### 常见问题

#### 1. 认证失败
**错误**: `AuthFailure.SignatureExpire`
**解决**: 检查系统时间是否正确，确保与标准时间同步

#### 2. 权限不足
**错误**: `AuthFailure.UnauthorizedOperation`
**解决**: 
- 确认已开通联网搜索服务
- 检查子账号权限配置
- 验证SecretId和SecretKey是否正确

#### 3. 参数错误
**错误**: `InvalidParameter`
**解决**:
- 检查query参数是否为空
- 确认query长度不超过1500字节
- 验证时间参数格式是否正确

#### 4. 配额超限
**错误**: `RequestLimitExceeded`
**解决**:
- 检查账户余额
- 确认调用频率是否超限
- 联系腾讯云客服调整配额

### 调试模式

启用调试模式查看详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能优化

### 1. 缓存策略
- 对相同查询结果进行缓存
- 设置合理的缓存过期时间

### 2. 批量处理
- 合并相似查询
- 使用异步调用提高效率

### 3. 错误重试
- 实现指数退避重试机制
- 设置最大重试次数

## 监控告警

### 1. 调用量监控
- 监控日调用量
- 设置用量告警阈值

### 2. 错误率监控
- 监控API调用成功率
- 设置错误率告警

### 3. 成本控制
- 监控每日费用
- 设置费用预算告警

## 安全建议

### 1. 密钥管理
- 定期轮换API密钥
- 使用子账号最小权限原则
- 避免在代码中硬编码密钥

### 2. 网络安全
- 使用HTTPS协议
- 配置IP白名单（如支持）
- 启用访问日志记录

### 3. 数据安全
- 不要搜索敏感信息
- 注意搜索结果的数据合规性
- 定期清理搜索日志

## 技术支持

### 官方支持
- 腾讯云工单系统
- 腾讯云技术支持热线
- 官方文档中心

### 社区支持
- GitHub Issues
- Dify社区论坛
- 技术交流群

---

如有其他问题，请参考 [README.md](./README.md) 或提交Issue。
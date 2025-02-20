## lark_notify

**Author:** opsworld30
**Version:** 0.0.1
**Type:** tool

### Description

LarkNotify 是一个用于向飞书群聊发送通知消息的插件。它支持发送文本消息和卡片消息，让你能够以更灵活和美观的方式向团队传递信息。

### Features

- 支持发送纯文本消息
- 支持发送卡片消息，包括：
  - 4种消息类型：信息、警告、成功、错误
  - 3种布局方式：水平、垂直、二分
  - 可选的时间戳显示
- 支持长文本自动分段发送
- 支持多语言界面（英文、中文、葡萄牙语）

### Prerequisites

- 飞书机器人 Webhook URL
  1. 在飞书群聊中添加自定义机器人
  2. 获取机器人的 Webhook URL
  3. 从 URL 中提取 webhook_key（/hook/ 后的部分）

### Configuration

在插件配置中，你需要设置以下凭据：

- `webhook_key`: 飞书机器人的 Webhook URL 密钥

### Usage Examples

1. 发送文本消息：
```json
{
  "message": "系统已完成数据备份",
  "msg_type": "text"
}
```

2. 发送成功状态卡片：
```json
{
  "message": "数据库迁移完成",
  "msg_type": "card",
  "title": "迁移通知",
  "card_type": "success"
}
```

3. 发送警告消息（无时间戳）：
```json
{
  "message": "服务器负载过高\n- CPU: 92%\n- 内存: 87%\n- 磁盘: 95%",
  "msg_type": "card",
  "title": "系统警告",
  "card_type": "warning",
  "card_layout": "vertical",
  "show_meta": false
}
```

### Privacy Policy

本插件仅收集以下必要信息用于消息发送：

1. 飞书机器人的 Webhook URL 密钥
2. 用户提供的消息内容

这些信息仅用于向指定的飞书群聊发送消息，不会用于其他用途或与第三方共享。

消息发送使用飞书官方的 API，相关隐私政策请参考：[飞书开放平台服务协议](https://www.feishu.cn/agreement/platform_service)




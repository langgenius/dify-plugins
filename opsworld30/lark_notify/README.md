# lark_notify

**Author:** opsworld30
**Version:** 0.0.1
**Type:** tool

### Description

LarkNotify is a plugin for sending notification messages to Lark (Feishu) group chats. It supports sending text messages and card messages, allowing you to communicate with your team in a more flexible and visually appealing way.

### Features

- Support for plain text messages
- Support for card messages, including:
  - 4 message types: info, warning, success, error
  - 3 layout options: horizontal, vertical, bisected
  - Optional timestamp display
- Support for automatic long text segmentation
- Multi-language interface (English, Chinese, Portuguese)

### Prerequisites

- Lark Bot Webhook URL
  1. Add a custom bot to your Lark group chat
  2. Get the bot's Webhook URL
  3. Use either the complete webhook URL or just the webhook key (the part after /hook/)

### Configuration

In the plugin configuration, you need to set the following credentials:

- `webhook_key`: You can input either:
  - The complete webhook URL: `https://open.feishu.cn/open-apis/bot/v2/hook/xxx`
  - Just the webhook key: `xxx`

### Usage Examples

1. Send a text message:
```json
{
  "message": "System backup completed",
  "msg_type": "text"
}
```

2. Send a success status card:
```json
{
  "message": "Database migration completed",
  "msg_type": "card",
  "title": "Migration Notice",
  "card_type": "success"
}
```

3. Send a warning message (without timestamp):
```json
{
  "message": "High server load\n- CPU: 92%\n- Memory: 87%\n- Disk: 95%",
  "msg_type": "card",
  "title": "System Warning",
  "card_type": "warning",
  "card_layout": "vertical",
  "show_meta": false
}
```

### Privacy Policy

This plugin only collects the following necessary information for message delivery:

1. Lark bot webhook URL/key
2. User-provided message content

This information is used solely for sending messages to the specified Lark group chat and will not be used for other purposes or shared with third parties.

Message sending uses Lark's official API. For related privacy policies, please refer to: [Lark Open Platform Service Agreement](https://www.larksuite.com/en_us/agreement)

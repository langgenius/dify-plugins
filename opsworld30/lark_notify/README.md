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
  - Markdown formatting support:
    - Bold text: **text**
    - Italic text: *text*
    - Links: [text](url)
    - Bullet points with -
    - @everyone with <at id=all></at>
  - Optional timestamp display
- Support for automatic long text segmentation
- Multi-language interface (English, Chinese, Japanese, Portuguese)

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
  "webhook": "xxx",
  "message": "System backup completed"
}
```

2. Send a card message with markdown:
```json
{
  "webhook": "xxx",
  "card_content": "**Deployment Status**: *Success*\n- Service: API Gateway\n- Version: 1.2.3\n- Time: 2024-02-25\n\nFor details, see [Deployment Log](https://example.com/logs)",
  "title": "Deployment Notice",
  "card_type": "success",
  "show_time": true
}
```

### Privacy Policy

This plugin only collects the following necessary information for message delivery:

1. Lark bot webhook URL/key
2. User-provided message content

This information is used solely for sending messages to the specified Lark group chat and will not be used for other purposes or shared with third parties.

Message sending uses Lark's official API. For related privacy policies, please refer to: [Lark Open Platform Service Agreement](https://www.larksuite.com/en_us/agreement)

### Support

If you encounter any issues or have questions, please:
1. Check the documentation in the GUIDE.md file
2. Raise an issue on the GitHub repository
3. Contact the plugin author

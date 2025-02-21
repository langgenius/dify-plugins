## Privacy

The Lark Notify plugin respects user privacy and handles data with care. Here's what you need to know about data collection and usage:

### Data Collection
- **Webhook Key**: The only credential required is your Lark bot's webhook key.
- **Message Content**: The content of messages you want to send.
- **No Personal Data**: We do not collect or store any personal user data.

### Data Usage
- The webhook key is used solely for sending messages to your specified Lark group chat.
- Message content is only used for delivery and is not stored or logged.
- All communication is done through Lark's official API endpoints.

### Data Storage
- No data is permanently stored by this plugin.
- Credentials are stored securely by the Dify platform.
- Message content is transmitted only and not retained.

### Third-party Services
- This plugin only interacts with Lark's official API service.
- No other third-party services are used.

### Security
- All communication with Lark API is done via HTTPS.
- The plugin includes retry mechanisms with exponential backoff for reliable message delivery.
- Error messages are sanitized to prevent sensitive information leakage.

For any privacy concerns or questions, please contact the plugin author or raise an issue on the GitHub repository.
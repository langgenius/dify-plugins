
# Dida Todo List Plugin for Dify

## Overview
This plugin integrates Dida Todo List functionality with Dify, allowing users to manage their tasks and todo lists directly through Dify's interface.

## Features
- Create, read, update, and delete tasks
- Manage task lists and projects
- Sync task status between Dify and Dida
- Secure authentication using tokens

## Data Privacy
This plugin handles user data with utmost care and transparency. For detailed information about data collection, usage, and protection measures, please refer to our [Privacy Policy](./privacy_policy.md).

## Installation
1. Install via Dify Marketplace
2. Configure your Dida authentication token
3. Start managing your tasks!

## Configuration
1. Obtain your Dida API token from your Dida account settings
2. Add the token to the plugin configuration in Dify
3. Configure optional settings like default list and sync frequency

## Usage
```python
# Example usage in your Dify application
credentials = {
    'token': 'your_dida_token'
}
dida_provider = DidaProvider(credentials)
```

## Security Considerations
- Tokens are stored securely and encrypted
- All API communications are encrypted via HTTPS
- No sensitive data is cached locally

## Support
For technical support or privacy concerns, please contact: [523018705@qq.com]
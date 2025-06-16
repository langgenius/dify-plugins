# Privacy Policy for Jenkins Tool Plugin

## Data Collection and Usage

The Jenkins Tool plugin is designed to interact with Jenkins servers and does not collect or store any personal data directly. However, to provide its functionality, the plugin requires and processes the following information:

### Required Information
- Jenkins server URL
- Jenkins username
- Jenkins API Token

### Data Processing
1. **Server Information**: The plugin uses the Jenkins server URL to establish connections. This information is only used for the intended purpose of connecting to your Jenkins instance.

2. **Authentication Data**: The username and API Token are used solely for authentication with your Jenkins server. These credentials are:
   - Not stored permanently
   - Not shared with any third parties
   - Only used for the duration of the API request

3. **Build Information**: When retrieving build information or logs, the plugin processes:
   - Build numbers
   - Build status
   - Console output
   - Build parameters

### Data Storage
- The plugin does not store any user data or credentials
- All data processing is done in-memory and is not persisted
- No data is collected for analytics or tracking purposes

## Third-Party Services

This plugin interacts with Jenkins servers, which may have their own privacy policies. We recommend reviewing the privacy policy of your Jenkins instance to understand how your data is handled on their end.

## Data Security

- All communications with Jenkins servers are recommended to be done over HTTPS
- API Tokens should be kept secure and not shared
- The plugin does not implement any data encryption as it relies on the security measures provided by Jenkins

## User Rights

As the plugin does not collect or store personal data, there are no specific data subject rights to exercise. However, you can:
- Revoke your Jenkins API Token at any time
- Stop using the plugin at any time
- Contact the plugin maintainers for any privacy-related concerns

## Updates to Privacy Policy

This privacy policy may be updated from time to time. Users will be notified of any significant changes through the plugin's update mechanism.

## Contact

For any privacy-related questions or concerns, please open an issue on the plugin's GitHub repository.
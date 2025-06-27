# BookStack Plugin for Dify

A comprehensive BookStack integration plugin for Dify that allows you to search, create, and manage content in your BookStack wiki platform through AI-powered workflows.

## Features

This plugin provides the following tools to interact with your BookStack instance:

### Search & Retrieval Tools
- **Search Content**: Search across books, chapters, and pages with flexible filtering
- **Get Book**: Retrieve detailed information about a specific book
- **Get Chapter**: Retrieve detailed information about a specific chapter  
- **Get Page**: Retrieve detailed information about a specific page
- **List Books**: Get a paginated list of all books
- **List Shelves**: Get a paginated list of all shelves

### Content Management Tools
- **Create Book**: Create new books with name and description
- **Create Chapter**: Create new chapters within existing books
- **Create Page**: Create new pages in books or chapters with HTML/Markdown content
- **Update Page**: Update existing page content, names, or both

## Prerequisites

1. A running BookStack instance (v0.31.0 or later recommended)
2. API access enabled in your BookStack instance
3. API Token and Secret generated in BookStack

## Setup Instructions

### 1. Enable BookStack API

1. Log into your BookStack instance as an administrator
2. Go to **Settings** → **Features & Security**
3. Enable **API Authentication**
4. Save the settings

### 2. Generate API Credentials

1. Go to your **User Profile** → **API Tokens**
2. Click **Create Token**
3. Give your token a descriptive name (e.g., "Dify Integration")
4. Copy both the **Token ID** and **Token Secret** - you'll need both

### 3. Install the Plugin in Dify

1. Import this plugin into your Dify instance
2. Configure the plugin with the following credentials:
   - **BookStack URL**: The base URL of your BookStack instance (e.g., `https://wiki.yourcompany.com`)
   - **API Token**: The Token ID from step 2
   - **API Secret**: The Token Secret from step 2

### 4. Test the Connection

Use the "List Books" tool to verify your connection is working properly.

## Usage Examples

### Basic Content Search
```
Search for "user authentication" across all content types with a limit of 10 results.
```

### Create Documentation Structure
```
1. Create a new book called "API Documentation"
2. Create a chapter called "Authentication" in that book
3. Create a page with setup instructions in the authentication chapter
```

### Content Retrieval
```
Get the full content of page ID 123 to review the current documentation.
```

## API Permissions

This plugin requires the following BookStack permissions:
- Read access to books, chapters, and pages
- Create access for new content
- Update access for existing pages
- Search functionality access

Ensure your BookStack user account has appropriate permissions for the operations you plan to perform.

## Configuration Options

### BookStack URL
The full URL to your BookStack instance including protocol (http/https) but without trailing slash.

### API Authentication
BookStack uses token-based authentication. Both the token ID and secret are required for all API calls.

## Error Handling

The plugin includes comprehensive error handling for:
- Network connectivity issues
- Authentication failures
- Invalid API responses
- Missing required parameters
- BookStack API rate limits

## Supported BookStack Versions

This plugin is compatible with:
- BookStack v0.31.0 and later
- Earlier versions may work but are not officially supported

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your API token and secret are correct
   - Ensure API authentication is enabled in BookStack settings
   - Check that your user account has necessary permissions

2. **Connection Timeout**
   - Verify the BookStack URL is accessible
   - Check network connectivity between Dify and BookStack
   - Ensure BookStack is running and responsive

3. **Permission Denied**
   - Verify your BookStack user has appropriate permissions
   - Check if the content you're trying to access has restrictions

### Debug Information

When reporting issues, please include:
- BookStack version
- Plugin version
- Error messages from Dify logs
- Steps to reproduce the issue

## Development

### Repository
Source code: [BookStack Plugin Repository]

### Contributing
Contributions are welcome! Please feel free to submit issues and pull requests.

### License
This plugin is released under the MIT License.

## Support

For support with this plugin:
1. Check the troubleshooting section above
2. Review BookStack's official API documentation
3. Submit an issue on the plugin repository

## Privacy Policy

This plugin:
- Only connects to the BookStack instance you configure
- Does not store or transmit your BookStack credentials to external services
- Operates entirely within your Dify environment
- API calls are made directly from your Dify instance to your BookStack instance

Your BookStack content and credentials remain private and are not shared with third parties.

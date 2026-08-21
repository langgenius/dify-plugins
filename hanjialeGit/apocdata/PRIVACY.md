# Privacy Policy

## Data Collection

This plugin collects the following data when making API calls:

- **Query Parameters**: Stock symbols, dates, and other user-provided parameters
- **API Responses**: Market data returned from the ApocData API

## Data Transmission

- All API calls are made over HTTPS to `https://www.apocdata.com`
- No user authentication or personal data is transmitted
- No data is stored by this plugin

## Third-Party Services

This plugin calls the ApocData API service:
- **Service**: ApocData A-Share Market Data API
- **URL**: https://www.apocdata.com/api/blade-dataplatform/open/data
- **Data Sent**: Query parameters (stock symbols, dates)
- **Data Received**: Market data (quotes, financials, etc.)

## Data Storage

- This plugin does NOT store any user data
- This plugin does NOT use any database
- All data is transient and exists only during the API call

## User Control

Users control what data is queried through the tool parameters they provide.

## Contact

For questions about this plugin, visit: https://github.com/ApocData/ApocData-mcp-server

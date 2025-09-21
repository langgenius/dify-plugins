# Privacy Policy for AKShare Stock Data Plugin

**Last Updated:** 2025-09-17

## 1. Introduction
This Privacy Policy explains how the AKShare Stock Data Plugin ("Plugin", "we", "us", or "our") handles information when you use our plugin to access financial data via the Dify platform. This policy applies only to the Plugin, not to the Dify platform itself or any third-party data sources.

**Important Note**: This plugin is a wrapper around the [AKShare](https://github.com/akfamily/akshare) Python library. Data access and processing are handled through AKShare, which connects to various financial data sources.

## 2. Data We Process
The Plugin acts as an intermediary to help you retrieve financial data using the AKShare Python library. When you use the Plugin, the following types of data may be processed in memory:

- **User Input Parameters**: Such as stock codes, date ranges, technical indicator types, or other query parameters you provide.
- **API Responses**: The financial data returned by AKShare in response to your queries, including but not limited to:
  - Real-time stock market data
  - Historical price data
  - Financial indicator data
  - Fund flow data
  - Technical analysis data
  - Market overview data
- **Temporary Logs**: Technical logs that may contain request parameters and response status (for debugging and error handling)

The Plugin does **not** persistently store any of this information. All data is processed in memory only for the duration of your request and is immediately cleared after request completion.

## 3. How We Use Data
Your data is used solely to:
- Pass your query parameters to the AKShare library to obtain financial data.
- Retrieve and return the requested financial data to you via the Dify platform.

We do not use your data for analytics, profiling, or advertising.

## 4. Data Sharing and Third Parties
The Plugin does not share your data with any third parties, except:

- **Dify Platform**: The Plugin operates within Dify. How Dify handles your data is governed by Dify's privacy policy.
- **AKShare Library**: The Plugin uses AKShare to access financial data. AKShare may connect to various financial data sources as part of its normal operation, including:
  - 东方财富网 (East Money)
  - 新浪财经 (Sina Finance)
  - 同花顺 (TongHuaShun)
  - 腾讯财经 (Tencent Finance)
  - 网易财经 (NetEase Finance)
  - Other financial data providers
- **Financial Data Sources**: Through AKShare, the Plugin may access data from financial websites and APIs, but this is handled entirely by AKShare, and we have no control over how these third parties handle data.

## 5. Data Retention
The Plugin is stateless and does **not** retain any user data after a request is completed. Any logging or data retention is subject to the policies of:
- The Dify platform.
- The data sources accessed via the Plugin (e.g., exchanges, public data interfaces exposed by AKShare).

## 6. User Rights
As the Plugin does not store your personal data, requests regarding access, correction, deletion, or portability of data should be directed to:
- The administrators of the Dify platform you are using.

You may stop using the Plugin at any time.

## 7. Security
We rely on the security measures of the Dify platform to protect data while it is being processed by the Plugin. If you provide sensitive information, ensure you trust the security of Dify.

## 8. Changes to This Privacy Policy
We may update this Privacy Policy from time to time. Changes will be posted within the Plugin's information page or documentation. Please review this policy periodically for updates.

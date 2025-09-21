# AKShare Stock Data Plugin for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

## 📞 Contact Information

- **Author**: shaoxing-xie
- **Email**: sxxiefg@163.com
- **Repository**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **Issue Reports**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 Overview

**AKShare Stock Data Plugin** is a comprehensive stock data tool developed specifically for the Dify platform, built on the renowned [AKShare](https://github.com/akfamily/akshare) Python library. This plugin provides users with a one-stop stock market data access solution, covering multiple dimensions of professional stock information including real-time quotes, historical data, financial analysis, capital flow, technical analysis, and Shanghai-Shenzhen-Hong Kong Stock Connect.

> **Important Notice**: This plugin is a Dify platform integration tool based on the AKShare library. AKShare is an open-source financial data interface library designed for academic research purposes. We express our sincere gratitude to the AKShare project team for their excellent work.

## 🚀 Core Features

### 💎 **No API Key Required**
- ✅ **Zero Configuration**: No need to apply for any API keys or tokens
- ✅ **Plug and Play**: Ready to use immediately after installation, no complex configuration required
- ✅ **Cost Savings**: Completely free to use with no usage limits

### 🌐 **Authoritative Data Sources**
- 📊 **East Money (东方财富网)**: Real-time quotes, financial data, market analysis
- 📈 **Sina Finance (新浪财经)**: Historical quotes, stock news
- 🏢 **Tonghuashun (同花顺)**: Technical indicators, capital flow analysis
- 💰 **Tencent Finance (腾讯财经)**: Hong Kong and US stock data
- 📱 **NetEase Finance (网易财经)**: Market overview, individual stock information
- 🔗 **Public APIs**: Official stock exchange data interfaces

### 🛠️ **Powerful Feature Matrix**
- 🎯 **8 Professional Tools**: Covering all aspects of stock data analysis
- 🌍 **113 Data Interfaces**: Extensive coverage of major global stock markets
- 📊 **Multi-Market Support**: A-shares, B-shares, Hong Kong stocks, US stocks, STAR Market, Beijing Stock Exchange
- 🔄 **Real-time + Historical**: Both real-time quotes and historical data analysis
- 📋 **Dual Output**: Markdown tables + JSON format for easy reading and processing

### 🔧 **Technical Advantages**
- 🛡️ **Smart Error Handling**: Automatic retry mechanism with graceful error recovery
- 🌐 **Full Unicode Support**: Perfect handling of Chinese characters and special symbols
- ⚡ **Performance Optimization**: Subprocess isolation and efficient memory management
- 🔄 **Parameter Validation**: Automatic parameter validation and format conversion

## 👥 Target Users

### 🎓 **Academic Researchers**
- Finance researchers conducting market analysis and academic studies
- Economics scholars studying stock market volatility patterns
- Data science researchers performing quantitative analysis

### 🤖 **AI Application Developers**
- Building intelligent investment assistants and financial chatbots
- Developing stock analysis and prediction models
- Creating automated investment decision systems

## 📦 How to Install

### Method 1: Dify Plugin Marketplace Installation (Recommended)
1. Open your Dify workspace
2. Navigate to **Tools** → **Browse Marketplace**
3. Search for **"AKShare Stock Data"** or **"AKShare 股票数据"**
4. Click the **Install** button
5. Wait for installation to complete and start using

### Method 2: Install via GitHub
1. Visit the plugin repository: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
2. Download the latest version plugin package (.difypkg file)
3. In your Dify workspace:
   - Navigate to **Tools** → **Local Plugins**
   - Click **Upload Plugin**
   - Select the downloaded .difypkg file
   - Confirm installation

### Method 3: Manual Installation
1. Clone this repository locally
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. Install Python dependencies
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. Package the plugin using Dify CLI
   ```bash
   dify plugin package
   ```
4. Upload the generated .difypkg file in Dify

## 🎯 How to Use

### Quick Start in Three Steps
1. **Select Tool**: Choose from 8 professional tools
2. **Select Interface**: Choose from 113 data interfaces for specific data sources
3. **Set Parameters**: Configure stock codes, date ranges, and other parameters

### Usage Examples

#### Get Stock Historical Quotes
```json
{
  "interface": "East Money - A-Share Historical Market Data",
  "symbol": "600519",
  "period": "daily",
  "start_date": "20240101",
  "end_date": "20241231",
  "adjust": "qfq"
}
```

#### Get Real-time Quote Data
```json
{
  "interface": "East Money - Shanghai A-Share Real-time Market",
  "symbol": "600519"
}
```

#### Query Individual Stock Financial Data
```json
{
  "interface": "East Money - Performance Express - Balance Sheet",
  "date": "20240331"
}
```

## 🛠️ Tool Details

### 🏠 **Tool 1: Stock Market Summary**
- **Interface Count**: 13
- **Function**: Get overall market overview and statistical data, including SSE and SZSE market summaries, equity pledge data, goodwill data, stock account statistics, stock comments, IPO subscription yields, suspension/resumption alerts, dividend distribution alerts, etc.
- **Use Cases**: Market analysis, macroeconomic research, risk monitoring

### 📊 **Tool 2: Stock Real-time Quotes**  
- **Interface Count**: 17
- **Function**: Get real-time stock quote data from various markets, including Shanghai/Shenzhen/Beijing A-shares, Hong Kong stocks, US stocks real-time quotes, new stock data, AH stock comparison, famous stock real-time quotes, etc.
- **Use Cases**: Real-time monitoring, trading decisions, cross-market comparison

### 📈 **Tool 3: Stock Historical Quotes**
- **Interface Count**: 9  
- **Function**: Get historical price data, including A-shares, Hong Kong stocks, US stocks daily and minute data, STAR Market historical data, pre-market data, etc.
- **Use Cases**: Technical analysis, backtesting research, quantitative modeling

### 🏢 **Tool 4: Individual Stock Information Summary**
- **Interface Count**: 14
- **Function**: Get individual stock basic information, financial data, research reports, including A-shares and Hong Kong stocks information, quotes, main business, news, dividend distribution, balance sheets, etc.
- **Use Cases**: Fundamental analysis, investment research, value assessment

### 💰 **Tool 5: Stock Financial Data Analysis**
- **Interface Count**: 14
- **Function**: Get financial statements and performance data, including A-shares performance reports (profit statements, cash flow statements, balance sheets), TongHuaShun financial indicators, Hong Kong and US stock financial data, etc.
- **Use Cases**: Financial analysis, value investing, cross-market comparison

### 🌊 **Tool 6: Capital Flow Analysis**
- **Interface Count**: 11
- **Function**: Analyze capital flow and market sentiment, including individual stock fund flow, sector fund flow rankings, main fund flow, industry and concept historical fund flow, chip distribution, etc.
- **Use Cases**: Capital flow analysis, market sentiment assessment, main force tracking

### 📊 **Tool 7: Stock Technical Analysis**
- **Interface Count**: 18
- **Function**: Technical indicators and new high/low data, including innovation highs/lows, continuous rise/fall, volume analysis, moving average breakthroughs, price-volume analysis, ESG ratings, individual stock indicators, dividend yields, etc.
- **Use Cases**: Technical analysis, trend judgment, ESG investing, dividend investing

### 🌉 **Tool 8: Shanghai-Shenzhen-Hong Kong Stock Connect Holdings**
- **Interface Count**: 7
- **Function**: Northbound capital holdings and flow data, including Hong Kong Stock Connect components, HSGT minute data, sector rankings, stock rankings, real-time quotes, historical data, specific stock holdings, etc.
- **Use Cases**: Foreign capital trend analysis, market sentiment, northbound capital tracking

## 🔒 Privacy & Security

This plugin strictly adheres to data privacy protection principles:
- ✅ **No User Data Storage**: All data is processed only in memory, no persistent storage
- ✅ **No Personal Information Collection**: Does not obtain or transmit any user personal sensitive information  
- ✅ **Transparent Data Processing**: All data sources and processing procedures are completely transparent
- ✅ **Open Source Auditable**: Source code is completely open for review and verification

For detailed information, please refer to [Privacy Policy](PRIVACY.md)

## ⚖️ Compliance Statement

This plugin fully complies with relevant laws and regulations:
- 📋 **Open Source Compliance**: Open source project based on MIT license
- 🌐 **Data Compliance**: Only uses publicly accessible data sources
- 🔍 **Transparent Operations**: Data acquisition methods and processing procedures are completely transparent
- ⚖️ **Legal Compliance**: Strictly adheres to relevant financial data usage regulations

For detailed information, please refer to [Legal Notice](LEGAL.md)

## 🙏 Acknowledgments

### AKShare Project Team
This plugin is built on the excellent [AKShare](https://github.com/akfamily/akshare) library. We extend our sincere gratitude to:
- **AKShare Development Team**: For creating and maintaining this comprehensive financial data interface library
- **Open Source Community Contributors**: For valuable contributions to the project's development

### Dify Platform
Thanks to the [Dify](https://dify.ai/) team for providing an excellent AI application development platform that makes AI applications for financial data more convenient.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Note**: This plugin is a wrapper tool for the AKShare library. For underlying data access functionality, please refer to AKShare's MIT license terms.

## 🤝 Contributing

We welcome community contributions! Please follow these steps to participate:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## 📞 Technical Support

If you encounter problems or have suggestions:
1. Check the [Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues) page
2. Create a new issue with detailed information
3. Refer to AKShare official documentation

## 📚 Detailed Tool Function Documentation

### Tool 1: Stock Market Summary

#### SSE - Stock Data Summary
**Function**: Retrieve comprehensive market overview data from Shanghai Stock Exchange, including circulating shares, total market value, average P/E ratio, number of listed companies and other key indicators for macroeconomic market analysis and investment decision reference.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest trading day's market summary data.

**Reference Information**:
**Interface**: `stock_sse_summary`
**Target URL**: http://www.sse.com.cn/market/stockdata/statistic/
**Description**: Shanghai Stock Exchange - Stock Data Summary
**Limit**: Returns stock data summary for the most recent trading day (current trading day data requires post-market statistics)

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_sse_summary_df = ak.stock_sse_summary()
print(stock_sse_summary_df)
```

#### SZSE - Market Overview - Securities Category Statistics
**Function**: Retrieve market statistics data from Shenzhen Stock Exchange categorized by security types, including quantity, trading amount, total market value and circulating market value for stocks, funds, bonds and other securities.

**Parameter Input**: Requires trading date parameter in YYYYMMDD format to query market overview data for the specified date. Current trading day data can only be obtained after exchange closing.

**Reference Information**:
**Interface**: `stock_szse_summary`
**Target URL**: http://www.szse.cn/market/overview/index.html
**Description**: Shenzhen Stock Exchange - Market Overview - Securities Category Statistics
**Limit**: Returns market overview data for specified date - Securities Category Statistics (current trading day data requires post-market statistics)

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| date | str  | date="20200619"; Current trading day data requires post-market statistics |

**Interface Example**
```python
import akshare as ak
stock_szse_summary_df = ak.stock_szse_summary(date="20200619")
print(stock_szse_summary_df)
```

#### SSE - Daily Stock Situation
**Function**: Retrieve detailed daily stock trading situation from Shanghai Stock Exchange, including number of listed stocks, market capitalization, circulating market value, trading amount, trading volume, average P/E ratio, turnover rate and other key trading indicators.

**Parameter Input**: Requires trading date parameter in YYYYMMDD format. Note that only data from December 27, 2021 (inclusive) onwards is supported, and current trading day data needs to be obtained after closing.

**Reference Information**:
**Interface**: `stock_sse_deal_daily`
**Target URL**: http://www.sse.com.cn/market/stockdata/overview/day/
**Description**: Shanghai Stock Exchange - Data - Stock Data - Trading Overview - Stock Trading Overview - Daily Stock Situation
**Limit**: Returns daily overview data for specified date, current trading day data needs to be obtained after closing; note that only data from 20211227 (inclusive) onwards is supported

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| date | str  | date="20250221"; Current trading day data requires post-exchange statistics; note that only data from 20211227 (inclusive) onwards is supported |

**Interface Example**
```python
import akshare as ak
stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date="20250221")
print(stock_sse_deal_daily_df)
```

#### East Money - Shanghai-Shenzhen Individual Stocks - Risk Warning Board
**Function**: Retrieve the list of individual stocks with risk warnings (ST, *ST, etc.) in Shanghai and Shenzhen markets along with their basic trading information, used to identify and monitor high-risk stocks and help investors avoid investment risks.

**Parameter Input**: This interface requires no input parameters. Call directly to get real-time data of all current risk warning board stocks.

**Reference Information**:
**Interface**: `stock_zh_a_st_em`
**Target URL**: https://quote.eastmoney.com/center/gridlist.html#st_board
**Description**: East Money - Shanghai-Shenzhen Individual Stocks - Risk Warning Board
**Limit**: Returns all Shanghai-Shenzhen individual stock risk warning board data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_zh_a_st_em_df = ak.stock_zh_a_st_em()
print(stock_zh_a_st_em_df)
```

#### East Money - Stock Market Calendar - Company News
**Function**: Retrieve important company news information for specified dates, including shareholder meetings, board meetings, earnings releases, dividend distributions and other significant corporate events, used to track major company matters and investment opportunities.

**Parameter Input**: Requires query date parameter in YYYYMMDD format to get company news information for that date.

**Reference Information**:
**Interface**: `stock_gsrl_gsdt_em`
**Target URL**: https://data.eastmoney.com/gsrl/gsdt.html
**Description**: East Money - Data Center - Stock Market Calendar - Company News
**Limit**: Returns company news data for specified date

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| date | str  | date="20240401"; Date format |

**Interface Example**
```python
import akshare as ak
stock_gsrl_gsdt_em_df = ak.stock_gsrl_gsdt_em(date="20240401")
print(stock_gsrl_gsdt_em_df)
```

#### East Money - Equity Pledge - Market Overview
**Function**: Retrieve overall overview data of equity pledges in A-share market, including number of pledge companies, pledged shares quantity, pledge market value and other statistical information, used to analyze market equity pledge risk conditions.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest equity pledge market overview data.

**Reference Information**:
**Interface**: `stock_gpzy_profile_em`
**Target URL**: https://data.eastmoney.com/gpzy/
**Description**: East Money - Data Center - Special Data - Equity Pledge - Equity Pledge Market Overview
**Limit**: Returns equity pledge market overview data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_gpzy_profile_em_df = ak.stock_gpzy_profile_em()
print(stock_gpzy_profile_em_df)
```

#### East Money - Equity Pledge - Listed Company Pledge Ratio - Industry Data
**Function**: Retrieve statistical data of equity pledge ratios for listed companies by industry, including number of pledge companies, average pledge ratio, pledge market value and other industry-dimension pledge analysis data.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest industry equity pledge data.

**Reference Information**:
**Interface**: `stock_gpzy_industry_data_em`
**Target URL**: https://data.eastmoney.com/gpzy/
**Description**: East Money - Data Center - Special Data - Equity Pledge - Listed Company Pledge Ratio - Industry Data
**Limit**: Returns industry equity pledge data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_gpzy_industry_data_em_df = ak.stock_gpzy_industry_data_em()
print(stock_gpzy_industry_data_em_df)
```

#### East Money - Goodwill - A-Share Goodwill Market Overview
**Function**: Retrieve overall overview data of goodwill in A-share market, including total goodwill amount, goodwill ratio to net assets, goodwill impairment and other statistical information, used to analyze goodwill risks of listed companies.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest A-share goodwill market overview data.

**Reference Information**:
**Interface**: `stock_sy_profile_em`
**Target URL**: https://data.eastmoney.com/sy/
**Description**: East Money - Data Center - Special Data - Goodwill - A-Share Goodwill Market Overview
**Limit**: Returns A-share goodwill market overview data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_sy_profile_em_df = ak.stock_sy_profile_em()
print(stock_sy_profile_em_df)
```

#### East Money - Special Data - Stock Account Statistics
**Function**: Retrieve statistical data of investor accounts in A-share market, including new account openings, ending account numbers and other investor structure information, used to analyze market participation and investor sentiment.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest stock account statistics data.

**Reference Information**:
**Interface**: `stock_account_statistics_em`
**Target URL**: https://data.eastmoney.com/cjsj/gpkhsj.html
**Description**: East Money - Data Center - Special Data - Stock Account Statistics
**Limit**: Returns stock account statistics data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_account_statistics_em_df = ak.stock_account_statistics_em()
print(stock_account_statistics_em_df)
```

#### East Money - Special Data - Stock Comments
**Function**: Retrieve professional evaluations and technical analysis of A-share individual stocks, including main force cost, institutional attention, comprehensive evaluation and other multi-dimensional stock assessment information, providing reference for investment decisions.

**Parameter Input**: This interface requires no input parameters. Call directly to get stock comments data for the entire market.

**Reference Information**:
**Interface**: `stock_comment_em`
**Target URL**: https://data.eastmoney.com/stockcomment/
**Description**: East Money - Data Center - Special Data - Stock Comments
**Limit**: Returns stock comments data for entire market

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_comment_em_df = ak.stock_comment_em()
print(stock_comment_em_df)
```

#### East Money - IPO Subscription - Lottery Yield
**Function**: Retrieve yield statistics data for IPO subscriptions, including winning yields, annualized returns and other new stock investment return analysis, helping investors evaluate the effectiveness of IPO subscription strategies.

**Parameter Input**: This interface requires no input parameters. Call directly to get the latest IPO subscription yield data.

**Reference Information**:
**Interface**: `stock_dxsyl_em`
**Target URL**: https://data.eastmoney.com/xg/xg/dxsyl.html
**Description**: East Money - Data Center - IPO Subscription - Lottery Yield
**Limit**: Returns lottery yield data

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_dxsyl_em_df = ak.stock_dxsyl_em()
print(stock_dxsyl_em_df)
```

#### Baidu Stock - Trading Alert - Suspension & Resumption
**Function**: Retrieve alert information for stock suspension and resumption in A-share market, including suspension reasons, suspension time, expected resumption time, etc., helping investors stay informed about stock trading status changes.

**Parameter Input**: Requires query date parameter in YYYYMMDD format to get suspension and resumption alert information for that date.

**Reference Information**:
**Interface**: `news_trade_notify_suspend_baidu`
**Target URL**: https://gupiao.baidu.com/
**Description**: Baidu Stock - Trading Alert - Suspension & Resumption
**Limit**: Returns suspension and resumption alert data for specified date

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| date | str  | date="20240401"; Date format |

**Interface Example**
```python
import akshare as ak
news_trade_notify_suspend_baidu_df = ak.news_trade_notify_suspend_baidu(date="20240401")
print(news_trade_notify_suspend_baidu_df)
```

#### Baidu Stock - Trading Alert - Dividend Distribution
**Function**: Retrieve alert information for stock dividend distributions in A-share market, including ex-dividend dates, dividend plans, dividend amounts and other important dividend information, helping investors seize dividend investment opportunities.

**Parameter Input**: Requires query date parameter in YYYYMMDD format to get dividend distribution alert information for that date.

**Reference Information**:
**Interface**: `news_trade_notify_dividend_baidu`
**Target URL**: https://gupiao.baidu.com/
**Description**: Baidu Stock - Trading Alert - Dividend Distribution
**Limit**: Returns dividend distribution alert data for specified date

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| date | str  | date="20240401"; Date format |

**Interface Example**
```python
import akshare as ak
news_trade_notify_dividend_baidu_df = ak.news_trade_notify_dividend_baidu(date="20240401")
print(news_trade_notify_dividend_baidu_df)
```

### Tool 2: Stock Real-time Quotes

#### East Money - Shanghai A-Share - Real-time Market Data
**Function**: Retrieve real-time market data for Shanghai Stock Exchange A-share market, including stock prices, price changes, trading volume, trading value, turnover rate and other key trading indicators for real-time monitoring of Shanghai A-share performance.

**Parameter Input**: This interface requires no input parameters. Call directly to get real-time market data for all Shanghai A-shares.

**Reference Information**:
**Interface**: `stock_sh_a_spot_em`
**Target URL**: https://quote.eastmoney.com/center/gridlist.html#sh_a_board
**Description**: East Money - Shanghai A-Shares
**Limit**: Returns real-time market data for all Shanghai A-shares

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| -    | -    | -           |

**Interface Example**
```python
import akshare as ak
stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
print(stock_sh_a_spot_em_df)
```

### Tool 3: Stock Historical Quotes

#### East Money - Shanghai-Shenzhen-Beijing A-Share - Daily Data
**Function**: Retrieve daily historical market data for Shanghai-Shenzhen-Beijing A-share markets, including complete daily data such as opening price, closing price, highest price, lowest price, trading volume, trading value, with support for forward adjustment, backward adjustment and other adjustment methods.

**Parameter Input**: Requires input of stock code, period (daily/weekly/monthly), start date, end date, adjustment method and other parameters to get historical market data for specified time period.

**Reference Information**:
**Interface**: `stock_zh_a_hist`
**Target URL**: https://finance.sina.com.cn/
**Description**: Sina Finance - A-Share Historical Market Data
**Limit**: Returns historical market data for specific stock

**Input Parameters**
| Name | Type | Description |
|------|------|-------------|
| symbol | str | symbol="000001"; Stock code |
| period | str | period="daily"; choice of {"daily", "weekly", "monthly"} |
| start_date | str | start_date="20170301"; Start date |
| end_date | str | end_date="20210907"; End date |
| adjust | str | adjust=""; choice of {"qfq": "Forward adjusted", "hfq": "Backward adjusted", "": "Not adjusted"} |

**Interface Example**
```python
import akshare as ak
stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date="20210907", adjust="")
print(stock_zh_a_hist_df)
```

### 🔗 Other Tool Interface Documentation

**Tool 4: Individual Stock Information Summary** - 14 interfaces, including East Money individual stock information, market quotes, TongHuaShun main business introduction, news information, company profile, IPO information, dividend distribution, research reports, balance sheets, financial summaries, Hong Kong stock security profiles, etc.

**Tool 5: Stock Financial Data Analysis** - 14 interfaces, including East Money performance reports (profit statements, cash flow statements, balance sheets), Beijing Stock Exchange performance reports, TongHuaShun financial indicators, Sina Finance financial statements, Hong Kong and US stock financial analysis, etc.

**Tool 6: Capital Flow Analysis** - 11 interfaces, including East Money individual stock fund flow, fund flow rankings, market fund flow, sector fund flow, main fund flow, industry fund flow, concept fund flow, TongHuaShun fund flow big deal tracking, HSGT fund flow, chip distribution, etc.

**Tool 7: Stock Technical Analysis** - 18 interfaces, including TongHuaShun technical stock selection (innovation highs/lows, continuous rise/fall, continuous volume increase/decrease, moving average breakthroughs, price-volume analysis, insurance capital placard raising), Sina Finance ESG ratings, LeGuGu individual stock indicators, dividend yields, equity-bond spreads, Buffett indicators, etc.

**Tool 8: Shanghai-Shenzhen-Hong Kong Stock Connect Holdings** - 7 interfaces, including East Money Hong Kong Stock Connect components, HSGT minute data, sector rankings, stock rankings, Hong Kong Stock Connect real-time quotes, HSGT historical data, specific stock holdings, etc.

For detailed parameter descriptions, function explanations and interface examples, please refer to each tool's configuration files or interface prompts when using the plugin.

## 🎯 Demo and Examples

### 📋 **Dify Workflow Demo**

We provide two complete Dify workflow demo files that showcase how to use various features of the AKShare Stock Data Plugin:

#### 🔧 **Demo File 1: Plugin Functionality Demo**
**File**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**Description**: Demonstrates the usage of all plugin tools and their interfaces, showcasing the complete functionality of 8 professional tools

**Demo Content**:
- **Stock Market Summary** - Market overview data acquisition
- **Individual Stock Information Summary** - Individual stock detailed information queries
- **Real-time Stock Quotes** - Real-time price data acquisition
- **Historical Stock Quotes** - Historical price data analysis
- **Shanghai-Shenzhen-Hong Kong Stock Connect Holdings** - Northbound capital holdings
- **Capital Flow Analysis** - Capital flow data analysis
- **Stock Financial Data Analysis** - Financial statement data acquisition
- **Stock Technical Analysis** - Technical indicator calculations

**Demo Features**:
- **Smart Conditional Branching** - Automatically selects appropriate data interfaces based on user input
- **Data Format Conversion** - Automatically converts Markdown tables to Excel files
- **Multi-dimensional Display** - Covers usage scenarios for all 8 professional tools
- **Complete Workflow** - Complete process from data acquisition to result display

#### 🤖 **Demo File 2: Individual Stock Deep Analysis Application**
**File**: `应用示例/个股行情分析-ChatFlow.yml`

**Description**: Individual stock deep analysis ChatFlow application based on AKShare Stock Data Plugin, providing multi-dimensional stock analysis

**Core Features**:
- **Intelligent Stock Recognition** - Automatically identifies stock codes and market types (Shanghai A-share, Shenzhen A-share, Beijing Stock Exchange)
- **Historical Quote Analysis** - Technical analysis based on one-year historical data
- **Financial Indicator Analysis** - Fundamental analysis based on financial data
- **Fund Flow Analysis** - Fund flow analysis based on capital flow data
- **Individual Stock Research Reports** - Access to latest individual stock research reports
- **Comprehensive Investment Recommendations** - Investment recommendations based on multi-dimensional data

**Technical Features**:
- **Dynamic Date Calculation** - Automatically calculates the latest historical data time range
- **A-share Market Validation** - Intelligently identifies and validates A-share stock codes
- **Multi-data Source Integration** - Integrates historical quotes, financial data, fund flow, research reports and other multi-dimensional data
- **Professional Analysis Reports** - Generates comprehensive analysis reports including technical, fundamental, and fund flow aspects

#### 🔧 **How to Use the Demo**
1. Import the corresponding demo file in the Dify platform
2. Ensure the AKShare Stock Data Plugin is installed
3. Run the workflow to experience various stock data features
4. Modify and customize the workflow as needed

### 📞 **Support**

For detailed interface usage instructions, please refer to:
- 📖 **[Detailed Function Documentation](AKShare%20股票数据插件详细功能文档.md)** - Complete technical documentation
- 🎯 **[Workflow Demo](应用示例/AKShare%20股票数据插件%20CHATFLOW-DEMO.yml)** - Complete demo example
- 🔧 **Plugin Configuration Files** - YAML configurations for each tool in the tools directory
- 📚 **AKShare Official Documentation** - https://github.com/akfamily/akshare

---

**Last Updated**: 2025-09-17  
**Version**: 0.5.0  
**Author**: AKShare Stock Data Plugin Team  
**License**: MIT License
# AKShare 股票數據插件 for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

## 📞 聯繫方式

- **作者**: shaoxing-xie
- **郵箱**: sxxiefg@163.com
- **代碼庫**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **問題反饋**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 概述

**AKShare 股票數據插件** 是一個專為 Dify 平台開發的綜合性股票數據工具，基於知名的 [AKShare](https://github.com/akfamily/akshare) Python 庫構建。本插件為用戶提供了一站式的股票市場數據訪問解決方案，涵蓋實時行情、歷史數據、財務分析、資金流向、技術分析、滬深港通等多個維度的專業股票信息。

> **重要聲明**: 本插件是 AKShare 庫的 Dify 平台集成工具，AKShare 是一個專為學術研究目的設計的開源金融數據接口庫。我們對 AKShare 項目團隊的卓越工作表示誠摯感謝。

## 🚀 核心特點

### 💎 **無需API密鑰**
- ✅ **零配置使用**: 無需申請任何API密鑰或令牌
- ✅ **即插即用**: 安裝後立即可用，無需複雜配置
- ✅ **成本節約**: 完全免費使用，無使用次數限制

### 🌐 **權威數據源**
- 📊 **東方財富網**: 實時行情、財務數據、市場分析
- 📈 **新浪財經**: 歷史行情、股票資訊
- 🏢 **同花順**: 技術指標、資金流向分析
- 💰 **騰訊財經**: 港股、美股數據
- 📱 **網易財經**: 市場概況、個股信息
- 🔗 **公開API**: 證券交易所官方數據接口

### 🛠️ **強大功能矩陣**
- 🎯 **8個專業工具**: 覆蓋股票數據分析的各個方面
- 🌍 **113個數據接口**: 廣泛覆蓋全球主要股票市場
- 📊 **多市場支持**: A股、B股、港股、美股、科創板、北交所
- 🔄 **實時+歷史**: 既有實時行情，也有歷史數據分析
- 📋 **雙重輸出**: Markdown表格 + JSON格式，便於閱讀和處理

### 🔧 **技術優勢**
- 🛡️ **智能錯誤處理**: 自動重試機制，優雅的錯誤恢復
- 🌐 **完整Unicode支持**: 完美處理中文字符和特殊符號
- ⚡ **性能優化**: 子進程隔離，高效內存管理
- 🔄 **參數驗證**: 自動參數校驗和格式轉換

## 👥 服務對象

### 🎓 **學術研究人員**
- 金融學研究者進行市場分析和學術研究
- 經濟學學者研究股市波動規律
- 數據科學研究者進行量化分析

### 🤖 **AI應用開發者**
- 構建智能投資助手和財經聊天機器人
- 開發基於AI的股票推薦系統
- 創建自動化金融數據分析工具

### 💼 **金融專業人士**
- 需要快速訪問市場數據的金融分析師
- 監控股票持倉的投資組合經理
- 提供基於數據洞察的投資顧問

## 📊 可用工具

### 1. 📈 **股票市場總貌** (`stock_market_summary`)
- **13個接口** 涵蓋A股市場數據
- 包括：上交所股票數據總貌、深交所證券類別統計、每日股票成交數據
- **主要接口**: `stock_sse_summary`, `stock_szse_summary`, `stock_sse_deal_daily`

### 2. 🏢 **個股信息總貌** (`stock_individual_info_summary`)
- **15個接口** 用於詳細企業信息
- 包括：企業基本信息、IPO數據、分紅信息
- **主要接口**: `stock_individual_info_em`, `stock_ipo_info`, `stock_dividend_detail`

### 3. 📊 **實時行情數據** (`stock_spot_quotations`)
- **20個接口** 用於實時市場數據
- 包括：A股、B股、港股、美股、科創板實時行情
- **主要接口**: `stock_zh_a_spot_em`, `stock_hk_spot_em`, `stock_us_spot_em`

### 4. 📈 **歷史行情數據** (`stock_hist_quotations`)
- **15個接口** 用於歷史價格數據
- 包括：日線、週線、月線、分鐘數據
- **主要接口**: `stock_zh_a_hist`, `stock_hk_hist`, `stock_us_hist`

### 5. 🔗 **滬深港通持股** (`stock_hsgt_holdings`)
- **12個接口** 用於滬深港通數據
- 包括：資金流向、持股數據、排行榜數據
- **主要接口**: `stock_hsgt_fund_flow_summary`, `stock_hsgt_hold_stock_em`

### 6. 💰 **資金流向分析** (`stock_fund_flow_analysis`)
- **18個接口** 用於資金流向分析
- 包括：行業資金流向、個股資金流向、排行榜數據
- **主要接口**: `stock_sector_fund_flow_rank`, `stock_individual_fund_flow_rank`

### 7. 📊 **股票財務分析** (`stock_financial_analysis`)
- **20個接口** 用於財務分析
- 包括：財務報表、財務指標、債務分析
- **主要接口**: `stock_financial_abstract`, `stock_balance_sheet_by_report_em`

### 8. 📈 **股票技術分析** (`stock_technical_analysis`)
- **12個接口** 用於技術指標
- 包括：移動平均線、RSI、MACD、布林帶
- **主要接口**: `stock_zh_a_hist_min_em`, `stock_zh_a_hist_pre_min_em`

## 🚀 安裝和使用

### 前置條件
- Dify Platform 1.0+
- Python 3.12+
- 網絡連接

### 安裝步驟

#### 方式一：Dify插件市場安裝（推薦）
1. 打開您的 Dify 工作空間
2. 導航至 **工具** → **瀏覽插件市場**
3. 搜索 **"AKShare 股票數據"** 或 **"AKShare Stock Data"**
4. 點擊 **安裝** 按鈕
5. 等待安裝完成，即可開始使用

#### 方式二：通過GitHub安裝
1. 訪問插件倉庫：[https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
2. 下載最新版本的插件包（.difypkg 文件）
3. 在 Dify 工作空間中：
   - 導航至 **工具** → **本地插件**
   - 點擊 **上傳插件**
   - 選擇下載的 .difypkg 文件
   - 確認安裝

#### 方式三：手動安裝
1. 克隆本倉庫到本地
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. 安裝Python依賴
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. 使用 Dify CLI 打包插件
   ```bash
   dify plugin package
   ```
4. 在 Dify 中上傳生成的 .difypkg 文件

### 基本使用
```python
# 在Dify工作流中的使用示例
{
  "interface": "stock_sse_summary",
  "retries": 5,
  "timeout": 300
}
```

## 📋 常用參數

### 網絡參數
- **retries**: 重試次數 (1-10, 默認: 5)
- **timeout**: 子進程超時時間，單位秒 (5-3600, 默認: 240)

### 日期參數
- **date**: 交易日期，格式YYYYMMDD (例: 20240101)
- **symbol**: 股票代碼 (例: 000001, 600000)

### 市場參數
- **market**: 特定市場 (A股、B股、港股、美股)
- **period**: 數據週期 (daily, weekly, monthly)

## 🔧 高級配置

### 按接口類型的超時設置
- **實時行情接口**: 15分鐘
- **財務數據接口**: 10分鐘
- **歷史數據接口**: 5分鐘
- **基礎接口**: 2分鐘

### 錯誤處理
- 指數退避自動重試
- 自動參數驗證
- 優雅的網絡錯誤恢復
- 詳細的調試日誌

## 📊 輸出示例

### Markdown格式
```markdown
| 項目 | 股票 | 主板 | 科創板 |
|------|------|------|--------|
| 流通股本 | 47466.3 | 45587.82 | 1878.47 |
| 總市值 | 615583.81 | 519873.03 | 95710.77 |
```

### JSON格式
```json
{
  "data": [
    {
      "項目": "流通股本",
      "股票": "47466.3",
      "主板": "45587.82",
      "科創板": "1878.47"
    }
  ],
  "columns": ["項目", "股票", "主板", "科創板"],
  "shape": [8, 4]
}
```

## 🤝 貢獻

歡迎貢獻！請在提交pull request前閱讀我們的貢獻指南。

### 如何貢獻
1. Fork 倉庫
2. 創建功能分支
3. 提交更改
4. 推送到分支
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件。

## 🙏 致謝

- [AKShare](https://github.com/akfamily/akshare) - Python金融數據庫
- [Dify](https://dify.ai/) - AI應用開發平台
- 所有項目貢獻者和用戶

## 📞 支持

## 🎯 演示和示例

### 📋 **Dify 工作流演示**

我們提供了兩個完整的 Dify 工作流演示文件，展示了如何使用 AKShare 股票數據插件的各種功能：

#### 🔧 **演示文件一：插件功能演示**
**文件**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**功能說明**: 演示插件所有工具及其接口的使用，展示8個專業工具的完整功能

**演示內容**:
- **股票市場總貌** - 市場概況數據獲取
- **個股信息總貌** - 個股詳細信息查詢
- **股票實時行情** - 實時價格數據獲取
- **股票歷史行情** - 歷史價格數據分析
- **滬深港通持股** - 北向資金持股情況
- **資金流向分析** - 資金流向數據分析
- **股票財務數據分析** - 財務報表數據獲取
- **股票技術分析** - 技術指標計算

**演示特色**:
- **智能條件分支** - 根據用戶輸入自動選擇合適的數據接口
- **數據格式轉換** - 自動將 Markdown 表格轉換為 Excel 文件
- **多維度展示** - 涵蓋所有8個專業工具的使用場景
- **完整工作流** - 從數據獲取到結果展示的完整流程

#### 🤖 **演示文件二：個股深度分析應用**
**文件**: `应用示例/个股行情分析-ChatFlow.yml`

**功能說明**: 基於AKShare股票數據插件的個股深度分析ChatFlow應用，提供多維度股票分析

**核心功能**:
- **智能股票識別** - 自動識別股票代碼和市場類型（滬市A股、深市A股、北交所）
- **歷史行情分析** - 基於一年期歷史數據的技術面分析
- **財務指標分析** - 基於財務數據的基本面分析
- **資金流向分析** - 基於資金流向的資金面分析
- **個股研報獲取** - 獲取最新的個股研究報告
- **綜合投資建議** - 基於多維度數據的投資建議

**技術特色**:
- **動態日期計算** - 自動計算最新的歷史數據時間範圍
- **A股市場驗證** - 智能識別並驗證A股股票代碼
- **多數據源整合** - 整合歷史行情、財務數據、資金流向、研報等多維度數據
- **專業分析報告** - 生成包含技術面、基本面、資金面的綜合分析報告

#### 🔧 **如何使用演示**
1. 在 Dify 平台中導入相應的演示文件
2. 確保已安裝 AKShare 股票數據插件
3. 運行工作流，體驗各種股票數據功能
4. 根據需要修改和定制工作流

如需支持和問題：
- 在GitHub開啟issue
- 查閱官方文檔
- 聯繫開發團隊

---

**為金融數據社區用心開發 ❤️**

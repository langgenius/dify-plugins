# AKShare 股票数据插件详细功能文档

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

> **文档说明**: 本文档是 AKShare 股票数据插件的详细功能文档，包含所有78个工具共190+个接口的完整技术说明。文档按功能域分类组织，便于查找和使用。

---

## 📑 文档目录（按功能域分类）

### 一、市场总貌类工具 (20个工具)
- [获取交易所市场总貌](#获取交易所市场总貌-get_exchange_market_overview)
- [获取股权质押数据](#获取股权质押数据-get_equity_pledge_data)
- [获取商誉数据](#获取商誉数据-get_goodwill_data)
- [获取股票账户统计](#获取股票账户统计-get_stock_account_statistics)
- [获取A股市场股东户数数据](#获取a股市场股东户数数据-get_shareholder_number_data)
- [获取股票评论数据](#获取股票评论数据-get_stock_comment_data)
- [获取IPO申购数据](#获取ipo申购数据-get_ipo_subscription_data)
- [获取交易事件通知](#获取交易事件通知-get_trading_event_notifications)
- [获取市场机构持股数据](#获取市场机构持股数据-get_institute_holdings_data)
- [获取个股评级记录与估值分析](#获取个股评级记录与估值分析-get_stock_rating_valuation)
- [获取公司公告数据](#获取公司公告数据-get_company_announcements)
- [获取公司信息披露数据](#获取公司信息披露数据-get_company_disclosure)
- [获取股票列表数据](#获取股票列表数据-get_stock_list)
- [获取龙虎榜数据](#获取龙虎榜数据-get_dragon_tiger_list)
- [获取大宗交易数据](#获取大宗交易数据-get_block_trading)
- [获取A股市场融资融券数据](#获取a股市场融资融券数据-get_margin_trading)
- [获取同花顺板块数据](#获取同花顺板块数据-get_board_ths)
- [获取东方财富板块数据](#获取东方财富板块数据-get_board_em)
- [获取A股市场股票热度数据](#获取a股市场股票热度数据-get_stock_hot)
- [获取A股市场涨停板行情数据](#获取a股市场涨停板行情数据-get_limit_up_down)

### 二、个股信息类工具 (6个工具)
- [获取个股基本信息](#获取个股基本信息-get_stock_basic_info)
- [获取个股新闻研报](#获取个股新闻研报-get_stock_news_research)
- [获取个股分红派息信息](#获取个股分红派息信息-get_stock_dividend_info)
- [获取个股股东持股变动信息](#获取个股股东持股变动信息-get_shareholder_holding_changes)
- [获取A股股东户数数据](#获取a股股东户数数据-get_stock_shareholder_number_detail)
- [获取股票发行与上市数据](#获取股票发行与上市数据-get_stock_issuance_release)

### 三、行情数据类工具 (8个工具)
- [获取个股实时行情](#获取个股实时行情-get_stock_real_time_quote)
- [获取个股历史行情](#获取个股历史行情-get_stock_historical_quotes)
- [获取个股日内分时行情](#获取个股日内分时行情-get_stock_intraday_quotes)
- [获取个股同行业对比](#获取个股同行业对比-get_stock_peer_comparison)
- [获取A股市场股票行情](#获取a股市场股票行情-get_a_share_market_quotes)
- [获取A股板块行情](#获取a股板块行情-get_a_share_board_quotes)
- [获取A股市场股票比价数据](#获取a股市场股票比价数据-get_stock_comparison_quotes)
- [获取A股市场特殊股票行情](#获取a股市场特殊股票行情-get_special_stock_quotes)

### 四、财务数据类工具 (6个工具)
- [获取A股业绩快报数据](#获取a股业绩快报数据-get_stock_performance_reports)
- [获取A股资产负债表](#获取a股资产负债表-get_stock_balance_sheet)
- [获取A股利润表](#获取a股利润表-get_stock_profit_sheet)
- [获取A股现金流量表](#获取a股现金流量表-get_stock_cash_flow_sheet)
- [获取A股财务指标](#获取a股财务指标-get_stock_financial_indicators)
- [获取A股财务分析指标](#获取a股财务分析指标-get_stock_financial_analysis_indicators)

### 五、资金流向类工具 (6个工具)
- [获取个股资金流向](#获取个股资金流向-get_stock_fund_flow)
- [获取个股筹码分布](#获取个股筹码分布-get_stock_chip_distribution)
- [获取市场股票资金流向排名](#获取市场股票资金流向排名-get_market_stock_fund_flow_rank)
- [获取市场资金流向历史](#获取市场资金流向历史-get_market_fund_flow_history)
- [获取板块资金流向排名](#获取板块资金流向排名-get_sector_fund_flow_rank)
- [获取大单追踪](#获取大单追踪-get_big_deal_tracking)

### 六、技术分析类工具 (7个工具)
- [获取技术选股-创新高新低](#获取技术选股-创新高新低-get_technical_innovation_high_low)
- [获取技术选股-连续涨跌](#获取技术选股-连续涨跌-get_technical_continuous_rise_fall)
- [获取技术选股-成交量分析](#获取技术选股-成交量分析-get_technical_volume_analysis)
- [获取技术选股-突破分析](#获取技术选股-突破分析-get_technical_breakthrough_analysis)
- [获取技术选股-价量分析](#获取技术选股-价量分析-get_technical_price_volume_analysis)
- [获取技术选股-保险披露](#获取技术选股-保险披露-get_technical_insurance_disclosure)
- [获取ESG评级数据](#获取esg评级数据-get_esg_rating_data)

### 七、技术指标类工具 (5个工具) ⭐ **扩展指标工具**
- [获取个股趋势动量震荡指标(日频)](#获取个股趋势动量震荡指标日频-get_stock_trend_momentum_daily)
- [获取个股趋势动量震荡指标(分钟)](#获取个股趋势动量震荡指标分钟-get_stock_trend_momentum_minute)
- [获取个股动态估值指标](#获取个股动态估值指标-get_stock_dynamic_valuation)
- [获取个股历史估值指标](#获取个股历史估值指标-get_stock_historical_valuation)
- [获取个股基本信息汇总](#获取个股基本信息汇总-get_stock_basic_info_summary)

### 八、沪深港通类工具 (4个工具)
- [获取沪深港通汇率数据](#获取沪深港通汇率数据-get_hsgt_exchange_rate_data)
- [获取沪深港通资金流向数据](#获取沪深港通资金流向数据-get_hsgt_fund_flow_data)
- [获取沪深港通排名数据](#获取沪深港通排名数据-get_hsgt_ranking_data)
- [获取沪深港通个股持仓](#获取沪深港通个股持仓-get_hsgt_individual_holdings)

### 九、指数数据类工具 (3个工具) ⭐ **指数分析工具**
- [获取A股指数实时行情](#获取a股指数实时行情-get_index_spot_quotes)
- [获取A股指数历史行情](#获取a股指数历史行情-get_index_historical_quotes)
- [获取指数趋势动量震荡指标(日频)](#获取指数趋势动量震荡指标日频-get_index_trend_momentum_daily)

### 十、港股数据类工具 (8个工具) ⭐ **独立工具**
- [获取港股个股基本信息](#获取港股个股基本信息-get_hk_individual_info)
- [获取港股个股历史行情](#获取港股个股历史行情-get_hk_historical_quotes)
- [获取港股每日分时行情](#获取港股每日分时行情-get_hk_daily_minute_quotes)
- [获取港股个股分红派息数据](#获取港股个股分红派息数据-get_hk_dividend_payout)
- [获取港股财务指标](#获取港股财务指标-get_hk_financial_indicators)
- [获取港股财务报表](#获取港股财务报表-get_hk_financial_statements)
- [获取港股个股行业对比数据](#获取港股个股行业对比数据-get_hk_industry_comparison)
- [获取港股实时行情](#获取港股实时行情-get_hk_spot_quotes)

### 十一、美股数据类工具 (5个工具) ⭐ **独立工具**
- [获取美股市场实时行情](#获取美股市场实时行情-get_us_spot_quotes)
- [获取美股个股历史行情](#获取美股个股历史行情-get_us_historical_quotes)
- [获取美股每日分时行情](#获取美股每日分时行情-get_us_daily_minute_quotes)
- [获取美股财务指标](#获取美股财务指标-get_us_financial_indicators)
- [获取美股财务报表](#获取美股财务报表-get_us_financial_statements)

---

## 🔄 版本兼容性

### 从0.6.0升级到0.7.0
- ✅ **工具拆分优化**: 从12个大工具拆分为78个细粒度工具，更便于精确调用
- ✅ **功能域分类**: 按功能域分类展示，更便于查找和使用
- ✅ **完全向后兼容**: 所有基于0.6.0版本的工作流可直接使用，无需修改
- ✅ **功能增强**: 获得更多数据接口和功能

🔗 **[详细升级指南](UPGRADE_GUIDE.md)**

## 🎯 服务对象

### 👨‍🎓 **学术研究人员**
- 金融学研究者进行市场分析和学术研究
- 经济学学者研究股市波动规律
- 数据科学研究者进行量化分析

### 💼 **AI应用开发者**
- 构建股票分析AI助手
- 开发量化交易系统
- 创建投资决策支持工具

---

## 📊 工具统计

| 功能域 | 工具数量 | 接口数量 |
|--------|---------|---------|
| 市场总貌类 | 20 | 60+ |
| 个股信息类 | 6 | 20+ |
| 行情数据类 | 8 | 25+ |
| 财务数据类 | 6 | 15+ |
| 资金流向类 | 6 | 15+ |
| 技术分析类 | 7 | 15+ |
| 技术指标类 | 5 | 5 |
| 沪深港通类 | 4 | 15+ |
| 指数数据类 | 3 | 7 |
| 港股数据类 | 8 | 30+ |
| 美股数据类 | 5 | 15+ |
| **总计** | **78** | **190+** |

---

## 一、市场总貌类工具（20个工具）

### 获取交易所市场总貌 (get_exchange_market_overview)

**工具说明**: 获取上海证券交易所和深圳证券交易所的市场概况数据，包括总市值、流通市值、上市公司数量、平均市盈率等关键指标。支持获取最新交易日数据和指定交易日的历史数据。

**接口列表**:
1. **上交所股票数据总貌-最近交易日** (`stock_sse_summary`)
   - **功能**: 获取上海证券交易所最近交易日的市场概况数据，包括总市值、流通市值、上市公司数量、平均市盈率、成交金额、成交量、换手率等关键指标
   - **参数**: 无需参数，自动返回最近交易日数据
   - **AKShare接口**: `stock_sse_summary`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回最近交易日的市场概况数据

2. **深交所证券类别统计-指定交易日** (`stock_szse_summary`)
   - **功能**: 获取深圳证券交易所指定交易日的证券类别统计数据，包括总市值、流通市值、上市公司数量、平均市盈率、成交金额、成交量、换手率等关键指标
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）
   - **AKShare接口**: `stock_szse_summary`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定交易日的证券类别统计数据

3. **上交所每日股票概况-指定交易日** (`stock_sse_deal_daily`)
   - **功能**: 获取上海证券交易所指定交易日的每日股票概况数据，包括总市值、流通市值、上市公司数量、平均市盈率、成交金额、成交量、换手率等关键指标
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）。注意：仅支持20211227（包含）之后的数据
   - **AKShare接口**: `stock_sse_deal_daily`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回指定交易日的每日股票概况数据

**使用示例**:
```json
{
  "interface": "stock_sse_summary",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_szse_summary",
  "date": "20250630",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取市场股权质押数据 (get_equity_pledge_data)

**工具说明**: 获取股权质押相关的市场概况、个股质押比例、行业数据、机构分布等数据。包括股权质押市场概况、上市公司质押比例、行业质押数据、质押机构分布统计等。

**接口列表**:
1. **股权质押市场概况-所有历史** (`stock_gpzy_profile_em`)
   - **功能**: 获取所有历史的股权质押市场概况数据，包括质押公司数量、质押总市值、质押比例、质押机构数量等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_gpzy_profile_em`
   - **目标地址**: https://data.eastmoney.com/gpzy/
   - **限量**: 单次返回所有历史数据，由于数据量比较大需要等待一定时间

2. **上市公司质押比例-指定交易日** (`stock_gpzy_pledge_ratio_em`)
   - **功能**: 获取指定交易日的上市公司质押比例数据，包括股票代码、股票简称、质押比例、质押市值、质押数量等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241220）
   - **AKShare接口**: `stock_gpzy_pledge_ratio_em`
   - **目标地址**: https://data.eastmoney.com/gpzy/pledgeRatio.aspx
   - **限量**: 单次返回指定交易日的所有上市公司质押比例数据

3. **行业质押数据** (`stock_gpzy_industry_data_em`)
   - **功能**: 获取各行业上市公司质押统计数据，包括行业名称、质押公司数量、质押总市值、平均质押比例等行业维度的质押分析数据
   - **参数**: 无需参数，自动返回行业质押数据
   - **AKShare接口**: `stock_gpzy_industry_data_em`
   - **目标地址**: https://data.eastmoney.com/gpzy/
   - **限量**: 单次返回行业质押数据

4. **质押机构分布统计-证券公司** (`stock_gpzy_distribute_statistics_company_em`)
   - **功能**: 获取证券公司的质押机构分布统计数据，包括证券公司名称、质押笔数、质押市值、质押比例等
   - **参数**: 无需参数，自动返回证券公司质押机构分布统计数据
   - **AKShare接口**: `stock_gpzy_distribute_statistics_company_em`
   - **目标地址**: https://data.eastmoney.com/gpzy/
   - **限量**: 单次返回证券公司质押机构分布统计数据

5. **质押机构分布统计-银行** (`stock_gpzy_distribute_statistics_bank_em`)
   - **功能**: 获取银行的质押机构分布统计数据，包括银行名称、质押笔数、质押市值、质押比例等
   - **参数**: 无需参数，自动返回银行质押机构分布统计数据
   - **AKShare接口**: `stock_gpzy_distribute_statistics_bank_em`
   - **目标地址**: https://data.eastmoney.com/gpzy/
   - **限量**: 单次返回银行质押机构分布统计数据

**使用示例**:
```json
{
  "interface": "stock_gpzy_profile_em",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_gpzy_pledge_ratio_em",
  "date": "20241220",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取商誉数据 (get_goodwill_data)

**工具说明**: 获取A股商誉市场概况、个股商誉明细、减值明细、行业商誉等数据。商誉是企业在并购中产生的无形资产，是重要的财务风险指标。

**接口列表**:
1. **A股商誉市场概况-所有历史** (`stock_sy_profile_em`)
   - **功能**: 获取A股市场商誉的整体概况数据，包括商誉公司数量、商誉总额、减值总额等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_sy_profile_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/SY.html
   - **限量**: 单次返回所有历史数据，由于数据量比较大需要等待一定时间

2. **个股商誉减值明细-指定日期(季末)** (`stock_sy_jz_em`)
   - **功能**: 获取指定日期的上市公司商誉减值明细数据，包括股票代码、股票简称、商誉减值金额、减值原因等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD，建议使用季末日期（如20241231、20240331等）
   - **AKShare接口**: `stock_sy_jz_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/SY.html
   - **限量**: 单次返回指定日期的所有历史数据

3. **个股商誉明细-指定日期(季末)** (`stock_sy_em`)
   - **功能**: 获取指定日期的上市公司商誉明细数据，包括股票代码、股票简称、商誉总额、商誉占净资产比例等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD，建议使用季末日期（如20241231、20240331等）
   - **AKShare接口**: `stock_sy_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/SY.html
   - **限量**: 单次返回指定日期的所有历史数据

4. **行业商誉-指定日期(季末)** (`stock_sy_hy_em`)
   - **功能**: 获取指定日期的各行业上市公司商誉统计数据，包括行业名称、商誉公司数量、商誉总额、平均商誉等行业维度的商誉分析数据
   - **参数**: 需要交易日期参数，格式为YYYYMMDD，建议使用季末日期（如20241231、20240331等）
   - **AKShare接口**: `stock_sy_hy_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/SY.html
   - **限量**: 单次返回指定日期的所有历史数据

**使用示例**:
```json
{
  "interface": "stock_sy_profile_em",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_sy_em",
  "date": "20241231",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取股票账户统计 (get_stock_account_statistics)

**工具说明**: 获取A股市场股票账户统计数据，包括新增开户数、期末账户数、持仓账户数、交易账户数等。适用于市场活跃度分析、投资者情绪研究和市场趋势判断。

**接口列表**:
1. **A股账户统计-所有历史** (`stock_account_statistics_em`)
   - **功能**: 获取A股市场所有历史的股票账户统计数据，包括新增开户数、期末账户数、持仓账户数、交易账户数、空仓账户数等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_account_statistics_em`
   - **目标地址**: https://data.eastmoney.com/cjsj/gpkhsj.html
   - **限量**: 单次返回所有历史数据，由于数据量比较大需要等待一定时间

**使用示例**:
```json
{
  "interface": "stock_account_statistics_em",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取A股市场股东户数数据 (get_shareholder_number_data)

**工具说明**: 获取A股市场股东户数数据。基于东方财富网的股东户数数据接口，获取指定日期的所有股票股东户数数据，包括股东户数、户均持股数、持股集中度等指标。适用于市场股东结构分析、股东集中度研究和投资决策。

**接口列表**:
1. **股东户数数据-指定日期** (`stock_zh_a_gdhs`)
   - **功能**: 获取指定日期的所有股票股东户数数据，包括股票代码、股票简称、股东户数、户均持股数、持股集中度等指标
   - **参数**: 需要股东户数统计日期参数，格式："最新" 或 YYYYMMDD（季度末日期，如20230930）
   - **AKShare接口**: `stock_zh_a_gdhs`
   - **目标地址**: https://data.eastmoney.com/gdhs/
   - **限量**: 单次返回指定日期的所有股票股东户数数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_gdhs",
  "gdhs_date": "最新",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_zh_a_gdhs",
  "gdhs_date": "20230930",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取股票评论数据 (get_stock_comment_data)

**工具说明**: 获取千股千评相关数据，包括千股千评总览、主力控盘机构参与度、综合评价历史评分、市场热度用户关注指数、日度市场参与意愿等数据。帮助了解股票的综合评价和市场关注度。

**接口列表**:
1. **千股千评-所有数据** (`stock_comment_em`)
   - **功能**: 获取所有股票的千股千评总览数据，包括股票代码、股票简称、综合评分、机构参与度、用户关注指数等统计信息
   - **参数**: 无需参数，自动返回所有数据
   - **AKShare接口**: `stock_comment_em`
   - **目标地址**: https://data.eastmoney.com/comment/
   - **限量**: 单次返回所有数据，由于数据量比较大需要等待一定时间

2. **机构参与度-指定股票** (`stock_comment_detail_zlkp_jgcyd_em`)
   - **功能**: 获取指定股票的主力控盘机构参与度数据，包括机构参与度评分、机构持股比例、机构持仓变化等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）
   - **AKShare接口**: `stock_comment_detail_zlkp_jgcyd_em`
   - **目标地址**: https://data.eastmoney.com/comment/
   - **限量**: 单次返回指定股票的机构参与度数据

3. **历史评分-指定股票** (`stock_comment_detail_zhpj_lspf_em`)
   - **功能**: 获取指定股票的综合评价历史评分数据，包括历史评分趋势、评分变化、评分等级等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）
   - **AKShare接口**: `stock_comment_detail_zhpj_lspf_em`
   - **目标地址**: https://data.eastmoney.com/comment/
   - **限量**: 单次返回指定股票的历史评分数据

4. **用户关注指数-指定股票** (`stock_comment_detail_scrd_focus_em`)
   - **功能**: 获取指定股票的市场热度用户关注指数数据，包括用户关注指数、关注度排名、关注度变化等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）
   - **AKShare接口**: `stock_comment_detail_scrd_focus_em`
   - **目标地址**: https://data.eastmoney.com/comment/
   - **限量**: 单次返回指定股票的用户关注指数数据

5. **日度市场参与意愿-指定股票** (`stock_comment_detail_scrd_desire_daily_em`)
   - **功能**: 获取指定股票的日度市场参与意愿数据，包括市场参与意愿指数、参与意愿趋势、参与意愿变化等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）
   - **AKShare接口**: `stock_comment_detail_scrd_desire_daily_em`
   - **目标地址**: https://data.eastmoney.com/comment/
   - **限量**: 单次返回指定股票的日度市场参与意愿数据

**使用示例**:
```json
{
  "interface": "stock_comment_em",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_comment_detail_zlkp_jgcyd_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取IPO申购数据 (get_ipo_subscription_data)

**工具说明**: 获取新股申购、中签率、打新收益率等相关数据。包括打新收益率历史数据和指定市场的新股申购与中签数据。

**接口列表**:
1. **打新收益率-所有数据** (`stock_dxsyl_em`)
   - **功能**: 获取所有历史的打新收益率数据，包括新股代码、新股简称、申购日期、中签率、上市首日涨幅、打新收益率等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_dxsyl_em`
   - **目标地址**: https://data.eastmoney.com/xg/xg/
   - **限量**: 单次返回所有历史数据，由于数据量比较大需要等待一定时间

2. **新股申购与中签-指定市场** (`stock_xgsglb_em`)
   - **功能**: 获取指定市场的新股申购与中签数据，包括新股代码、新股简称、申购日期、中签率、申购上限、中签号等详细信息
   - **参数**: 需要市场选择参数，选项包括：全部股票、沪市主板、科创板、深市主板、创业板、北交所
   - **AKShare接口**: `stock_xgsglb_em`
   - **目标地址**: https://data.eastmoney.com/xg/xg/
   - **限量**: 单次返回指定市场的新股申购与中签数据

3. **新股上市首日** (`stock_xgsr_ths`)
   - **功能**: 获取所有新股上市首日数据，包括新股代码、新股简称、上市日期、上市首日涨幅、上市首日换手率等统计信息
   - **参数**: 无需参数，自动返回所有新股上市首日数据
   - **AKShare接口**: `stock_xgsr_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有新股上市首日数据

**使用示例**:
```json
{
  "interface": "stock_dxsyl_em",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_xgsglb_em",
  "symbol": "全部股票",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取交易事件通知 (get_trading_event_notifications)

**工具说明**: 获取停复牌、分红派息、历史分红等交易相关事件通知，以及公司重要动态信息。帮助投资者及时了解股票交易中的重要事件和上市公司的重要动态。

**接口列表**:
1. **停复牌通知-指定日期** (`news_trade_notify_suspend_baidu`)
   - **功能**: 获取指定日期的停复牌通知数据，包括股票代码、股票简称、停牌日期、复牌日期、停牌原因等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）
   - **AKShare接口**: `news_trade_notify_suspend_baidu`
   - **目标地址**: 百度股市通
   - **限量**: 单次返回指定日期的停复牌通知数据

2. **分红派息通知-指定日期** (`news_trade_notify_dividend_baidu`)
   - **功能**: 获取指定日期的分红派息通知数据，包括股票代码、股票简称、分红日期、每股派息、派息比例等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）
   - **AKShare接口**: `news_trade_notify_dividend_baidu`
   - **目标地址**: 百度股市通
   - **限量**: 单次返回指定日期的分红派息通知数据

3. **分红配送-指定日期** (`stock_fhps_em`)
   - **功能**: 获取指定日期的分红配送数据，包括股票代码、股票简称、分红日期、每股派息、派息比例、送股比例等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）
   - **AKShare接口**: `stock_fhps_em`
   - **目标地址**: https://data.eastmoney.com/yjfp/
   - **限量**: 单次返回指定日期的分红配送数据

4. **历史分红** (`stock_history_dividend`)
   - **功能**: 获取所有历史分红数据，包括股票代码、股票简称、分红日期、每股派息、派息比例、送股比例等统计信息
   - **参数**: 无需参数，自动返回所有历史分红数据
   - **AKShare接口**: `stock_history_dividend`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有历史分红数据

5. **公司动态-指定交易日** (`stock_gsrl_gsdt_em`)
   - **功能**: 获取指定交易日的公司动态数据，包括股票代码、股票简称、动态日期、动态内容、动态类型等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20250630）
   - **AKShare接口**: `stock_gsrl_gsdt_em`
   - **目标地址**: https://data.eastmoney.com/gsrl/
   - **限量**: 单次返回指定交易日的公司动态数据

**使用示例**:
```json
{
  "interface": "news_trade_notify_suspend_baidu",
  "date": "20250630",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_history_dividend",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取市场机构持股数据 (get_institute_holdings_data)

**工具说明**: 获取机构持股相关数据，包括机构持股一览表和机构持股详情。帮助了解机构投资者对股票的持仓情况。适用于机构持股分析、投资决策和股票研究。

**接口列表**:
1. **机构持股一览表-指定报告期** (`stock_institute_hold`)
   - **功能**: 获取指定报告期的机构持股一览表数据，包括股票代码、股票简称、机构持股数量、机构持股比例、机构持股市值等统计信息
   - **参数**: 需要报告期参数，格式为YYYY[1-4]（如20241表示2024年一季报）。从2005年开始，一季报用1、中报用2、三季报用3、年报用4
   - **AKShare接口**: `stock_institute_hold`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定报告期的所有机构持股一览表数据

2. **机构持股详情-指定股票和报告期** (`stock_institute_hold_detail`)
   - **功能**: 获取指定股票和报告期的机构持股详情数据，包括机构名称、持股数量、持股比例、持股市值、持股变化等详细信息
   - **参数**: 需要股票代码和报告期参数。股票代码格式如"600519"（沪市）或"000001"（深市）。报告期格式为YYYY[1-4]（如20241表示2024年一季报）
   - **AKShare接口**: `stock_institute_hold_detail`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票和报告期的机构持股详情数据

**使用示例**:
```json
{
  "interface": "stock_institute_hold",
  "quarter": "20244",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_institute_hold_detail",
  "stock": "600519",
  "quarter": "20244",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取个股评级记录与估值分析 (get_stock_rating_valuation)

**工具说明**: 获取股票的机构评级记录和估值分析数据。包括个股级别的评级记录和估值分析，以及市场级别的投资评级数据。帮助了解股票的机构评级情况和估值水平，以及市场整体的投资评级情况。适用于股票评级分析、估值研究和投资决策。

**接口列表**:
1. **股票评级记录-指定股票** (`stock_institute_recommend_detail`)
   - **功能**: 获取指定股票的机构评级记录数据，包括评级机构、评级日期、投资评级、目标价、评级变化等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_institute_recommend_detail`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的机构评级记录数据

2. **估值分析-指定股票** (`stock_value_em`)
   - **功能**: 获取指定股票的估值分析数据，包括市盈率、市净率、市销率等估值指标，以及与行业对比情况
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_value_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/Index?type=web&code=sh600519
   - **限量**: 单次返回指定股票的估值分析数据

3. **投资评级-指定日期** (`stock_rank_forecast_cninfo`)
   - **功能**: 获取指定交易日的所有股票投资评级数据，包括证券代码、证券简称、研究机构、研究员、投资评级、评级变化、目标价格等统计信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20210910）
   - **AKShare接口**: `stock_rank_forecast_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定交易日的所有股票投资评级数据

**使用示例**:
```json
{
  "interface": "stock_institute_recommend_detail",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_rank_forecast_cninfo",
  "date": "20210910",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取公司公告数据 (get_company_announcements)

**工具说明**: 获取公司公告数据。包括股东大会、重大合同明细、公告大全等数据。帮助了解公司的重要公告内容、重大合同和公司治理相关信息。适用于公司公告跟踪、公司治理研究和投资决策。

**接口列表**:
1. **股东大会** (`stock_gddh_em`)
   - **功能**: 获取所有股票的股东大会信息，包括股票代码、股票简称、股东大会日期、股东大会内容等统计信息
   - **参数**: 无需参数，自动返回所有股票的股东大会信息
   - **AKShare接口**: `stock_gddh_em`
   - **目标地址**: https://data.eastmoney.com/notices/
   - **限量**: 单次返回所有股票的股东大会信息

2. **重大合同明细-指定日期范围** (`stock_zdhtmx_em`)
   - **功能**: 获取指定日期范围内的重大合同明细数据，包括股票代码、股票简称、合同日期、合同金额、合同内容等详细信息
   - **参数**: 需要开始日期和结束日期参数，格式为YYYYMMDD（如20220819、20230819）
   - **AKShare接口**: `stock_zdhtmx_em`
   - **目标地址**: https://data.eastmoney.com/notices/
   - **限量**: 单次返回指定日期范围内的重大合同明细数据

3. **公告大全-指定公告类型和日期** (`stock_notice_report`)
   - **功能**: 获取指定类型和日期的公告数据，包括股票代码、股票简称、公告日期、公告类型、公告内容等详细信息
   - **参数**: 需要公告类型和交易日期参数。公告类型选项包括：全部、重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动。交易日期格式为YYYYMMDD（如20240613）
   - **AKShare接口**: `stock_notice_report`
   - **目标地址**: https://data.eastmoney.com/notices/
   - **限量**: 单次返回指定类型和日期的公告数据

**使用示例**:
```json
{
  "interface": "stock_gddh_em",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_notice_report",
  "date": "20240613",
  "notice_category": "财务报告",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取公司信息披露数据 (get_company_disclosure)

**工具说明**: 获取公司信息披露数据。包括信息披露公告和信息披露调研等数据。帮助了解公司的重要信息披露内容、公告详情和调研信息。适用于公司信息披露分析、公告跟踪和投资决策。

**接口列表**:
1. **信息披露公告-指定股票、市场、类别、日期范围** (`stock_zh_a_disclosure_report_cninfo`)
   - **功能**: 获取指定股票的信息披露公告数据，包括公告标题、公告日期、公告类别、公告内容等详细信息
   - **参数**: 需要股票代码、市场、公告类别、开始日期和结束日期参数。股票代码格式如"000001"（深市）或"600519"（沪市）。市场选项包括：沪深京、港股、三板、基金、债券、监管、预披露。公告类别选项包括：年报、半年报、一季报、三季报、业绩预告、权益分派、董事会、监事会、股东大会、日常经营、公司治理、中介报告、首发、增发、股权激励、配股、解禁、公司债、可转债、其他融资、股权变动、补充更正、澄清致歉、风险提示、特别处理和退市、退市整理期。日期格式为YYYYMMDD（如20230618、20231219）
   - **AKShare接口**: `stock_zh_a_disclosure_report_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票、市场、类别和日期范围的信息披露公告数据

2. **信息披露调研-指定股票、市场、日期范围** (`stock_zh_a_disclosure_relation_cninfo`)
   - **功能**: 获取指定股票的信息披露调研数据，包括调研日期、调研机构、调研内容等详细信息
   - **参数**: 需要股票代码、市场、开始日期和结束日期参数。股票代码格式如"000001"（深市）或"600519"（沪市）。市场选项包括：沪深京、港股、三板、基金、债券、监管、预披露。日期格式为YYYYMMDD（如20230618、20231219）
   - **AKShare接口**: `stock_zh_a_disclosure_relation_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票、市场和日期范围的信息披露调研数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_disclosure_report_cninfo",
  "symbol": "000001",
  "market": "沪深京",
  "category": "公司治理",
  "start_date": "20230618",
  "end_date": "20231219",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取股票列表数据 (get_stock_list)

**工具说明**: 获取股票列表数据。包括A股、上证、深证、北证股票列表，以及终止/暂停上市股票等数据。帮助了解股票代码和简称信息，以及上市状态。适用于股票代码查询、股票列表管理和市场分析。

**接口列表**:
1. **沪深京A股股票代码和股票简称数据** (`stock_info_a_code_name`)
   - **功能**: 获取所有A股股票代码和简称数据，包括股票代码、股票简称等基本信息
   - **参数**: 无需参数，自动返回所有A股股票代码和简称
   - **AKShare接口**: `stock_info_a_code_name`
   - **目标地址**: AKShare
   - **限量**: 单次返回所有A股股票代码和简称数据

2. **上海证券交易所股票代码和简称数据-指定板块类型** (`stock_info_sh_name_code`)
   - **功能**: 获取指定板块的股票代码、简称、公司全称、上市日期等信息
   - **参数**: 需要板块类型参数，选项包括：主板A股、主板B股、科创板
   - **AKShare接口**: `stock_info_sh_name_code`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回指定板块的股票代码和简称数据

3. **深证证券交易所股票代码和股票简称数据-指定板块类型** (`stock_info_sz_name_code`)
   - **功能**: 获取指定板块的股票代码、简称、上市日期、股本等信息
   - **参数**: 需要板块类型参数，选项包括：A股列表、B股列表、CDR列表、AB股列表
   - **AKShare接口**: `stock_info_sz_name_code`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定板块的股票代码和简称数据

4. **北京证券交易所股票代码和简称数据** (`stock_info_bj_name_code`)
   - **功能**: 获取所有北证股票代码和简称数据，包括股票代码、股票简称等基本信息
   - **参数**: 无需参数，自动返回所有北证股票代码和简称
   - **AKShare接口**: `stock_info_bj_name_code`
   - **目标地址**: 北京证券交易所
   - **限量**: 单次返回所有北证股票代码和简称数据

5. **深证证券交易所终止/暂停上市股票-指定类型** (`stock_info_sz_delist`)
   - **功能**: 获取指定类型的终止或暂停上市股票信息，包括股票代码、股票简称、终止/暂停日期等详细信息
   - **参数**: 需要类型参数，选项包括：暂停上市公司、终止上市公司
   - **AKShare接口**: `stock_info_sz_delist`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定类型的终止或暂停上市股票信息

6. **上海证券交易所暂停/终止上市股票-指定类型** (`stock_info_sh_delist`)
   - **功能**: 获取指定类型的暂停或终止上市股票信息，包括股票代码、股票简称、暂停/终止日期等详细信息
   - **参数**: 需要类型参数，选项包括：全部、沪市、科创板
   - **AKShare接口**: `stock_info_sh_delist`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回指定类型的暂停或终止上市股票信息

**使用示例**:
```json
{
  "interface": "stock_info_a_code_name",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_info_sh_name_code",
  "symbol": "主板A股",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取龙虎榜数据 (get_dragon_tiger_list)

**工具说明**: 获取龙虎榜数据。包括龙虎榜详情、个股上榜统计、机构买卖每日统计、机构席位追踪、每日活跃营业部等数据。帮助了解股票异常交易情况、机构资金流向和营业部活跃度。适用于龙虎榜分析、机构资金追踪和投资决策。

**接口列表**:
1. **龙虎榜详情-指定日期范围** (`stock_lhb_detail_em`)
   - **功能**: 获取指定日期范围内的龙虎榜详情数据，包括股票代码、股票简称、上榜日期、买入金额、卖出金额、净买入金额等详细信息
   - **参数**: 需要开始日期和结束日期参数，格式为YYYYMMDD（如20250701、20251105）
   - **AKShare接口**: `stock_lhb_detail_em`
   - **目标地址**: https://data.eastmoney.com/stock/lhb/
   - **限量**: 单次返回指定日期范围内的龙虎榜详情数据

2. **个股上榜统计-指定统计周期** (`stock_lhb_stock_statistic_em`)
   - **功能**: 获取指定周期内的个股上榜统计信息，包括股票代码、股票简称、上榜次数、买入金额、卖出金额等统计信息
   - **参数**: 需要统计周期参数，选项包括：近一月、近三月、近六月、近一年
   - **AKShare接口**: `stock_lhb_stock_statistic_em`
   - **目标地址**: https://data.eastmoney.com/stock/lhb/
   - **限量**: 单次返回指定周期内的个股上榜统计信息

3. **机构买卖每日统计-指定日期范围** (`stock_lhb_jgmmtj_em`)
   - **功能**: 获取指定日期范围内的机构买卖每日统计数据，包括日期、买入金额、卖出金额、净买入金额等统计信息
   - **参数**: 需要开始日期和结束日期参数，格式为YYYYMMDD（如20250701、20251105）
   - **AKShare接口**: `stock_lhb_jgmmtj_em`
   - **目标地址**: https://data.eastmoney.com/stock/lhb/
   - **限量**: 单次返回指定日期范围内的机构买卖每日统计数据

4. **机构席位追踪-指定统计周期** (`stock_lhb_jgstatistic_em`)
   - **功能**: 获取指定周期内的机构席位追踪数据，包括机构名称、买入金额、卖出金额、净买入金额等统计信息
   - **参数**: 需要统计周期参数，选项包括：近一月、近三月、近六月、近一年
   - **AKShare接口**: `stock_lhb_jgstatistic_em`
   - **目标地址**: https://data.eastmoney.com/stock/lhb/
   - **限量**: 单次返回指定周期内的机构席位追踪数据

5. **每日活跃营业部-指定日期范围** (`stock_lhb_hyyyb_em`)
   - **功能**: 获取指定日期范围内的每日活跃营业部数据，包括营业部名称、买入金额、卖出金额、净买入金额等统计信息
   - **参数**: 需要开始日期和结束日期参数，格式为YYYYMMDD（如20250701、20251105）
   - **AKShare接口**: `stock_lhb_hyyyb_em`
   - **目标地址**: https://data.eastmoney.com/stock/lhb/
   - **限量**: 单次返回指定日期范围内的每日活跃营业部数据

**使用示例**:
```json
{
  "interface": "stock_lhb_detail_em",
  "start_date": "20250701",
  "end_date": "20251105",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_lhb_stock_statistic_em",
  "period": "近一月",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取大宗交易数据 (get_block_trading)

**工具说明**: 获取大宗交易数据。包括市场统计、每日明细、每日统计、活跃A股统计、活跃营业部统计、营业部排行等数据。帮助了解大宗交易的成交情况、活跃股票和营业部信息。适用于大宗交易分析、资金流向追踪和投资决策。

**接口列表**:
1. **市场统计-所有历史** (`stock_dzjy_sctj`)
   - **功能**: 获取所有历史的大宗交易市场统计数据，包括交易日期、成交金额、成交数量等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_dzjy_sctj`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回所有历史数据，由于数据量比较大需要等待一定时间

2. **每日明细-指定证券类型和日期范围** (`stock_dzjy_mrmx`)
   - **功能**: 获取指定类型和日期范围的每日明细数据，包括股票代码、股票简称、交易日期、成交价格、成交数量、成交金额等详细信息
   - **参数**: 需要证券类型和日期范围参数。证券类型选项包括：A股、B股、基金、债券。日期格式为YYYYMMDD（如20251103、20251104）
   - **AKShare接口**: `stock_dzjy_mrmx`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回指定类型和日期范围的每日明细数据

3. **每日统计-指定日期范围** (`stock_dzjy_mrtj`)
   - **功能**: 获取指定日期范围的每日统计数据，包括交易日期、成交金额、成交数量等统计信息
   - **参数**: 需要日期范围参数，格式为YYYYMMDD（如20251103、20251104）
   - **AKShare接口**: `stock_dzjy_mrtj`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回指定日期范围的每日统计数据

4. **活跃A股统计-指定统计周期** (`stock_dzjy_hygtj`)
   - **功能**: 获取指定周期内的活跃A股统计数据，包括股票代码、股票简称、成交金额、成交数量等统计信息
   - **参数**: 需要统计周期参数，选项包括：近一月、近三月、近六月、近一年
   - **AKShare接口**: `stock_dzjy_hygtj`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回指定周期内的活跃A股统计数据

5. **活跃营业部统计-指定统计周期** (`stock_dzjy_hyyybtj`)
   - **功能**: 获取指定周期内的活跃营业部统计数据，包括营业部名称、成交金额、成交数量等统计信息
   - **参数**: 需要统计周期参数，选项包括：当前交易日、近3日、近5日、近10日、近30日
   - **AKShare接口**: `stock_dzjy_hyyybtj`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回指定周期内的活跃营业部统计数据

6. **营业部排行-指定统计周期** (`stock_dzjy_yybph`)
   - **功能**: 获取指定周期内的营业部排行数据，包括营业部名称、成交金额、成交数量、排名等统计信息
   - **参数**: 需要统计周期参数，选项包括：近一月、近三月、近六月、近一年
   - **AKShare接口**: `stock_dzjy_yybph`
   - **目标地址**: https://data.eastmoney.com/dzjy/
   - **限量**: 单次返回指定周期内的营业部排行数据

**使用示例**:
```json
{
  "interface": "stock_dzjy_sctj",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_dzjy_mrmx",
  "security_type": "A股",
  "start_date": "20251103",
  "end_date": "20251104",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取A股市场融资融券数据 (get_margin_trading)

**工具说明**: 获取A股市场融资融券数据。包括标的证券名单、保证金比例、两融账户信息、上证所和深交所的融资融券汇总和明细数据、标的证券信息等。帮助了解融资融券交易情况、资金流向和市场风险。适用于融资融券分析、风险监控和投资决策。

**接口列表**:
1. **标的证券名单及保证金比例查询-指定日期** (`stock_margin_ratio_pa`)
   - **功能**: 获取指定日期的标的证券名单及保证金比例数据，包括股票代码、股票简称、保证金比例等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20251013）
   - **AKShare接口**: `stock_margin_ratio_pa`
   - **目标地址**: 平安证券
   - **限量**: 单次返回指定日期的标的证券名单及保证金比例数据

2. **两融账户信息-所有历史** (`stock_margin_account_info`)
   - **功能**: 获取所有历史的两融账户信息数据，包括账户数量、融资余额、融券余额等统计信息
   - **参数**: 无需参数，自动返回所有历史数据
   - **AKShare接口**: `stock_margin_account_info`
   - **目标地址**: https://data.eastmoney.com/rzrq/
   - **限量**: 单次返回所有历史数据

3. **上海证券交易所-融资融券汇总数据-指定日期范围** (`stock_margin_sse`)
   - **功能**: 获取指定日期范围的融资融券汇总数据，包括交易日期、融资余额、融券余额、融资买入额、融券卖出量等统计信息
   - **参数**: 需要开始日期和结束日期参数，格式为YYYYMMDD（如20010106、20251231）
   - **AKShare接口**: `stock_margin_sse`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回指定日期范围的融资融券汇总数据

4. **上海证券交易所-融资融券明细数据-指定日期** (`stock_margin_detail_sse`)
   - **功能**: 获取指定日期的融资融券明细数据，包括股票代码、股票简称、融资余额、融券余额、融资买入额、融券卖出量等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20251013）
   - **AKShare接口**: `stock_margin_detail_sse`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回指定日期的融资融券明细数据

5. **深圳证券交易所-融资融券汇总数据-指定日期** (`stock_margin_szse`)
   - **功能**: 获取指定日期的融资融券汇总数据，包括交易日期、融资余额、融券余额、融资买入额、融券卖出量等统计信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20251013）
   - **AKShare接口**: `stock_margin_szse`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定日期的融资融券汇总数据

6. **深圳证券交易所-融资融券明细数据-指定日期** (`stock_margin_detail_szse`)
   - **功能**: 获取指定日期的融资融券明细数据，包括股票代码、股票简称、融资余额、融券余额、融资买入额、融券卖出量等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20251013）
   - **AKShare接口**: `stock_margin_detail_szse`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定日期的融资融券明细数据

7. **深圳证券交易所-标的证券信息-指定日期** (`stock_margin_underlying_info_szse`)
   - **功能**: 获取指定日期的标的证券信息数据，包括股票代码、股票简称、标的证券类型等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20251013）
   - **AKShare接口**: `stock_margin_underlying_info_szse`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回指定日期的标的证券信息数据

**使用示例**:
```json
{
  "interface": "stock_margin_account_info",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_margin_detail_sse",
  "date": "20251013",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取同花顺板块数据 (get_board_ths)

**工具说明**: 获取同花顺板块数据。包括概念板块名列表、概念板块指数、概念板块简介、行业板块一览表和行业板块指数等。帮助了解同花顺板块的行情走势和基本信息。适用于板块分析、主题投资和行业研究。

**接口列表**:
1. **概念板块名列表** (`stock_board_concept_name_ths`)
   - **功能**: 获取所有同花顺概念板块名称，包括板块代码、板块名称等基本信息
   - **参数**: 无需参数，自动返回所有同花顺概念板块名称
   - **AKShare接口**: `stock_board_concept_name_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有同花顺概念板块名称

2. **概念板块指数-指定概念板块、日期范围** (`stock_board_concept_index_ths`)
   - **功能**: 获取指定概念板块的日频指数数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要概念名称和日期范围参数。概念名称使用同花顺概念名称（如"阿里巴巴概念"）。日期格式为YYYYMMDD（如20200101、20250321）
   - **AKShare接口**: `stock_board_concept_index_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定概念板块和日期范围的日频指数数据

3. **概念板块简介-指定概念板块** (`stock_board_concept_info_ths`)
   - **功能**: 获取指定概念板块的简介信息，包括板块名称、板块简介、板块成份股等详细信息
   - **参数**: 需要概念名称参数，使用同花顺概念名称（如"阿里巴巴概念"）
   - **AKShare接口**: `stock_board_concept_info_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定概念板块的简介信息

4. **同花顺行业一览表** (`stock_board_industry_summary_ths`)
   - **功能**: 获取当前时刻同花顺行业一览表，包括行业代码、行业名称等基本信息
   - **参数**: 无需参数，自动返回当前时刻同花顺行业一览表
   - **AKShare接口**: `stock_board_industry_summary_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回当前时刻同花顺行业一览表

5. **行业板块指数-指定行业板块、日期范围** (`stock_board_industry_index_ths`)
   - **功能**: 获取指定行业板块的日频指数数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要行业名称和日期范围参数。行业名称使用同花顺行业名称（如"元件"）。日期格式为YYYYMMDD（如20200101、20250321）
   - **AKShare接口**: `stock_board_industry_index_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定行业板块和日期范围的日频指数数据

**使用示例**:
```json
{
  "interface": "stock_board_concept_name_ths",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_board_concept_index_ths",
  "symbol": "阿里巴巴概念",
  "start_date": "20200101",
  "end_date": "20250321",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取东方财富板块数据 (get_board_em)

**工具说明**: 获取东方财富板块数据。包括概念板块和行业板块的列表、实时行情、板块成份、历史行情和分时数据等。帮助了解东方财富板块的行情走势和基本信息。适用于板块分析、主题投资和行业研究。

**接口列表**:
1. **概念板块-所有数据** (`stock_board_concept_name_em`)
   - **功能**: 获取所有概念板块的实时行情数据，包括板块代码、板块名称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 无需参数，自动返回所有概念板块的实时行情数据
   - **AKShare接口**: `stock_board_concept_name_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#concept_board
   - **限量**: 单次返回所有概念板块的实时行情数据

2. **概念板块-实时行情-指定概念板块** (`stock_board_concept_spot_em`)
   - **功能**: 获取指定概念板块的实时行情数据，包括板块代码、板块名称、最新价、涨跌幅、成交量等详细信息
   - **参数**: 需要概念名称参数，使用东方财富概念名称（如"融资融券"、"绿色电力"）或板块代码（如"BK0655"）
   - **AKShare接口**: `stock_board_concept_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#concept_board
   - **限量**: 单次返回指定概念板块的实时行情数据

3. **概念板块-板块成份-指定概念板块或板块代码** (`stock_board_concept_cons_em`)
   - **功能**: 获取指定概念板块的成份股数据，包括股票代码、股票简称、最新价、涨跌幅等详细信息
   - **参数**: 需要概念名称或板块代码参数，使用东方财富概念名称（如"融资融券"、"绿色电力"）或板块代码（如"BK0655"）
   - **AKShare接口**: `stock_board_concept_cons_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#concept_board
   - **限量**: 单次返回指定概念板块的成份股数据

4. **概念板块-历史行情数据-指定概念板块、周期、日期范围和复权方式** (`stock_board_concept_hist_em`)
   - **功能**: 获取指定概念板块的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要概念名称、周期、日期范围和复权方式参数。概念名称使用东方财富概念名称（如"融资融券"、"绿色电力"）或板块代码（如"BK0655"）。周期选项包括：daily（日线）、weekly（周线）、monthly（月线）。日期格式为YYYYMMDD（如20200101、20250321）。复权方式选项包括：none（不复权）、qfq（前复权）、hfq（后复权）
   - **AKShare接口**: `stock_board_concept_hist_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#concept_board
   - **限量**: 单次返回指定概念板块、周期、日期范围和复权方式的历史行情数据

5. **概念板块-分时历史行情数据-指定概念板块和分时周期** (`stock_board_concept_hist_min_em`)
   - **功能**: 获取指定概念板块的分时数据，包括时间、开盘价、收盘价、最高价、最低价、成交量等
   - **参数**: 需要概念名称和分时周期参数。概念名称使用东方财富概念名称（如"融资融券"、"绿色电力"）或板块代码（如"BK0655"）。分时周期选项包括：1（1分钟）、5（5分钟）、15（15分钟）、30（30分钟）、60（60分钟）
   - **AKShare接口**: `stock_board_concept_hist_min_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#concept_board
   - **限量**: 单次返回指定概念板块和分时周期的分时数据

6. **行业板块-所有数据** (`stock_board_industry_name_em`)
   - **功能**: 获取所有行业板块的实时行情数据，包括板块代码、板块名称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 无需参数，自动返回所有行业板块的实时行情数据
   - **AKShare接口**: `stock_board_industry_name_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#industry_board
   - **限量**: 单次返回所有行业板块的实时行情数据

7. **行业板块-实时行情-指定行业名称** (`stock_board_industry_spot_em`)
   - **功能**: 获取指定行业板块的实时行情数据，包括板块代码、板块名称、最新价、涨跌幅、成交量等详细信息
   - **参数**: 需要行业名称参数，使用东方财富行业名称（如"小金属"、"煤炭行业"）或板块代码（如"BK1027"）
   - **AKShare接口**: `stock_board_industry_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#industry_board
   - **限量**: 单次返回指定行业板块的实时行情数据

8. **行业板块-板块成份-指定行业名称或板块代码** (`stock_board_industry_cons_em`)
   - **功能**: 获取指定行业板块的成份股数据，包括股票代码、股票简称、最新价、涨跌幅等详细信息
   - **参数**: 需要行业名称或板块代码参数，使用东方财富行业名称（如"小金属"、"煤炭行业"）或板块代码（如"BK1027"）
   - **AKShare接口**: `stock_board_industry_cons_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#industry_board
   - **限量**: 单次返回指定行业板块的成份股数据

9. **行业板块-历史行情数据-指定行业名称、周期、日期范围和复权方式** (`stock_board_industry_hist_em`)
   - **功能**: 获取指定行业板块的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要行业名称、周期、日期范围和复权方式参数。行业名称使用东方财富行业名称（如"小金属"、"煤炭行业"）或板块代码（如"BK1027"）。周期选项包括：日k（日线）、周k（周线）、月k（月线）。日期格式为YYYYMMDD（如20200101、20250321）。复权方式选项包括：none（不复权）、qfq（前复权）、hfq（后复权）
   - **AKShare接口**: `stock_board_industry_hist_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#industry_board
   - **限量**: 单次返回指定行业板块、周期、日期范围和复权方式的历史行情数据

10. **行业板块-分时历史行情数据-指定行业名称和分时周期** (`stock_board_industry_hist_min_em`)
    - **功能**: 获取指定行业板块的分时数据，包括时间、开盘价、收盘价、最高价、最低价、成交量等
    - **参数**: 需要行业名称和分时周期参数。行业名称使用东方财富行业名称（如"小金属"、"煤炭行业"）或板块代码（如"BK1027"）。分时周期选项包括：1（1分钟）、5（5分钟）、15（15分钟）、30（30分钟）、60（60分钟）
    - **AKShare接口**: `stock_board_industry_hist_min_em`
    - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#industry_board
    - **限量**: 单次返回指定行业板块和分时周期的分时数据

**使用示例**:
```json
{
  "interface": "stock_board_concept_name_em",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_board_concept_hist_em",
  "symbol": "融资融券",
  "period": "daily",
  "start_date": "20200101",
  "end_date": "20250321",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取A股市场股票热度数据 (get_stock_hot)

**工具说明**: 获取A股市场股票热度数据。包括雪球和东方财富的股票热度排行榜，如关注排行榜、讨论排行榜、交易排行榜、人气榜、飙升榜等。帮助了解股票的市场关注度、讨论热度和交易活跃度。适用于股票热度分析、市场情绪监测和投资决策。

**接口列表**:
1. **关注排行榜-指定排行类别** (`stock_hot_follow_xq`)
   - **功能**: 获取指定类别的关注排行榜数据，包括股票代码、股票简称、关注人数、关注度排名等统计信息
   - **参数**: 需要排行类别参数，选项包括：最热门、本周新增
   - **AKShare接口**: `stock_hot_follow_xq`
   - **目标地址**: 雪球
   - **限量**: 单次返回指定类别的关注排行榜数据

2. **讨论排行榜-指定排行类别** (`stock_hot_tweet_xq`)
   - **功能**: 获取指定类别的讨论排行榜数据，包括股票代码、股票简称、讨论数量、讨论度排名等统计信息
   - **参数**: 需要排行类别参数，选项包括：最热门、本周新增
   - **AKShare接口**: `stock_hot_tweet_xq`
   - **目标地址**: 雪球
   - **限量**: 单次返回指定类别的讨论排行榜数据

3. **交易排行榜-指定排行类别** (`stock_hot_deal_xq`)
   - **功能**: 获取指定类别的交易排行榜数据，包括股票代码、股票简称、交易数量、交易度排名等统计信息
   - **参数**: 需要排行类别参数，选项包括：最热门、本周新增
   - **AKShare接口**: `stock_hot_deal_xq`
   - **目标地址**: 雪球
   - **限量**: 单次返回指定类别的交易排行榜数据

4. **人气榜-A股-全部** (`stock_hot_rank_em`)
   - **功能**: 获取A股人气榜前100名数据，包括股票代码、股票简称、人气指数、人气排名等统计信息
   - **参数**: 无需参数，自动返回A股人气榜前100名数据
   - **AKShare接口**: `stock_hot_rank_em`
   - **目标地址**: https://guba.eastmoney.com/rank/
   - **限量**: 单次返回A股人气榜前100名数据

5. **飙升榜-A股-全部** (`stock_hot_up_em`)
   - **功能**: 获取A股飙升榜前100名数据，包括股票代码、股票简称、飙升指数、飙升排名等统计信息
   - **参数**: 无需参数，自动返回A股飙升榜前100名数据
   - **AKShare接口**: `stock_hot_up_em`
   - **目标地址**: https://guba.eastmoney.com/rank/
   - **限量**: 单次返回A股飙升榜前100名数据

6. **人气榜-港股-全部** (`stock_hk_hot_rank_em`)
   - **功能**: 获取港股人气榜前100名数据，包括股票代码、股票简称、人气指数、人气排名等统计信息
   - **参数**: 无需参数，自动返回港股人气榜前100名数据
   - **AKShare接口**: `stock_hk_hot_rank_em`
   - **目标地址**: https://guba.eastmoney.com/rank/
   - **限量**: 单次返回港股人气榜前100名数据

**使用示例**:
```json
{
  "interface": "stock_hot_rank_em",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_hot_follow_xq",
  "symbol": "最热门",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取A股市场涨停板行情数据 (get_limit_up_down)

**工具说明**: 获取A股市场涨停板行情数据。包括涨停股池、昨日涨停股池、强势股池、次新股池、炸板股池、跌停股池等。帮助了解涨停板股票的行情、封板情况、连板数和后续表现。适用于涨停板分析、强势股筛选和风险监控。注意：这些接口只能获取近期的数据。

**接口列表**:
1. **涨停股池-指定日期** (`stock_zt_pool_em`)
   - **功能**: 获取指定日期的涨停股池数据，包括股票代码、股票简称、涨停价格、封板时间、连板数等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的涨停股池数据

2. **昨日涨停股池-指定日期** (`stock_zt_pool_previous_em`)
   - **功能**: 获取指定日期的昨日涨停股池数据，包括股票代码、股票简称、昨日涨停价格、今日价格、涨跌幅等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_previous_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的昨日涨停股池数据

3. **强势股池-指定日期** (`stock_zt_pool_strong_em`)
   - **功能**: 获取指定日期的强势股池数据，包括股票代码、股票简称、涨幅、连板数等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_strong_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的强势股池数据

4. **次新股池-指定日期** (`stock_zt_pool_sub_new_em`)
   - **功能**: 获取指定日期的次新股池数据，包括股票代码、股票简称、上市日期、涨幅等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_sub_new_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的次新股池数据

5. **炸板股池-指定日期** (`stock_zt_pool_zbgc_em`)
   - **功能**: 获取指定日期的炸板股池数据，包括股票代码、股票简称、炸板时间、炸板价格等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_zbgc_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的炸板股池数据

6. **跌停股池-指定日期** (`stock_zt_pool_dtgc_em`)
   - **功能**: 获取指定日期的跌停股池数据，包括股票代码、股票简称、跌停价格、封板时间等详细信息
   - **参数**: 需要交易日期参数，格式为YYYYMMDD（如20241008）。注意：只能获取近期的数据
   - **AKShare接口**: `stock_zt_pool_dtgc_em`
   - **目标地址**: https://quote.eastmoney.com/ztb/
   - **限量**: 单次返回指定日期的跌停股池数据

**使用示例**:
```json
{
  "interface": "stock_zt_pool_em",
  "date": "20241008",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_zt_pool_previous_em",
  "date": "20241008",
  "retries": 5,
  "timeout": 240
}
```

---

## 二、个股信息类工具（6个工具）

### 获取个股基本信息 (get_stock_basic_info)

**工具说明**: 获取股票的基本信息，包括股票概况、主营业务介绍、主营构成等数据。帮助了解股票的基本面信息。适用于股票研究、投资分析和公司基本面了解。

**接口列表**:
1. **股票信息-指定股票** (`stock_individual_info_em`)
   - **功能**: 获取指定股票的基本信息，包括股票代码、股票名称、所属行业、所属概念、最新价格、总市值、流通市值、总股本、流通股等
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_individual_info_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/Index?type=web&code=sh600519
   - **限量**: 单次返回指定股票的基本信息

2. **主营介绍-指定股票** (`stock_zyjs_ths`)
   - **功能**: 获取指定股票的主营业务介绍数据，包括主营业务描述、经营范围、产品类型、产品名称等
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_zyjs_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票的主营业务介绍数据

3. **主营构成-指定股票** (`stock_zygc_em`)
   - **功能**: 获取指定股票的主营业务构成数据，包括按产品或地区分类的主营业务构成信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_zygc_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/Index?type=web&code=sh600519
   - **限量**: 单次返回指定股票的主营业务构成数据

4. **公司概况-指定股票** (`stock_profile_cninfo`)
   - **功能**: 获取指定股票的公司概况数据，包括公司基本信息、业务范围、财务指标等
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_profile_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票的公司概况数据

5. **上市相关资讯-指定股票** (`stock_ipo_summary_cninfo`)
   - **功能**: 获取指定股票的上市相关资讯数据，包括上市日期、发行价格、募集资金等
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_ipo_summary_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票的上市相关资讯数据

**使用示例**:
```json
{
  "interface": "stock_individual_info_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_zygc_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取个股新闻研报 (get_stock_news_research)

**工具说明**: 获取股票的新闻资讯和研究报告数据。帮助投资者了解股票的最新动态和机构分析。适用于股票新闻跟踪、研究报告分析和投资决策。

**接口列表**:
1. **新闻资讯数据-指定股票** (`stock_news_em`)
   - **功能**: 获取指定股票相关的新闻资讯数据，包括新闻标题、发布时间、新闻链接等信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_news_em`
   - **目标地址**: https://guba.eastmoney.com/list,600519.html
   - **限量**: 单次返回指定股票相关的新闻资讯数据

2. **个股研报-指定股票** (`stock_research_report_em`)
   - **功能**: 获取指定股票的券商研究报告数据，包括研究报告标题、发布机构、发布时间、投资评级、目标价等信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_research_report_em`
   - **目标地址**: https://data.eastmoney.com/report/
   - **限量**: 单次返回指定股票的券商研究报告数据

**使用示例**:
```json
{
  "interface": "stock_news_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_research_report_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取个股分红派息信息 (get_stock_dividend_info)

**工具说明**: 获取股票的分红送配详情和历史分红数据。帮助了解股票的分红派息情况。适用于分红分析、投资决策和收益评估。

**接口列表**:
1. **分红送配详情-指定股票** (`stock_fhps_detail_em`)
   - **功能**: 获取指定股票的分红送配详情数据，包括分红日期、分红金额、送股、转增等信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_fhps_detail_em`
   - **目标地址**: https://data.eastmoney.com/yjfp/
   - **限量**: 单次返回指定股票的分红送配详情数据

2. **分红情况-指定股票** (`stock_fhps_detail_ths`)
   - **功能**: 获取指定股票的分红情况数据，包括分红年度、分红方案等信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_fhps_detail_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票的分红情况数据

3. **历史分红-指定股票** (`stock_dividend_cninfo`)
   - **功能**: 获取指定股票的历史分红记录数据，包括分红日期、除权除息日、股权登记日等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_dividend_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票的历史分红记录数据

**使用示例**:
```json
{
  "interface": "stock_fhps_detail_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_dividend_cninfo",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取个股股东持股变动信息 (get_shareholder_holding_changes)

**工具说明**: 获取股票的股东持股变动信息和股本结构数据，包括基金持股、主要股东、高管持股变动、股东持股变动、公司股本变动、股本结构、十大股东等数据。帮助了解股票的股东变化情况和股本结构变化。适用于股东分析、股本研究和投资决策。

**接口列表**:
1. **股本结构-指定股票** (`stock_zh_a_gbjg_em`)
   - **功能**: 获取指定股票的所有历史股本结构数据，包括总股本、流通受限股份、已流通股份、已上市流通A股、变动原因等详细信息
   - **参数**: 需要股票代码参数，格式为带市场后缀格式如"603392.SH"或"000001.SZ"
   - **AKShare接口**: `stock_zh_a_gbjg_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CapitalStructure/Index?type=web&code=sh603392
   - **限量**: 单次返回指定股票的所有历史股本结构数据

2. **基金持股-指定股票** (`stock_fund_stock_holder`)
   - **功能**: 获取指定股票的基金持股信息，包括基金名称、持股数量、持股比例等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_fund_stock_holder`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的基金持股信息

3. **主要股东-指定股票** (`stock_main_stock_holder`)
   - **功能**: 获取指定股票的主要股东持股信息，包括股东名称、持股数量、持股比例等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_main_stock_holder`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的主要股东持股信息

4. **公司高管持股变动-指定股票** (`stock_management_change_ths`)
   - **功能**: 获取指定股票的公司高管持股变动记录，包括高管姓名、变动日期、变动数量、变动原因等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_management_change_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票的公司高管持股变动记录

5. **公司股东持股变动-指定股票** (`stock_shareholder_change_ths`)
   - **功能**: 获取指定股票的公司股东持股变动记录，包括股东名称、变动日期、变动数量、变动原因等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_shareholder_change_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票的公司股东持股变动记录

6. **公司股本变动-指定股票、时间范围** (`stock_share_change_cninfo`)
   - **功能**: 获取指定股票和时间范围内的股本变动历史数据，包括变动日期、变动原因、变动数量等详细信息
   - **参数**: 需要股票代码、开始日期和结束日期参数。股票代码格式如"600519"（沪市）或"000001"（深市）。日期格式为YYYYMMDD（如20200101、20241231）
   - **AKShare接口**: `stock_share_change_cninfo`
   - **目标地址**: 巨潮资讯
   - **限量**: 单次返回指定股票和时间范围内的股本变动历史数据

7. **十大流通股东-指定股票、日期(季末)** (`stock_gdfx_free_top_10_em`)
   - **功能**: 获取指定股票和日期的十大流通股东数据，包括流通股东排名、持股数量、持股比例等信息
   - **参数**: 需要股票代码和日期参数。股票代码格式如"600519"（沪市）或"000001"（深市）。日期格式为YYYYMMDD，通常为季末日期（如20240930、20241231）
   - **AKShare接口**: `stock_gdfx_free_top_10_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&code=sh600519
   - **限量**: 单次返回指定股票和日期的十大流通股东数据

8. **十大股东-指定股票、日期(季末)** (`stock_gdfx_top_10_em`)
   - **功能**: 获取指定股票和日期的十大股东数据，包括股东排名、持股数量、持股比例等信息
   - **参数**: 需要股票代码和日期参数。股票代码格式如"600519"（沪市）或"000001"（深市）。日期格式为YYYYMMDD，通常为季末日期（如20240930、20241231）
   - **AKShare接口**: `stock_gdfx_top_10_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&code=sh600519
   - **限量**: 单次返回指定股票和日期的十大股东数据

**使用示例**:
```json
{
  "interface": "stock_fund_stock_holder",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_share_change_cninfo",
  "symbol": "600519",
  "start_date": "20200101",
  "end_date": "20241231",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_gdfx_top_10_em",
  "symbol": "600519",
  "date": "20240930",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取A股股东户数数据 (get_stock_shareholder_number_detail)

**工具说明**: 获取A股股东户数数据。基于东方财富网的股东户数详情接口，获取指定股票的股东户数历史数据，包括股东户数、户均持股数、持股集中度等指标的变化趋势。适用于股东结构分析、股东集中度研究和投资决策。

**接口列表**:
1. **股东户数详情-指定股票** (`stock_zh_a_gdhs_detail_em`)
   - **功能**: 获取指定股票的股东户数历史数据，包括股东户数、户均持股数、持股集中度等指标的变化趋势
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_zh_a_gdhs_detail_em`
   - **目标地址**: https://data.eastmoney.com/gdhs/
   - **限量**: 单次返回指定股票的股东户数历史数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_gdhs_detail_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取股票发行与上市数据 (get_stock_issuance_release)

**工具说明**: 获取股票的新股发行、增发和限售解禁数据。帮助了解股票的发行情况和限售股解禁计划。适用于发行分析、解禁监控和投资决策。

**接口列表**:
1. **新股发行-指定股票** (`stock_ipo_info`)
   - **功能**: 获取指定股票的新股发行信息，包括发行价格、发行数量、募集资金等详细信息
   - **参数**: 需要股票代码参数，格式如"600004"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_ipo_info`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的新股发行信息

2. **股票增发-指定股票** (`stock_add_stock`)
   - **功能**: 获取指定股票的股票增发信息，包括增发价格、增发数量、募集资金等详细信息
   - **参数**: 需要股票代码参数，格式如"600004"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_add_stock`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的股票增发信息

3. **限售解禁-指定股票** (`stock_restricted_release_queue_sina`)
   - **功能**: 获取指定股票的限售解禁信息，包括解禁日期、解禁数量、解禁类型等详细信息
   - **参数**: 需要股票代码参数，格式如"600004"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_restricted_release_queue_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票的限售解禁信息

**使用示例**:
```json
{
  "interface": "stock_ipo_info",
  "symbol": "600004",
  "retries": 5,
  "timeout": 240
}
```

```json
{
  "interface": "stock_restricted_release_queue_sina",
  "symbol": "600004",
  "retries": 5,
  "timeout": 240
}
```

---

## 三、行情数据类工具（8个工具）

### 获取个股实时行情 (get_stock_real_time_quote)

**工具说明**: 获取指定股票的实时报价数据，包括买盘卖盘挂单信息。帮助了解股票的实时买卖盘情况。适用于实时行情监控、买卖盘分析和交易决策。

**接口列表**:
1. **行情报价-指定股票** (`stock_bid_ask_em`)
   - **功能**: 获取指定股票的实时买盘卖盘挂单信息，包括买盘价格、买盘数量、卖盘价格、卖盘数量等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）或"000001"（深市）。支持带市场前缀的格式如"SH600519"或"SZ000001"
   - **AKShare接口**: `stock_bid_ask_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回指定股票的实时买盘卖盘挂单信息

**使用示例**:
```json
{
  "interface": "stock_bid_ask_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 240
}
```

---

### 获取个股历史行情 (get_stock_historical_quotes)

**工具说明**: 获取指定股票的历史行情数据，包括日线、周线、月线等不同周期的数据，并可选择前复权、后复权等复权方式。支持A股和科创板历史行情数据。适用于历史行情分析、技术分析和回测研究。

**接口列表**:
1. **沪深京A股-日频率数据-指定股票、周期、复权方式和日期区间** (`stock_zh_a_hist`)
   - **功能**: 获取指定股票的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要股票代码、周期、日期范围和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）。周期选项包括：daily（日线）、weekly（周线）、monthly（月线）。日期格式为YYYYMMDD（如20250801、20250915）。复权方式选项包括：qfq（前复权）、hfq（后复权）、none（不复权）
   - **AKShare接口**: `stock_zh_a_hist`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回指定股票、周期、日期范围和复权方式的历史行情数据

2. **沪深京A股-历史行情日频率数据-指定股票、复权方式和日期区间** (`stock_zh_a_hist_tx`)
   - **功能**: 获取指定股票的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要股票代码、日期范围和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）。日期格式为YYYYMMDD（如20250801、20250915）。复权方式选项包括：qfq（前复权）、hfq（后复权）、none（不复权）
   - **AKShare接口**: `stock_zh_a_hist_tx`
   - **目标地址**: 腾讯证券
   - **限量**: 单次返回指定股票、日期范围和复权方式的历史行情数据

3. **科创板股票历史行情数据-指定股票、复权方式** (`stock_zh_kcb_daily`)
   - **功能**: 获取指定科创板股票的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要股票代码和复权方式参数。股票代码格式为科创板代码（以688开头）。复权方式选项包括：qfq（前复权）、hfq（后复权）、none（不复权）
   - **AKShare接口**: `stock_zh_kcb_daily`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定科创板股票和复权方式的历史行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_hist",
  "symbol": "000001",
  "period": "daily",
  "start_date": "20250801",
  "end_date": "20250915",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "stock_zh_kcb_daily",
  "symbol": "688001",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取个股日内分时行情 (get_stock_intraday_quotes)

**工具说明**: 获取指定股票的日内行情数据，包括分时行情、日内分时数据、分钟数据（包括盘前）、分笔行情数据等。帮助了解股票的日内交易情况。适用于日内交易分析、分时图分析和盘中决策。

**接口列表**:
1. **沪深京A股-每日分时行情-指定股票、分时周期、复权方式和日期区间** (`stock_zh_a_hist_min_em`)
   - **功能**: 获取指定股票的每日分时行情数据，包括时间、开盘价、收盘价、最高价、最低价、成交量、成交额等
   - **参数**: 需要股票代码、分时周期、日期范围和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）。分时周期选项包括：1（1分钟）、5（5分钟）、15（15分钟）、30（30分钟）、60（60分钟）。日期格式为YYYYMMDD（如20250801、20250915）。复权方式选项包括：qfq（前复权）、hfq（后复权）、none（不复权）。注意：1分钟数据不支持复权
   - **AKShare接口**: `stock_zh_a_hist_min_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回指定股票、分时周期、日期范围和复权方式的每日分时行情数据

2. **最近一个交易日-日内分时数据(包括盘前)-指定股票** (`stock_intraday_em`)
   - **功能**: 获取指定股票最近一个交易日的日内分时数据（包括盘前），包括时间、价格、成交量等详细信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_intraday_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回指定股票最近一个交易日的日内分时数据

3. **最近一个交易日-分钟数据(包括盘前)-指定股票、时间区间** (`stock_zh_a_hist_pre_min_em`)
   - **功能**: 获取指定股票最近一个交易日的分钟数据（包括盘前），包括时间、价格、成交量等详细信息
   - **参数**: 需要股票代码和时间区间参数。股票代码格式如"000001"（深市）或"600519"（沪市）。时间格式为HH:MM:SS（如09:00:00、15:00:00）
   - **AKShare接口**: `stock_zh_a_hist_pre_min_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回指定股票最近一个交易日的分钟数据（包括盘前）

4. **最近交易日-历史分笔行情数据-指定股票** (`stock_zh_a_tick_tx`)
   - **功能**: 获取指定股票最近交易日的历史分笔行情数据，包括时间、价格、成交量、买卖方向等详细信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_zh_a_tick_tx`
   - **目标地址**: 腾讯财经
   - **限量**: 单次返回指定股票最近交易日的历史分笔行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_hist_min_em",
  "symbol": "000001",
  "period2": "5",
  "start_date": "20250801",
  "end_date": "20250915",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_intraday_em",
  "symbol": "000001",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股同行业对比 (get_stock_peer_comparison)

**工具说明**: 获取指定股票与同行业公司的比较数据，包括成长性比较、估值比较、杜邦分析比较、公司规模比较等。帮助了解股票在同行业中的地位和表现。适用于行业对比分析、投资决策和基本面研究。

**接口列表**:
1. **同行比较-成长性比较-指定股票** (`stock_zh_growth_comparison_em`)
   - **功能**: 获取指定股票与同行业公司的成长性对比数据，包括营收增长率、利润增长率等成长性指标
   - **参数**: 需要股票代码参数，格式如"000895"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_zh_growth_comparison_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanyCompare/Index?type=web&code=sz000895
   - **限量**: 单次返回指定股票与同行业公司的成长性对比数据

2. **同行比较-估值比较-指定股票** (`stock_zh_valuation_comparison_em`)
   - **功能**: 获取指定股票与同行业公司的估值对比数据，包括市盈率、市净率等估值指标
   - **参数**: 需要股票代码参数，格式如"000895"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_zh_valuation_comparison_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanyCompare/Index?type=web&code=sz000895
   - **限量**: 单次返回指定股票与同行业公司的估值对比数据

3. **同行比较-杜邦分析比较-指定股票** (`stock_zh_dupont_comparison_em`)
   - **功能**: 获取指定股票与同行业公司的杜邦分析对比数据，包括ROE、ROA等财务指标
   - **参数**: 需要股票代码参数，格式如"000895"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_zh_dupont_comparison_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanyCompare/Index?type=web&code=sz000895
   - **限量**: 单次返回指定股票与同行业公司的杜邦分析对比数据

4. **同行比较-公司规模-指定股票** (`stock_zh_scale_comparison_em`)
   - **功能**: 获取指定股票与同行业公司的规模对比数据，包括总资产、净资产等规模指标
   - **参数**: 需要股票代码参数，格式如"000895"（深市）或"600519"（沪市）
   - **AKShare接口**: `stock_zh_scale_comparison_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/CompanyCompare/Index?type=web&code=sz000895
   - **限量**: 单次返回指定股票与同行业公司的规模对比数据

**使用示例**:
```json
{
  "interface": "stock_zh_growth_comparison_em",
  "symbol": "000895",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_zh_valuation_comparison_em",
  "symbol": "000895",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取A股市场股票行情 (get_a_share_market_quotes)

**工具说明**: 获取A股各市场的实时行情数据，包括沪深京A股、沪市、深市、京市、新股等全量市场数据。数据量较大，返回所有股票的实时价格、涨跌幅、成交量等信息。适用于市场行情监控、全量数据分析和投资决策。

**接口列表**:
1. **沪深京A股-实时行情数据-新浪财经** (`stock_zh_a_spot`)
   - **功能**: 获取所有沪深京A股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有沪深京A股的实时行情数据
   - **AKShare接口**: `stock_zh_a_spot`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有沪深京A股的实时行情数据，由于数据量比较大需要等待一定时间

2. **沪深京A股-实时行情数据-东方财富网** (`stock_zh_a_spot_em`)
   - **功能**: 获取所有沪深京A股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有沪深京A股的实时行情数据
   - **AKShare接口**: `stock_zh_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有沪深京A股的实时行情数据，由于数据量比较大需要等待一定时间

3. **沪A股-实时行情数据** (`stock_sh_a_spot_em`)
   - **功能**: 获取所有沪A股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有沪A股的实时行情数据
   - **AKShare接口**: `stock_sh_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有沪A股的实时行情数据，由于数据量比较大需要等待一定时间

4. **深A股-实时行情数据** (`stock_sz_a_spot_em`)
   - **功能**: 获取所有深A股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有深A股的实时行情数据
   - **AKShare接口**: `stock_sz_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有深A股的实时行情数据，由于数据量比较大需要等待一定时间

5. **京A股-实时行情数据** (`stock_bj_a_spot_em`)
   - **功能**: 获取所有京A股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有京A股的实时行情数据
   - **AKShare接口**: `stock_bj_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有京A股的实时行情数据

6. **新股-实时行情数据** (`stock_new_a_spot_em`)
   - **功能**: 获取所有新股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有新股的实时行情数据
   - **AKShare接口**: `stock_new_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有新股的实时行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_spot_em",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "stock_sh_a_spot_em",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取A股板块行情 (get_a_share_board_quotes)

**工具说明**: 获取A股特殊板块的实时行情数据，包括创业板、科创板、新股板块、次新股、风险警示板等全量板块数据。数据量较大，返回板块内所有股票的实时价格、涨跌幅、成交量等信息。适用于板块行情监控、板块数据分析和投资决策。

**接口列表**:
1. **创业板-实时行情** (`stock_cy_a_spot_em`)
   - **功能**: 获取所有创业板股票的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有创业板股票的实时行情数据
   - **AKShare接口**: `stock_cy_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有创业板股票的实时行情数据，由于数据量比较大需要等待一定时间

2. **科创板-实时行情** (`stock_kc_a_spot_em`)
   - **功能**: 获取所有科创板股票的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有科创板股票的实时行情数据
   - **AKShare接口**: `stock_kc_a_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有科创板股票的实时行情数据，由于数据量比较大需要等待一定时间

3. **新股板块-实时行情** (`stock_zh_a_new_em`)
   - **功能**: 获取所有新股板块股票的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有新股板块股票的实时行情数据
   - **AKShare接口**: `stock_zh_a_new_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有新股板块股票的实时行情数据

4. **次新股-实时行情** (`stock_zh_a_new`)
   - **功能**: 获取所有次新股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有次新股的实时行情数据
   - **AKShare接口**: `stock_zh_a_new`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有次新股的实时行情数据

5. **风险警示板-实时行情** (`stock_zh_a_st_em`)
   - **功能**: 获取所有风险警示板股票的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有风险警示板股票的实时行情数据
   - **AKShare接口**: `stock_zh_a_st_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有风险警示板股票的实时行情数据

**使用示例**:
```json
{
  "interface": "stock_cy_a_spot_em",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "stock_kc_a_spot_em",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取A股市场股票比价数据 (get_stock_comparison_quotes)

**工具说明**: 获取股票比价数据，包括AH股比价和AB股比价。帮助了解同一公司在不同市场的价格对比情况。适用于跨市场分析、套利机会识别和投资决策。

**接口列表**:
1. **AH股比价-实时行情** (`stock_zh_ah_spot_em`)
   - **功能**: 获取所有同时在A股和港股上市的公司的价格对比数据，包括A股代码、H股代码、A股价格、H股价格、价差、溢价率等统计信息
   - **参数**: 无需参数，自动返回所有符合条件的AH股比价数据
   - **AKShare接口**: `stock_zh_ah_spot_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有符合条件的AH股比价数据

2. **全量AB股比价** (`stock_zh_ab_comparison_em`)
   - **功能**: 获取所有同时在A股和B股上市的公司的价格对比数据，包括A股代码、B股代码、A股价格、B股价格、价差、溢价率等统计信息
   - **参数**: 无需参数，自动返回所有符合条件的AB股比价数据
   - **AKShare接口**: `stock_zh_ab_comparison_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有符合条件的AB股比价数据

**使用示例**:
```json
{
  "interface": "stock_zh_ah_spot_em",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "stock_zh_ab_comparison_em",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取A股市场特殊股票行情 (get_special_stock_quotes)

**工具说明**: 获取特殊股票类型的实时行情数据，包括两网及退市股票、IPO受益股等。帮助了解特殊股票的交易情况。适用于特殊股票监控、退市股票分析和投资决策。

**接口列表**:
1. **两网及退市-实时行情** (`stock_zh_a_stop_em`)
   - **功能**: 获取所有两网及退市股票的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有两网及退市股票的实时行情数据
   - **AKShare接口**: `stock_zh_a_stop_em`
   - **目标地址**: https://quote.eastmoney.com/center/gridlist.html#hs_a_board
   - **限量**: 单次返回所有两网及退市股票的实时行情数据

2. **IPO受益股-实时行情** (`stock_ipo_benefit_ths`)
   - **功能**: 获取所有IPO受益股的实时行情数据，包括股票代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、换手率等统计信息
   - **参数**: 无需参数，自动返回所有IPO受益股的实时行情数据
   - **AKShare接口**: `stock_ipo_benefit_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有IPO受益股的实时行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_a_stop_em",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "stock_ipo_benefit_ths",
  "retries": 5,
  "timeout": 900
}
```

---

## 四、财务数据类工具（6个工具）

### 获取A股业绩快报数据 (get_stock_performance_reports)

**工具说明**: 获取A股上市公司的业绩快报数据，包括业绩报表、业绩快报、业绩预告以及三大财务报表（利润表、现金流量表、资产负债表）的业绩快报数据。适用于业绩分析、业绩跟踪和投资决策。

**接口列表**:
1. **业绩报表-指定报告日期** (`stock_yjbb_em`)
   - **功能**: 获取指定报告期的业绩报表数据，包括股票代码、股票简称、报告期、营业收入、净利润等统计信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20100331开始
   - **AKShare接口**: `stock_yjbb_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的业绩报表数据

2. **业绩快报-指定报告日期** (`stock_yjkb_em`)
   - **功能**: 获取指定报告期的业绩快报数据，包括股票代码、股票简称、报告期、营业收入、净利润等统计信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20100331开始
   - **AKShare接口**: `stock_yjkb_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的业绩快报数据

3. **业绩预告-指定报告日期** (`stock_yjyg_em`)
   - **功能**: 获取指定报告期的业绩预告数据，包括股票代码、股票简称、报告期、预告类型、预告净利润等统计信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20100331开始
   - **AKShare接口**: `stock_yjyg_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的业绩预告数据

4. **业绩快报-利润表-指定报告日期** (`stock_lrb_em`)
   - **功能**: 获取指定报告期的利润表数据，包括股票代码、股票简称、报告期、营业收入、营业成本、净利润等详细信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20120331开始
   - **AKShare接口**: `stock_lrb_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的利润表数据

5. **业绩快报-现金流量表-指定报告日期** (`stock_xjll_em`)
   - **功能**: 获取指定报告期的现金流量表数据，包括股票代码、股票简称、报告期、经营活动产生的现金流量净额、投资活动产生的现金流量净额、筹资活动产生的现金流量净额等详细信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20120331开始
   - **AKShare接口**: `stock_xjll_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的现金流量表数据

6. **业绩快报-资产负债表-指定报告日期** (`stock_zcfz_em`)
   - **功能**: 获取指定报告期的资产负债表数据，包括股票代码、股票简称、报告期、资产总计、负债总计、所有者权益合计等详细信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'，从20120331开始
   - **AKShare接口**: `stock_zcfz_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回指定报告期的资产负债表数据

7. **北交所-业绩快报-资产负债表-指定报告日期** (`stock_zcfz_bj_em`)
   - **功能**: 获取北交所指定报告期的资产负债表数据，包括股票代码、股票简称、报告期、资产总计、负债总计、所有者权益合计等详细信息
   - **参数**: 需要报告日期参数，格式为YYYYMMDD（如20250630）。格式为'XXXX0331', 'XXXX0630', 'XXXX0930', 'XXXX1231'
   - **AKShare接口**: `stock_zcfz_bj_em`
   - **目标地址**: https://data.eastmoney.com/bkzj/BK0500.html
   - **限量**: 单次返回北交所指定报告期的资产负债表数据

**使用示例**:
```json
{
  "interface": "stock_yjkb_em",
  "date": "20250630",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_lrb_em",
  "date": "20250630",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股财务报表-资产负债表 (get_stock_balance_sheet)

**工具说明**: 获取指定股票的资产负债表数据，包括资产、负债、所有者权益等完整的资产负债表信息，支持东方财富网、同花顺、新浪财经等多个数据源。适用于财务分析、偿债能力分析和投资决策。

**接口列表**:
1. **资产负债表(按报告期)-指定股票** (`stock_balance_sheet_by_report_em`)
   - **功能**: 获取指定股票所有报告期的资产负债表数据，包括资产、负债、所有者权益等完整的资产负债表信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_balance_sheet_by_report_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有报告期的资产负债表数据

2. **资产负债表(按年度)-指定股票** (`stock_balance_sheet_by_yearly_em`)
   - **功能**: 获取指定股票所有年度的资产负债表数据，包括资产、负债、所有者权益等完整的资产负债表信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_balance_sheet_by_yearly_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有年度的资产负债表数据

3. **资产负债表-指定股票、报告类型** (`stock_financial_debt_ths`)
   - **功能**: 获取指定股票指定报告类型的资产负债表所有历史数据，包括资产、负债、所有者权益等完整的资产负债表信息
   - **参数**: 需要股票代码和报告类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）。报告类型选项包括：按年度、按报告期、按单季度
   - **AKShare接口**: `stock_financial_debt_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票指定报告类型的资产负债表所有历史数据

4. **财务报表-三大报表-指定股票、报表类型** (`stock_financial_report_sina`)
   - **功能**: 获取指定股票指定报表类型的所有年份历史数据，包括资产、负债、所有者权益等完整的资产负债表信息
   - **参数**: 需要股票代码和报表类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）。报表类型选项包括：资产负债表、利润表、现金流量表
   - **AKShare接口**: `stock_financial_report_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票指定报表类型的所有年份历史数据

**使用示例**:
```json
{
  "interface": "stock_balance_sheet_by_report_em",
  "stock_code": "000001",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_financial_debt_ths",
  "stock_code": "000001",
  "report_type": "按年度",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股财务报表-利润表 (get_stock_profit_sheet)

**工具说明**: 获取指定股票的利润表数据，包括营业收入、营业成本、净利润等完整的利润表信息，支持东方财富网、同花顺等多个数据源。适用于盈利能力分析、财务分析和投资决策。

**接口列表**:
1. **利润表(按报告期)-指定股票** (`stock_profit_sheet_by_report_em`)
   - **功能**: 获取指定股票所有报告期的利润表数据，包括营业收入、营业成本、净利润等完整的利润表信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_profit_sheet_by_report_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有报告期的利润表数据

2. **利润表(按年度)-指定股票** (`stock_profit_sheet_by_yearly_em`)
   - **功能**: 获取指定股票所有年度的利润表数据，包括营业收入、营业成本、净利润等完整的利润表信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_profit_sheet_by_yearly_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有年度的利润表数据

3. **利润表(按单季度)-指定股票** (`stock_profit_sheet_by_quarterly_em`)
   - **功能**: 获取指定股票所有季度的利润表数据，包括营业收入、营业成本、净利润等完整的利润表信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_profit_sheet_by_quarterly_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有季度的利润表数据

4. **个股利润表-指定股票、报告类型** (`stock_financial_benefit_ths`)
   - **功能**: 获取指定股票指定报告类型的利润表所有历史数据，包括营业收入、营业成本、净利润等完整的利润表信息
   - **参数**: 需要股票代码和报告类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）。报告类型选项包括：年报、季报、中报
   - **AKShare接口**: `stock_financial_benefit_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票指定报告类型的利润表所有历史数据

**使用示例**:
```json
{
  "interface": "stock_profit_sheet_by_report_em",
  "stock_code": "000001",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_financial_benefit_ths",
  "stock_code": "000001",
  "report_type": "年报",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股财务报表-现金流量表 (get_stock_cash_flow_sheet)

**工具说明**: 获取指定股票的现金流量表数据，包括经营活动、投资活动、筹资活动的现金流量信息，支持东方财富网、同花顺等多个数据源。适用于现金流分析、财务分析和投资决策。

**接口列表**:
1. **现金流量表(按报告期)-指定股票** (`stock_cash_flow_sheet_by_report_em`)
   - **功能**: 获取指定股票所有报告期的现金流量表数据，包括经营活动、投资活动、筹资活动的现金流量信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_cash_flow_sheet_by_report_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有报告期的现金流量表数据

2. **现金流量表(按年度)-指定股票** (`stock_cash_flow_sheet_by_yearly_em`)
   - **功能**: 获取指定股票所有年度的现金流量表数据，包括经营活动、投资活动、筹资活动的现金流量信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_cash_flow_sheet_by_yearly_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有年度的现金流量表数据

3. **现金流量表(按单季度)-指定股票** (`stock_cash_flow_sheet_by_quarterly_em`)
   - **功能**: 获取指定股票所有季度的现金流量表数据，包括经营活动、投资活动、筹资活动的现金流量信息
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_cash_flow_sheet_by_quarterly_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票所有季度的现金流量表数据

4. **现金流量表-指定股票、报告类型** (`stock_financial_cash_ths`)
   - **功能**: 获取指定股票指定报告类型的现金流量表所有历史数据，包括经营活动、投资活动、筹资活动的现金流量信息
   - **参数**: 需要股票代码和报告类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）。报告类型选项包括：按年度、按报告期、按单季度
   - **AKShare接口**: `stock_financial_cash_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票指定报告类型的现金流量表所有历史数据

**使用示例**:
```json
{
  "interface": "stock_cash_flow_sheet_by_report_em",
  "stock_code": "000001",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_financial_cash_ths",
  "stock_code": "000001",
  "report_type": "按年度",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股财务指标数据 (get_stock_financial_indicators)

**工具说明**: 获取指定股票的关键财务指标和主要指标数据，包括每股收益、净资产收益率、毛利率、净利率等核心财务指标数据。适用于财务指标分析、投资决策和基本面研究。

**接口列表**:
1. **财务报表-关键指标-指定股票** (`stock_financial_abstract`)
   - **功能**: 获取指定股票所有历史关键指标数据，包括每股收益、净资产收益率、毛利率、净利率等核心财务指标
   - **参数**: 需要股票代码参数，格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）
   - **AKShare接口**: `stock_financial_abstract`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票所有历史关键指标数据

2. **财务指标-主要指标-指定股票、指标类型** (`stock_financial_abstract_ths`)
   - **功能**: 获取指定股票指定指标类型的主要指标所有历史数据，包括每股收益、净资产收益率、毛利率、净利率等核心财务指标
   - **参数**: 需要股票代码和指标类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）。指标类型选项包括：按报告期、按年度、按单季度
   - **AKShare接口**: `stock_financial_abstract_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定股票指定指标类型的主要指标所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_abstract",
  "stock_code": "000001",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_financial_abstract_ths",
  "stock_code": "000001",
  "indicator_ths": "按报告期",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股财务分析指标 (get_stock_financial_analysis_indicators)

**工具说明**: 获取指定股票的详细财务分析指标数据，包括140项详细的财务分析指标，提供全面的财务健康状况分析，支持多年度的财务指标对比分析。适用于综合财务分析、财务健康状况评估和投资决策。

**接口列表**:
1. **A股财务分析-主要指标-指定股票、报告类型** (`stock_financial_analysis_indicator_em`)
   - **功能**: 获取指定股票指定报告类型的财务分析指标所有历史数据，包括140项详细的财务分析指标
   - **参数**: 需要股票代码和报告类型参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）。报告类型选项包括：按报告期、按单季度
   - **AKShare接口**: `stock_financial_analysis_indicator_em`
   - **目标地址**: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sz000001
   - **限量**: 单次返回指定股票指定报告类型的财务分析指标所有历史数据

2. **财务分析-财务指标-指定股票、起始年份** (`stock_financial_analysis_indicator`)
   - **功能**: 获取指定股票从起始年份开始的财务分析指标所有历史数据，包括140项详细的财务分析指标
   - **参数**: 需要股票代码和起始年份参数。股票代码格式如"000001"（深市）或"600519"（沪市）。起始年份格式为YYYY（如2024）
   - **AKShare接口**: `stock_financial_analysis_indicator`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定股票从起始年份开始的财务分析指标所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_analysis_indicator_em",
  "stock_code": "000001",
  "indicator_ths": "按报告期",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_financial_analysis_indicator",
  "stock_code": "000001",
  "start_year": "2024",
  "retries": 5,
  "timeout": 600
}
```

---

## 五、资金流向类工具（6个工具）

### 获取个股资金流向数据 (get_stock_fund_flow)

**工具说明**: 获取指定个股的资金流向数据，包括主力资金、散户资金的流入流出情况，用于分析资金面对个股的影响。适用于资金面分析、主力动向追踪和投资决策。

**接口列表**:
1. **个股资金流向-指定股票、证交所** (`stock_individual_fund_flow`)
   - **功能**: 获取指定个股近100个交易日的资金流向数据，包括主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入等
   - **参数**: 需要股票代码和证交所参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）。证交所选项包括：sh（上海证券交易所）、sz（深圳证券交易所）、bj（北京证券交易所）
   - **AKShare接口**: `stock_individual_fund_flow`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定个股近100个交易日的资金流向数据

**使用示例**:
```json
{
  "interface": "stock_individual_fund_flow",
  "stock_code": "600519",
  "market": "sh",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股筹码分布数据 (get_stock_chip_distribution)

**工具说明**: 获取指定股票的筹码分布数据，分析不同价位的持股成本分布，用于技术分析和主力成本分析。适用于筹码分析、成本分析和投资决策。

**接口列表**:
1. **日K-筹码分布-指定股票、复权方式** (`stock_cyq_em`)
   - **功能**: 获取指定股票近90个交易日的筹码分布数据，包括获利比例、平均成本、90成本区间、70成本区间、集中度等
   - **参数**: 需要股票代码和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"430xxx"（北交所）。复权方式选项包括：前复权(qfq)、后复权(hfq)、不复权(none)
   - **AKShare接口**: `stock_cyq_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定股票近90个交易日的筹码分布数据

**使用示例**:
```json
{
  "interface": "stock_cyq_em",
  "stock_code": "600519",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取当前市场资金流向个股排名 (get_market_stock_fund_flow_rank)

**工具说明**: 获取当前市场中的资金流向个股排名数据，包括整体市场和指定行业内的个股排名，帮助了解哪些个股资金流入流出最多。适用于资金流向分析、个股筛选和投资决策。

**接口列表**:
1. **个股资金流-指定排行类别** (`stock_fund_flow_individual`)
   - **功能**: 获取整体市场个股资金流排行，包括股票代码、股票简称、资金流向、涨跌幅等统计信息
   - **参数**: 需要排行类别参数。排行类别选项包括：即时、3日排行、5日排行、10日排行、20日排行
   - **AKShare接口**: `stock_fund_flow_individual`
   - **目标地址**: 同花顺
   - **限量**: 单次返回整体市场个股资金流排行

2. **行业资金流-xx行业个股资金流-指定行业名称、统计周期** (`stock_sector_fund_flow_summary`)
   - **功能**: 获取指定行业内个股资金流排名，包括股票代码、股票简称、资金流向、涨跌幅等统计信息
   - **参数**: 需要行业名称和统计周期参数。行业名称示例：汽车服务、电源设备、软件开发等。统计周期选项包括：今日、5日、10日（注意：不支持"3日"选项）
   - **AKShare接口**: `stock_sector_fund_flow_summary`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定行业内个股资金流排名

3. **资金流向-排名-指定统计周期** (`stock_individual_fund_flow_rank`)
   - **功能**: 获取整体市场个股资金流排名，包括股票代码、股票简称、资金流向、涨跌幅等统计信息
   - **参数**: 需要统计周期参数。统计周期选项包括：今日、3日、5日、10日
   - **AKShare接口**: `stock_individual_fund_flow_rank`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回整体市场个股资金流排名

4. **主力净流入排名-指定市场选择** (`stock_main_fund_flow`)
   - **功能**: 获取指定市场的主力净流入排名，包括股票代码、股票简称、主力净流入、涨跌幅等统计信息
   - **参数**: 需要市场选择参数。市场选择选项包括：全部股票、沪深A股、沪市A股、科创板、深市A股、创业板、沪市B股、深市B股
   - **AKShare接口**: `stock_main_fund_flow`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定市场的主力净流入排名

**使用示例**:
```json
{
  "interface": "stock_fund_flow_individual",
  "symbol": "即时",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_sector_fund_flow_summary",
  "industry_name": "汽车服务",
  "indicator": "今日",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取市场资金流向历史数据 (get_market_fund_flow_history)

**工具说明**: 获取市场资金流向历史数据，包括大盘总体、行业和概念板块的历史数据，帮助分析资金流向的历史趋势和变化规律。适用于资金流向趋势分析、历史数据研究和投资决策。

**接口列表**:
1. **资金流向-大盘-历史数据** (`stock_market_fund_flow`)
   - **功能**: 获取大盘总体的历史资金流向数据，包括日期、主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_market_fund_flow`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回大盘总体的历史资金流向数据

2. **行业历史资金流-指定行业名称** (`stock_sector_fund_flow_hist`)
   - **功能**: 获取指定行业的历史资金流向数据，包括日期、主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入等统计信息
   - **参数**: 需要行业名称参数。行业名称示例：汽车服务、电源设备、软件开发等。参照东方财富网行业分类
   - **AKShare接口**: `stock_sector_fund_flow_hist`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定行业的历史资金流向数据

3. **概念历史资金流-指定概念名称** (`stock_concept_fund_flow_hist`)
   - **功能**: 获取指定概念板块的历史资金流向数据，包括日期、主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入等统计信息
   - **参数**: 需要概念名称参数。概念名称示例：数据要素、租售同权、人工智能等。参照东方财富网概念分类
   - **AKShare接口**: `stock_concept_fund_flow_hist`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定概念板块的历史资金流向数据

**使用示例**:
```json
{
  "interface": "stock_market_fund_flow",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_sector_fund_flow_hist",
  "industry_name": "汽车服务",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取板块资金流向排名 (get_sector_fund_flow_rank)

**工具说明**: 获取板块资金流向排名数据，包括行业、概念、地域等板块的资金流向排名，帮助了解哪些板块资金流入流出最多。适用于板块资金分析、板块筛选和投资决策。

**接口列表**:
1. **概念资金流-指定排行类别** (`stock_fund_flow_concept`)
   - **功能**: 获取概念板块资金流排行，包括概念名称、资金流向、涨跌幅等统计信息
   - **参数**: 需要排行类别参数。排行类别选项包括：即时、3日排行、5日排行、10日排行、20日排行
   - **AKShare接口**: `stock_fund_flow_concept`
   - **目标地址**: 同花顺
   - **限量**: 单次返回概念板块资金流排行

2. **行业资金流-指定排行类别** (`stock_fund_flow_industry`)
   - **功能**: 获取行业板块资金流排行，包括行业名称、资金流向、涨跌幅等统计信息
   - **参数**: 需要排行类别参数。排行类别选项包括：即时、3日排行、5日排行、10日排行、20日排行
   - **AKShare接口**: `stock_fund_flow_industry`
   - **目标地址**: 同花顺
   - **限量**: 单次返回行业板块资金流排行

3. **板块资金流-排名-指定统计周期、板块类型** (`stock_sector_fund_flow_rank`)
   - **功能**: 获取板块资金流排名，包括板块名称、资金流向、涨跌幅等统计信息，支持行业资金流/概念资金流/地域资金流
   - **参数**: 需要统计周期和板块类型参数。统计周期选项包括：今日、5日、10日（注意：不支持"3日"选项）。板块类型选项包括：行业资金流、概念资金流、地域资金流
   - **AKShare接口**: `stock_sector_fund_flow_rank`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回板块资金流排名

**使用示例**:
```json
{
  "interface": "stock_fund_flow_concept",
  "symbol": "即时",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_sector_fund_flow_rank",
  "indicator": "今日",
  "sector_type": "行业资金流",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取大单追踪数据 (get_big_deal_tracking)

**工具说明**: 获取大单交易的资金流向追踪数据，包括大单买入、卖出的详细信息，用于分析大资金的动向。适用于主力动向追踪、大单分析和投资决策。

**接口列表**:
1. **资金流向-大单追踪** (`stock_fund_flow_big_deal`)
   - **功能**: 获取当前时点的所有大单追踪数据，包括成交时间、股票代码、股票简称、成交价格、成交量、成交额、大单性质、涨跌幅等
   - **参数**: 无需参数
   - **AKShare接口**: `stock_fund_flow_big_deal`
   - **目标地址**: 同花顺
   - **限量**: 单次返回当前时点的所有大单追踪数据

**使用示例**:
```json
{
  "interface": "stock_fund_flow_big_deal",
  "retries": 5,
  "timeout": 600
}
```

---

## 六、技术分析类工具（7个工具）

### 获取技术选股-创新高新低 (get_technical_innovation_high_low)

**工具说明**: 获取股票创新高/创新低的技术选股数据，包括创月新高、半年新高、一年新高、历史新高、创月新低、半年新低、一年新低、历史新低等。适用于技术选股、趋势分析和投资决策。

**接口列表**:
1. **技术选股-创新高-指定新高类别** (`stock_rank_cxg_ths`)
   - **功能**: 获取指定新高类别的所有股票数据，包括股票代码、股票简称、新高日期、新高价格等统计信息
   - **参数**: 需要新高类别参数。新高类别选项包括：创月新高、半年新高、一年新高、历史新高
   - **AKShare接口**: `stock_rank_cxg_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定新高类别的所有股票数据

2. **技术选股-创新低-指定新低类别** (`stock_rank_cxd_ths`)
   - **功能**: 获取指定新低类别的所有股票数据，包括股票代码、股票简称、新低日期、新低价格等统计信息
   - **参数**: 需要新低类别参数。新低类别选项包括：创月新低、半年新低、一年新低、历史新低
   - **AKShare接口**: `stock_rank_cxd_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定新低类别的所有股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_cxg_ths",
  "high_category": "创月新高",
  "retries": 5,
  "timeout": 120
}
```

```json
{
  "interface": "stock_rank_cxd_ths",
  "low_category": "创月新低",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取技术选股-连续涨跌 (get_technical_continuous_rise_fall)

**工具说明**: 获取股票连续上涨/连续下跌的技术选股数据，包括连涨天数、连续涨跌幅、累计换手率等信息。适用于趋势分析、反转分析和投资决策。

**接口列表**:
1. **技术选股-连续上涨** (`stock_rank_lxsz_ths`)
   - **功能**: 获取所有连续上涨的股票数据，包括股票代码、股票简称、连涨天数、连续涨跌幅、累计换手率等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_lxsz_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有连续上涨的股票数据

2. **技术选股-连续下跌** (`stock_rank_lxxd_ths`)
   - **功能**: 获取所有连续下跌的股票数据，包括股票代码、股票简称、连跌天数、连续涨跌幅、累计换手率等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_lxxd_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有连续下跌的股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_lxsz_ths",
  "retries": 5,
  "timeout": 120
}
```

```json
{
  "interface": "stock_rank_lxxd_ths",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取技术选股-成交量分析 (get_technical_volume_analysis)

**工具说明**: 获取股票持续放量/持续缩量的技术选股数据，包括放量天数、缩量天数、阶段涨跌幅等信息。适用于量价分析、技术选股和投资决策。

**接口列表**:
1. **技术选股-持续放量** (`stock_rank_cxfl_ths`)
   - **功能**: 获取所有持续放量的股票数据，包括股票代码、股票简称、放量天数、阶段涨跌幅等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_cxfl_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有持续放量的股票数据

2. **技术选股-持续缩量** (`stock_rank_cxsl_ths`)
   - **功能**: 获取所有持续缩量的股票数据，包括股票代码、股票简称、缩量天数、阶段涨跌幅等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_cxsl_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有持续缩量的股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_cxfl_ths",
  "retries": 5,
  "timeout": 120
}
```

```json
{
  "interface": "stock_rank_cxsl_ths",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取技术选股-突破分析 (get_technical_breakthrough_analysis)

**工具说明**: 获取股票向上突破/向下突破均线的技术选股数据，包括突破不同均线类型（5日、10日、20日、30日、60日、90日、250日、500日均线）的股票信息。适用于突破分析、趋势判断和投资决策。

**接口列表**:
1. **技术选股-向上突破-指定均线类型** (`stock_rank_xstp_ths`)
   - **功能**: 获取向上突破指定均线类型的所有股票数据，包括股票代码、股票简称、突破日期、突破价格等统计信息
   - **参数**: 需要均线类型参数。均线类型选项包括：5日均线、10日均线、20日均线、30日均线、60日均线、90日均线、250日均线、500日均线
   - **AKShare接口**: `stock_rank_xstp_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回向上突破指定均线类型的所有股票数据

2. **技术选股-向下突破-指定均线类型** (`stock_rank_xxtp_ths`)
   - **功能**: 获取向下突破指定均线类型的所有股票数据，包括股票代码、股票简称、突破日期、突破价格等统计信息
   - **参数**: 需要均线类型参数。均线类型选项包括：5日均线、10日均线、20日均线、30日均线、60日均线、90日均线、250日均线、500日均线
   - **AKShare接口**: `stock_rank_xxtp_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回向下突破指定均线类型的所有股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_xstp_ths",
  "ma_type": "5日均线",
  "retries": 5,
  "timeout": 120
}
```

```json
{
  "interface": "stock_rank_xxtp_ths",
  "ma_type": "5日均线",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取技术选股-价量分析 (get_technical_price_volume_analysis)

**工具说明**: 获取股票量价齐升/量价齐跌的技术选股数据，包括量价齐升天数、量价齐跌天数、阶段涨幅、累计换手率等信息。适用于量价关系分析、技术选股和投资决策。

**接口列表**:
1. **技术选股-量价齐升** (`stock_rank_ljqs_ths`)
   - **功能**: 获取所有量价齐升的股票数据，包括股票代码、股票简称、量价齐升天数、阶段涨幅、累计换手率等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_ljqs_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有量价齐升的股票数据

2. **技术选股-量价齐跌** (`stock_rank_ljqd_ths`)
   - **功能**: 获取所有量价齐跌的股票数据，包括股票代码、股票简称、量价齐跌天数、阶段涨幅、累计换手率等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_ljqd_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有量价齐跌的股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_ljqs_ths",
  "retries": 5,
  "timeout": 120
}
```

```json
{
  "interface": "stock_rank_ljqd_ths",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取技术选股-保险披露 (get_technical_insurance_disclosure)

**工具说明**: 获取险资举牌的技术选股数据，包括举牌公告日、举牌方、增持数量、交易均价、持股比例等信息。适用于保险资金动向分析、投资决策和风险监控。

**接口列表**:
1. **技术选股-险资举牌** (`stock_rank_xzjp_ths`)
   - **功能**: 获取所有险资举牌的股票数据，包括股票代码、股票简称、举牌公告日、举牌方、增持数量、交易均价、持股比例等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_rank_xzjp_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回所有险资举牌的股票数据

**使用示例**:
```json
{
  "interface": "stock_rank_xzjp_ths",
  "retries": 5,
  "timeout": 120
}
```

---

### 获取ESG评级数据 (get_esg_rating_data)

**工具说明**: 获取股票的ESG评级数据，包括MSCI、路孚特、秩鼎、华证指数等评级机构的ESG评分、环境总评、社会责任总评、治理总评等信息。适用于ESG投资、社会责任投资和投资决策。

**接口列表**:
1. **ESG评级-MSCI** (`stock_esg_msci_sina`)
   - **功能**: 获取所有股票的MSCI ESG评级数据，包括股票代码、股票简称、ESG评分、环境总评、社会责任总评、治理总评等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_esg_msci_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有股票的MSCI ESG评级数据

2. **ESG评级-路孚特** (`stock_esg_rft_sina`)
   - **功能**: 获取所有股票的路孚特ESG评级数据，包括股票代码、股票简称、ESG评分、环境总评、社会责任总评、治理总评等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_esg_rft_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有股票的路孚特ESG评级数据

3. **ESG评级-秩鼎** (`stock_esg_zd_sina`)
   - **功能**: 获取所有股票的秩鼎ESG评级数据，包括股票代码、股票简称、ESG评分、环境总评、社会责任总评、治理总评等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_esg_zd_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有股票的秩鼎ESG评级数据

4. **ESG评级-华证指数** (`stock_esg_hz_sina`)
   - **功能**: 获取所有股票的华证指数ESG评级数据，包括股票代码、股票简称、ESG评分、环境总评、社会责任总评、治理总评等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_esg_hz_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有股票的华证指数ESG评级数据

**使用示例**:
```json
{
  "interface": "stock_esg_msci_sina",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_esg_rft_sina",
  "retries": 5,
  "timeout": 300
}
```

---

## 七、技术指标类工具（5个工具） ⭐ **扩展指标工具**

### 获取个股趋势动量震荡指标(日频) (get_stock_trend_momentum_daily)

**工具说明**: 获取个股趋势动量震荡指标(日频)。基于历史行情数据自动计算多种技术分析指标，包括移动平均线（MA5/MA10/MA20/MA30/MA60）、RSI相对强弱指标（RSI6/RSI12/RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5/VMA10/VMA20）等。支持日线、周线、月线周期，适用于股票技术分析、趋势判断和交易决策。可帮助投资者识别股票的趋势方向、买卖信号和超买超卖状态。

**接口列表**:
1. **个股趋势动量震荡指标(日频)-指定股票、周期、日期范围、复权方式** (`stock_trend_momentum_oscillator`)
   - **功能**: 基于历史行情数据计算技术指标，包括移动平均线（MA5、MA10、MA20、MA30、MA60）、RSI相对强弱指标（RSI6、RSI12、RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5、VMA10、VMA20）等
   - **参数**: 需要股票代码、周期、开始日期、结束日期和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"688356"（科创板）。周期选项包括：daily(日线)、weekly(周线)、monthly(月线)。开始日期和结束日期格式为YYYYMMDD（如20250101）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)
   - **AKShare接口**: `stock_trend_momentum_oscillator`
   - **目标地址**: 基于AKShare历史行情数据计算
   - **限量**: 单次返回指定股票指定周期和日期范围的技术指标数据

**使用示例**:
```json
{
  "symbol": "000001",
  "period": "daily",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股趋势动量震荡指标(分钟) (get_stock_trend_momentum_minute)

**工具说明**: 获取个股趋势动量震荡指标(分钟)。基于分钟级历史行情数据自动计算多种技术分析指标，包括移动平均线（MA5/MA10/MA20/MA30/MA60）、RSI相对强弱指标（RSI6/RSI12/RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5/VMA10/VMA20）等。支持1分钟、5分钟、15分钟、30分钟、60分钟周期，适用于日内短线交易、分时图技术分析和盘中交易决策。可帮助投资者捕捉短期价格波动、识别日内买卖时机和监控盘中资金流向。

**接口列表**:
1. **个股趋势动量震荡指标(分钟)-指定股票、分钟周期、日期范围、复权方式** (`stock_trend_momentum_oscillator_minute`)
   - **功能**: 基于分钟级历史行情数据计算技术指标，包括移动平均线（MA5、MA10、MA20、MA30、MA60）、RSI相对强弱指标（RSI6、RSI12、RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5、VMA10、VMA20）等
   - **参数**: 需要股票代码、分钟周期、开始日期、结束日期和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"688356"（科创板）。分钟周期选项包括：1(1分钟)、5(5分钟)、15(15分钟)、30(30分钟)、60(60分钟)。开始日期和结束日期格式为YYYYMMDD（如20250101），会自动转换为YYYY-MM-DD 09:30:00和YYYY-MM-DD 15:00:00。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)
   - **AKShare接口**: `stock_trend_momentum_oscillator_minute`
   - **目标地址**: 基于AKShare分钟级历史行情数据计算
   - **限量**: 单次返回指定股票指定分钟周期和日期范围的技术指标数据

**使用示例**:
```json
{
  "symbol": "000001",
  "period": "5",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股动态估值指标 (get_stock_dynamic_valuation)

**工具说明**: 获取个股动态估值指标。基于最新财务数据和当前股价实时计算多种估值指标，包括PE动态、PB动态、PCF动态、PE加权、PE扣非、PB调整后、每股资本公积金比率、每股未分配利润比率、PEG、市净率×ROE等估值指标，以及财务健康度评分、成长性评分、运营效率评分、综合财务评分、评分等级等。适用于股票价值评估、投资决策和基本面分析。可帮助投资者判断股票是否被高估或低估，评估公司的财务健康状况和成长潜力。

**接口列表**:
1. **个股动态估值指标-指定股票** (`stock_dynamic_valuation`)
   - **功能**: 基于最新财务数据和当前股价实时计算估值指标，包括PE动态、PB动态、PCF动态、PE加权、PE扣非、PB调整后、每股资本公积金比率、每股未分配利润比率、PEG、市净率×ROE等估值指标，以及财务健康度评分、成长性评分、运营效率评分、综合财务评分、评分等级等
   - **参数**: 需要股票代码参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"688356"（科创板）
   - **AKShare接口**: `stock_dynamic_valuation`
   - **目标地址**: 基于AKShare最新财务数据和当前股价计算
   - **限量**: 单次返回指定股票的动态估值指标数据

**使用示例**:
```json
{
  "symbol": "000001",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股历史估值指标 (get_stock_historical_valuation)

**工具说明**: 获取个股历史估值指标。基于历史行情数据和历史财务数据计算历史估值指标，包括PE历史、PB历史、PCF历史、PE加权历史、PE扣非历史、PB调整后历史、每股资本公积金比率历史、每股未分配利润比率历史、PEG历史、市净率×ROE历史等，按交易日显示历史估值变化趋势。支持日线、周线、月线周期，适用于估值趋势分析、历史估值对比和投资时机判断。可帮助投资者了解股票估值的历史变化规律，识别估值波动周期，辅助判断最佳买入或卖出时机。

**接口列表**:
1. **个股历史估值指标-指定股票、周期、日期范围、复权方式** (`stock_historical_valuation`)
   - **功能**: 基于历史行情数据和历史财务数据计算历史估值指标，包括PE历史、PB历史、PCF历史、PE加权历史、PE扣非历史、PB调整后历史、每股资本公积金比率历史、每股未分配利润比率历史、PEG历史、市净率×ROE历史等，按交易日显示历史估值变化
   - **参数**: 需要股票代码、周期、开始日期、结束日期和复权方式参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"688356"（科创板）。周期选项包括：daily(日线)、weekly(周线)、monthly(月线)。开始日期和结束日期格式为YYYYMMDD（如20250101）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)
   - **AKShare接口**: `stock_historical_valuation`
   - **目标地址**: 基于AKShare历史行情数据和历史财务数据计算
   - **限量**: 单次返回指定股票指定周期和日期范围的历史估值指标数据

**使用示例**:
```json
{
  "symbol": "000001",
  "period": "daily",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "qfq",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取个股基本信息汇总 (get_stock_basic_info_summary)

**工具说明**: 获取个股基本信息汇总。整合多个数据接口，一次性获取个股的全面基本信息，包括证券资料（股票代码、股票简称、所属行业、最新价格、总市值、流通市值、总股本、流通股等）、公司概况（公司全称、所属市场、成立时间、上市时间、法人代表、注册地址、办公地址、官方网站、联系方式等）、主营业务（主营业务、经营范围、产品类型、产品名称等）、主营业务构成（业务构成详情）等。适用于股票研究、投资分析和公司基本面了解。可帮助投资者快速了解公司的基本情况、业务范围和行业地位，为投资决策提供基础信息支持。

**接口列表**:
1. **个股基本信息汇总-指定股票** (`stock_basic_info_summary`)
   - **功能**: 整合多个接口提供个股的全面基本信息，包括证券资料（股票代码、股票简称、所属行业、最新价格、总市值、流通市值、总股本、流通股等）、公司概况（公司全称、所属市场、成立时间、上市时间、法人代表、注册地址、办公地址、官方网站、联系方式等）、主营业务（主营业务、经营范围、产品类型、产品名称等）、主营业务构成（业务构成详情）等
   - **参数**: 需要股票代码参数。股票代码格式如"000001"（深市）或"600519"（沪市）或"688356"（科创板）
   - **AKShare接口**: `stock_basic_info_summary`
   - **目标地址**: 整合多个AKShare接口
   - **限量**: 单次返回指定股票的全面基本信息汇总数据

**使用示例**:
```json
{
  "symbol": "000001",
  "retries": 5,
  "timeout": 600
}
```

---

## 八、沪深港通类工具（4个工具）

### 获取沪深港通汇率与结算数据 (get_hsgt_exchange_rate_data)

**工具说明**: 获取沪深港通相关的汇率与结算数据，包括深港通和沪港通的结算汇率、参考汇率等信息。帮助了解沪深港通的汇率设置情况。适用于汇率分析、资金结算和投资决策。

**接口列表**:
1. **深港通-港股通业务信息-结算汇率** (`stock_sgt_settlement_exchange_rate_szse`)
   - **功能**: 获取深港通港股通业务信息的结算汇率数据，包括结算日期、结算汇率等详细信息
   - **参数**: 无需参数，自动返回深港通结算汇率数据
   - **AKShare接口**: `stock_sgt_settlement_exchange_rate_szse`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回深港通结算汇率数据

2. **沪港通-港股通信息披露-结算汇兑** (`stock_sgt_settlement_exchange_rate_sse`)
   - **功能**: 获取沪港通港股通信息披露的结算汇兑数据，包括结算日期、结算汇率等详细信息
   - **参数**: 无需参数，自动返回沪港通结算汇率数据
   - **AKShare接口**: `stock_sgt_settlement_exchange_rate_sse`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回沪港通结算汇率数据

3. **深港通-港股通业务信息-参考汇率** (`stock_sgt_reference_exchange_rate_szse`)
   - **功能**: 获取深港通港股通业务信息的参考汇率数据，包括参考日期、参考汇率等详细信息
   - **参数**: 无需参数，自动返回深港通参考汇率数据
   - **AKShare接口**: `stock_sgt_reference_exchange_rate_szse`
   - **目标地址**: 深圳证券交易所
   - **限量**: 单次返回深港通参考汇率数据

4. **沪港通-港股通信息披露-参考汇率** (`stock_sgt_reference_exchange_rate_sse`)
   - **功能**: 获取沪港通港股通信息披露的参考汇率数据，包括参考日期、参考汇率等详细信息
   - **参数**: 无需参数，自动返回沪港通参考汇率数据
   - **AKShare接口**: `stock_sgt_reference_exchange_rate_sse`
   - **目标地址**: 上海证券交易所
   - **限量**: 单次返回沪港通参考汇率数据

**使用示例**:
```json
{
  "interface": "stock_sgt_settlement_exchange_rate_szse",
  "retries": 5,
  "timeout": 300
}
```

```json
{
  "interface": "stock_sgt_reference_exchange_rate_sse",
  "retries": 5,
  "timeout": 300
}
```

---

### 获取沪深港通资金流向数据 (get_hsgt_fund_flow_data)

**工具说明**: 获取沪深港通相关的资金流向数据，包括分时数据、资金流向汇总、历史数据等。帮助了解沪深港通的资金流向情况。适用于资金流向分析、市场情绪监测和投资决策。

**接口列表**:
1. **沪深港通资金流向** (`stock_hsgt_fund_flow_summary_em`)
   - **功能**: 获取沪深港通资金流向汇总数据，包括北向资金、南向资金、沪股通、深股通、港股通沪、港股通深的资金流向、成交额、净流入等统计信息
   - **参数**: 无需参数，自动返回沪深港通资金流向汇总数据
   - **AKShare接口**: `stock_hsgt_fund_flow_summary_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回沪深港通资金流向汇总数据

2. **市场概括-分时数据-指定资金类别** (`stock_hsgt_fund_min_em`)
   - **功能**: 获取沪深港通分时资金流向数据，包括时间、资金流向、成交额、净流入等详细信息
   - **参数**: 需要资金类别参数，选项包括：北向资金、南向资金
   - **AKShare接口**: `stock_hsgt_fund_min_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回指定资金类别的沪深港通分时资金流向数据

3. **资金流向-历史数据-指定历史数据类别** (`stock_hsgt_hist_em`)
   - **功能**: 获取沪深港通历史资金流向数据，包括日期、资金流向、成交额、净流入等详细信息
   - **参数**: 需要历史数据类别参数，选项包括：北向资金、沪股通、深股通、南向资金、港股通沪、港股通深
   - **AKShare接口**: `stock_hsgt_hist_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回指定历史数据类别的沪深港通历史资金流向数据

**使用示例**:
```json
{
  "interface": "stock_hsgt_fund_flow_summary_em",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hsgt_fund_min_em",
  "fund_category": "北向资金",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hsgt_hist_em",
  "historical_data_category": "北向资金",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取沪深港通排行数据 (get_hsgt_ranking_data)

**工具说明**: 获取沪深港通相关的排行数据，包括板块排行、个股排行等。帮助了解沪深港通中不同板块和个股的持股情况排行。适用于排行分析、板块研究和投资决策。

**接口列表**:
1. **沪深港通持股-板块排行-指定排行类别和统计周期** (`stock_hsgt_board_rank_em`)
   - **功能**: 获取板块的沪深港通持股排行数据，包括板块名称、持股比例、持股数量、增持比例等统计信息
   - **参数**: 需要排行类别和统计周期参数。排行类别选项包括：北向资金增持行业板块排行、北向资金增持概念板块排行、北向资金增持地域板块排行。统计周期选项包括：今日、3日、5日、10日、1月、1季、1年
   - **AKShare接口**: `stock_hsgt_board_rank_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回指定排行类别和统计周期的板块排行数据

2. **沪深港通持股-个股排行-指定沪深港通类别和统计周期** (`stock_hsgt_hold_stock_em`)
   - **功能**: 获取个股的沪深港通持股排行数据，包括股票代码、股票名称、持股比例、持股数量、增持比例等统计信息
   - **参数**: 需要沪深港通类别和统计周期参数。沪深港通类别选项包括：北向、沪股通、深股通。统计周期选项包括：今日、3日、5日、10日、1月、1季、1年
   - **AKShare接口**: `stock_hsgt_hold_stock_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回指定沪深港通类别和统计周期的个股排行数据

**使用示例**:
```json
{
  "interface": "stock_hsgt_board_rank_em",
  "symbol": "北向资金增持行业板块排行",
  "indicator": "今日",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hsgt_hold_stock_em",
  "market": "北向",
  "indicator": "1月",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取沪深港通个股持股数据 (get_hsgt_individual_holdings)

**工具说明**: 获取指定股票的沪深港通持股数据，包括A股和港股的持股情况。帮助了解特定股票在沪深港通中的持股情况。适用于个股分析、持股研究和投资决策。

**接口列表**:
1. **沪深港通持股-具体股票-指定A股和港股** (`stock_hsgt_individual_em`)
   - **功能**: 获取指定股票在沪深港通中的持股数据，包括持股比例、持股数量、持股市值等详细信息
   - **参数**: 需要股票代码参数，格式如"600519"（沪市）、"000001"（深市）、"00700"（港股）等
   - **AKShare接口**: `stock_hsgt_individual_em`
   - **目标地址**: https://data.eastmoney.com/hsgt/
   - **限量**: 单次返回指定股票的沪深港通持股数据

**使用示例**:
```json
{
  "interface": "stock_hsgt_individual_em",
  "symbol": "600519",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hsgt_individual_em",
  "symbol": "00700",
  "retries": 5,
  "timeout": 600
}
```

---

## 九、指数数据类工具（3个工具） ⭐ **指数分析工具**

### 获取A股指数实时行情 (get_index_spot_quotes)

**工具说明**: 获取A股指数实时行情数据。包括新浪财经和东方财富网的A股指数实时行情接口，支持按类别查询指数数据。适用于指数监控、市场分析和大盘走势判断。可帮助投资者了解当前市场主要指数的实时表现，辅助判断市场整体趋势。

**接口列表**:
1. **A股指数-实时行情** (`stock_zh_index_spot_sina`)
   - **功能**: 获取所有A股指数实时行情数据，包括指数代码、指数名称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_zh_index_spot_sina`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有A股指数实时行情数据

2. **A股指数-实时行情-按类别** (`stock_zh_index_spot_em`)
   - **功能**: 按类别获取A股指数实时行情数据，包括指数代码、指数名称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 需要指数类别参数。指数类别选项包括：沪深重要指数、上证系列指数、深证系列指数、指数成份、中证系列指数
   - **AKShare接口**: `stock_zh_index_spot_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定类别的A股指数实时行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_index_spot_sina",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_zh_index_spot_em",
  "index_category": "沪深重要指数",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取A股指数历史行情 (get_index_historical_quotes)

**工具说明**: 获取A股指数历史行情数据。包括新浪财经、腾讯证券和东方财富网的A股指数历史行情接口，支持不同周期的历史数据查询（日线、周线、月线）。适用于指数历史走势分析、技术分析和回测研究。可帮助投资者了解指数的历史表现，分析指数趋势和波动规律。

**接口列表**:
1. **A股指数-历史行情数据-指定指数** (`stock_zh_index_daily`)
   - **功能**: 获取指定指数的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要指数代码参数，格式如"sh000001"（上证指数）或"sz399552"（深证成指）
   - **AKShare接口**: `stock_zh_index_daily`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定指数的历史行情数据

2. **A股指数-历史行情数据-指定指数(腾讯)** (`stock_zh_index_daily_tx`)
   - **功能**: 获取指定指数的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要指数代码参数，格式如"sh000001"（上证指数）或"sz399552"（深证成指）
   - **AKShare接口**: `stock_zh_index_daily_tx`
   - **目标地址**: 腾讯证券
   - **限量**: 单次返回指定指数的历史行情数据

3. **A股指数-历史行情数据-指定指数、日期范围** (`stock_zh_index_daily_em`)
   - **功能**: 获取指定指数指定日期范围的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要指数代码、开始日期和结束日期参数。指数代码格式如"sh000001"（上证指数）或"sz399552"（深证成指）。开始日期和结束日期格式为YYYYMMDD（如20250101）
   - **AKShare接口**: `stock_zh_index_daily_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定指数指定日期范围的历史行情数据

4. **A股指数-历史行情数据-通用-指定指数、周期、日期范围** (`index_zh_a_hist`)
   - **功能**: 获取指定指数指定周期和日期范围的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要指数代码、周期、开始日期和结束日期参数。指数代码格式为纯数字（如"000001"上证指数或"399006"创业板指）。周期选项包括：daily(日线)、weekly(周线)、monthly(月线)。开始日期和结束日期格式为YYYYMMDD（如20250101）
   - **AKShare接口**: `index_zh_a_hist`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定指数指定周期和日期范围的历史行情数据

**使用示例**:
```json
{
  "interface": "stock_zh_index_daily",
  "symbol": "sh000001",
  "retries": 5,
  "timeout": 900
}
```

```json
{
  "interface": "index_zh_a_hist",
  "symbol": "000001",
  "period": "daily",
  "start_date": "20250101",
  "end_date": "20251231",
  "retries": 5,
  "timeout": 900
}
```

---

### 获取指数趋势动量震荡指标(日频) (get_index_trend_momentum_daily)

**工具说明**: 获取指数趋势动量震荡指标(日频)。基于历史行情数据自动计算多种技术分析指标，包括移动平均线（MA5/MA10/MA20/MA30/MA60）、RSI相对强弱指标（RSI6/RSI12/RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5/VMA10/VMA20）等。适用于指数技术分析、趋势判断和交易决策。可帮助投资者识别指数的趋势方向、买卖信号和超买超卖状态。

**接口列表**:
1. **指数趋势动量震荡指标-指定指数、日期范围** (`index_trend_momentum_oscillator`)
   - **功能**: 基于历史行情数据计算技术指标，包括移动平均线（MA5、MA10、MA20、MA30、MA60）、RSI相对强弱指标（RSI6、RSI12、RSI24）、MACD指标、KDJ随机指标、布林带指标、成交量均线（VMA5、VMA10、VMA20）等
   - **参数**: 需要指数代码、开始日期和结束日期参数。指数代码格式为带市场标识格式（如"sh000001"上证指数或"sz399552"深证成指）。开始日期和结束日期格式为YYYYMMDD（如20250101）
   - **AKShare接口**: `index_trend_momentum_oscillator`
   - **目标地址**: 基于AKShare历史行情数据计算
   - **限量**: 单次返回指定指数指定日期范围的技术指标数据

**使用示例**:
```json
{
  "interface": "index_trend_momentum_oscillator",
  "symbol": "sh000001",
  "start_date": "20250101",
  "end_date": "20251231",
  "retries": 5,
  "timeout": 900
}
```

---

## 十、港股数据类工具（8个工具） ⭐ **独立工具**

### 获取港股个股基本信息 (get_hk_individual_info)

**工具说明**: 获取港股个股基本信息，包括证券资料和公司资料。适用于港股基本面分析、公司研究和投资决策。

**接口列表**:
1. **港股-个股-证券资料-指定股票代码** (`stock_hk_security_profile_em`)
   - **功能**: 获取指定港股的证券资料数据，包括股票代码、股票简称、所属行业、最新价格、总市值、流通市值、总股本、流通股等详细信息
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）或"HK00700"
   - **AKShare接口**: `stock_hk_security_profile_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的证券资料数据

2. **港股-个股-公司资料-指定股票代码** (`stock_hk_company_profile_em`)
   - **功能**: 获取指定港股的公司资料数据，包括公司全称、所属市场、成立时间、上市时间、法人代表、注册地址、办公地址、官方网站、联系方式等详细信息
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）或"HK00700"
   - **AKShare接口**: `stock_hk_company_profile_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的公司资料数据

**使用示例**:
```json
{
  "interface": "stock_hk_security_profile_em",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hk_company_profile_em",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股个股历史行情 (get_hk_historical_quotes)

**工具说明**: 获取港股个股历史行情数据，包括历史K线数据，支持指定股票代码、周期、日期范围和复权方式。适用于港股技术分析、回测研究和投资决策。

**接口列表**:
1. **港股-历史行情数据-指定股票代码、周期、日期范围、复权方式** (`stock_hk_hist`)
   - **功能**: 获取指定港股指定周期和日期范围的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要港股代码、周期、开始日期、结束日期和复权方式参数。港股代码格式如"00700"（腾讯控股）或"03900"（美团）。周期选项包括：daily(日线)、weekly(周线)、monthly(月线)。开始日期和结束日期格式为YYYYMMDD（如20250101）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)
   - **AKShare接口**: `stock_hk_hist`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股指定周期和日期范围的历史行情数据

2. **港股-历史行情数据-指定股票代码、复权方式** (`stock_hk_daily`)
   - **功能**: 获取指定港股的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要港股代码和复权方式参数。港股代码格式如"00700"（腾讯控股）或"03900"（美团）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)、qfq-factor(前复权因子)、hfq-factor(后复权因子)
   - **AKShare接口**: `stock_hk_daily`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定港股的历史行情数据

**使用示例**:
```json
{
  "interface": "stock_hk_hist",
  "stock_code": "00700",
  "period": "daily",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "none",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hk_daily",
  "stock_code": "00700",
  "adjust": "none",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股每日分时行情 (get_hk_daily_minute_quotes)

**工具说明**: 获取港股个股每日分时行情数据，支持指定股票代码、周期、日期范围和复权方式。帮助了解港股个股的分时交易情况。适用于港股分时分析、日内交易和投资决策。

**接口列表**:
1. **港股-每日分时行情-指定股票代码、周期、日期范围、复权方式** (`stock_hk_hist_min_em`)
   - **功能**: 获取指定港股指定周期和日期范围的每日分时行情数据，包括时间、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要港股代码、周期、开始日期、结束日期和复权方式参数。港股代码格式如"00700"（腾讯控股）或"03900"（美团）。周期选项包括：1(1分钟)、5(5分钟)、15(15分钟)、30(30分钟)、60(60分钟)。开始日期和结束日期格式为YYYYMMDD（如20250101）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)
   - **AKShare接口**: `stock_hk_hist_min_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股指定周期和日期范围的每日分时行情数据

**使用示例**:
```json
{
  "interface": "stock_hk_hist_min_em",
  "stock_code": "00700",
  "period": "5",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "none",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股个股分红派息数据 (get_hk_dividend_payout)

**工具说明**: 获取港股个股分红派息数据，包括同花顺和东方财富网的分红派息信息。帮助了解港股个股的分红派息情况。适用于港股分红分析、股息投资和投资决策。

**接口列表**:
1. **港股-个股-分红派息-指定股票代码** (`stock_hk_fhpx_detail_ths`)
   - **功能**: 获取指定港股的分红派息数据，包括分红日期、分红金额、派息日期、派息金额等详细信息
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）。注意：同花顺接口需要4位数字代码（如0700），会自动转换
   - **AKShare接口**: `stock_hk_fhpx_detail_ths`
   - **目标地址**: 同花顺
   - **限量**: 单次返回指定港股的分红派息数据

2. **港股-个股-分红派息-指定股票代码** (`stock_hk_dividend_payout_em`)
   - **功能**: 获取指定港股的分红派息数据，包括分红日期、分红金额、派息日期、派息金额等详细信息
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）。注意：东方财富网接口需要5位数字代码（如00700）
   - **AKShare接口**: `stock_hk_dividend_payout_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的分红派息数据

**使用示例**:
```json
{
  "interface": "stock_hk_fhpx_detail_ths",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hk_dividend_payout_em",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股财务指标 (get_hk_financial_indicators)

**工具说明**: 获取港股财务分析主要指标数据，支持指定股票代码和指标类型。适用于港股财务分析、投资决策和基本面研究。

**接口列表**:
1. **港股-财务分析-主要指标-指定股票代码、指标类型** (`stock_financial_hk_analysis_indicator_em`)
   - **功能**: 获取指定港股指定指标类型的主要指标所有历史数据，包括每股收益、净资产收益率、毛利率、净利率等核心财务指标
   - **参数**: 需要港股代码和指标类型参数。港股代码格式如"00700"（腾讯控股）或"03900"（美团）。指标类型选项包括：年度、报告期
   - **AKShare接口**: `stock_financial_hk_analysis_indicator_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股指定指标类型的主要指标所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_hk_analysis_indicator_em",
  "stock_code": "00700",
  "indicator_hk": "年度",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股财务报表 (get_hk_financial_statements)

**工具说明**: 获取港股财务分析三大报表数据，包括资产负债表、利润表和现金流量表，支持指定股票代码、报表类型和指标类型。适用于港股财务报表分析、财务分析和投资决策。

**接口列表**:
1. **港股-财务报表-三大报表-指定股票代码、报表类型、指标类型** (`stock_financial_hk_report_em`)
   - **功能**: 获取指定港股指定报表类型和指标类型的三大报表所有历史数据，包括资产负债表、利润表、现金流量表的详细信息
   - **参数**: 需要港股代码、报表类型和指标类型参数。港股代码格式如"00700"（腾讯控股）或"03900"（美团）。报表类型选项包括：资产负债表、利润表、现金流量表。指标类型选项包括：年度、报告期
   - **AKShare接口**: `stock_financial_hk_report_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股指定报表类型和指标类型的三大报表所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_hk_report_em",
  "stock_code": "00700",
  "report_type": "资产负债表",
  "indicator_hk": "年度",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股个股行业对比数据 (get_hk_industry_comparison)

**工具说明**: 获取港股个股行业对比数据，包括成长性对比、估值对比和规模对比。帮助了解港股个股在同行业中的相对表现。适用于港股行业对比、估值分析和投资决策。

**接口列表**:
1. **港股-行业对比-成长性对比-指定股票代码** (`stock_hk_growth_comparison_em`)
   - **功能**: 获取指定港股的成长性对比数据，包括该股票在同行业中的排名和成长性指标对比数据
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）
   - **AKShare接口**: `stock_hk_growth_comparison_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的成长性对比数据

2. **港股-行业对比-估值对比-指定股票代码** (`stock_hk_valuation_comparison_em`)
   - **功能**: 获取指定港股的估值对比数据，包括该股票在同行业中的排名和估值指标对比数据（市盈率、市净率、市销率、市现率等）
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）
   - **AKShare接口**: `stock_hk_valuation_comparison_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的估值对比数据

3. **港股-行业对比-规模对比-指定股票代码** (`stock_hk_scale_comparison_em`)
   - **功能**: 获取指定港股的规模对比数据，包括该股票在同行业中的排名和规模指标对比数据（总市值、流通市值、营业总收入、净利润等）
   - **参数**: 需要港股代码参数，格式如"00700"（腾讯控股）或"03900"（美团）
   - **AKShare接口**: `stock_hk_scale_comparison_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的规模对比数据

**使用示例**:
```json
{
  "interface": "stock_hk_growth_comparison_em",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_hk_valuation_comparison_em",
  "stock_code": "00700",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取港股实时行情 (get_hk_spot_quotes)

**工具说明**: 获取港股实时行情数据，包括东方财富网和新浪的港股实时行情接口，提供港股主板和知名港股实时行情数据。适用于港股实时监控、市场分析和投资决策。

**接口列表**:
1. **港股-实时行情(延15分钟)** (`stock_hk_spot`)
   - **功能**: 获取所有港股的实时行情数据（延迟15分钟），包括股票代码、股票简称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_hk_spot`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有港股的实时行情数据

**使用示例**:
```json
{
  "interface": "stock_hk_spot",
  "retries": 5,
  "timeout": 600
}
```

---

## 十一、美股数据类工具（5个工具） ⭐ **独立工具**

### 获取美股市场实时行情 (get_us_spot_quotes)

**工具说明**: 获取美股市场实时行情数据，包括新浪的美股实时行情接口。适用于美股实时监控、市场分析和投资决策。

**接口列表**:
1. **美股-实时行情(延15分钟)** (`stock_us_spot`)
   - **功能**: 获取所有美股的实时行情数据（延迟15分钟），包括股票代码、股票简称、最新价、涨跌幅、成交量等统计信息
   - **参数**: 无需参数
   - **AKShare接口**: `stock_us_spot`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回所有美股的实时行情数据

**使用示例**:
```json
{
  "interface": "stock_us_spot",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取美股个股历史行情 (get_us_historical_quotes)

**工具说明**: 获取美股个股历史行情数据，包括历史K线数据，支持指定股票代码、周期、日期范围和复权方式。适用于美股技术分析、回测研究和投资决策。

**接口列表**:
1. **美股-每日行情-指定股票代码、周期、日期范围、复权方式** (`stock_us_hist`)
   - **功能**: 获取指定美股指定周期和日期范围的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要美股代码、周期、开始日期、结束日期和复权方式参数。美股代码格式如"AAPL"（苹果）或"MSFT"（微软）或"GOOGL"（谷歌）。周期选项包括：daily(日线)、weekly(周线)、monthly(月线)。开始日期和结束日期格式为YYYYMMDD（如20250101）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)。注意：接口会自动将股票代码转换为105.AAPL格式
   - **AKShare接口**: `stock_us_hist`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定美股指定周期和日期范围的历史行情数据

2. **美股-历史行情数据-指定股票代码、复权方式** (`stock_us_daily`)
   - **功能**: 获取指定美股的历史行情数据，包括日期、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要美股代码和复权方式参数。美股代码格式如"AAPL"（苹果）或"MSFT"（微软）或"GOOGL"（谷歌）。复权方式选项包括：qfq(前复权)、hfq(后复权)、none(不复权)、qfq-factor(前复权因子)、hfq-factor(后复权因子)。注意：新浪接口使用原始格式
   - **AKShare接口**: `stock_us_daily`
   - **目标地址**: 新浪财经
   - **限量**: 单次返回指定美股的历史行情数据

**使用示例**:
```json
{
  "interface": "stock_us_hist",
  "stock_code": "AAPL",
  "period": "daily",
  "start_date": "20250101",
  "end_date": "20251231",
  "adjust": "none",
  "retries": 5,
  "timeout": 600
}
```

```json
{
  "interface": "stock_us_daily",
  "stock_code": "AAPL",
  "adjust": "none",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取美股每日分时行情 (get_us_daily_minute_quotes)

**工具说明**: 获取美股个股每日分时行情数据，自动返回最近5天的分时数据，支持指定股票代码。适用于美股分时分析、日内交易和投资决策。

**接口列表**:
1. **美股-每日分时行情(自动最近5天)-指定股票代码** (`stock_us_hist_min_em`)
   - **功能**: 获取指定港股的最近5天每日分时行情数据，包括时间、开盘价、收盘价、最高价、最低价、成交量等详细信息
   - **参数**: 需要美股代码参数，格式如"AAPL"（苹果）或"MSFT"（微软）或"GOOGL"（谷歌）。注意：接口会自动将股票代码转换为105.AAPL格式，并自动返回最近5天的分时数据
   - **AKShare接口**: `stock_us_hist_min_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定港股的最近5天每日分时行情数据

**使用示例**:
```json
{
  "interface": "stock_us_hist_min_em",
  "stock_code": "AAPL",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取美股财务指标 (get_us_financial_indicators)

**工具说明**: 获取美股财务分析主要指标数据，支持指定股票代码和指标类型。适用于美股财务分析、投资决策和基本面研究。

**接口列表**:
1. **美股-财务分析-主要指标-指定股票代码、指标类型** (`stock_financial_us_analysis_indicator_em`)
   - **功能**: 获取指定美股指定指标类型的主要指标所有历史数据，包括每股收益、净资产收益率、毛利率、净利率等核心财务指标
   - **参数**: 需要美股代码和指标类型参数。美股代码格式如"AAPL"（苹果）或"MSFT"（微软）或"GOOGL"（谷歌）。指标类型选项包括：年报、单季报、累计季报。注意：财务分析接口使用原始格式（不需要105.前缀）
   - **AKShare接口**: `stock_financial_us_analysis_indicator_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定美股指定指标类型的主要指标所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_us_analysis_indicator_em",
  "stock_code": "AAPL",
  "indicator_us": "年报",
  "retries": 5,
  "timeout": 600
}
```

---

### 获取美股财务报表 (get_us_financial_statements)

**工具说明**: 获取美股财务分析三大报表数据，包括资产负债表、利润表和现金流量表，支持指定股票代码、报表类型和指标类型。适用于美股财务报表分析、财务分析和投资决策。

**接口列表**:
1. **美股-财务分析-三大报表-指定股票代码、报表类型、指标类型** (`stock_financial_us_report_em`)
   - **功能**: 获取指定美股指定报表类型和指标类型的三大报表所有历史数据，包括资产负债表、利润表、现金流量表的详细信息
   - **参数**: 需要美股代码、报表类型和指标类型参数。美股代码格式如"AAPL"（苹果）或"MSFT"（微软）或"GOOGL"（谷歌）。报表类型选项包括：资产负债表、利润表、现金流量表。指标类型选项包括：年报、单季报、累计季报。注意：财务分析接口使用原始格式（不需要105.前缀）
   - **AKShare接口**: `stock_financial_us_report_em`
   - **目标地址**: 东方财富网
   - **限量**: 单次返回指定美股指定报表类型和指标类型的三大报表所有历史数据

**使用示例**:
```json
{
  "interface": "stock_financial_us_report_em",
  "stock_code": "AAPL",
  "report_type": "资产负债表",
  "indicator_us": "年报",
  "retries": 5,
  "timeout": 600
}
```

---

## 📝 使用说明

1. **参数格式**: 严格按照各接口要求的参数格式输入
2. **数据更新**: 不同接口的数据更新频率不同，实时数据通常有15分钟延迟
3. **访问限制**: 部分接口有访问频率限制，建议合理控制调用频率
4. **错误处理**: 插件内置重试机制，网络异常时会自动重试
5. **数据格式**: 所有接口返回Markdown表格和JSON两种格式

---

**最后更新**: 2025-11-06  
**版本**: 0.7.0  
**文档类型**: 详细功能文档  
**相关文档**: [README.md](README.md) | [README_EN.md](README_EN.md) | [README_ZH_TW.md](README_ZH_TW.md) | [README_PT_BR.md](README_PT_BR.md)


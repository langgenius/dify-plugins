工具英文名：stock_individual_info_summary
工具中文名：个股信息总貌

identity:
  author: shaoxing_xie
  name: stock_individual_info_summary
  label:
    zh_Hans: 个股信息总貌
    en_US: stock individual information summary  
description:单次返回指定股票代码(symbol)的个股相关信息,包括A股、港股、美股等。

parameters:
  - name: interface
    type: select
    required: true
    form: llm
    default: stock_individual_info_em
    description: 接口名称
    llm_description: 通过AKShare封装的数据接口，获取指定股票代码(symbol)的个股相关信息
    human_description:通过AKShare封装的数据接口，获取指定股票代码(symbol)的个股相关信息
    label:
      en_US: Interface
      zh_Hans: 接口名称
  - name: symbol
    type: string
    required: true
    form: llm
    description: 股票代码
    llm_description: 股票代码，格式：600519、000001、SH600519、SZ000001。A股：6位数字代码(600519)或带市场前缀(SH600519)。B股：9位数字代码(900001)或带市场前缀(SH900001)。美股：股票代码(AAPL、MSFT)。港股：5位数字代码(00700)或带市场前缀(HK00700)。
    human_description:股票代码，格式：600519、000001、SH600519、SZ000001。A股：6位数字代码(600519)或带市场前缀(SH600519)。B股：9位数字代码(900001)或带市场前缀(SH900001)。美股：股票代码(AAPL、MSFT)。港股：5位数字代码(00700)或带市场前缀(HK00700)。
    label:
      en_US: stock code
      zh_Hans: 股票代码
  - name: timeout
    type: number
    required: false
    form: llm
    description: 超时时间
    llm_description: 网络请求超时时间（秒）。范围：5-120。默认：20。网络较慢或数据量较大时可增加。
    human_description:网络请求超时时间（秒）。范围：5-120。默认：20。网络较慢或数据量较大时可增加。
    label:
      en_US: Timeout
      zh_Hans: 超时时间
    min: 5
    max: 120
    
1、接口: stock_individual_info_em
接口中文名：东方财富-个股-股票信息

目标地址: http://quote.eastmoney.com/concept/sh603777.html?from=classic

描述: 东方财富-个股-股票信息

限量: 单次返回指定 symbol 的个股信息

输入参数

| 名称      | 类型    | 描述                      |
|---------|-------|-------------------------|
| symbol  | str   | symbol="603777"; 股票代码   |
| timeout | float | timeout=None; 默认不设置超时参数 |
接口示例：
```python
import akshare as ak

stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)
```

2、接口: stock_bid_ask_em
接口中文名：东方财富-个股-行情报价

目标地址: https://quote.eastmoney.com/sz000001.html

描述: 东方财富-行情报价

限量: 单次返回指定股票的行情报价数据

输入参数

| 名称     | 类型  | 描述                    |
|--------|-----|-----------------------|
| symbol | str | symbol="000001"; 股票代码 |
接口示例：
```python
import akshare as ak

stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol="000001")
print(stock_bid_ask_em_df)
```
3、接口:  stock_zyjs_ths
接口中文名：同花顺-个股-主营介绍

目标地址: https://basic.10jqka.com.cn/new/000066/operate.html

描述: 同花顺-主营介绍

限量: 单次返回所有数据

输入参数

| 名称     | 类型  | 描述              |
|--------|-----|-----------------|
| symbol | str | symbol="000066" |

接口示例：
```python
import akshare as ak

stock_zyjs_ths_df = ak.stock_zyjs_ths(symbol="000066")
print(stock_zyjs_ths_df)
```

4、接口英文名: stock_zygc_em
接口中文名：东方财富网-个股-主营构成

目标地址: https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/Index?type=web&code=SH688041#

描述: 东方财富网-个股-主营构成

限量: 单次返回所有历史数据

输入参数

| 名称     | 类型  | 描述                |
|--------|-----|-------------------|
| symbol | str | symbol="SH688041" |
接口示例：
```python
import akshare as ak

stock_zygc_em_df = ak.stock_zygc_em(symbol="SH688041")
print(stock_zygc_em_df)
```

5、接口英文名:  stock_news_em
接口中文名：东方财富-个股-新闻资讯数据

目标地址: https://so.eastmoney.com/news/s?keyword=603777

描述: 东方财富指定个股的新闻资讯数据

限量: 指定 symbol 当日最近 100 条新闻资讯数据

输入参数

| 名称     | 类型  | 描述                          |
|--------|-----|-----------------------------|
| symbol | str | symbol="603777"; 股票代码或其他关键词 |
接口示例：
```python
import akshare as ak

stock_news_em_df = ak.stock_news_em(symbol="603777")
print(stock_news_em_df)
```

6、接口英文名: stock_profile_cninfo
接口中文名：A股-个股-公司概况

目标地址: http://webapi.cninfo.com.cn/#/company

描述: 巨潮资讯-个股-公司概况

限量: 单次获取指定 symbol 的公司概况

输入参数

| 名称         | 类型  | 描述                    |
|------------|-----|-----------------------|
| symbol     | str | symbol="600030"       |
接口示例：
```python
import akshare as ak

stock_profile_cninfo_df = ak.stock_profile_cninfo(symbol="600030")
print(stock_profile_cninfo_df)
```

7、接口英文名: stock_ipo_summary_cninfo
接口中文名：A股-个股-上市相关资讯

目标地址: https://webapi.cninfo.com.cn/#/company

描述: 巨潮资讯-个股-上市相关资讯

限量: 单次获取指定 symbol 的上市相关数据

输入参数

| 名称         | 类型  | 描述                    |
|------------|-----|-----------------------|
| symbol     | str | symbol="600030"       |
接口示例：
```python
import akshare as ak

stock_ipo_summary_cninfo_df = ak.stock_ipo_summary_cninfo(symbol="600030")
print(stock_ipo_summary_cninfo_df)
```

8、接口英文名: stock_fhps_detail_em
接口中文名：东方财富网-个股-分红送配详情

目标地址: https://data.eastmoney.com/yjfp/detail/300073.html

描述: 东方财富网-数据中心-分红送配-分红送配详情

限量: 单次获取指定 symbol 的分红配送详情数据

输入参数

| 名称     | 类型  | 描述              |
|--------|-----|-----------------|
| symbol | str | symbol="300073" |
接口示例：
```python
import akshare as ak

stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol="300073")
print(stock_fhps_detail_em_df)
```


9、接口英文名: stock_research_report_em
接口中文名：东方财富网-研究报告-个股研报

目标地址: https://data.eastmoney.com/report/stock.jshtml

描述: 东方财富网-数据中心-研究报告-个股研报

限量: 单次返回指定 symbol 的所有数据

输入参数

| 名称     | 类型  | 描述              |
|--------|-----|-----------------|
| symbol | str | symbol="000001" |
接口示例：
```python
import akshare as ak

stock_research_report_em_df = ak.stock_research_report_em(symbol="000001")
print(stock_research_report_em_df)
```

10、接口英文名: stock_balance_sheet_by_report_em
接口中文名：东方财富-个股-资产负债表-按报告期

目标地址: https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0

描述: 东方财富-股票-财务分析-资产负债表-按报告期

限量: 单次获取指定 symbol 的资产负债表-按报告期数据

输入参数

| 名称     | 类型  | 描述                      |
|--------|-----|-------------------------|
| symbol | str | symbol="SH600519"; 股票代码 |
接口示例：
```python
import akshare as ak

stock_balance_sheet_by_report_em_df = ak.stock_balance_sheet_by_report_em(symbol="SH600519")
print(stock_balance_sheet_by_report_em_df)
```

11、接口英文名: stock_financial_abstract
接口中文名：新浪财经-个股-财务报表-关键指标

目标地址: https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/600004.phtml

描述: 新浪财经-财务报表-关键指标

限量: 单次获取关键指标所有历史数据

输入参数

| 名称     | 类型  | 描述                    |
|--------|-----|-----------------------|
| symbol | str | symbol="600004"; 股票代码 |
接口示例：
```python
import akshare as ak

stock_financial_abstract_df = ak.stock_financial_abstract(symbol="600004")
print(stock_financial_abstract_df)
```

12、接口: stock_hk_security_profile_em
接口中文名：东方财富-港股-个股-证券资料

目标地址: https://emweb.securities.eastmoney.com/PC_HKF10/pages/home/index.html?code=03900&type=web&color=w#/CompanyProfile

描述: 东方财富-港股-证券资料

限量: 单次返回全部数据

输入参数

| 名称     | 类型  | 描述             |
|--------|-----|----------------|
| symbol | str | symbol="03900" |
接口示例：
```python
import akshare as ak

stock_hk_security_profile_em_df = ak.stock_hk_security_profile_em(symbol="03900")
print(stock_hk_security_profile_em_df)
```

13、接口: stock_hk_company_profile_em
接口中文名：东方财富-港股-个股-公司资料

目标地址: https://emweb.securities.eastmoney.com/PC_HKF10/pages/home/index.html?code=03900&type=web&color=w#/CompanyProfile

描述: 东方财富-港股-公司资料

限量: 单次返回全部数据

输入参数

| 名称     | 类型  | 描述             |
|--------|-----|----------------|
| symbol | str | symbol="03900" |
接口示例：
```python
import akshare as ak

stock_hk_company_profile_em_df = ak.stock_hk_company_profile_em(symbol="03900")
print(stock_hk_company_profile_em_df)
```

14、接口: stock_hk_fhpx_detail_ths
接口中文名：同花顺-港股-个股-分红派息

目标地址: https://stockpage.10jqka.com.cn/HK0700/bonus/

描述: 同花顺-港股-分红派息

限量: 单次获取指定股票的分红派息数据

输入参数

| 名称     | 类型  | 描述                  |
|--------|-----|---------------------|
| symbol | str | symbol="0700"; 港股代码 |
接口示例：
```python
import akshare as ak

stock_hk_fhpx_detail_ths_df = ak.stock_hk_fhpx_detail_ths(symbol="0700")
print(stock_hk_fhpx_detail_ths_df)
```

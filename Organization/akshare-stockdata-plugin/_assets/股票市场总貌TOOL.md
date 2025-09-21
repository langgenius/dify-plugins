工具英文名：stock_market_summary
工具中文名：股票市场总貌

identity:
  author: shaoxing_xie
  name: stock_market_summary
  label:
    zh_Hans: 股票市场总貌
    en_US: stock market summary
description:单次返回最近交易日或指定date的股票市场总貌数据(当前交易日的数据需要交易所收盘后统计)

parameters:
  - name: interface
    type: select
    required: true
    form: llm
    default: stock_sse_summary
    description: 接口名称
    llm_description: 通过AKShare封装的数据接口，获取股票市场总貌数据
    human_description:通过AKShare封装的数据接口，获取股票市场总貌数据
    label:
      en_US: Interface
      zh_Hans: 接口名称
  - name: date
    type: string
    required: false
    form: llm
    description: 交易日期
    llm_description: 交易日期，格式如20250901;"上交所-股票数据总貌"接口：不用填写，其它接口都要填写
    human_description:交易日期，格式如20250901;"上交所-股票数据总貌"接口：不用填写，其它接口都要填写
    label:
      en_US: Trading Date
      zh_Hans: 交易日期
    
包括以下接口:
1、接口: stock_sse_summary 
接口中文名：上交所-股票数据总貌 

目标地址: http://www.sse.com.cn/market/stockdata/statistic/

描述: 上海证券交易所-股票数据总貌

限量: 单次返回最近交易日的股票数据总貌(当前交易日的数据需要交易所收盘后统计)

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例
```python
import akshare as ak

stock_sse_summary_df = ak.stock_sse_summary()
print(stock_sse_summary_df)
```

2、接口: stock_szse_summary
接口中文名：深交所-市场总貌-证券类别统计

目标地址: http://www.szse.cn/market/overview/index.html

描述: 深圳证券交易所-市场总貌-证券类别统计

限量: 单次返回指定 date 的市场总貌数据-证券类别统计(当前交易日的数据需要交易所收盘后统计)

输入参数

| 名称   | 类型  | 描述                                  |
|------|-----|-------------------------------------|
| date | str | date="20200619"; 当前交易日的数据需要交易所收盘后统计 |
接口示例：
```python
import akshare as ak

stock_szse_summary_df = ak.stock_szse_summary(date="20200619")
print(stock_szse_summary_df)
```

3、接口: stock_sse_deal_daily
接口中文名：上交所-股票成交概况-每日股票情况

目标地址: http://www.sse.com.cn/market/stockdata/overview/day/

描述: 上海证券交易所-数据-股票数据-成交概况-股票成交概况-每日股票情况

限量: 单次返回指定日期的每日概况数据, 当前交易日数据需要在收盘后获取; 注意仅支持获取在 20211227（包含）之后的数据

输入参数

| 名称   | 类型  | 描述                                                              |
|------|-----|-----------------------------------------------------------------|
| date | str | date="20250221"; 当前交易日的数据需要交易所收盘后统计; 注意仅支持获取在 20211227（包含）之后的数据 |
接口示例:
```python
import akshare as ak

stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date="20250221")
print(stock_sse_deal_daily_df)
```

5、接口: stock_zh_a_st_em
接口中文名：东方财富网-沪深个股-风险警示板

目标地址: https://quote.eastmoney.com/center/gridlist.html#st_board

描述: 东方财富网-行情中心-沪深个股-风险警示板

限量: 单次返回当前交易日风险警示板的所有股票的行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例:
```python
import akshare as ak

stock_zh_a_st_em_df = ak.stock_zh_a_st_em()
print(stock_zh_a_st_em_df)
```

4、接口: stock_gsrl_gsdt_em
接口中文名：东方财富网-股市日历-公司动态

目标地址: https://data.eastmoney.com/gsrl/gsdt.html

描述: 东方财富网-数据中心-股市日历-公司动态

限量: 单次返回指定交易日的数据

输入参数

| 名称   | 类型  | 描述                   |
|------|-----|----------------------|
| date | str | date="20230808"; 交易日 |
接口示例:
```python
import akshare as ak

stock_gsrl_gsdt_em_df = ak.stock_gsrl_gsdt_em(date="20230808")
print(stock_gsrl_gsdt_em_df)
```

6、接口: stock_gpzy_profile_em
接口中文名：东方财富网-股权质押-股权质押市场概况

目标地址: https://data.eastmoney.com/gpzy/marketProfile.aspx

描述: 东方财富网-数据中心-特色数据-股权质押-股权质押市场概况

限量: 单次所有历史数据, 由于数据量比较大需要等待一定时间

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例:
```python
import akshare as ak

stock_gpzy_profile_em_df = ak.stock_gpzy_profile_em()
print(stock_gpzy_profile_em_df)
```

8、接口: stock_gpzy_industry_data_em
接口中文名：东方财富网-股权质押-上市公司质押比例-行业数据

目标地址: https://data.eastmoney.com/gpzy/industryData.aspx

描述: 东方财富网-数据中心-特色数据-股权质押-上市公司质押比例-行业数据

限量: 单次返回所有历史数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例:
```python
import akshare as ak

stock_gpzy_industry_data_em_df = ak.stock_gpzy_industry_data_em()
print(stock_gpzy_industry_data_em_df)
```

9、接口: stock_sy_profile_em
接口中文名：东方财富网-商誉-A股商誉市场概况

目标地址:  https://data.eastmoney.com/sy/scgk.html

描述: 东方财富网-数据中心-特色数据-商誉-A股商誉市场概况

限量: 单次所有历史数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例:
```python
import akshare as ak

stock_sy_profile_em_df = ak.stock_sy_profile_em()
print(stock_sy_profile_em_df)
```

10、接口: stock_account_statistics_em
接口中文名：东方财富网-特色数据-股票账户统计

目标地址: https://data.eastmoney.com/cjsj/gpkhsj.html

描述: 东方财富网-数据中心-特色数据-股票账户统计

限量: 单次返回从 201504 开始 202308 的所有历史数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |

接口示例:
```python
import akshare as ak

stock_account_statistics_em_df = ak.stock_account_statistics_em()
print(stock_account_statistics_em_df)
```

### 千股千评

接口: stock_comment_em
接口中文名：东方财富网-特色数据-千股千评

目标地址: https://data.eastmoney.com/stockcomment/

描述: 东方财富网-数据中心-特色数据-千股千评

限量: 单次获取所有数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |

接口示例

```python
import akshare as ak

stock_comment_em_df = ak.stock_comment_em()
print(stock_comment_em_df)
```


#### 打新收益率

接口: stock_dxsyl_em
接口中文名：东方财富网-新股申购-打新收益率

目标地址: https://data.eastmoney.com/xg/xg/dxsyl.html

描述: 东方财富网-数据中心-新股申购-打新收益率

限量: 单次获取所有打新收益率数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |

输出参数

| 名称       | 类型      | 描述      |
|----------|---------|---------|
| 股票代码     | object  | -       |
| 股票简称     | object  | -       |
| 发行价      | float64 | -       |
| 最新价      | float64 | -       |
| 网上发行中签率  | float64 | 注意单位: % |
| 网上有效申购股数 | int64   | -       |
| 网上有效申购户数 | int64   | 注意单位: 户 |
| 网上超额认购倍数 | float64 | -       |
| 网下配售中签率  | float64 | 注意单位: % |
| 网下有效申购股数 | int64   | -       |
| 网下有效申购户数 | int64   | 注意单位: 户 |
| 网下配售认购倍数 | float64 | -       |
| 总发行数量    | int64   | -       |
| 开盘溢价     | float64 | -       |
| 首日涨幅     | float64 | -       |
| 上市日期     | object  | -       |

接口示例

```python
import akshare as ak

stock_dxsyl_em_df = ak.stock_dxsyl_em()
print(stock_dxsyl_em_df)
```

数据示例

```
      序号   股票代码  股票简称  发行价  ...   总发行数量    开盘溢价  首日涨幅    上市日期
0        1  301502  N华阳智   28.01  ...  1427.1000  114.209211  114.1021  2024-02-02
1        2  603082   C北自   21.28  ...  4055.6900  116.165414  118.0451  2024-01-30
2        3  603375   盛景微   38.18  ...  2516.6667   70.246202   54.4002  2024-01-24
3        4  301577  美信科技   36.51  ...  1109.5149  119.118050   88.7976  2024-01-24
4        5  001379  腾达科技   16.98  ...  5000.0000   64.899882   42.6973  2024-01-19
    ...     ...   ...     ...  ...        ...         ...       ...         ...
3494  3495  688709  成都华微   15.69  ...  9560.0000         NaN       NaN         NaT
3495  3496  688584  上海合晶   22.66  ...  6620.6036         NaN       NaN         NaT
3496  3497  603341  龙旗科技     NaN  ...  6000.0000         NaN       NaN         NaT
3497  3498  301591  肯特股份     NaN  ...  2103.0000         NaN       NaN         NaT
3498  3499  301589  诺瓦星云  126.89  ...  1284.0000         NaN       NaN         NaT
[3499 rows x 17 columns]
```

### 停复牌

接口: news_trade_notify_suspend_baidu
接口中文名：百度股市通-交易提醒-停复牌

目标地址: https://gushitong.baidu.com/calendar

描述: 百度股市通-交易提醒-停复牌

限量: 单次获取指定 date 的停复牌数据, 提供港股的停复牌数据

输入参数

| 名称   | 类型  | 描述              |
|------|-----|-----------------|
| date | str | date="20241107" |

输出参数

| 名称     | 类型     | 描述  |
|--------|--------|-----|
| 股票代码   | object |     |
| 股票简称   | object |     |
| 交易所    | object |     |
| 停牌时间   | object |     |
| 复牌时间   | object |     |
| 停牌事项说明 | object |     |

接口示例

```python
import akshare as ak

news_trade_notify_suspend_baidu_df = ak.news_trade_notify_suspend_baidu(date="20241107")
print(news_trade_notify_suspend_baidu_df)
```

### 分红派息

接口: news_trade_notify_dividend_baidu
接口中文名：百度股市通-交易提醒-分红派息

目标地址: https://gushitong.baidu.com/calendar

描述: 百度股市通-交易提醒-分红派息

限量: 单次获取指定 date 的分红派息数据, 提供港股的分红派息数据

输入参数

| 名称   | 类型  | 描述              |
|------|-----|-----------------|
| date | str | date="20241107" |

输出参数

| 名称   | 类型     | 描述  |
|------|--------|-----|
| 股票代码 | object |     |
| 除权日  | object |     |
| 分红   | object |     |
| 送股   | object |     |
| 转增   | object |     |
| 实物   | object |     |
| 交易所  | object |     |
| 股票简称 | object |     |
| 报告期  | object |     |

接口示例

```python
import akshare as ak

news_trade_notify_dividend_baidu_df = ak.news_trade_notify_dividend_baidu(date="20241107")
print(news_trade_notify_dividend_baidu_df)
```

工具英文名：Stock_hist_quotations
工具中文名：股票历史行情

identity:
  author: shaoxing_xie
  name: Stock hist quotations
  label:
    zh_Hans: 股票历史行情
    en_US: Stock History quotations 
description:单次返回指定股票市场上市公司、指定周期和指定日期间的历史行情日频率数据;历史数据按日频率更新, 当日收盘价请在收盘后获取。

parameters:
  - name: interface
    type: select
    required: true
    form: llm
    default: stock_zh_a_hist
    description: 接口名称
    llm_description: 通过AKShare封装的数据接口，获取指定股票市场上市公司、指定周期和指定日期间的历史行情日频率数据;历史数据按日频率更新, 当日收盘价请在收盘后获取。
    human_description:通过AKShare封装的数据接口，获取指定股票市场上市公司、指定周期和指定日期间的历史行情日频率数据;历史数据按日频率更新, 当日收盘价请在收盘后获取。
    label:
      en_US: Interface
      zh_Hans: 接口名称
      
1、接口 stock_zh_a_hist
接口中文名：东方财富-沪深京A股-日频率数据

描述: 东方财富-沪深京 A 股日频率数据; 历史数据按日频率更新, 当日收盘价请在收盘后获取
限量: 单次返回指定沪深京 A 股上市公司、指定周期和指定日期间的历史行情日频率数据
输入参数：
| 名称         | 类型    | 描述                                                       |
|------------|-------|----------------------------------------------------------|
| symbol     | str   | symbol='603777'; 股票代码可以在 **ak.stock_zh_a_spot_em()** 中获取 |
| period     | str   | period='daily'; choice of {'daily', 'weekly', 'monthly'} |
| start_date | str   | start_date='20210301'; 开始查询的日期                           |
| end_date   | str   | end_date='20210616'; 结束查询的日期                             |
| adjust     | str   | 默认返回不复权的数据; qfq: 返回前复权后的数据; hfq: 返回后复权后的数据               |
| timeout    | float | timeout=None; 默认不设置超时参数  
接口示例：
```python
import akshare as ak

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="")
print(stock_zh_a_hist_df)
```

2、接口: stock_zh_a_hist_min_em
接口中文名：东方财富网-沪深京 A 股-每日分时行情

描述: 东方财富网-行情首页-沪深京 A 股-每日分时行情; 该接口只能获取近期的分时数据，注意时间周期的设置
限量: 单次返回指定股票、频率、复权调整和时间区间的分时数据, 其中 1 分钟数据只返回近 5 个交易日数据且不复权
输入参数：
|------------|-----|-----------------------------------------------------------------------------------------------------|
| symbol     | str | symbol='000300'; 股票代码                                                                               |
| start_date | str | start_date="1979-09-01 09:32:00"; 日期时间; 默认返回所有数据                                                    |
| end_date   | str | end_date="2222-01-01 09:32:00"; 日期时间; 默认返回所有数据                                                      |
| period     | str | period='5'; choice of {'1', '5', '15', '30', '60'}; 其中 1 分钟数据返回近 5 个交易日数据且不复权                       |
| adjust     | str | adjust=''; choice of {'', 'qfq', 'hfq'}; '': 不复权, 'qfq': 前复权, 'hfq': 后复权, 其中 1 分钟数据返回近 5 个交易日数据且不复权 |
接口示例：
```python
import akshare as ak

# 注意：该接口返回的数据只有最近一个交易日的有开盘价，其他日期开盘价为 0
stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000001", start_date="2024-03-20 09:30:00", end_date="2024-03-20 15:00:00", period="1", adjust="")
print(stock_zh_a_hist_min_em_df)
```

3、接口: stock_intraday_em
接口中文名：东方财富-最近一个交易日-分时数据
描述: 东方财富-分时数据
限量: 单次返回指定股票最近一个交易日的分时数据, 包含盘前数据
输入参数：
| 名称         | 类型  | 描述                                  |
|------------|-----|-------------------------------------|
| symbol     | str | symbol="000001"; 股票代码               |
接口示例：
```python
import akshare as ak

stock_intraday_em_df = ak.stock_intraday_em(symbol="000001")
print(stock_intraday_em_df)
```

4、接口: stock_zh_a_hist_pre_min_em
接口中文名：东方财富-最近一个交易日-盘前数据
描述: 东方财富-股票行情-盘前数据
限量: 单次返回指定 symbol 的最近一个交易日的股票分钟数据, 包含盘前分钟数据
输入参数：
|------------|-----|-------------------------------------|
| symbol     | str | symbol="000001"; 股票代码               |
| start_time | str | start_time="09:00:00"; 时间; 默认返回所有数据 |
| end_time   | str | end_time="15:40:00"; 时间; 默认返回所有数据   |
接口示例：
```python
import akshare as ak

stock_zh_a_hist_pre_min_em_df = ak.stock_zh_a_hist_pre_min_em(symbol="000001", start_time="09:00:00", end_time="15:40:00")
print(stock_zh_a_hist_pre_min_em_df)
```

5、接口: stock_zh_kcb_daily
接口中文名：新浪财经-科创板股票历史行情数据

描述: 新浪财经-科创板股票历史行情数据
限量: 单次返回指定 symbol 和 adjust 的所有历史行情数据; 请控制采集的频率, 大量抓取容易封IP
输入参数：
| 名称     | 类型  | 描述                                                                                 |
|--------|-----|------------------------------------------------------------------------------------|
| symbol | str | symbol="sh688008"; 带市场标识的股票代码                                                      |
| adjust | str | 默认不复权的数据; qfq: 返回前复权后的数据; hfq: 返回后复权后的数据; hfq-factor: 返回后复权因子; qfq-factor: 返回前复权因子 |
接口示例：
```python
import akshare as ak

stock_zh_kcb_daily_df = ak.stock_zh_kcb_daily(symbol="sh688399", adjust="hfq")
print(stock_zh_kcb_daily_df)
```

6、接口: stock_hk_hist
接口中文名：东方财富-港股-历史行情数据

目标地址: https://quote.eastmoney.com/hk/08367.html

描述: 港股-历史行情数据, 可以选择返回复权后数据, 更新频率为日频

限量: 单次返回指定上市公司的历史行情数据
输入参数：
| 名称         | 类型  | 描述                                                             |
|------------|-----|----------------------------------------------------------------|
| symbol     | str | symbol="00593"; 港股代码,可以通过 **ak.stock_hk_spot_em()** 函数返回所有港股代码 |
| period     | str | period='daily'; choice of {'daily', 'weekly', 'monthly'}       |
| start_date | str | start_date="19700101"; 开始日期                                    |
| end_date   | str | end_date="22220101"; 结束日期                                      |
| adjust     | str | adjust="": 返回未复权的数据, 默认; qfq: 返回前复权数据; hfq: 返回后复权数据;       
接口示例：
```python
import akshare as ak

stock_hk_hist_df = ak.stock_hk_hist(symbol="00593", period="daily", start_date="19700101", end_date="22220101", adjust="")
print(stock_hk_hist_df)
```

7、接口: stock_hk_hist_min_em
接口中文名：东方财富网-港股-每日分时行情

目标地址: http://quote.eastmoney.com/hk/00948.html

描述: 东方财富网-行情首页-港股-每日分时行情

限量: 单次返回指定上市公司最近 5 个交易日分钟数据, 注意港股有延时

输入参数：
| 名称         | 类型  | 描述                                                                                                  |
|------------|-----|-----------------------------------------------------------------------------------------------------|
| symbol     | str | symbol="01611"; 港股代码可以通过 **ak.stock_hk_spot_em()** 函数返回所有的 pandas.DataFrame 里面的 `代码` 字段获取           |
| period     | str | period='5'; choice of {'1', '5', '15', '30', '60'}; 其中 1 分钟数据返回近 5 个交易日数据且不复权                       |
| adjust     | str | adjust=''; choice of {'', 'qfq', 'hfq'}; '': 不复权, 'qfq': 前复权, 'hfq': 后复权, 其中 1 分钟数据返回近 5 个交易日数据且不复权 |
| start_date | str | start_date="1979-09-01 09:32:00"; 日期时间; 默认返回所有数据                                                    |
| end_date   | str | end_date="2222-01-01 09:32:00"; 日期时间; 默认返回所有数据   
接口示例：
```python
import akshare as ak

stock_hk_hist_min_em_df = ak.stock_hk_hist_min_em(symbol="01611", period='1', adjust='',
                                                  start_date="2021-09-01 09:32:00",
                                                  end_date="2021-09-07 18:32:00")  # 其中的 start_date 和 end_date 需要设定为近期
print(stock_hk_hist_min_em_df)
```

8、接口: stock_us_hist
接口中文名：东方财富网-美股-每日行情

描述: 东方财富网-行情-美股-每日行情
限量: 单次返回指定上市公司的指定 adjust 后的所有历史行情数据；注意其中复权参数是否生效！
输入参数：
| 名称         | 类型  | 描述                                                                          |
|------------|-----|-----------------------------------------------------------------------------|
| symbol     | str | 美股代码, 可以通过 **ak.stock_us_spot_em()** 函数返回所有的 pandas.DataFrame 里面的 `代码` 字段获取 |
| period     | str | period='daily'; choice of {'daily', 'weekly', 'monthly'}                    |
| start_date | str | start_date="20210101"                                                       |
| end_date   | str | end_date="20210601"                                                         |
| adjust     | str | 默认 adjust="", 则返回未复权的数据; adjust="qfq" 则返回前复权的数据, adjust="hfq" 则返回后复权的数据     |
接口示例：
```python
import akshare as ak

stock_us_hist_df = ak.stock_us_hist(symbol='106.TTE', period="daily", start_date="20200101", end_date="20240214", adjust="qfq")
print(stock_us_hist_df)
```

9、接口: stock_us_hist_min_em
接口中文名：东方财富网-美股-每日分时行情

描述: 东方财富网-行情首页-美股-每日分时行情
限量: 单次返回指定上市公司最近 5 个交易日分钟数据, 注意美股数据更新有延时
输入参数：
| 名称         | 类型  | 描述                                                                                           |
|------------|-----|----------------------------------------------------------------------------------------------|
| symbol     | str | symbol="105.ATER"; 美股代码可以通过 **ak.stock_us_spot_em()** 函数返回所有的 pandas.DataFrame 里面的 `代码` 字段获取 |
| start_date | str | start_date="1979-09-01 09:32:00"; 日期时间; 默认返回所有数据                                             |
| end_date   | str | end_date="2222-01-01 09:32:00"; 日期时间; 默认返回所有数据     
接口示例：
```python
import akshare as ak

stock_us_hist_min_em_df = ak.stock_us_hist_min_em(symbol="105.ATER")
print(stock_us_hist_min_em_df)
```

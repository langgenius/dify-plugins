工具英文名：Stock_spot_quotations
工具中文名：实时行情数据

identity:
  author: shaoxing_xie
  name: Stock_spot_quotations
  label:
    zh_Hans: 实时行情数据
    en_US: Stock spot quotations 
description:单次返回指定股票市场所有上市公司的实时行情数据，包括A股、港股、美股等。

parameters:
  - name: interface
    type: select
    required: true
    form: llm
    default: stock_zh_a_spot_em
    description: 接口名称
    llm_description: 通过AKShare封装的数据接口，获取指定股票市场所有上市公司的实时行情数据
    human_description:通过AKShare封装的数据接口，获取指定股票市场所有上市公司的实时行情数据
    label:
      en_US: Interface
      zh_Hans: 接口名称

1、接口: stock_sh_a_spot_em
接口中文名：东方财富网-沪A股-实时行情数据

目标地址: http://quote.eastmoney.com/center/gridlist.html#sh_a_board

描述: 东方财富网-沪 A 股-实时行情数据

限量: 单次返回所有沪 A 股上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
print(stock_sh_a_spot_em_df)
```

2、接口: stock_sz_a_spot_em
接口中文名：东方财富网-深A股-实时行情数据

目标地址: http://quote.eastmoney.com/center/gridlist.html#sz_a_board

描述: 东方财富网-深 A 股-实时行情数据

限量: 单次返回所有深 A 股上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_sz_a_spot_em_df = ak.stock_sz_a_spot_em()
print(stock_sz_a_spot_em_df)
```

3、接口: stock_bj_a_spot_em
接口中文名：东方财富网-京A股-实时行情数据

目标地址: http://quote.eastmoney.com/center/gridlist.html#bj_a_board

描述: 东方财富网-京 A 股-实时行情数据

限量: 单次返回所有京 A 股上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_bj_a_spot_em_df = ak.stock_bj_a_spot_em()
print(stock_bj_a_spot_em_df)
```

4、接口: stock_new_a_spot_em
接口中文名：东方财富网-新股-实时行情数据

目标地址: http://quote.eastmoney.com/center/gridlist.html#newshares

描述: 东方财富网-新股-实时行情数据

限量: 单次返回所有新股上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_new_a_spot_em_df = ak.stock_new_a_spot_em()
print(stock_new_a_spot_em_df)
```

5、接口: stock_cy_a_spot_em
接口中文名：东方财富网-创业板-实时行情

目标地址: https://quote.eastmoney.com/center/gridlist.html#gem_board

描述: 东方财富网-创业板-实时行情

限量: 单次返回所有创业板的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_cy_a_spot_em_df = ak.stock_cy_a_spot_em()
print(stock_cy_a_spot_em_df)
```

6、接口: stock_kc_a_spot_em
接口中文名：东方财富网-科创板-实时行情

目标地址: http://quote.eastmoney.com/center/gridlist.html#kcb_board

描述: 东方财富网-科创板-实时行情

限量: 单次返回所有科创板的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_kc_a_spot_em_df = ak.stock_kc_a_spot_em()
print(stock_kc_a_spot_em_df)
```

7、接口: stock_zh_ah_spot_em
接口中文名：东方财富网-沪深港通-AH股比价-实时行情

目标地址: https://quote.eastmoney.com/center/gridlist.html#ah_comparison

描述: 东方财富网-行情中心-沪深港通-AH股比价-实时行情, 延迟 15 分钟更新

限量: 单次返回所有 A+H 上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_zh_ah_spot_em_df = ak.stock_zh_ah_spot_em()
print(stock_zh_ah_spot_em_df)
```

8、接口: stock_zh_ab_comparison_em
接口中文名：东方财富网-沪深京个股-全部AB股比价

目标地址: https://quote.eastmoney.com/center/gridlist.html#ab_comparison

描述: 东方财富网-行情中心-沪深京个股-AB股比价-全部AB股比价

限量: 单次返回全部 AB 股比价的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_zh_ab_comparison_em_df = ak.stock_zh_ab_comparison_em()
print(stock_zh_ab_comparison_em_df)
```

9、接口: stock_zh_a_new
接口中文名：新浪财经-沪深股市-次新股-实时行情

目标地址: http://vip.stock.finance.sina.com.cn/mkt/#new_stock

描述: 新浪财经-行情中心-沪深股市-次新股

限量: 单次返回所有次新股行情数据, 由于次新股名单随着交易日变化而变化，只能获取最近交易日的数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_zh_a_new_df = ak.stock_zh_a_new()
print(stock_zh_a_new_df)

10、接口: stock_zh_a_new_em
接口中文名：东方财富网-沪深个股-新股-实时行情

目标地址: https://quote.eastmoney.com/center/gridlist.html#newshares

描述: 东方财富网-行情中心-沪深个股-新股

限量: 单次返回当前交易日新股板块的所有股票的行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_zh_a_new_em_df = ak.stock_zh_a_new_em()
print(stock_zh_a_new_em_df)
```

11、接口: stock_xgsr_ths
接口中文名：同花顺-新股数据-新股上市首日

目标地址: https://data.10jqka.com.cn/ipo/xgsr/

描述: 同花顺-数据中心-新股数据-新股上市首日

限量: 单次返回当前交易日的所有数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_xgsr_ths_df = ak.stock_xgsr_ths()
print(stock_xgsr_ths_df)
```

### 两网及退市

12、接口: stock_zh_a_stop_em
接口中文名：东方财富网-沪深个股-两网及退市
目标地址: http://quote.eastmoney.com/center/gridlist.html#staq_net_board

描述: 东方财富网-行情中心-沪深个股-两网及退市

限量: 单次返回当前交易日两网及退市的所有股票的行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |

输出参数

| 名称     | 类型      | 描述      |
|--------|---------|---------|
| 序号     | int64   | -       |
| 代码     | object  | -       |
| 名称     | object  | -       |
| 最新价    | float64 | -       |
| 涨跌幅    | float64 | 注意单位: % |
| 涨跌额    | float64 | -       |
| 成交量    | float64 | -       |
| 成交额    | float64 | -       |
| 振幅     | float64 | 注意单位: % |
| 最高     | float64 | -       |
| 最低     | float64 | -       |
| 今开     | float64 | -       |
| 昨收     | float64 | -       |
| 量比     | float64 | -       |
| 换手率    | float64 | 注意单位: % |
| 市盈率-动态 | float64 | -       |
| 市净率    | float64 | -       |

接口示例

```python
import akshare as ak

stock_zh_a_stop_em_df = ak.stock_zh_a_stop_em()
print(stock_zh_a_stop_em_df)
```

数据示例

```
      序号 代码    名称      最新价 涨跌幅 涨跌额  ... 今开 昨收 量比 换手率 市盈率-动态市净率
0      1  400010  鹫  峰 5  1.90  4.97  0.09  ... NaN  1.81 NaN  NaN  -87.16  20.41
1      2  400069     吉恩5  9.96  4.95  0.47  ... NaN  9.49 NaN  NaN   19.61   3.78
2      3  400073    上普A5  7.08  4.89  0.33  ... NaN  6.75 NaN  NaN   97.79  11.69
3      4  400008   水仙Ａ 5  4.96  4.86  0.23  ... NaN  4.73 NaN  NaN -539.13  992.0
4      5  400059     天珑5  3.50  4.79  0.16  ... NaN  3.34 NaN  NaN   50.29   3.72
..   ...     ...     ...   ...   ...   ...  ...  ..   ...  ..  ...     ...    ...
100  101  400027  生  态 5  1.05 -4.55 -0.05  ... NaN   1.1 NaN  NaN  -57.07    4.7
101  102  400036     天创5  1.64 -4.65 -0.08  ... NaN  1.72 NaN  NaN   103.8   1.57
102  103  400005   海国实 5  1.01 -4.72 -0.05  ... NaN  1.06 NaN  NaN  -91.82   15.3
103  104  400039  华  圣 5  0.95 -5.00 -0.05  ... NaN   1.0 NaN  NaN  -65.97   4.64
104  105  400028  金  马 5  0.95 -5.00 -0.05  ... NaN   1.0 NaN  NaN -226.19    9.3
```

13、接口: stock_hk_spot_em
接口中文名：东方财富-港股-实时行情(延15分钟）

目标地址: http://quote.eastmoney.com/center/gridlist.html#hk_stocks

描述: 所有港股的实时行情数据; 该数据有 15 分钟延时

限量: 单次返回最近交易日的所有港股的数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_hk_spot_em_df = ak.stock_hk_spot_em()
print(stock_hk_spot_em_df)
```

14、接口: stock_hk_main_board_spot_em
接口中文名：东方财富-港股主板-实时行情(延15分钟）

目标地址: https://quote.eastmoney.com/center/gridlist.html#hk_mainboard

描述: 港股主板的实时行情数据; 该数据有 15 分钟延时

限量: 单次返回港股主板的数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_hk_main_board_spot_em_df = ak.stock_hk_main_board_spot_em()
print(stock_hk_main_board_spot_em_df)
```

#### 知名港股

15、接口: stock_hk_famous_spot_em
接口中文名：东方财富网-知名港股实时行情数据
目标地址: https://quote.eastmoney.com/center/gridlist.html#hk_wellknown

描述: 东方财富网-行情中心-港股市场-知名港股实时行情数据

限量: 单次返回全部行情数据

输入参数

| 名称 | 类型 | 描述 |
|----|----|----|
| -  | -  | -  |

输出参数

| 名称  | 类型      | 描述       |
|-----|---------|----------|
| 序号  | int64   | -        |
| 代码  | object  | -        |
| 名称  | object  | -        |
| 最新价 | float64 | 注意单位: 港元 |
| 涨跌额 | float64 | 注意单位: 港元 |
| 涨跌幅 | float64 | 注意单位: %  |
| 今开  | float64 | 注意单位: 港元 |
| 最高  | float64 | 注意单位: 港元 |
| 最低  | float64 | 注意单位: 港元 |
| 昨收  | float64 | 注意单位: 港元 |
| 成交量 | float64 | 注意单位: 股  |
| 成交额 | float64 | 注意单位: 港元 |

接口示例

```python
import akshare as ak

stock_hk_famous_spot_em_df = ak.stock_hk_famous_spot_em()
print(stock_hk_famous_spot_em_df)
```

数据示例

```
      序号 代码       名称    最新价  ...    最低     昨收    成交量           成交额
0      1  01918      融创中国   2.04  ...   1.91   1.91  633638656.0  1.295074e+09
1      2  00763      中兴通讯  34.65  ...  31.50  32.85   90643056.0  3.088137e+09
2      3  00753      中国国航   4.56  ...   4.25   4.33   34639744.0  1.560062e+08
3      4  01928  金沙中国有限公司  18.08  ...  17.20  17.18   37260253.0  6.721171e+08
4      5  03900      绿城中国  10.38  ...   9.89   9.91   33031905.0  3.421672e+08
..   ...    ...       ...    ...  ...    ...    ...          ...           ...
113  114  02400      心动公司  32.15  ...  31.60  34.20    4769000.0  1.544492e+08
114  115  01833     平安好医生   8.68  ...   8.55   9.31   53910271.0  4.845739e+08
115  116  02269      药明生物  23.65  ...  23.10  26.00  170040773.0  4.052070e+09
116  117  02359      药明康德  62.90  ...  62.40  70.00   20403989.0  1.314193e+09
117  118  09698   万国数据-SW  42.70  ...  41.30  48.30   24768786.0  1.068253e+09
[118 rows x 12 columns]
```
16、接口 stock_us_spot_em
接口中文名：东方财富网-美股-实时行情

目标地址: https://quote.eastmoney.com/center/gridlist.html#us_stocks

描述: 东方财富网-美股-实时行情

限量: 单次返回美股所有上市公司的实时行情数据

输入参数

| 名称  | 类型  | 描述  |
|-----|-----|-----|
| -   | -   | -   |
接口示例：
```python
import akshare as ak

stock_us_spot_em_df = ak.stock_us_spot_em()
print(stock_us_spot_em_df)
```

#### 知名美股

17、接口: stock_us_famous_spot_em
接口中文名：东方财富网-知名美股的实时行情数据
目标地址: http://quote.eastmoney.com/center/gridlist.html#us_wellknown

描述: 美股-知名美股的实时行情数据

限量: 单次返回指定 symbol 的行情数据

输入参数

| 名称     | 类型  | 描述                                                                       |
|--------|-----|--------------------------------------------------------------------------|
| symbol | str | symbol="科技类"; choice of {'科技类', '金融类', '医药食品类', '媒体类', '汽车能源类', '制造零售类'} |

输出参数

| 名称  | 类型      | 描述              |
|-----|---------|-----------------|
| 序号  | int64   | -               |
| 名称  | object  | -               |
| 最新价 | float64 | 注意单位: 美元        |
| 涨跌额 | float64 | 注意单位: 美元        |
| 涨跌幅 | float64 | 注意单位: %         |
| 开盘价 | float64 | 注意单位: 美元        |
| 最高价 | float64 | 注意单位: 美元        |
| 最低价 | float64 | 注意单位: 美元        |
| 昨收价 | float64 | 注意单位: 美元        |
| 总市值 | float64 | 注意单位: 美元        |
| 市盈率 | float64 | -               |
| 代码  | object  | 注意: 用来获取历史数据的代码 |

接口示例

```python
import akshare as ak

stock_us_famous_spot_em_df = ak.stock_us_famous_spot_em(symbol='科技类')
print(stock_us_famous_spot_em_df)
```

数据示例

```
    序号              名称           最新价  ...         总市值     市盈率        代码
0    1  Silvergate Capital Corp-A   116.34  ...     3085409047   61.93    106.SI
1    2  Opendoor Technologies Inc    18.94  ...    11451903533  -19.65  105.OPEN
2    3                     阿勒格尼技术    17.55  ...     2233160842   -1.82   106.ATI
3    4                Yandex NV-A    78.71  ...    28129406798  131.13  105.YNDX
4    5                        爱立信    11.83  ...    39443015025   16.44  105.ERIC
5    6                        诺基亚     5.91  ...    33269348763  -14.11   106.NOK
6    7              Groupon Inc-A    22.16  ...      654264338   73.65  105.GRPN
7    8                         推特    62.46  ...    49840992399  129.65  106.TWTR
8    9             Facebook Inc-A   378.00  ...  1065750021378   27.36    105.FB
9   10                         惠普    28.21  ...    32512553599    7.98   106.HPQ
10  11                       谷歌-C  2898.27  ...  1932435735616   16.84  105.GOOG
11  12                      阿卡迈技术   113.38  ...    18461647373   31.60  105.AKAM
12  13                      超威半导体   106.15  ...   128756264684   37.47   105.AMD
13  14                         思科    58.60  ...   247159324736   23.34  105.CSCO
14  15                       中华电信    40.05  ...    31068573413   24.84   106.CHT
15  16                       德州仪器   188.47  ...   173997383234   25.87   105.TXN
16  17                        奥多比   661.68  ...   315224352000   56.47  105.ADBE
17  18                        高知特    76.48  ...    40197673856   23.91  105.CTSH
18  19                        英特尔    53.40  ...   216643800000   11.68  105.INTC
19  20                     美国电话电报    27.42  ...   195778800000 -100.55     106.T
20  21                         高通   141.58  ...   159702240000   17.35  105.QCOM
21  22                         苹果   154.07  ...  2546802675620   29.34  105.AAPL
22  23              IBM国际商业机器(US)   137.74  ...   123459126717   23.15   106.IBM
23  24                         陶氏    60.28  ...    44955123381   10.96   106.DOW
24  25                        思爱普   145.68  ...   171841118251   23.58   106.SAP
25  26                        英伟达   221.77  ...   554425000000   78.33  105.NVDA
26  27                      威瑞森通讯    54.44  ...   225387915421   11.28    106.VZ
27  28                         微软   297.25  ...  2233801423468   36.46  105.MSFT
28  29                   摩托罗拉解决方案   244.00  ...    41315202400   35.80   106.MSI
29  30                        亚马逊  3484.16  ...  1764519802163   59.94  105.AMZN
30  31                         易趣    73.00  ...    47454073765    3.68  105.EBAY
31  32                    沃达丰(US)    16.61  ...    46152628937  351.55   105.VOD
32  33                Zynga Inc-A     8.28  ...     9040854574  -53.06  105.ZNGA
33  34          SentinelOne Inc-A    66.04  ...    16930759265  -85.17     106.S
```

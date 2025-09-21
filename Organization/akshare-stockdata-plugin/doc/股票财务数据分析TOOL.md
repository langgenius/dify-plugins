#### 利润表

接口: stock_lrb_em
接口中文名：东方财富-业绩快报-利润表
目标地址: http://data.eastmoney.com/bbsj/202003/lrb.html

描述: 东方财富-数据中心-年报季报-业绩快报-利润表

限量: 单次获取指定 date 的利润表数据

输入参数

| 名称   | 类型  | 描述                                                                                         |
|------|-----|--------------------------------------------------------------------------------------------|
| date | str | date="20240331"; choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; 从 20120331 开始 |

输出参数

| 名称          | 类型      | 描述      |
|-------------|---------|---------|
| 序号          | int64   | -       |
| 股票代码        | object  | -       |
| 股票简称        | object  | -       |
| 净利润         | float64 | 注意单位: 元 |
| 净利润同比       | float64 | 注意单位: % |
| 营业总收入       | float64 | 注意单位: 元 |
| 营业总收入同比     | float64 | 注意单位: % |
| 营业总支出-营业支出  | float64 | 注意单位: 元 |
| 营业总支出-销售费用  | float64 | 注意单位: 元 |
| 营业总支出-管理费用  | float64 | 注意单位: 元 |
| 营业总支出-财务费用  | float64 | 注意单位: 元 |
| 营业总支出-营业总支出 | float64 | 注意单位: 元 |
| 营业利润        | float64 | 注意单位: 元 |
| 利润总额        | float64 | 注意单位: 元 |
| 公告日期        | object  | -       |

接口示例

```python
import akshare as ak

stock_lrb_em_df = ak.stock_lrb_em(date="20240331")
print(stock_lrb_em_df)
```

数据示例

```
     序号    股票代码   股票简称  ...   营业利润         利润总额       公告日期
0        1  603156   养元饮品  ...  1.078460e+09  1.078821e+09  2024-09-10
1        2  002569   ST步森  ... -8.504272e+06 -8.601409e+06  2024-09-07
2        3  603260   合盛硅业  ...  7.390596e+08  7.561255e+08  2024-08-30
3        4  300417   南华仪器  ... -4.807409e+06 -4.815009e+06  2024-08-30
4        5  300081   恒信东方  ... -3.694795e+07 -3.697999e+07  2024-08-30
...    ...     ...    ...  ...           ...           ...         ...
5123  5124  300076  GQY视讯  ... -2.973570e+05 -2.575340e+05  2024-04-10
5124  5125  002644   佛慈制药  ...  2.299932e+07  2.260271e+07  2024-04-10
5125  5126  603058   永吉股份  ...  5.088006e+07  5.084289e+07  2024-04-09
5126  5127  600873   梅花生物  ...  8.858530e+08  8.755312e+08  2024-04-09
5127  5128  000818   航锦科技  ...  8.761395e+07  8.890215e+07  2024-04-03
[5128 rows x 15 columns]
```

#### 现金流量表

接口: stock_xjll_em
接口中文名：东方财富-业绩快报-现金流量表
目标地址: http://data.eastmoney.com/bbsj/202003/xjll.html

描述: 东方财富-数据中心-年报季报-业绩快报-现金流量表

限量: 单次获取指定 date 的现金流量表数据

输入参数

| 名称   | 类型  | 描述                                                                                         |
|------|-----|--------------------------------------------------------------------------------------------|
| date | str | date="20200331"; choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; 从 20081231 开始 |

输出参数

| 名称            | 类型      | 描述      |
|---------------|---------|---------|
| 序号            | int64   | -       |
| 股票代码          | object  | -       |
| 股票简称          | object  | -       |
| 净现金流-净现金流     | float64 | 注意单位: 元 |
| 净现金流-同比增长     | float64 | 注意单位: % |
| 经营性现金流-现金流量净额 | float64 | 注意单位: 元 |
| 经营性现金流-净现金流占比 | float64 | 注意单位: % |
| 投资性现金流-现金流量净额 | float64 | 注意单位: 元 |
| 投资性现金流-净现金流占比 | float64 | 注意单位: % |
| 融资性现金流-现金流量净额 | float64 | 注意单位: 元 |
| 融资性现金流-净现金流占比 | float64 | 注意单位: % |
| 公告日期          | object  | -       |

接口示例

```python
import akshare as ak

stock_xjll_em_df = ak.stock_xjll_em(date="20240331")
print(stock_xjll_em_df)
```

数据示例

```
      序号   股票代码   股票简称  ... 融资性现金流-现金流量净额 融资性现金流-净现金流占比  公告日期
0        1  603156   养元饮品  ...   8.906149e+07       8.556244  2024-09-10
1        2  002569   ST步森  ...            NaN            NaN  2024-09-07
2        3  603260   合盛硅业  ...   3.236085e+09    7017.983443  2024-08-30
3        4  300417   南华仪器  ...  -1.980000e+04      -0.047350  2024-08-30
4        5  300081   恒信东方  ...  -6.422119e+06     -30.968169  2024-08-30
...    ...     ...    ...  ...            ...            ...         ...
5123  5124  300076  GQY视讯  ...   3.252000e+05       1.435320  2024-04-10
5124  5125  002644   佛慈制药  ...  -1.388667e+07     -43.325298  2024-04-10
5125  5126  603058   永吉股份  ...   3.204449e+06       5.454042  2024-04-09
5126  5127  600873   梅花生物  ...   1.604316e+08      47.970510  2024-04-09
5127  5128  000818   航锦科技  ...   5.813673e+08     274.656484  2024-04-03
[5128 rows x 12 columns]
```

#### 资产负债表-沪深

接口: stock_zcfz_em
接口中文名：东方财富-业绩快报-资产负债表
目标地址: https://data.eastmoney.com/bbsj/202003/zcfz.html

描述: 东方财富-数据中心-年报季报-业绩快报-资产负债表

限量: 单次获取指定 date 的资产负债表数据

输入参数

| 名称   | 类型  |  描述                                                                                        |
|------|-----|--------------------------------------------------------------------------------------------|
| date | str | date="20240331"; choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; 从 20081231 开始 |

输出参数

| 名称       | 类型      | 描述      |
|----------|---------|---------|
| 序号       | int64   | -       |
| 股票代码     | object  | -       |
| 股票简称     | object  | -       |
| 资产-货币资金  | float64 | 注意单位: 元 |
| 资产-应收账款  | float64 | 注意单位: 元 |
| 资产-存货    | float64 | 注意单位: 元 |
| 资产-总资产   | float64 | 注意单位: 元 |
| 资产-总资产同比 | float64 | 注意单位: % |
| 负债-应付账款  | float64 | 注意单位: 元 |
| 负债-总负债   | float64 | 注意单位: 元 |
| 负债-预收账款  | float64 | 注意单位: 元 |
| 负债-总负债同比 | float64 | 注意单位: % |
| 资产负债率    | float64 | 注意单位: % |
| 股东权益合计   | float64 | 注意单位: 元 |
| 公告日期     | object  | -       |

接口示例

```python
import akshare as ak

stock_zcfz_em_df = ak.stock_zcfz_em(date="20240331")
print(stock_zcfz_em_df)
```

数据示例

```
     序号    股票代码   股票简称  ...   资产负债率  股东权益合计       公告日期
0        1  603156   养元饮品  ...  20.992996  1.160939e+10  2024-09-10
1        2  002569   ST步森  ...  62.799334  8.476112e+07  2024-09-07
2        3  603260   合盛硅业  ...  63.774717  3.253375e+10  2024-08-30
3        4  300417   南华仪器  ...   8.130360  4.507915e+08  2024-08-30
4        5  300081   恒信东方  ...  30.634305  1.319848e+09  2024-08-30
...    ...     ...    ...  ...        ...           ...         ...
5123  5124  300076  GQY视讯  ...  10.010959  9.880683e+08  2024-04-10
5124  5125  002644   佛慈制药  ...  29.294961  1.787072e+09  2024-04-10
5125  5126  603058   永吉股份  ...  35.639627  1.237896e+09  2024-04-09
5126  5127  600873   梅花生物  ...  36.564962  1.486533e+10  2024-04-09
5127  5128  000818   航锦科技  ...  40.879097  4.118588e+09  2024-04-03
[5128 rows x 15 columns]
```

#### 资产负债表-北交所

接口: stock_zcfz_bj_em
接口中文名：东方财富-北交所-业绩快报-资产负债表
目标地址: https://data.eastmoney.com/bbsj/202003/zcfz.html

描述: 东方财富-数据中心-年报季报-业绩快报-资产负债表

限量: 单次获取指定 date 的资产负债表数据

输入参数

| 名称   | 类型  | 描述                                                                                         |
|------|-----|--------------------------------------------------------------------------------------------|
| date | str | date="20240331"; choice of {"XXXX0331", "XXXX0630", "XXXX0930", "XXXX1231"}; 从 20081231 开始 |

输出参数

| 名称       | 类型      | 描述      |
|----------|---------|---------|
| 序号       | int64   | -       |
| 股票代码     | object  | -       |
| 股票简称     | object  | -       |
| 资产-货币资金  | float64 | 注意单位: 元 |
| 资产-应收账款  | float64 | 注意单位: 元 |
| 资产-存货    | float64 | 注意单位: 元 |
| 资产-总资产   | float64 | 注意单位: 元 |
| 资产-总资产同比 | float64 | 注意单位: % |
| 负债-应付账款  | float64 | 注意单位: 元 |
| 负债-总负债   | float64 | 注意单位: 元 |
| 负债-预收账款  | float64 | 注意单位: 元 |
| 负债-总负债同比 | float64 | 注意单位: % |
| 资产负债率    | float64 | 注意单位: % |
| 股东权益合计   | float64 | 注意单位: 元 |
| 公告日期     | object  | -       |

接口示例

```python
import akshare as ak

stock_zcfz_bj_em_df = ak.stock_zcfz_bj_em(date="20240331")
print(stock_zcfz_bj_em_df)
```

数据示例

```
     序号 股票代码  股票简称  ...  资产负债率    股东权益合计     公告日期
0      1  873223  荣亿精密  ...  38.708142  2.856643e+08  2024-08-29
1      2  838030  德众汽车  ...  72.413909  4.696866e+08  2024-08-28
2      3  830974  凯大催化  ...  26.834128  6.476251e+08  2024-08-28
3      4  834415  恒拓开源  ...  16.546915  5.229393e+08  2024-06-27
4      5  920118  太湖远大  ...  57.054651  4.325410e+08  2024-05-23
..   ...     ...   ...  ...        ...           ...         ...
249  250  835892  中科美菱  ...  19.425219  6.066262e+08  2024-04-18
250  251  834261   一诺威  ...  38.597474  1.475388e+09  2024-04-18
251  252  873703  广厦环能  ...  25.348767  1.018675e+09  2024-04-16
252  253  838262   太湖雪  ...  36.163348  3.227086e+08  2024-04-15
253  254  833394   民士达  ...  19.625162  6.865148e+08  2024-04-11
[254 rows x 15 columns]
```

##### 资产负债表

接口: stock_financial_debt_ths
接口中文名：同花顺-财务指标-资产负债表
目标地址: https://basic.10jqka.com.cn/new/000063/finance.html

描述: 同花顺-财务指标-资产负债表

限量: 单次获取资产负债表所有历史数据

输入参数

| 名称        | 类型  | 描述                                                  |
|-----------|-----|-----------------------------------------------------|
| symbol    | str | symbol="000063"; 股票代码                               |
| indicator | str | indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"} |

输出参数

| 名称 | 类型 | 描述         |
|----|----|------------|
| -  | -  | 80 项，不逐一列出 |

接口示例

```python
import akshare as ak

stock_financial_debt_ths_df = ak.stock_financial_debt_ths(symbol="600519", indicator="按年度")
print(stock_financial_debt_ths_df)
```

数据示例

```
     报告期 报表核心指标 *所有者权益（或股东权益）合计  ...    少数股东权益 所有者权益（或股东权益）合计 负债和所有者权益（或股东权益）合计
0   2022                595.43亿  ...     9.02亿        595.43亿          1809.54亿
1   2021                532.88亿  ...    18.06亿        532.88亿          1687.63亿
2   2020                461.23亿  ...    28.26亿        461.23亿          1506.35亿
3   2019                379.54亿  ...    28.75亿        379.54亿          1412.02亿
4   2018                329.61亿  ...    38.11亿        329.61亿          1293.51亿
5   2017                453.80亿  ...    44.12亿        453.80亿          1439.62亿
6   2016                408.85亿  ...    51.63亿        408.85亿          1416.41亿
7   2015                433.49亿  ...    43.67亿        433.49亿          1248.32亿
8   2014                262.93亿  ...    14.14亿        262.93亿          1062.14亿
9   2013                236.26亿  ...    10.93亿        236.26亿          1000.79亿
10  2012                225.93亿  ...    11.36亿        225.93亿          1074.46亿
11  2011                262.89亿  ...    20.57亿        262.89亿          1053.68亿
12  2010                249.62亿  ...    18.68亿        249.62亿           841.52亿
13  2009                179.49亿  ...    11.24亿        179.49亿           683.42亿
14  2008                151.84亿  ...     9.34亿        151.84亿           508.66亿
15  2007                128.88亿  ...     7.51亿        128.88亿           391.73亿
16  2006                113.26亿  ...     5.62亿        113.26亿           257.61亿
17  2005                105.96亿  ...     4.71亿        105.96亿           217.79亿
18  2004                 96.39亿  ...     4.65亿         96.39亿           208.30亿
19  2003                 52.77亿  ...     2.33亿         52.77亿           157.67亿
20  2002                 46.04亿  ...     2.17亿         46.04亿           122.17亿
21  2001                 39.18亿  ...  9910.63万         39.18亿            90.55亿
22  2000                 19.50亿  ...  6403.16万         19.50亿            63.21亿
23  1999                 15.79亿  ...  4952.78万         15.79亿            33.85亿
24  1998                  9.60亿  ...  2223.74万          9.60亿            21.94亿
25  1997                  7.01亿  ...   589.60万          7.01亿            13.57亿
26  1996                  1.30亿  ...    10.00万          1.30亿             3.83亿
27  1995               7839.06万  ...     False       7839.06万             2.36亿
28  1994               4254.78万  ...     False       4254.78万             1.45亿
[29 rows x 80 columns]
```

##### 利润表

接口: stock_financial_benefit_ths
接口中文名：同花顺-财务指标-利润表
目标地址: https://basic.10jqka.com.cn/new/000063/finance.html

描述: 同花顺-财务指标-利润表

限量: 单次获取利润表所有历史数据

输入参数

| 名称        | 类型  | 描述                                                  |
|-----------|-----|-----------------------------------------------------|
| symbol    | str | symbol="000063"; 股票代码                               |
| indicator | str | indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"} |

输出参数

| 名称 | 类型 | 描述         |
|----|----|------------|
| -  | -  | 45 项，不逐一列出 |

接口示例

```python
import akshare as ak

stock_financial_benefit_ths_df = ak.stock_financial_benefit_ths(symbol="000063", indicator="按报告期")
print(stock_financial_benefit_ths_df)
```

数据示例

```
           报告期 报表核心指标      *净利润  ... 八、综合收益总额 归属于母公司股东的综合收益总额 归属于少数股东的综合收益总额
0   2023-09-30           77.57亿  ...   77.05亿          77.94亿      -8842.60万
1   2023-06-30           53.92亿  ...   53.41亿          54.24亿      -8317.50万
2   2023-03-31           26.14亿  ...   24.85亿          25.17亿      -3237.00万
3   2022-12-31           77.92亿  ...   77.24亿          80.15亿         -2.90亿
4   2022-09-30           66.90亿  ...   66.52亿          67.88亿         -1.36亿
..         ...    ...       ...  ...      ...             ...            ...
95  1997-12-31            1.21亿  ...    False           False          False
96  1997-06-30         4124.14万  ...    False           False          False
97  1996-12-31         9905.67万  ...    False           False          False
98  1995-12-31         7314.86万  ...    False           False          False
99  1994-12-31         8071.26万  ...    False           False          False
[100 rows x 45 columns]
```

##### 现金流量表

接口: stock_financial_cash_ths
接口中文名：同花顺-财务指标-现金流量表
目标地址: https://basic.10jqka.com.cn/new/000063/finance.html

描述: 同花顺-财务指标-现金流量表

限量: 单次获取现金流量表所有历史数据

输入参数

| 名称        | 类型  | 描述                                                  |
|-----------|-----|-----------------------------------------------------|
| symbol    | str | symbol="000063"; 股票代码                               |
| indicator | str | indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"} |

输出参数

| 名称 | 类型 | 描述         |
|----|----|------------|
| -  | -  | 75 项，不逐一列出 |

接口示例

```python
import akshare as ak

stock_financial_cash_ths_df = ak.stock_financial_cash_ths(symbol="000063", indicator="按单季度")
print(stock_financial_cash_ths_df)
```

数据示例

```
    报告期 报表核心指标 *现金及现金等价物净增加额  ... 加：现金等价物的期末余额 减：现金等价物的期初余额 间接法-现金及现金等价物净增加额
0   2023-09-30               15.54亿  ...
1   2023-06-30               52.02亿  ...
2   2023-03-31               26.73亿  ...        False        False            False
3   2022-12-31              107.72亿  ...
4   2022-09-30              -77.82亿  ...
..         ...    ...           ...  ...          ...          ...              ...
78  2004-03-31              -16.81亿  ...        False        False          -16.81亿
79  2003-12-31               19.40亿  ...                                     19.40亿
80  2003-09-30              -10.76亿  ...                                    -10.76亿
81  2003-06-30               13.89亿  ...                                     13.89亿
82  2003-03-31              -14.06亿  ...        False        False          -14.06亿
[83 rows x 75 columns]
```

#### 关键指标-新浪

接口: stock_financial_abstract
接口中文名：新浪财经-财务报表-关键指标
目标地址: https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/600004.phtml

描述: 新浪财经-财务报表-关键指标

限量: 单次获取关键指标所有历史数据

输入参数

| 名称     | 类型  | 描述                    |
|--------|-----|-----------------------|
| symbol | str | symbol="600004"; 股票代码 |

输出参数

| 名称       | 类型     | 描述  |
|----------|--------|-----|
| 选项       | object | -   |
| 指标       | object | -   |
| 【具体的报告期】 | object | -   |

接口示例

```python
import akshare as ak

stock_financial_abstract_df = ak.stock_financial_abstract(symbol="600004")
print(stock_financial_abstract_df)
```

数据示例

```
      选项        指标      20220930  ...      20020630      20011231      20001231
0   常用指标     归母净利润 -6.271849e+08  ...  1.365679e+08  2.967902e+08  1.967577e+08
1   常用指标     营业总收入  3.307660e+09  ...  4.381153e+08  8.515877e+08  7.833500e+08
2   常用指标      营业成本  4.212766e+09  ...  2.664150e+08  5.317826e+08  4.654766e+08
3   常用指标       净利润 -6.321978e+08  ...  1.406112e+08  3.009773e+08  2.019293e+08
4   常用指标     扣非净利润 -6.532030e+08  ...  1.364059e+08  1.985243e+08  1.967577e+08
..   ...       ...           ...  ...           ...           ...           ...
74  营运能力    总资产周转率  1.202050e-01  ...           NaN  6.501820e-01           NaN
75  营运能力   总资产周转天数  2.246150e+03  ...           NaN  5.536909e+02           NaN
76  营运能力   流动资产周转率  8.849150e-01  ...           NaN  9.480880e-01           NaN
77  营运能力  流动资产周转天数  3.051139e+02  ...           NaN  3.797112e+02           NaN
78  营运能力   应付账款周转率  5.311671e+00  ...           NaN  2.140125e+01           NaN
```

#### 关键指标-同花顺

接口: stock_financial_abstract_ths
接口中文名：同花顺-财务指标-主要指标
目标地址: https://basic.10jqka.com.cn/new/000063/finance.html

描述: 同花顺-财务指标-主要指标

限量: 单次获取指定 symbol 的所有数据

输入参数

| 名称        | 类型  | 描述                                                  |
|-----------|-----|-----------------------------------------------------|
| symbol    | str | symbol="000063"; 股票代码                               |
| indicator | str | indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"} |

输出参数

| 名称         | 类型     | 描述 |
|------------|--------|----|
| 报告期        | object | -  |
| 净利润        | object | -  |
| 净利润同比增长率   | object | -  |
| 扣非净利润      | object | -  |
| 扣非净利润同比增长率 | object | -  |
| 营业总收入      | object | -  |
| 营业总收入同比增长率 | object | -  |
| 基本每股收益     | object | -  |
| 每股净资产      | object | -  |
| 每股资本公积金    | object | -  |
| 每股未分配利润    | object | -  |
| 每股经营现金流    | object | -  |
| 销售净利率      | object | -  |
| 销售毛利率      | object | -  |
| 净资产收益率     | object | -  |
| 净资产收益率-摊薄  | object | -  |
| 营业周期       | object | -  |
| 存货周转率      | object | -  |
| 存货周转天数     | object | -  |
| 应收账款周转天数   | object | -  |
| 流动比率       | object | -  |
| 速动比率       | object | -  |
| 保守速动比率     | object | -  |
| 产权比率       | object | -  |
| 资产负债率      | object | -  |

接口示例

```python
import akshare as ak

stock_financial_abstract_ths_df = ak.stock_financial_abstract_ths(symbol="000063", indicator="按报告期")
print(stock_financial_abstract_ths_df)
```

数据示例

```
     报告期     净利润 净利润同比增长率  扣非净利润  ... 速动比率 保守速动比率 产权比率 资产负债率
0    1994-12-31  8071.26万    False   False  ...   0.74   0.68   2.42  70.75%
1    1995-12-31  7314.86万   -9.37%   False  ...   0.67   0.61   2.02  66.84%
2    1996-12-31  9905.67万   35.42%   False  ...   0.72   0.66   1.95  66.06%
3    1997-06-30  4101.36万    False   False  ...  False  False  False   False
4    1997-12-31     1.17亿   18.17%   False  ...   1.31   1.21   0.94  48.33%
..          ...       ...      ...     ...  ...    ...    ...    ...     ...
100  2023-12-31    93.26亿   15.41%  74.00亿  ...   1.32   1.21   1.95  66.00%
101  2024-03-31    27.41亿    3.74%  26.49亿  ...   1.37   1.27   1.94  65.82%
102  2024-06-30    57.32亿    4.76%  49.64亿  ...   1.28   1.21   1.91  65.57%
103  2024-09-30    79.06亿    0.83%  68.98亿  ...   1.22   1.13   1.76  63.63%
104  2024-12-31    84.25亿   -9.66%  61.79亿  ...   1.10   0.99   1.84  64.74%
[105 rows x 25 columns]
```

#### 财务指标

接口: stock_financial_analysis_indicator
接口中文名：新浪财经-财务分析-财务指标
目标地址: https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/600004/ctrl/2019/displaytype/4.phtml

描述: 新浪财经-财务分析-财务指标

限量: 单次获取指定 symbol 和 start_year 的所有财务指标历史数据

输入参数

| 名称         | 类型  | 描述                         |
|------------|-----|----------------------------|
| symbol     | str | symbol="600004"; 股票代码      |
| start_year | str | start_year="2020"; 开始查询的时间 |

输出参数

| 名称                | 类型      | 描述 |
|-------------------|---------|----|
| 日期                | object  | -  |
| 摊薄每股收益(元)         | float64 | -  |
| 加权每股收益(元)         | float64 | -  |
| 每股收益_调整后(元)       | float64 | -  |
| 扣除非经常性损益后的每股收益(元) | float64 | -  |
| 每股净资产_调整前(元)      | float64 | -  |
| 每股净资产_调整后(元)      | float64 | -  |
| 每股经营性现金流(元)       | float64 | -  |
| 每股资本公积金(元)        | float64 | -  |
| 每股未分配利润(元)        | float64 | -  |
| 调整后的每股净资产(元)      | float64 | -  |
| 总资产利润率(%)         | float64 | -  |
| 主营业务利润率(%)        | float64 | -  |
| 总资产净利润率(%)        | float64 | -  |
| 成本费用利润率(%)        | float64 | -  |
| 营业利润率(%)          | float64 | -  |
| 主营业务成本率(%)        | float64 | -  |
| 销售净利率(%)          | float64 | -  |
| 股本报酬率(%)          | float64 | -  |
| 净资产报酬率(%)         | float64 | -  |
| 资产报酬率(%)          | float64 | -  |
| 销售毛利率(%)          | float64 | -  |
| 三项费用比重            | float64 | -  |
| 非主营比重             | float64 | -  |
| 主营利润比重            | float64 | -  |
| 股息发放率(%)          | float64 | -  |
| 投资收益率(%)          | float64 | -  |
| 主营业务利润(元)         | float64 | -  |
| 净资产收益率(%)         | float64 | -  |
| 加权净资产收益率(%)       | float64 | -  |
| 扣除非经常性损益后的净利润(元)  | float64 | -  |
| 主营业务收入增长率(%)      | float64 | -  |
| 净利润增长率(%)         | float64 | -  |
| 净资产增长率(%)         | float64 | -  |
| 总资产增长率(%)         | float64 | -  |
| 应收账款周转率(次)        | float64 | -  |
| 应收账款周转天数(天)       | float64 | -  |
| 存货周转天数(天)         | float64 | -  |
| 存货周转率(次)          | float64 | -  |
| 固定资产周转率(次)        | float64 | -  |
| 总资产周转率(次)         | float64 | -  |
| 总资产周转天数(天)        | float64 | -  |
| 流动资产周转率(次)        | float64 | -  |
| 流动资产周转天数(天)       | float64 | -  |
| 股东权益周转率(次)        | float64 | -  |
| 流动比率              | float64 | -  |
| 速动比率              | float64 | -  |
| 现金比率(%)           | float64 | -  |
| 利息支付倍数            | float64 | -  |
| 长期债务与营运资金比率(%)    | float64 | -  |
| 股东权益比率(%)         | float64 | -  |
| 长期负债比率(%)         | float64 | -  |
| 股东权益与固定资产比率(%)    | float64 | -  |
| 负债与所有者权益比率(%)     | float64 | -  |
| 长期资产与长期资金比率(%)    | float64 | -  |
| 资本化比率(%)          | float64 | -  |
| 固定资产净值率(%)        | float64 | -  |
| 资本固定化比率(%)        | float64 | -  |
| 产权比率(%)           | float64 | -  |
| 清算价值比率(%)         | float64 | -  |
| 固定资产比重(%)         | float64 | -  |
| 资产负债率(%)          | float64 | -  |
| 总资产(元)            | float64 | -  |
| 经营现金净流量对销售收入比率(%) | float64 | -  |
| 资产的经营现金流量回报率(%)   | float64 | -  |
| 经营现金净流量与净利润的比率(%) | float64 | -  |
| 经营现金净流量对负债比率(%)   | float64 | -  |
| 现金流量比率(%)         | float64 | -  |
| 短期股票投资(元)         | float64 | -  |
| 短期债券投资(元)         | float64 | -  |
| 短期其它经营性投资(元)      | float64 | -  |
| 长期股票投资(元)         | float64 | -  |
| 长期债券投资(元)         | float64 | -  |
| 长期其它经营性投资(元)      | float64 | -  |
| 1年以内应收帐款(元)       | float64 | -  |
| 1-2年以内应收帐款(元)     | float64 | -  |
| 2-3年以内应收帐款(元)     | float64 | -  |
| 3年以内应收帐款(元)       | float64 | -  |
| 1年以内预付货款(元)       | float64 | -  |
| 1-2年以内预付货款(元)     | float64 | -  |
| 2-3年以内预付货款(元)     | float64 | -  |
| 3年以内预付货款(元)       | float64 | -  |
| 1年以内其它应收款(元)      | float64 | -  |
| 1-2年以内其它应收款(元)    | float64 | -  |
| 2-3年以内其它应收款(元)    | float64 | -  |
| 3年以内其它应收款(元)      | float64 | -  |

接口示例

```python
import akshare as ak

stock_financial_analysis_indicator_df = ak.stock_financial_analysis_indicator(symbol="600004", start_year="2020")
print(stock_financial_analysis_indicator_df)
```

数据示例

```
         日期  摊薄每股收益(元)  ... 2-3年以内其它应收款(元) 3年以内其它应收款(元)
0   2020-03-31    -0.0307  ...             NaN           NaN
1   2020-06-30    -0.0816  ...      1189862.00           NaN
2   2020-09-30    -0.1380  ...             NaN           NaN
3   2020-12-31    -0.0980  ...      1495234.99           NaN
4   2021-03-31    -0.0645  ...             NaN           NaN
5   2021-06-30    -0.1686  ...      3471186.42           NaN
6   2021-09-30    -0.2038  ...             NaN           NaN
7   2021-12-31    -0.1628  ...      1380992.96           NaN
8   2022-03-31    -0.0326  ...             NaN           NaN
9   2022-06-30    -0.2242  ...      1680204.08           NaN
10  2022-09-30    -0.2671  ...             NaN           NaN
11  2022-12-31    -0.4613  ...      2459538.50           NaN
12  2023-03-31     0.0216  ...             NaN           NaN
13  2023-06-30     0.0720  ...      2591827.74           NaN
14  2023-09-30     0.1232  ...             NaN           NaN
15  2023-12-31     0.2032  ...      7162683.42           NaN
16  2024-03-31     0.0841  ...             NaN           NaN
[17 rows x 86 columns]
```

#### 港股财务指标

接口: stock_financial_hk_analysis_indicator_em
接口中文名：东方财富-港股-财务分析-主要指标
目标地址: https://emweb.securities.eastmoney.com/PC_HKF10/NewFinancialAnalysis/index?type=web&code=00700

描述: 东方财富-港股-财务分析-主要指标

限量: 单次获取财务指标所有历史数据

输入参数

| 名称        | 类型  | 描述                                      |
|-----------|-----|-----------------------------------------|
| symbol    | str | symbol="00700"; 股票代码                    |
| indicator | str | indicator="年度"; choice of {"年度", "报告期"} |

输出参数

| 名称                  | 类型      | 描述 |
|---------------------|---------|----|
| SECUCODE            | object  | -  |
| SECURITY_CODE       | object  | -  |
| SECURITY_NAME_ABBR  | object  | -  |
| ORG_CODE            | object  | -  |
| REPORT_DATE         | object  | -  |
| DATE_TYPE_CODE      | object  | -  |
| PER_NETCASH_OPERATE | float64 | -  |
| PER_OI              | float64 | -  |
| BPS                 | float64 | -  |
| BASIC_EPS           | float64 | -  |
| DILUTED_EPS         | float64 | -  |
| OPERATE_INCOME      | int64   | -  |
| OPERATE_INCOME_YOY  | float64 | -  |
| GROSS_PROFIT        | int64   | -  |
| GROSS_PROFIT_YOY    | float64 | -  |
| HOLDER_PROFIT       | int64   | -  |
| HOLDER_PROFIT_YOY   | float64 | -  |
| GROSS_PROFIT_RATIO  | float64 | -  |
| EPS_TTM             | float64 | -  |
| OPERATE_INCOME_QOQ  | float64 | -  |
| NET_PROFIT_RATIO    | float64 | -  |
| ROE_AVG             | float64 | -  |
| GROSS_PROFIT_QOQ    | float64 | -  |
| ROA                 | float64 | -  |
| HOLDER_PROFIT_QOQ   | float64 | -  |
| ROE_YEARLY          | float64 | -  |
| ROIC_YEARLY         | float64 | -  |
| TAX_EBT             | float64 | -  |
| OCF_SALES           | float64 | -  |
| DEBT_ASSET_RATIO    | float64 | -  |
| CURRENT_RATIO       | float64 | -  |
| CURRENTDEBT_DEBT    | float64 | -  |
| START_DATE          | object  | -  |
| FISCAL_YEAR         | object  | -  |
| CURRENCY            | object  | -  |
| IS_CNY_CODE         | int64   | -  |

接口示例

```python
import akshare as ak

stock_financial_hk_analysis_indicator_em_df = ak.stock_financial_hk_analysis_indicator_em(symbol="00700", indicator="年度")
print(stock_financial_hk_analysis_indicator_em_df)
```

数据示例

```
   SECUCODE SECURITY_CODE SECURITY_NAME_ABBR  ... FISCAL_YEAR CURRENCY IS_CNY_CODE
0  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
1  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
2  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
3  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
4  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
5  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
6  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
7  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
8  00700.HK         00700               腾讯控股  ...       12-31      HKD           0
[9 rows x 36 columns]
```

#### 美股财务指标

接口: stock_financial_us_analysis_indicator_em
接口中文名：东方财富-美股-财务分析-主要指标
目标地址: https://emweb.eastmoney.com/PC_USF10/pages/index.html?code=TSLA&type=web&color=w#/cwfx/zyzb

描述: 东方财富-美股-财务分析-主要指标

限量: 单次获取指定股票的所有历史数据

输入参数

| 名称        | 类型  | 描述                                              |
|-----------|-----|-------------------------------------------------|
| symbol    | str | symbol="TSLA"; 股票代码                             |
| indicator | str | indicator="年报"; choice of {"年报", "单季报", "累计季报"} |

输出参数

| 名称                          | 类型      | 描述 |
|-----------------------------|---------|----|
| SECUCODE                    | object  | -  |
| SECURITY_CODE               | object  | -  |
| SECURITY_NAME_ABBR          | object  | -  |
| ORG_CODE                    | object  | -  |
| SECURITY_INNER_CODE         | object  | -  |
| ACCOUNTING_STANDARDS        | object  | -  |
| NOTICE_DATE                 | object  | -  |
| START_DATE                  | object  | -  |
| REPORT_DATE                 | object  | -  |
| FINANCIAL_DATE              | object  | -  |
| STD_REPORT_DATE             | object  | -  |
| CURRENCY                    | object  | -  |
| DATE_TYPE                   | object  | -  |
| DATE_TYPE_CODE              | object  | -  |
| REPORT_TYPE                 | object  | -  |
| REPORT_DATA_TYPE            | object  | -  |
| ORGTYPE                     | object  | -  |
| OPERATE_INCOME              | float64 | -  |
| OPERATE_INCOME_YOY          | float64 | -  |
| GROSS_PROFIT                | float64 | -  |
| GROSS_PROFIT_YOY            | float64 | -  |
| PARENT_HOLDER_NETPROFIT     | int64   | -  |
| PARENT_HOLDER_NETPROFIT_YOY | float64 | -  |
| BASIC_EPS                   | float64 | -  |
| DILUTED_EPS                 | float64 | -  |
| GROSS_PROFIT_RATIO          | float64 | -  |
| NET_PROFIT_RATIO            | float64 | -  |
| ACCOUNTS_RECE_TR            | float64 | -  |
| INVENTORY_TR                | float64 | -  |
| TOTAL_ASSETS_TR             | float64 | -  |
| ACCOUNTS_RECE_TDAYS         | float64 | -  |
| INVENTORY_TDAYS             | float64 | -  |
| TOTAL_ASSETS_TDAYS          | float64 | -  |
| ROE_AVG                     | float64 | -  |
| ROA                         | float64 | -  |
| CURRENT_RATIO               | float64 | -  |
| SPEED_RATIO                 | float64 | -  |
| OCF_LIQDEBT                 | float64 | -  |
| DEBT_ASSET_RATIO            | float64 | -  |
| EQUITY_RATIO                | float64 | -  |
| BASIC_EPS_YOY               | float64 | -  |
| GROSS_PROFIT_RATIO_YOY      | float64 | -  |
| NET_PROFIT_RATIO_YOY        | float64 | -  |
| ROE_AVG_YOY                 | float64 | -  |
| ROA_YOY                     | float64 | -  |
| DEBT_ASSET_RATIO_YOY        | float64 | -  |
| CURRENT_RATIO_YOY           | float64 | -  |
| SPEED_RATIO_YOY             | float64 | -  |

接口示例

```python
import akshare as ak

stock_financial_us_analysis_indicator_em_df = ak.stock_financial_us_analysis_indicator_em(symbol="TSLA", indicator="年报")
print(stock_financial_us_analysis_indicator_em_df)
```

数据示例

```
   SECUCODE SECURITY_CODE  ... CURRENT_RATIO_YOY SPEED_RATIO_YOY
0    TSLA.O          TSLA  ...         17.325422       28.440175
1    TSLA.O          TSLA  ...         12.659536       19.087360
2    TSLA.O          TSLA  ...         11.391821       -2.942407
3    TSLA.O          TSLA  ...        -26.656933      -31.763438
4    TSLA.O          TSLA  ...         65.265821       98.010070
5    TSLA.O          TSLA  ...         36.490497       54.229892
6    TSLA.O          TSLA  ...         -2.902445       -7.382595
7    TSLA.O          TSLA  ...        -20.306070      -21.998647
8    TSLA.O          TSLA  ...          8.548288       34.456320
9    TSLA.O          TSLA  ...        -34.422709      -49.356229
10   TSLA.O          TSLA  ...        -19.511791      -22.928303
11   TSLA.O          TSLA  ...         92.625823      188.401364
12   TSLA.O          TSLA  ...        -50.045468      -71.819999
13   TSLA.O          TSLA  ...        -29.317702      -24.315460
14   TSLA.O          TSLA  ...         57.604938       65.676565
15   TSLA.O          TSLA  ...        389.435012      700.530829
16   TSLA.O          TSLA  ...        -17.820400      -57.326660
17   TSLA.O          TSLA  ...               NaN             NaN
18   TSLA.O          TSLA  ...               NaN             NaN
[19 rows x 48 columns]
```

#### 港股财务报表

接口: stock_financial_hk_report_em
接口中文名：东方财富-港股-财务报表-三大报表
目标地址: https://emweb.securities.eastmoney.com/PC_HKF10/FinancialAnalysis/index?type=web&code=00700

描述: 东方财富-港股-财务报表-三大报表

限量: 单次获取指定股票、指定报告且指定报告期的数据

输入参数

| 名称        | 类型  | 描述                                                  |
|-----------|-----|-----------------------------------------------------|
| stock     | str | stock="00700"; 股票代码                                 |
| symbol    | str | symbol="现金流量表"; choice of {"资产负债表", "利润表", "现金流量表"} |
| indicator | str | indicator="年度"; choice of {"年度", "报告期"}             |

输出参数

| 名称                 | 类型      | 描述 |
|--------------------|---------|----|
| SECUCODE           | object  | -  |
| SECURITY_CODE      | object  | -  |
| SECURITY_NAME_ABBR | object  | -  |
| ORG_CODE           | object  | -  |
| REPORT_DATE        | object  | -  |
| DATE_TYPE_CODE     | object  | -  |
| FISCAL_YEAR        | object  | -  |
| STD_ITEM_CODE      | object  | -  |
| STD_ITEM_NAME      | object  | -  |
| AMOUNT             | float64 | -  |
| STD_REPORT_DATE    | object  | -  |

```python
import akshare as ak

stock_financial_hk_report_em_df = ak.stock_financial_hk_report_em(stock="00700", symbol="资产负债表", indicator="年度")
print(stock_financial_hk_report_em_df)
```

数据示例

```
     SECUCODE SECURITY_CODE  ...        AMOUNT      STD_REPORT_DATE
0    00700.HK         00700  ...  5.397800e+10  2022-12-31 00:00:00
1    00700.HK         00700  ...  5.590000e+08  2022-12-31 00:00:00
2    00700.HK         00700  ...  1.618020e+11  2022-12-31 00:00:00
3    00700.HK         00700  ...  1.804600e+10  2022-12-31 00:00:00
4    00700.HK         00700  ...  9.229000e+09  2022-12-31 00:00:00
..        ...           ...  ...           ...                  ...
965  00700.HK         00700  ...  4.817800e+07  2001-12-31 00:00:00
966  00700.HK         00700  ...  4.832400e+07  2001-12-31 00:00:00
967  00700.HK         00700  ...  4.832400e+07  2001-12-31 00:00:00
968  00700.HK         00700  ...  4.832400e+07  2001-12-31 00:00:00
969  00700.HK         00700  ...  6.554200e+07  2001-12-31 00:00:00
[970 rows x 11 columns]
```

#### 美股财务报表

接口: stock_financial_us_report_em
接口中文名：东方财富-美股-财务分析-三大报表
目标地址: https://emweb.eastmoney.com/PC_USF10/pages/index.html?code=TSLA&type=web&color=w#/cwfx/zyzb

描述: 东方财富-美股-财务分析-三大报表

限量: 单次获取指定股票、指定报告且指定报告期的数据

输入参数

| 名称        | 类型  | 描述                                                    |
|-----------|-----|-------------------------------------------------------|
| stock     | str | stock="TSLA"; 股票代码                                    |
| symbol    | str | symbol="资产负债表"; choice of {"资产负债表", "综合损益表", "现金流量表"} |
| indicator | str | indicator="年报"; choice of {"年报", "单季报", "累计季报"}       |

输出参数

| 名称                 | 类型      | 描述 |
|--------------------|---------|----|
| SECUCODE           | object  | -  |
| SECURITY_CODE      | object  | -  |
| SECURITY_NAME_ABBR | object  | -  |
| REPORT_DATE        | object  | -  |
| REPORT_TYPE        | object  | -  |
| REPORT             | object  | -  |
| STD_ITEM_CODE      | object  | -  |
| AMOUNT             | float64 | -  |
| ITEM_NAME          | object  | -  |


```python
import akshare as ak

stock_financial_us_report_em_df = ak.stock_financial_us_report_em(stock="TSLA", symbol="资产负债表", indicator="年报")
print(stock_financial_us_report_em_df)
```

数据示例

```
    SECUCODE SECURITY_CODE  ...        AMOUNT ITEM_NAME
0     TSLA.O          TSLA  ...  1.613900e+10  现金及现金等价物
1     TSLA.O          TSLA  ...  1.639800e+10  现金及现金等价物
2     TSLA.O          TSLA  ...  1.625300e+10  现金及现金等价物
3     TSLA.O          TSLA  ...  1.757600e+10  现金及现金等价物
4     TSLA.O          TSLA  ...  1.938400e+10  现金及现金等价物
..       ...           ...  ...           ...       ...
619   TSLA.O          TSLA  ...  3.670390e+08     非运算项目
620   TSLA.O          TSLA  ...           NaN     非运算项目
621   TSLA.O          TSLA  ...  3.192250e+08     非运算项目
622   TSLA.O          TSLA  ...  1.011780e+08     非运算项目
623   TSLA.O          TSLA  ...  1.011780e+08     非运算项目
[624 rows x 9 columns]
```
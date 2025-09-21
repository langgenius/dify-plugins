"""
AKShare Eastmoney接口注册表
管理东方财富股票数据接口的配置信息
"""
import akshare as ak
from typing import Dict, Any, Callable, List, Optional


def normalize_symbol(symbol: str) -> str:
    """标准化股票代码，支持多种格式输入"""
    if not symbol:
        return ""
    
    # 提取数字部分
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return symbol
    
    # 对于 stock_zh_a_hist 等接口，直接返回纯数字格式
    # 因为 AKShare 的股票历史数据接口只接受纯数字格式
    return digits


def normalize_us_symbol(symbol: str) -> str:
    """标准化美股股票代码，将常见简称转换为AKShare需要的格式"""
    if not symbol:
        return ""
    
    # 常见美股股票代码映射
    us_symbol_map = {
        "AAPL": "105.AAPL",
        "MSFT": "105.MSFT", 
        "GOOGL": "105.GOOGL",
        "AMZN": "105.AMZN",
        "TSLA": "105.TSLA",
        "META": "105.META",
        "NVDA": "105.NVDA",
        "NFLX": "105.NFLX",
        "TTE": "106.TTE",
        "BABA": "106.BABA",
        "JD": "106.JD",
        "PDD": "106.PDD",
        "NIO": "106.NIO",
        "XPEV": "106.XPEV",
        "LI": "106.LI"
    }
    
    # 如果已经是正确格式（包含点号），直接返回
    if "." in symbol:
        return symbol
    
    # 转换为大写进行匹配
    symbol_upper = symbol.upper()
    
    # 如果在映射表中，返回对应的格式
    if symbol_upper in us_symbol_map:
        return us_symbol_map[symbol_upper]
    
    # 如果不在映射表中，尝试添加默认前缀
    # 大多数美股使用 105 前缀
    return f"105.{symbol_upper}"


def get_symbol_candidates(symbol: str) -> List[str]:
    """获取股票代码的多种候选格式"""
    if not symbol:
        return []
    
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return [symbol]
    
    if digits.startswith("6"):
        market = "sh"
    else:
        market = "sz"
    
    return [digits, f"{market}{digits}", f"{market.upper()}{digits}"]


# AKShare东方财富接口注册表
REGISTRY: Dict[str, Dict[str, Any]] = {
    "stock_individual_info_em": {
        "label": {"zh_Hans": "个股信息", "en_US": "Individual Stock Info"},
        "fn": ak.stock_individual_info_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定股票的个股信息"
    },
    
    "stock_bid_ask_em": {
        "label": {"zh_Hans": "行情报价", "en_US": "Quote (Bid/Ask)"},
        "fn": ak.stock_bid_ask_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "get_symbol_candidates"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取指定股票的行情报价数据"
    },
    
    "stock_zh_a_hist": {
        "label": {"zh_Hans": "股票历史数据", "en_US": "Stock History"},
        "fn": ak.stock_zh_a_hist,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "period": {"type": "str", "default": "daily"},
                "start_date": {"type": "str", "default": "20240101"},
                "end_date": {"type": "str", "default": "20500101"}
            },
            "optional": {
                "adjust": {"type": "str", "default": ""}
            }
        },
        "supports_timeout": True,
        "description": "获取股票历史数据"
    },
    
    "stock_zh_a_hist_pre_min_em": {
        "label": {"zh_Hans": "盘前数据", "en_US": "Pre-market Data"},
        "fn": ak.stock_zh_a_hist_pre_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "start_time": {"type": "str", "default": "09:00:00"},
                "end_time": {"type": "str", "default": "15:40:00"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定股票的盘前分钟数据"
    },
    
    "stock_zh_b_spot_em": {
        "label": {"zh_Hans": "B股实时行情", "en_US": "B-share Real-time Data"},
        "fn": ak.stock_zh_b_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有B股上市公司的实时行情数据"
    },
    
    "stock_gsrl_gsdt_em": {
        "label": {"zh_Hans": "公司动态", "en_US": "Company Dynamics"},
        "fn": ak.stock_gsrl_gsdt_em,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取指定交易日的公司动态数据"
    },
    
    "stock_zh_a_st_em": {
        "label": {"zh_Hans": "ST股票", "en_US": "ST Stocks"},
        "fn": ak.stock_zh_a_st_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取ST股票列表"
    },
    
    "stock_zh_a_new_em": {
        "label": {"zh_Hans": "沪深个股-新股板块实时行情", "en_US": "A-share New Stocks Real-time Data"},
        "fn": ak.stock_zh_a_new_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪深个股新股板块实时行情数据"
    },
    
    "stock_zh_a_stop_em": {
        "label": {"zh_Hans": "停牌股票", "en_US": "Suspended Stocks"},
        "fn": ak.stock_zh_a_stop_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取停牌股票列表"
    },
    
    "stock_zh_kcb_report_em": {
        "label": {"zh_Hans": "科创板报告", "en_US": "STAR Market Report"},
        "fn": ak.stock_zh_kcb_report_em,
        "params": {
            "required": {},
            "optional": {
                "from_page": {"type": "int", "default": 1},
                "to_page": {"type": "int", "default": 100}
            }
        },
        "supports_timeout": True,
        "description": "获取所有科创板上市公司的报告数据"
    },
    
    "stock_zh_ah_spot_em": {
        "label": {"zh_Hans": "AH股比价", "en_US": "A/H Share Comparison"},
        "fn": ak.stock_zh_ah_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有A+H上市公司的实时行情数据，延迟15分钟更新"
    },
    
    "stock_us_hist": {
        "label": {"zh_Hans": "美股历史数据", "en_US": "US Stock History"},
        "fn": ak.stock_us_hist,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_us_symbol"},
                "period": {"type": "str", "default": "daily"},
                "start_date": {"type": "str", "default": "20240101"},
                "end_date": {"type": "str", "default": "20500101"},
                "adjust": {"type": "str", "default": ""}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定美股上市公司的历史行情数据"
    },
    
    "stock_us_hist_min_em": {
        "label": {"zh_Hans": "美股分钟历史", "en_US": "US Stock Minute History"},
        "fn": ak.stock_us_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_us_symbol"}
            },
            "optional": {
                "start_date": {"type": "str", "default": "1979-09-01 09:32:00"},
                "end_date": {"type": "str", "default": "2222-01-01 09:32:00"}
            }
        },
        "supports_timeout": True,
        "description": "获取指定美股上市公司的分钟级历史数据"
    },
    
    "stock_hk_hist_min_em": {
        "label": {"zh_Hans": "港股分钟历史", "en_US": "HK Stock Minute History"},
        "fn": ak.stock_hk_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "period": {"type": "str", "default": "5"},
                "start_date": {"type": "str", "default": "1979-09-01 09:32:00"},
                "end_date": {"type": "str", "default": "2222-01-01 09:32:00"},
                "adjust": {"type": "str", "default": ""}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定港股上市公司的分钟级历史数据"
    },
    
    # 股票市场总貌相关接口
    "stock_sse_summary": {
        "label": {"zh_Hans": "上交所-股票数据总貌", "en_US": "SSE Stock Summary"},
        "fn": ak.stock_sse_summary,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取上海证券交易所股票数据总貌"
    },
    
    "stock_szse_summary": {
        "label": {"zh_Hans": "深交所-市场总貌-证券类别统计", "en_US": "SZSE Market Summary"},
        "fn": ak.stock_szse_summary,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取深圳证券交易所市场总貌-证券类别统计"
    },
    
    
    "stock_sse_deal_daily": {
        "label": {"zh_Hans": "上交所-每日股票情况", "en_US": "SSE Daily Trading"},
        "fn": ak.stock_sse_deal_daily,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取上海证券交易所每日股票情况"
    },
    
    # 新增的7个股票市场总貌接口
    "stock_gpzy_profile_em": {
        "label": {"zh_Hans": "股权质押-股权质押市场概况", "en_US": "Equity Pledge Market Overview"},
        "fn": ak.stock_gpzy_profile_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取股权质押市场概况数据"
    },
    
    
    "stock_gpzy_industry_data_em": {
        "label": {"zh_Hans": "股权质押-上市公司质押比例-行业数据", "en_US": "Pledge Ratio Industry Data"},
        "fn": ak.stock_gpzy_industry_data_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取上市公司质押比例行业数据"
    },
    
    "stock_sy_profile_em": {
        "label": {"zh_Hans": "商誉-A股商誉市场概况", "en_US": "A-Share Goodwill Market Overview"},
        "fn": ak.stock_sy_profile_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股商誉市场概况数据"
    },
    
    "stock_account_statistics_em": {
        "label": {"zh_Hans": "特色数据-股票账户统计", "en_US": "Stock Account Statistics"},
        "fn": ak.stock_account_statistics_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取股票账户统计数据"
    },
    
    "stock_comment_em": {
        "label": {"zh_Hans": "特色数据-千股千评", "en_US": "Stock Comments"},
        "fn": ak.stock_comment_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取千股千评数据"
    },
    
    "stock_hsgt_fund_flow_summary_em": {
        "label": {"zh_Hans": "资金流向-沪深港通资金流向", "en_US": "HSGT Fund Flow Summary"},
        "fn": ak.stock_hsgt_fund_flow_summary_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪深港通资金流向数据"
    },
    
    # 个股信息总貌相关接口
    "stock_hk_security_profile_em": {
        "label": {"zh_Hans": "港股-个股-证券概况", "en_US": "HK Security Profile"},
        "fn": ak.stock_hk_security_profile_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股证券概况信息"
    },
    
    "stock_hk_company_profile_em": {
        "label": {"zh_Hans": "港股-个股-公司概况", "en_US": "HK Company Profile"},
        "fn": ak.stock_hk_company_profile_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股公司概况信息"
    },
    
    "stock_zyjs_ths": {
        "label": {"zh_Hans": "A股-个股-主营业务", "en_US": "A-share Main Business"},
        "fn": ak.stock_zyjs_ths,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股主营业务信息"
    },
    
    "stock_zygc_em": {
        "label": {"zh_Hans": "A股-个股-主营业务", "en_US": "A-share Main Business"},
        "fn": ak.stock_zygc_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股主营业务信息"
    },
    
    "stock_news_em": {
        "label": {"zh_Hans": "A股-个股-相关新闻资讯", "en_US": "A-share News"},
        "fn": ak.stock_news_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股相关新闻资讯"
    },
    
    "stock_profile_cninfo": {
        "label": {"zh_Hans": "A股-个股-公司概况", "en_US": "A-share Company Profile"},
        "fn": ak.stock_profile_cninfo,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股公司概况信息"
    },
    
    
    "stock_ipo_summary_cninfo": {
        "label": {"zh_Hans": "A股-个股-IPO信息", "en_US": "A-share IPO Info"},
        "fn": ak.stock_ipo_summary_cninfo,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股IPO信息"
    },
    
    "stock_fhps_detail_em": {
        "label": {"zh_Hans": "A股-个股-分红配股", "en_US": "A-share Dividend"},
        "fn": ak.stock_fhps_detail_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股分红配股信息"
    },
    
    "stock_hk_fhpx_detail_ths": {
        "label": {"zh_Hans": "港股-个股-分红信息", "en_US": "HK Dividend"},
        "fn": ak.stock_hk_fhpx_detail_ths,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股分红信息"
    },
    
    "stock_research_report_em": {
        "label": {"zh_Hans": "A股-个股-研报列表", "en_US": "A-share Research Report"},
        "fn": ak.stock_research_report_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股研报列表"
    },
    
    "stock_balance_sheet_by_report_em": {
        "label": {"zh_Hans": "A股-个股-资产负债表", "en_US": "A-share Balance Sheet"},
        "fn": ak.stock_balance_sheet_by_report_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股资产负债表信息"
    },
    
    "stock_financial_abstract": {
        "label": {"zh_Hans": "A股-个股-财务摘要", "en_US": "A-share Financial Abstract"},
        "fn": ak.stock_financial_abstract,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取A股财务摘要信息"
    },
    
    # 股票实时行情相关接口
    "stock_sh_a_spot_em": {
        "label": {"zh_Hans": "沪A股-实时行情", "en_US": "Shanghai A-share Real-time Data"},
        "fn": ak.stock_sh_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪A股所有上市公司的实时行情数据"
    },
    
    "stock_sz_a_spot_em": {
        "label": {"zh_Hans": "深A股-实时行情", "en_US": "Shenzhen A-share Real-time Data"},
        "fn": ak.stock_sz_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取深A股所有上市公司的实时行情数据"
    },
    
    "stock_bj_a_spot_em": {
        "label": {"zh_Hans": "京A股-实时行情", "en_US": "Beijing A-share Real-time Data"},
        "fn": ak.stock_bj_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取京A股所有上市公司的实时行情数据"
    },
    
    "stock_new_a_spot_em": {
        "label": {"zh_Hans": "新股-实时行情", "en_US": "New A-share Real-time Data"},
        "fn": ak.stock_new_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取新股所有上市公司的实时行情数据"
    },
    
    "stock_cy_a_spot_em": {
        "label": {"zh_Hans": "创业板-实时行情", "en_US": "Growth Enterprise Market Real-time Data"},
        "fn": ak.stock_cy_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取创业板所有上市公司的实时行情数据"
    },
    
    "stock_kc_a_spot_em": {
        "label": {"zh_Hans": "科创板-实时行情", "en_US": "Science and Technology Innovation Board Real-time Data"},
        "fn": ak.stock_kc_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取科创板所有上市公司的实时行情数据"
    },
    
    "stock_zh_ab_comparison_em": {
        "label": {"zh_Hans": "沪深京A股-全量AB股比价", "en_US": "A/B Share Comparison"},
        "fn": ak.stock_zh_ab_comparison_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪深京A股全量AB股比价数据"
    },
    
    "stock_zh_a_new": {
        "label": {"zh_Hans": "沪深股市-次新股-实时行情", "en_US": "A-share Secondary New Stocks Real-time Data"},
        "fn": ak.stock_zh_a_new,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪深股市次新股实时行情数据"
    },
    
    "stock_xgsr_ths": {
        "label": {"zh_Hans": "沪深个股-新股上市首日", "en_US": "A-share New Stock First Day Listing"},
        "fn": ak.stock_xgsr_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取沪深个股新股上市首日数据"
    },
    
    "stock_hk_spot_em": {
        "label": {"zh_Hans": "港股-实时行情", "en_US": "HK Stock Real-time Data"},
        "fn": ak.stock_hk_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有港股的实时行情数据，延迟15分钟更新"
    },
    
    "stock_hk_main_board_spot_em": {
        "label": {"zh_Hans": "港股主板-实时行情", "en_US": "HK Main Board Real-time Data"},
        "fn": ak.stock_hk_main_board_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股主板的实时行情数据，延迟15分钟更新"
    }
}


def get_interface_config(interface_name: str) -> Optional[Dict[str, Any]]:
    """获取接口配置"""
    return REGISTRY.get(interface_name)


def get_available_interfaces() -> List[str]:
    """获取所有可用的接口名称"""
    return list(REGISTRY.keys())


def validate_interface_params(interface_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证并处理接口参数"""
    import logging
    logging.info(f"validate_interface_params called with interface: {interface_name}, params: {params}")
    
    config = get_interface_config(interface_name)
    if not config:
        raise ValueError(f"Unknown interface: {interface_name}")
    
    processed_params = {}
    
    # 只处理接口配置中定义的参数，忽略其他参数
    all_defined_params = set(config["params"]["required"].keys()) | set(config["params"]["optional"].keys())
    
    # 处理必需参数
    for param_name, param_config in config["params"]["required"].items():
        if param_name not in params:
            if "default" in param_config:
                processed_params[param_name] = param_config["default"]
            else:
                raise ValueError(f"Required parameter '{param_name}' is missing")
        else:
            value = params[param_name]
            # 类型转换
            if param_config["type"] == "str":
                value = str(value)
            elif param_config["type"] == "int":
                value = int(value)
            elif param_config["type"] == "float":
                value = float(value)
            
            # 参数验证
            if param_name == "period" and interface_name == "stock_zh_a_hist":
                # stock_zh_a_hist 的 period 参数只接受 daily, weekly, monthly
                valid_periods = ["daily", "weekly", "monthly"]
                if value not in valid_periods:
                    logging.warning(f"Invalid period '{value}' for stock_zh_a_hist, using default 'daily'")
                    value = "daily"
            
            # 日期验证
            if param_name in ["start_date", "end_date", "date"]:
                try:
                    from datetime import datetime
                    # 解析日期字符串 (格式: YYYYMMDD)
                    if len(str(value)) == 8:
                        date_obj = datetime.strptime(str(value), "%Y%m%d")
                        today = datetime.now()
                        # 检查是否是未来日期（超过今天）
                        if date_obj.date() > today.date():
                            logging.warning(f"Future date '{value}' detected for {param_name}, using current date")
                            value = today.strftime("%Y%m%d")
                except ValueError:
                    logging.warning(f"Invalid date format '{value}' for {param_name}")
                    # 保持原值，让AKShare函数处理
            
            # 预处理
            if "preprocess" in param_config:
                preprocess_func = param_config["preprocess"]
                if preprocess_func == "normalize_symbol":
                    # 只对 symbol 参数应用 normalize_symbol
                    if param_name == "symbol":
                        value = normalize_symbol(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "normalize_us_symbol":
                    # 对美股股票代码进行标准化
                    if param_name == "symbol":
                        value = normalize_us_symbol(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "get_symbol_candidates":
                    # 对于需要多候选的接口，返回候选列表
                    return get_symbol_candidates(value)
            
            processed_params[param_name] = value
    
    # 处理可选参数
    for param_name, param_config in config["params"]["optional"].items():
        if param_name in params:
            value = params[param_name]
            if param_config["type"] == "str":
                value = str(value)
            elif param_config["type"] == "int":
                value = int(value)
            elif param_config["type"] == "float":
                value = float(value)
            processed_params[param_name] = value
        elif "default" in param_config:
            processed_params[param_name] = param_config["default"]
    
    logging.info(f"validate_interface_params returning: {processed_params}")
    return processed_params

from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol


class StockFinancialAnalysisTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        import logging
        try:
            logging.info(f"StockFinancialAnalysisTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")  # 股票代码
            date = tool_parameters.get("date", "")  # 报告日期
            indicator_ths = tool_parameters.get("indicator_ths", "")  # A股同花顺指标类型
            indicator_hk = tool_parameters.get("indicator_hk", "")  # 港股指标类型
            indicator_us = tool_parameters.get("indicator_us", "")  # 美股指标类型
            start_year = tool_parameters.get("start_year", "")  # 起始年份
            report_type = tool_parameters.get("report_type", "")  # 报表类型
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Date: {date}, IndicatorTHS: {indicator_ths}, IndicatorHK: {indicator_hk}, IndicatorUS: {indicator_us}, StartYear: {start_year}, ReportType: {report_type}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 按功能分类
        interface_configs = {
            # 日期类接口（需要date参数）
            "stock_lrb_em": {
                "fn": ak.stock_lrb_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "A股-业绩快报-利润表"
            },
            "stock_xjll_em": {
                "fn": ak.stock_xjll_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "A股-业绩快报-现金流量表"
            },
            "stock_zcfz_em": {
                "fn": ak.stock_zcfz_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,  # 设置为200秒，平衡超时和性能
                "description": "沪深-业绩快报-资产负债表"
            },
            "stock_zcfz_bj_em": {
                "fn": ak.stock_zcfz_bj_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "北交所-业绩快报-资产负债表"
            },
            
            # 股票代码+指标类接口（需要symbol+indicator_ths参数）
            "stock_financial_debt_ths": {
                "fn": ak.stock_financial_debt_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_ths": True,
                "requires_start_year": False,
                "timeout": 600,  # 增加超时时间，财务数据量大
                "description": "A股-财务指标-资产负债表"
            },
            "stock_financial_benefit_ths": {
                "fn": ak.stock_financial_benefit_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_ths": True,
                "requires_start_year": False,
                "timeout": 600,  # 增加超时时间，财务数据量大
                "description": "A股-财务指标-利润表"
            },
            "stock_financial_cash_ths": {
                "fn": ak.stock_financial_cash_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_ths": True,
                "requires_start_year": False,
                "timeout": 600,  # 增加超时时间，财务数据量大
                "description": "A股-财务指标-现金流量表"
            },
            "stock_financial_abstract_ths": {
                "fn": ak.stock_financial_abstract_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_ths": True,
                "requires_start_year": False,
                "timeout": 600,  # 增加超时时间，财务数据量大
                "description": "A股-财务指标-主要指标"
            },
            
            # 股票代码类接口（只需要symbol参数）
            "stock_financial_abstract": {
                "fn": ak.stock_financial_abstract,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,  # 增加超时时间，财务数据量大
                "description": "A股-财务报表-关键指标"
            },
            
            # 股票代码+年份类接口（需要symbol+start_year参数）
            "stock_financial_analysis_indicator": {
                "fn": ak.stock_financial_analysis_indicator,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": True,
                "timeout": 600,
                "description": "A股-财务分析-财务指标"
            },
            
            # 港股财务分析接口（需要symbol+indicator_hk参数）
            "stock_financial_hk_analysis_indicator_em": {
                "fn": ak.stock_financial_hk_analysis_indicator_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_hk": True,
                "requires_start_year": False,
                "timeout": 600,
                "description": "港股-财务分析-主要指标"
            },
            
            # 美股财务分析接口（需要symbol+indicator_us参数）
            "stock_financial_us_analysis_indicator_em": {
                "fn": ak.stock_financial_us_analysis_indicator_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_us": True,
                "requires_start_year": False,
                "timeout": 600,
                "description": "美股-财务分析-主要指标"
            },
            
            # 港股财务报表接口（需要stock+symbol+indicator_hk参数）
            "stock_financial_hk_report_em": {
                "fn": ak.stock_financial_hk_report_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_hk": True,
                "requires_start_year": False,
                "requires_report_type": True,  # 需要报表类型参数
                "timeout": 600,
                "description": "港股-财务报表-三大报表",
                "param_mapping": {"stock": "symbol", "symbol": "report_type", "indicator": "indicator_hk"}
            },
            
            # 美股财务报表接口（需要stock+symbol+indicator_us参数）
            "stock_financial_us_report_em": {
                "fn": ak.stock_financial_us_report_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator_us": True,
                "requires_start_year": False,
                "requires_report_type": True,  # 需要报表类型参数
                "timeout": 600,
                "description": "美股-财务分析-三大报表",
                "param_mapping": {"stock": "symbol", "symbol": "report_type", "indicator": "indicator"}
            }
        }
        
        # 获取接口配置  
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 参数验证
        try:
            # 验证必需参数
            if config["requires_symbol"] and not symbol:
                yield self.create_text_message(f"接口 {config['description']} 需要股票代码参数")
                yield self.create_json_message({"error": f"symbol required for {interface}"})
                return
                
            if config["requires_date"] and not date:
                yield self.create_text_message(f"接口 {config['description']} 需要报告日期参数")
                yield self.create_json_message({"error": f"date required for {interface}"})
                return
                
            if config.get("requires_indicator_ths", False) and not indicator_ths:
                yield self.create_text_message(f"接口 {config['description']} 需要A股同花顺指标类型参数")
                yield self.create_json_message({"error": f"indicator_ths required for {interface}"})
                return
                
            if config.get("requires_indicator_hk", False) and not indicator_hk:
                yield self.create_text_message(f"接口 {config['description']} 需要港股指标类型参数")
                yield self.create_json_message({"error": f"indicator_hk required for {interface}"})
                return
                
            if config.get("requires_indicator_us", False) and not indicator_us:
                yield self.create_text_message(f"接口 {config['description']} 需要美股指标类型参数")
                yield self.create_json_message({"error": f"indicator_us required for {interface}"})
                return
                
            if config["requires_start_year"] and not start_year:
                yield self.create_text_message(f"接口 {config['description']} 需要起始年份参数")
                yield self.create_json_message({"error": f"start_year required for {interface}"})
                return
                
            if config.get("requires_report_type", False) and not report_type:
                yield self.create_text_message(f"接口 {config['description']} 需要报表类型参数")
                yield self.create_json_message({"error": f"report_type required for {interface}"})
                return
            
            # 验证股票代码格式
            if config["requires_symbol"] and symbol:
                validation_result = None
                for result in validate_stock_symbol(symbol, self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
            
            # 验证日期格式
            if config["requires_date"] and date:
                if not self._validate_date_format(date):
                    yield self.create_text_message(f"日期格式不正确，应为YYYYMMDD格式: {date}")
                    yield self.create_json_message({"error": f"invalid date format, should be YYYYMMDD: {date}"})
                    return
            
            # 验证年份格式
            if config["requires_start_year"] and start_year:
                if not self._validate_year_format(start_year):
                    yield self.create_text_message(f"年份格式不正确，应为YYYY格式: {start_year}")
                    yield self.create_json_message({"error": f"invalid year format, should be YYYY: {start_year}"})
                    return
                    
        except Exception as e:
            logging.error(f"Error in parameter validation: {e}")
            yield self.create_text_message(f"参数验证错误: {e}")
            yield self.create_json_message({"error": f"parameter validation error: {e}"})
            return
        
        # 构建调用参数
        try:
            call_params = {}
            
            # 根据接口需求添加参数
            if config["requires_symbol"]:
                call_params["symbol"] = symbol
                
            if config["requires_date"]:
                call_params["date"] = date
                
            if config.get("requires_indicator_ths", False):
                call_params["indicator"] = indicator_ths
            elif config.get("requires_indicator_hk", False):
                call_params["indicator"] = indicator_hk
            elif config.get("requires_indicator_us", False):
                call_params["indicator"] = indicator_us
                
            if config["requires_start_year"]:
                call_params["start_year"] = start_year
                
            if config.get("requires_report_type", False):
                call_params["report_type"] = report_type
            
            # 使用参数映射系统（如果存在）
            param_mapping = config.get("param_mapping", {})
            if param_mapping:
                # 清空之前的参数，使用映射系统
                call_params = {}
                for ak_param, tool_param in param_mapping.items():
                    if tool_param == "symbol" and symbol:
                        call_params[ak_param] = symbol
                    elif tool_param == "report_type" and report_type:
                        call_params[ak_param] = report_type
                    elif tool_param == "indicator":
                        # 根据接口类型选择正确的indicator参数
                        if config.get("requires_indicator_ths", False) and indicator_ths:
                            call_params[ak_param] = indicator_ths
                        elif config.get("requires_indicator_hk", False) and indicator_hk:
                            call_params[ak_param] = indicator_hk
                        elif config.get("requires_indicator_us", False) and indicator_us:
                            call_params[ak_param] = indicator_us
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            logging.info(f"Final call params: {call_params}")
            logging.info(f"Using timeout: {interface_timeout}")
            
        except Exception as e:
            logging.error(f"Error in parameter construction: {e}")
            yield self.create_text_message(f"参数构建错误: {e}")
            yield self.create_json_message({"error": f"parameter construction error: {e}"})
            return
        
        # 调用AKShare接口
        try:
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
            
            if result is None:
                yield self.create_text_message("接口返回空数据")
                yield self.create_json_message({"data": []})
                return
            
            # 处理返回结果
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    yield self.create_text_message("暂无数据")
                    yield self.create_json_message({"data": []})
                else:
                    # 处理DataFrame输出
                    yield from process_dataframe_output(result, self)
            else:
                # 处理其他类型输出
                yield from process_other_output(result, self)
                
        except Exception as e:
            logging.error(f"Error in AKShare call: {e}")
            
            # 检查是否是网络连接错误
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {e}")
                yield self.create_json_message({
                    "error": "network_error",
                    "message": "网络连接中断",
                    "details": str(e),
                    "suggestion": "请稍后重试或检查网络连接"
                })
            else:
                # 其他错误
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}, 日期: {date}, 指标: {indicator}, 起始年份: {start_year}", str(interface_timeout))
    
    def _validate_date_format(self, date_str: str) -> bool:
        """验证日期格式是否为YYYYMMDD"""
        try:
            if len(date_str) != 8:
                return False
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            # 基本范围检查
            if year < 2000 or year > 2030:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
                
            return True
        except (ValueError, IndexError):
            return False
    
    def _validate_year_format(self, year_str: str) -> bool:
        """验证年份格式是否为YYYY"""
        try:
            if len(year_str) != 4:
                return False
            year = int(year_str)
            return 2000 <= year <= 2030
        except ValueError:
            return False

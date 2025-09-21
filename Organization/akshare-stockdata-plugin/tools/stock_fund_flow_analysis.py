from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol


class StockFundFlowAnalysisTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        import logging
        try:
            logging.info(f"StockFundFlowAnalysisTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            stock_code = tool_parameters.get("stock_code", "")  # 股票代码
            market = tool_parameters.get("market", "")  # 市场
            indicator = tool_parameters.get("indicator", "")  # 指标
            sector_type = tool_parameters.get("sector_type", "")  # 板块类型
            market_choice = tool_parameters.get("market_choice", "")  # 市场选择
            industry_name = tool_parameters.get("industry_name", "")  # 行业名称
            concept_name = tool_parameters.get("concept_name", "")  # 概念名称
            adjust = tool_parameters.get("adjust", "")  # 复权方式
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, StockCode: {stock_code}, Market: {market}, Indicator: {indicator}, SectorType: {sector_type}, MarketChoice: {market_choice}, IndustryName: {industry_name}, ConceptName: {concept_name}, Adjust: {adjust}, Retries: {retries}, Timeout: {timeout}")
            
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
            # 个股类接口
            "stock_individual_fund_flow": {
                "fn": ak.stock_individual_fund_flow,
                "requires_stock_code": True,
                "requires_market": True,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "个股资金流向",
                "timeout": 600,
                "param_mapping": {"stock": "stock_code", "market": "market"}
            },
            "stock_individual_fund_flow_rank": {
                "fn": ak.stock_individual_fund_flow_rank,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": True,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "个股资金流向排行",
                "timeout": 600,  # 增加到3分钟，因为需要处理53页数据
                "param_mapping": {"indicator": "indicator"}
            },
            "stock_cyq_em": {
                "fn": ak.stock_cyq_em,
                "requires_stock_code": True,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": True,
                "description": "筹码分布",
                "timeout": 600,
                "param_mapping": {"symbol": "stock_code", "adjust": "adjust"}
            },
            # 市场类接口
            "stock_market_fund_flow": {
                "fn": ak.stock_market_fund_flow,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "市场资金流向",
                "timeout": 600,
                "param_mapping": {}
            },
            "stock_main_fund_flow": {
                "fn": ak.stock_main_fund_flow,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": True,  # 使用market_choice参数
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "主力资金流向",
                "timeout": 600,  # 增加到200秒，因为需要处理28页数据，耗时较长
                "param_mapping": {"symbol": "market_choice"}
            },
            # 板块类接口
            "stock_sector_fund_flow_rank": {
                "fn": ak.stock_sector_fund_flow_rank,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": True,
                "requires_sector_type": True,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "板块资金流向排行",
                "timeout": 600,  # 增加超时时间，板块数据量较大
                "param_mapping": {"indicator": "indicator", "sector_type": "sector_type"}
            },
            "stock_sector_fund_flow_summary": {
                "fn": ak.stock_sector_fund_flow_summary,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": True,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": True,  # 使用industry_name参数
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "行业个股资金流向",
                "timeout": 600,  # 增加超时时间，行业数据量较大
                "param_mapping": {"symbol": "industry_name", "indicator": "indicator"}
            },
            "stock_sector_fund_flow_hist": {
                "fn": ak.stock_sector_fund_flow_hist,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": True,  # 使用industry_name参数
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "行业历史资金流向",
                "timeout": 600,
                "param_mapping": {"symbol": "industry_name"}
            },
            # 概念类接口
            "stock_concept_fund_flow_hist": {
                "fn": ak.stock_concept_fund_flow_hist,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": True,  # 使用concept_name参数
                "requires_adjust": False,
                "description": "概念历史资金流向",
                "timeout": 600,
                "param_mapping": {"symbol": "concept_name"}
            },
            # 大单追踪接口
            "stock_fund_flow_big_deal": {
                "fn": ak.stock_fund_flow_big_deal,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "A股-资金流向-大单追踪",
                "timeout": 600,
                "param_mapping": {}
            },
            # 沪深港通资金流向接口
            "stock_hsgt_fund_flow_summary_em": {
                "fn": ak.stock_hsgt_fund_flow_summary_em,
                "requires_stock_code": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_sector_type": False,
                "requires_market_choice": False,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "requires_adjust": False,
                "description": "资金流向-沪深港通资金流向",
                "timeout": 600,
                "param_mapping": {}
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 参数验证
        if config["requires_stock_code"] and not stock_code:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'stock_code' 参数。请提供股票代码。")
            yield self.create_json_message({"error": "stock_code_required", "message": f"{interface} requires 'stock_code' parameter"})
            return
        
        if config["requires_market"] and not market:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'market' 参数。请提供市场代码（sh/sz/bj）。")
            yield self.create_json_message({"error": "market_required", "message": f"{interface} requires 'market' parameter"})
            return
        
        if config["requires_indicator"] and not indicator:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'indicator' 参数。请提供指标（今日/3日/5日/10日）。")
            yield self.create_json_message({"error": "indicator_required", "message": f"{interface} requires 'indicator' parameter"})
            return
        
        if config["requires_sector_type"] and not sector_type:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'sector_type' 参数。请提供板块类型。")
            yield self.create_json_message({"error": "sector_type_required", "message": f"{interface} requires 'sector_type' parameter"})
            return
        
        if config["requires_market_choice"] and not market_choice:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'market_choice' 参数。请提供市场选择。")
            yield self.create_json_message({"error": "market_choice_required", "message": f"{interface} requires 'market_choice' parameter"})
            return
        
        if config["requires_industry_name"] and not industry_name:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'industry_name' 参数。请提供行业名称。")
            yield self.create_json_message({"error": "industry_name_required", "message": f"{interface} requires 'industry_name' parameter"})
            return
        
        if config["requires_concept_name"] and not concept_name:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'concept_name' 参数。请提供概念名称。")
            yield self.create_json_message({"error": "concept_name_required", "message": f"{interface} requires 'concept_name' parameter"})
            return
        
        if config["requires_adjust"] and adjust is None:
            yield self.create_text_message(f"错误：'{config['description']}'接口需要 'adjust' 参数。请提供复权方式。")
            yield self.create_json_message({"error": "adjust_required", "message": f"{interface} requires 'adjust' parameter"})
            return
        
        # 股票代码格式验证（仅对需要股票代码的接口）
        if config["requires_stock_code"] and stock_code:
            validation_result = None
            for result in validate_stock_symbol(stock_code, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
            
            # 验证市场参数与股票代码的匹配性
            if config["requires_market"] and market and stock_code:
                if not self._validate_market_symbol_match(stock_code, market):
                    yield self.create_text_message(f"错误：股票代码 '{stock_code}' 与市场 '{market}' 不匹配。\n\n请检查：\n- 600xxx、601xxx、603xxx、688xxx、689xxx 对应 'sh'（上海）\n- 000xxx、001xxx、002xxx、003xxx、300xxx 对应 'sz'（深圳）\n- 430xxx、830xxx、870xxx 对应 'bj'（北京）")
                    yield self.create_json_message({"error": "market_symbol_mismatch", "message": f"Stock symbol '{stock_code}' does not match market '{market}'"})
                    return
        
        # 构建调用参数 - 使用参数映射系统
        call_params = {}
        param_mapping = config.get("param_mapping", {})
        
        # 根据参数映射构建调用参数
        for ak_param, tool_param in param_mapping.items():
            if tool_param == "stock_code" and stock_code:
                call_params[ak_param] = stock_code
            elif tool_param == "market" and market:
                call_params[ak_param] = market
            elif tool_param == "indicator" and indicator:
                call_params[ak_param] = indicator
            elif tool_param == "sector_type" and sector_type:
                call_params[ak_param] = sector_type
            elif tool_param == "market_choice" and market_choice:
                call_params[ak_param] = market_choice
            elif tool_param == "industry_name" and industry_name:
                call_params[ak_param] = industry_name
            elif tool_param == "concept_name" and concept_name:
                call_params[ak_param] = concept_name
            elif tool_param == "adjust" and adjust is not None:
                if adjust == "none":
                    call_params[ak_param] = ""  # "none" 对应空字符串，表示不复权
                else:
                    call_params[ak_param] = adjust
        
        # 使用接口特定的超时时间
        interface_timeout = config.get("timeout", timeout)
        
        logging.info(f"Call params: {call_params}")
        logging.info(f"Function: {config['fn']}")
        logging.info(f"Interface timeout: {interface_timeout}")
        
        # 调用AKShare接口
        try:
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
        except Exception as e:
            # 检查是否是已知的AKShare接口问题
            error_msg = str(e)
            if "'NoneType' object is not subscriptable" in error_msg:
                yield self.create_text_message(f"接口暂时不可用：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 数据源暂时不可用或维护中\n2. AKShare库中该接口存在已知问题\n3. 网络连接问题\n\n建议：\n1. 稍后重试\n2. 尝试使用其他接口\n3. 检查网络连接")
                yield self.create_json_message({
                    "error": "interface_unavailable",
                    "message": "接口暂时不可用",
                    "details": error_msg,
                    "suggestion": "稍后重试或使用其他接口"
                })
                return
            elif "KeyError" in error_msg and ("sector" in call_params or "symbol" in call_params):
                # 处理行业名称或概念名称错误的情况
                yield from self._handle_invalid_sector_name(e, interface, call_params)
                return
            elif any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded", "ReadTimeout", "Read timed out"]):
                yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 资金流向数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他资金流向接口")
                yield self.create_json_message({
                    "error": "ssl_timeout_error",
                    "message": "SSL连接超时，资金流向数据获取失败",
                    "details": error_msg,
                    "suggestion": "稍后重试或尝试其他接口"
                })
                return
            else:
                # 使用统一的错误处理机制
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}, 市场: {market}, 指标: {indicator}, 板块类型: {sector_type}, 市场选择: {market_choice}, 行业/概念: {sector}, 复权: {adjust}", str(interface_timeout))
                return
        
        # 处理结果
        if result is None:
            yield from handle_empty_result(self)
            return
        
        # 检查是否为空
        if hasattr(result, 'empty') and result.empty:
            yield from handle_empty_result(self)
            return
        
        # 输出处理
        if isinstance(result, pd.DataFrame):
            yield from process_dataframe_output(result, self)
        else:
            yield from process_other_output(result, self)
    
    def _handle_invalid_sector_name(self, error, interface, call_params):
        """处理行业名称或概念名称错误的情况"""
        import akshare as ak
        import logging
        
        try:
            # 根据接口类型获取相应的可选值清单
            if interface == "stock_concept_fund_flow_hist":
                # 概念历史资金流向 - 获取概念名称
                yield from self._get_concept_names(error)
            else:
                # 行业相关接口 - 获取行业名称
                yield from self._get_industry_names(error)
                
        except Exception as e:
            logging.error(f"Error getting sector names: {e}")
            # 如果获取名称失败，提供通用建议
            yield self.create_text_message(f"名称错误：\n\n{str(error)}\n\n建议：\n1. 请检查名称是否正确\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用常见的名称")
            yield self.create_json_message({
                "error": "invalid_sector_name",
                "message": "名称错误",
                "details": str(error),
                "suggestion": "请使用正确的名称"
            })
    
    def _get_industry_names(self, error):
        """获取行业名称列表"""
        import akshare as ak
        import logging
        
        try:
            # 获取可用的行业名称列表
            industry_names_df = ak.stock_board_industry_name_em()
            if not industry_names_df.empty and '板块名称' in industry_names_df.columns:
                available_names = industry_names_df['板块名称'].tolist()[:20]  # 取前20个作为示例
                names_text = "、".join(available_names)
                
                yield self.create_text_message(f"行业名称错误：\n\n您输入的行业名称不存在或格式不正确。\n\n可用的行业名称示例（前20个）：\n{names_text}\n\n建议：\n1. 请从上述列表中选择正确的行业名称\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用更常见的行业名称")
                yield self.create_json_message({
                    "error": "invalid_industry_name",
                    "message": "行业名称错误",
                    "details": str(error),
                    "suggestion": "请使用正确的行业名称",
                    "available_names": available_names
                })
            else:
                # 如果无法获取行业名称列表，提供通用建议
                yield self.create_text_message(f"行业名称错误：\n\n{str(error)}\n\n建议：\n1. 请检查行业名称是否正确\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用常见的行业名称，如：电源设备、汽车服务、软件开发等")
                yield self.create_json_message({
                    "error": "invalid_industry_name",
                    "message": "行业名称错误",
                    "details": str(error),
                    "suggestion": "请使用正确的行业名称"
                })
        except Exception as e:
            logging.error(f"Error getting industry names: {e}")
            # 如果获取行业名称失败，提供通用建议
            yield self.create_text_message(f"行业名称错误：\n\n{str(error)}\n\n建议：\n1. 请检查行业名称是否正确\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用常见的行业名称，如：电源设备、汽车服务、软件开发等")
            yield self.create_json_message({
                "error": "invalid_industry_name",
                "message": "行业名称错误",
                "details": str(error),
                "suggestion": "请使用正确的行业名称"
            })
    
    def _get_concept_names(self, error):
        """获取概念名称列表"""
        import akshare as ak
        import logging
        
        try:
            # 获取可用的概念名称列表
            concept_names_df = ak.stock_board_concept_name_em()
            if not concept_names_df.empty and '板块名称' in concept_names_df.columns:
                available_names = concept_names_df['板块名称'].tolist()[:20]  # 取前20个作为示例
                names_text = "、".join(available_names)
                
                yield self.create_text_message(f"概念名称错误：\n\n您输入的概念名称不存在或格式不正确。\n\n可用的概念名称示例（前20个）：\n{names_text}\n\n建议：\n1. 请从上述列表中选择正确的概念名称\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用更常见的概念名称")
                yield self.create_json_message({
                    "error": "invalid_concept_name",
                    "message": "概念名称错误",
                    "details": str(error),
                    "suggestion": "请使用正确的概念名称",
                    "available_names": available_names
                })
            else:
                # 如果无法获取概念名称列表，提供通用建议
                yield self.create_text_message(f"概念名称错误：\n\n{str(error)}\n\n建议：\n1. 请检查概念名称是否正确\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用常见的概念名称，如：数据要素、人工智能、新能源等")
                yield self.create_json_message({
                    "error": "invalid_concept_name",
                    "message": "概念名称错误",
                    "details": str(error),
                    "suggestion": "请使用正确的概念名称"
                })
        except Exception as e:
            logging.error(f"Error getting concept names: {e}")
            # 如果获取概念名称失败，提供通用建议
            yield self.create_text_message(f"概念名称错误：\n\n{str(error)}\n\n建议：\n1. 请检查概念名称是否正确\n2. 确保名称完全匹配（区分大小写）\n3. 可以尝试使用常见的概念名称，如：数据要素、人工智能、新能源等")
            yield self.create_json_message({
                "error": "invalid_concept_name",
                "message": "概念名称错误",
                "details": str(error),
                "suggestion": "请使用正确的概念名称"
            })
    
    def _validate_market_symbol_match(self, symbol: str, market: str) -> bool:
        """
        验证市场参数与股票代码的匹配性
        
        Args:
            symbol: 股票代码
            market: 市场代码
            
        Returns:
            bool: 是否匹配
        """
        if not symbol or not market:
            return True  # 如果任一为空，跳过验证
            
        symbol = symbol.strip().upper()
        market = market.strip().lower()
        
        # 移除市场前缀（如SH、SZ等）
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('HK', '').replace('-', '').replace('.', '')
        
        # 上海证券交易所：600xxx, 601xxx, 603xxx, 688xxx, 689xxx
        if clean_symbol.startswith(('600', '601', '603', '688', '689')):
            return market == 'sh'
        # 深圳证券交易所：000xxx, 001xxx, 002xxx, 003xxx, 300xxx
        elif clean_symbol.startswith(('000', '001', '002', '003', '300')):
            return market == 'sz'
        # 北京证券交易所：430xxx, 830xxx, 870xxx
        elif clean_symbol.startswith(('430', '830', '870')):
            return market == 'bj'
        else:
            return True  # 无法识别的代码，跳过验证
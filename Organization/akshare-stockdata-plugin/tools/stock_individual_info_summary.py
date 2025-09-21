from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol


class StockIndividualInfoSummaryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockIndividualInfoSummaryTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
            if not symbol:
                yield self.create_text_message("请提供股票代码")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
            
            # 验证股票代码格式
            validation_result = None
            for result in validate_stock_symbol(symbol, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 按A股、港股、美股顺序排列
        interface_configs = {
            # A股相关接口
            "stock_individual_info_em": {
                "fn": ak.stock_individual_info_em,
                "description": "A股-个股-股票信息"
            },
            "stock_bid_ask_em": {
                "fn": ak.stock_bid_ask_em,
                "description": "A股-个股-买卖盘口"
            },
            "stock_zyjs_ths": {
                "fn": ak.stock_zyjs_ths,
                "description": "A股-个股-主营业务"
            },
            "stock_zygc_em": {
                "fn": ak.stock_zygc_em,
                "description": "A股-个股-主营构成"
            },
            "stock_news_em": {
                "fn": ak.stock_news_em,
                "description": "A股-个股-相关新闻资讯"
            },
            "stock_profile_cninfo": {
                "fn": ak.stock_profile_cninfo,
                "description": "巨潮资讯-个股-公司概况"
            },
            "stock_ipo_summary_cninfo": {
                "fn": ak.stock_ipo_summary_cninfo,
                "description": "巨潮资讯-个股-上市相关资讯"
            },
            "stock_fhps_detail_em": {
                "fn": ak.stock_fhps_detail_em,
                "description": "A股-个股-分红配股"
            },
            "stock_research_report_em": {
                "fn": ak.stock_research_report_em,
                "description": "A股-个股-研报列表"
            },
            "stock_balance_sheet_by_report_em": {
                "fn": ak.stock_balance_sheet_by_report_em,
                "description": "A股-个股-资产负债表"
            },
            "stock_financial_abstract": {
                "fn": ak.stock_financial_abstract,
                "description": "A股-个股-财务摘要"
            },
            # 港股相关接口
            "stock_hk_security_profile_em": {
                "fn": ak.stock_hk_security_profile_em,
                "description": "港股-个股-证券概况"
            },
            "stock_hk_company_profile_em": {
                "fn": ak.stock_hk_company_profile_em,
                "description": "港股-个股-公司概况"
            },
            "stock_hk_fhpx_detail_ths": {
                "fn": ak.stock_hk_fhpx_detail_ths,
                "description": "港股-个股-分红信息"
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 网络参数 - 统一处理逻辑
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数，对特定接口进行代码格式转换
            processed_symbol = self._process_symbol_format(symbol, interface)
            call_params = {"symbol": processed_symbol}
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制
            try:
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            except Exception as e:
                # 检查是否是SSL连接错误
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 个股数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他个股信息接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，个股信息获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    # 使用统一的错误处理机制
                    yield from handle_akshare_error(e, self, f"股票代码: {symbol}, 接口: {interface}", str(timeout))
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
                
        except Exception as e:
            import logging
            logging.error(f"StockIndividualInfoSummaryTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
    def _analyze_symbol_format(self, symbol: str, interface: str) -> str:
        """分析股票代码格式并提供针对性建议"""
        if not symbol:
            return "股票代码为空"
        
        # 接口与市场对应关系 - 按A股、港股、美股顺序排列
        interface_market_map = {
            # A股相关接口
            "stock_individual_info_em": "A股",
            "stock_bid_ask_em": "A股", 
            "stock_zyjs_ths": "A股",
            "stock_zygc_em": "A股",
            "stock_news_em": "A股",
            "stock_profile_cninfo": "A股",
            "stock_ipo_summary_cninfo": "A股",
            "stock_fhps_detail_em": "A股",
            "stock_research_report_em": "A股",
            "stock_balance_sheet_by_report_em": "A股",
            "stock_financial_abstract": "A股",
            # 港股相关接口
            "stock_hk_security_profile_em": "港股",
            "stock_hk_company_profile_em": "港股",
            "stock_hk_fhpx_detail_ths": "港股"
        }
        
        expected_market = interface_market_map.get(interface, "未知")
        
        # 分析股票代码格式
        symbol_upper = symbol.upper()
        
        # 检查是否是A股代码
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith(('60', '68')):
                detected_market = "A股(上交所)"
            elif symbol.startswith(('00', '30')):
                detected_market = "A股(深交所)"
            else:
                detected_market = "A股(未知交易所)"
        elif symbol_upper.startswith(('SH', 'SZ')):
            detected_market = "A股(带市场前缀)"
        # 检查是否是港股代码
        elif symbol.isdigit() and len(symbol) == 5:
            detected_market = "港股"
        elif symbol_upper.startswith('HK'):
            detected_market = "港股(带市场前缀)"
        # 检查是否是美股代码
        elif symbol_upper.isalpha() and len(symbol) <= 5:
            detected_market = "美股"
        else:
            detected_market = "未知格式"
        
        # 生成分析结果
        analysis = f"代码分析：\n- 输入代码：{symbol}\n- 检测到市场：{detected_market}\n- 接口期望市场：{expected_market}"
        
        if detected_market != expected_market:
            if expected_market == "A股":
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要A股代码，但您输入的是{detected_market}代码。\n建议使用：600519、000001、SH600519、SZ000001"
            elif expected_market == "港股":
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要港股代码，但您输入的是{detected_market}代码。\n建议使用：00700、03900、HK00700"
            else:
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要{expected_market}代码，但您输入的是{detected_market}代码。"
        else:
            analysis += f"\n\n✅ 代码格式匹配：{detected_market}代码适用于{expected_market}接口"
        
        return analysis
    
    def _process_symbol_format(self, symbol: str, interface: str) -> str:
        """处理股票代码格式，根据接口要求进行转换"""
        if not symbol:
            return symbol
        
        # 需要带市场前缀的接口
        prefix_required_interfaces = [
            "stock_zygc_em",  # 主营构成需要SH/SZ前缀
            "stock_balance_sheet_by_report_em"  # 资产负债表需要SH/SZ前缀
        ]
        
        # 港股接口需要特殊格式处理
        hk_interfaces = [
            "stock_hk_fhpx_detail_ths",  # 港股分红信息
            # 注意：stock_hk_security_profile_em 和 stock_hk_company_profile_em 需要保持原始格式
        ]
        
        # 处理港股接口的代码格式
        if interface in hk_interfaces:
            # 移除HK前缀（如果有）
            if symbol.upper().startswith('HK'):
                symbol = symbol[2:]
            
            # 港股代码格式转换：00700 -> 0700
            if symbol.isdigit() and len(symbol) == 5 and symbol.startswith('0'):
                return symbol[1:]  # 移除开头的0
        
        # 如果接口需要前缀且当前代码没有前缀
        if interface in prefix_required_interfaces and not any(symbol.upper().startswith(prefix) for prefix in ['SH', 'SZ', 'HK']):
            # 根据代码判断市场
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"SH{symbol}"
                elif symbol.startswith(('00', '30')):
                    return f"SZ{symbol}"
        
        return symbol
    

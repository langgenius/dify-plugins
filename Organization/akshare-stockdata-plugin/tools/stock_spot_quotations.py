from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, handle_akshare_error


class StockSpotQuotationsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockSpotQuotationsTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            logging.info(f"Interface: {interface}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 按A股、港股、美股顺序排列
        interface_configs = {
            # A股相关接口
            "stock_sh_a_spot_em": {
                "fn": ak.stock_sh_a_spot_em,
                "description": "沪A股-实时行情"
            },
            "stock_sz_a_spot_em": {
                "fn": ak.stock_sz_a_spot_em,
                "description": "深A股-实时行情"
            },
            "stock_bj_a_spot_em": {
                "fn": ak.stock_bj_a_spot_em,
                "description": "京A股-实时行情"
            },
            "stock_new_a_spot_em": {
                "fn": ak.stock_new_a_spot_em,
                "description": "新股-实时行情"
            },
            "stock_cy_a_spot_em": {
                "fn": ak.stock_cy_a_spot_em,
                "description": "创业板-实时行情"
            },
            "stock_kc_a_spot_em": {
                "fn": ak.stock_kc_a_spot_em,
                "description": "科创板-实时行情"
            },
            "stock_zh_ah_spot_em": {
                "fn": ak.stock_zh_ah_spot_em,
                "description": "沪深港通-AH股比价-实时行情"
            },
            "stock_zh_ab_comparison_em": {
                "fn": ak.stock_zh_ab_comparison_em,
                "description": "沪深京A股-全量AB股比价"
            },
            "stock_zh_a_new": {
                "fn": ak.stock_zh_a_new,
                "description": "沪深京A股-新股-实时行情"
            },
            "stock_zh_a_new_em": {
                "fn": ak.stock_zh_a_new_em,
                "description": "沪深个股-新股板块实时行情"
            },
            "stock_zh_a_stop_em": {
                "fn": ak.stock_zh_a_stop_em,
                "description": "沪深个股-两网及退市"
            },
            "stock_xgsr_ths": {
                "fn": ak.stock_xgsr_ths,
                "description": "沪深京A股-新股申购"
            },
            # 港股相关接口
            "stock_hk_spot_em": {
                "fn": ak.stock_hk_spot_em,
                "description": "港股-实时行情"
            },
            "stock_hk_main_board_spot_em": {
                "fn": ak.stock_hk_main_board_spot_em,
                "description": "港股主板-实时行情"
            },
            "stock_hk_famous_spot_em": {
                "fn": ak.stock_hk_famous_spot_em,
                "description": "港股市场-知名港股实时行情数据"
            },
            # 美股相关接口
            "stock_us_spot_em": {
                "fn": ak.stock_us_spot_em,
                "description": "美股-实时行情"
            },
            "stock_us_famous_spot_em": {
                "fn": ak.stock_us_famous_spot_em,
                "requires_symbol": True,
                "description": "美股-知名美股的实时行情数据"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 检查是否需要 symbol 参数
            symbol = tool_parameters.get("symbol", "")
            if config.get("requires_symbol", False) and not symbol:
                yield self.create_text_message(f"错误：'{config['description']}'接口需要 'symbol' 参数。请选择美股类别。")
                yield self.create_json_message({"error": "symbol_required", "message": f"{interface} requires 'symbol' parameter"})
                return
            
            # 网络参数 - 统一处理逻辑
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数
            call_params = {}
            if config.get("requires_symbol", False) and symbol:
                call_params["symbol"] = symbol
            
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
                # 检查是否是SSL连接错误（实时行情接口常见问题）
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 实时行情数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 如果问题持续，可以尝试其他实时行情接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，实时行情数据获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    # 使用统一的错误处理机制
                    yield from handle_akshare_error(e, self, f"接口: {interface}", str(timeout))
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
            logging.error(f"StockSpotQuotationsTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
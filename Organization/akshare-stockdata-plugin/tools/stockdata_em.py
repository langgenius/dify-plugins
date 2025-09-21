from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config, validate_interface_params, get_symbol_candidates
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class StockdataEmTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockdataEmTool received parameters: {tool_parameters}")
            
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
        
        # 获取接口配置
        config = get_interface_config(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 检查接口特定的参数要求
            if interface == "stock_gsrl_gsdt_em":
                if "symbol" in tool_parameters and "date" not in tool_parameters:
                    yield self.create_text_message("错误：'公司动态'接口需要 'date' 参数（交易日），而不是 'symbol' 参数。请提供日期格式如 '20240101'。")
                    yield self.create_json_message({"error": "parameter_mismatch", "message": "stock_gsrl_gsdt_em requires 'date' parameter, not 'symbol'"})
                    return
            
            # 验证和处理参数
            logging.info(f"About to call validate_interface_params with interface: {interface}")
            processed_params = validate_interface_params(interface, tool_parameters)
            logging.info(f"Processed params: {processed_params}")
            
            # 网络参数 - 统一处理逻辑
            retries = int(tool_parameters.get("retries", 3))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 特殊处理：对于网络不稳定的接口，增加重试次数
            if interface == "stock_us_spot_em":
                retries = max(retries, 5)  # 至少重试5次
                logging.info(f"Enhanced retries for {interface} - retries: {retries}")
            
            # 特殊处理：对于需要多候选格式的接口（如stock_bid_ask_em）
            if isinstance(processed_params, list):
                # 多候选格式，依次尝试
                result = None
                last_error = None
                
                for candidate in processed_params:
                    try:
                        call_params = {"symbol": candidate}
                        
                        result = safe_ak_call(
                            config["fn"],
                            retries=retries,
                            timeout=float(timeout) if config["supports_timeout"] and timeout is not None else None,
                            **call_params
                        )
                        if result is not None and not (hasattr(result, 'empty') and result.empty):
                            break
                    except Exception as e:
                        last_error = e
                        continue
                
                if result is None:
                    if last_error:
                        text, payload = build_error_payload(last_error)
                        yield self.create_text_message(text)
                        yield self.create_json_message(payload)
                    else:
                        yield self.create_text_message("未找到该代码的数据")
                        yield self.create_json_message({"error": "symbol not found"})
                    return
            else:
                # 普通调用
                call_params = dict(processed_params)
                logging.info(f"Call params: {call_params}")
                logging.info(f"Function: {config['fn']}")
                
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            
            # 处理结果
            if result is None:
                yield self.create_text_message("暂无数据")
                yield self.create_json_message({"data": []})
                return
            
            # 检查是否为空
            if hasattr(result, 'empty') and result.empty:
                yield self.create_text_message("暂无数据")
                yield self.create_json_message({"data": []})
                return
            
            # 输出处理
            if isinstance(result, pd.DataFrame):
                # DataFrame 输出为 Markdown 表格和 JSON records
                try:
                    text_output = result.to_markdown(index=True)
                except Exception:
                    text_output = result.to_string(index=True)
                
                yield self.create_text_message(text_output)
                yield self.create_json_message({"data": result.to_dict(orient="records")})
            else:
                # 其他类型直接输出
                text_output = str(result)
                yield self.create_text_message(text_output)
                yield self.create_json_message({"data": result})
                
        except Exception as e:
            import logging
            logging.error(f"StockdataEmTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

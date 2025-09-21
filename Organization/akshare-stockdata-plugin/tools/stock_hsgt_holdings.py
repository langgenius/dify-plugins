from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    process_other_output, 
    handle_empty_result, 
    validate_required_params, 
    handle_akshare_error, 
    validate_stock_symbol,
    validate_date_format,
    validate_date_range
)


class StockHSGTHoldingsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockHSGTHoldingsTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")  # 类别一（分时/历史数据类）
            symbol2 = tool_parameters.get("symbol2", "")  # 类别二（板块排行类）
            symbol4 = tool_parameters.get("symbol4", "")  # 股票代码
            market = tool_parameters.get("market", "")  # 市场一（个股排行类）
            indicator = tool_parameters.get("indicator", "")  # 指标一（板块排行类）
            indicator2 = tool_parameters.get("indicator2", "")  # 指标二（个股排行类）
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Symbol2: {symbol2}, Symbol4: {symbol4}, Market: {market}, Indicator: {indicator}, Indicator2: {indicator2}, Start: {start_date}, End: {end_date}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置
        interface_configs = {
            # 港股通成份股
            "stock_hk_ggt_components_em": {
                "fn": ak.stock_hk_ggt_components_em,
                "requires_symbol": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "港股通成份股-实时行情"
            },
            # 沪深港通分时数据 - 使用类别一（资金流向类）
            "stock_hsgt_fund_min_em": {
                "fn": ak.stock_hsgt_fund_min_em,
                "requires_symbol": True,
                "symbol_type": "fund_flow",  # 资金流向类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "沪深港通分时数据"
            },
            # 板块排行 - 使用类别二（板块排行类）
            "stock_hsgt_board_rank_em": {
                "fn": ak.stock_hsgt_board_rank_em,
                "requires_symbol": True,
                "symbol_type": "board_ranking",  # 板块排行类
                "requires_market": False,
                "requires_indicator": True,
                "indicator_type": "board_ranking",  # 板块排行类
                "requires_date_range": False,
                "description": "板块排行"
            },
            # （已移除）沪深港通持股-个股排行
            # 个股排行
            "stock_hsgt_hold_stock_em": {
                "fn": ak.stock_hsgt_hold_stock_em,
                "requires_symbol": False,
                "requires_market": True,
                "market_type": "stock_ranking",  # 个股排行类
                "requires_indicator": True,
                "indicator_type": "stock_ranking",  # 个股排行类
                "requires_date_range": False,
                "description": "个股排行"
            },
            # 港股通实时行情
            "stock_hsgt_sh_hk_spot_em": {
                "fn": ak.stock_hsgt_sh_hk_spot_em,
                "requires_symbol": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "沪深港通-港股通(沪>港)实时行情"
            },
            # 沪深港通历史数据 - 使用类别一（资金流向类）
            "stock_hsgt_hist_em": {
                "fn": ak.stock_hsgt_hist_em,
                "requires_symbol": True,
                "symbol_type": "fund_flow",  # 资金流向类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "沪深港通历史数据"
            },
            # 沪深港通持股-个股 - 使用类别三（个股类）
            "stock_hsgt_individual_em": {
                "fn": ak.stock_hsgt_individual_em,
                "requires_symbol": True,
                "symbol_type": "individual_stock",  # 个股类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "沪深港通持股-个股"
            },
            # 沪深港通持股-个股详情 - 使用类别三（个股类）
            # 注意：该接口当前数据源不可用，暂时禁用
            # "stock_hsgt_individual_detail_em": {
            #     "fn": ak.stock_hsgt_individual_detail_em,
            #     "requires_symbol": True,
            #     "symbol_type": "individual_stock",  # 个股类
            #     "requires_market": False,
            #     "requires_indicator": False,
            #     "requires_date_range": True,
            #     "description": "沪深港通持股-个股详情"
            # }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数
        if config.get("requires_symbol", False):
            # 根据接口类型确定使用哪个类别参数
            symbol_type = config.get("symbol_type", "")
            if symbol_type == "fund_flow" and not symbol:
                yield self.create_text_message("请提供类别一（资金流向类）参数")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
            elif symbol_type == "board_ranking" and not symbol2:
                yield self.create_text_message("请提供类别二（板块排行类）参数")
                yield self.create_json_message({"error": "symbol2 required", "received_params": tool_parameters})
                return
            elif symbol_type == "individual_stock" and not symbol4:
                yield self.create_text_message("请提供股票代码（如：600519、000001、00700 等）")
                yield self.create_json_message({"error": "symbol4 required", "received_params": tool_parameters})
                return
            elif not symbol_type and not symbol:
                yield self.create_text_message("请提供类别参数")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
            
        if config.get("requires_market", False):
            # 根据接口类型确定使用哪个市场参数
            market_type = config.get("market_type", "")
            if market_type == "stock_ranking" and not market:
                yield self.create_text_message("请提供市场一（个股排行类）参数")
                yield self.create_json_message({"error": "market required", "received_params": tool_parameters})
                return
            elif not market_type and not market:
                yield self.create_text_message("请选择市场")
                yield self.create_json_message({"error": "market required", "received_params": tool_parameters})
                return
            
        if config.get("requires_indicator", False):
            # 根据接口类型确定使用哪个指标参数
            indicator_type = config.get("indicator_type", "")
            if indicator_type == "board_ranking" and not indicator:
                yield self.create_text_message("请提供指标一（板块排行类）参数")
                yield self.create_json_message({"error": "indicator required", "received_params": tool_parameters})
                return
            elif indicator_type == "stock_ranking" and not indicator2:
                yield self.create_text_message("请提供指标二（个股排行类）参数")
                yield self.create_json_message({"error": "indicator2 required", "received_params": tool_parameters})
                return
            elif not indicator_type and not indicator:
                yield self.create_text_message("请选择指标")
                yield self.create_json_message({"error": "indicator required", "received_params": tool_parameters})
                return
        
        if config.get("requires_date_range", False):
            if not start_date:
                yield self.create_text_message("请提供开始日期")
                yield self.create_json_message({"error": "start_date required", "received_params": tool_parameters})
                return
            if not end_date:
                yield self.create_text_message("请提供结束日期")
                yield self.create_json_message({"error": "end_date required", "received_params": tool_parameters})
                return
        
        # 验证日期格式（如果需要）
        if config.get("requires_date_range", False) and start_date and end_date:
            validation_result = None
            for result in validate_date_format(start_date, "YYYYMMDD", self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
            
            validation_result = None
            for result in validate_date_format(end_date, "YYYYMMDD", self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
            
            validation_result = None
            for result in validate_date_range(start_date, end_date, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        
        # 验证股票代码格式（仅对个股相关接口）
        individual_interfaces = ["stock_hsgt_individual_em", "stock_hsgt_individual_detail_em"]
        if interface in individual_interfaces and symbol4:
            validation_result = None
            for result in validate_stock_symbol(symbol4, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        
        try:
            # 网络参数 - 统一处理逻辑
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")

            # （已移除）针对 stock_hsgt_hold_stock_em 的重试特例
            
            # 构建调用参数 - 根据接口要求动态构建
            call_params = {}
            
            # 根据接口要求添加参数
            if config.get("requires_symbol", False):
                # 根据接口类型确定使用哪个类别参数
                symbol_type = config.get("symbol_type", "")
                if symbol_type == "fund_flow":
                    if not symbol:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：类别一（分时/历史数据类）"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = symbol
                elif symbol_type == "board_ranking":
                    if not symbol2:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：类别二（板块排行类）"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = symbol2
                elif symbol_type == "individual_stock":
                    if not symbol4:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：股票代码"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    # 验证股票代码格式
                    validation_result = None
                    for result in validate_stock_symbol(symbol4, self):
                        if isinstance(result, bool):
                            validation_result = result
                        else:
                            yield result
                    if validation_result is False:
                        return
                    call_params["symbol"] = symbol4
                # 如果没有指定symbol_type，但接口需要symbol参数，则使用默认的symbol
                elif not symbol_type:
                    if not symbol:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：类别"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = symbol
            
            if config.get("requires_market", False):
                # 根据接口类型确定使用哪个市场参数
                market_type = config.get("market_type", "")
                if market_type == "stock_ranking":
                    if not market:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：市场一（个股排行类）"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["market"] = market
                elif not market_type and market:
                    call_params["market"] = market
            
            if config.get("requires_indicator", False):
                # 根据接口类型确定使用哪个指标参数
                indicator_type = config.get("indicator_type", "")
                if indicator_type == "board_ranking":
                    if not indicator:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：指标一（板块排行类）"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["indicator"] = indicator
                elif indicator_type == "stock_ranking":
                    if not indicator2:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：指标二（个股排行类）"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    
                    # 个股排行类指标映射
                    indicator_mapping = {
                        "今日": "今日排行",
                        "3日": "3日排行", 
                        "5日": "5日排行",
                        "10日": "10日排行",
                        "1月": "月排行",
                        "1季": "季排行",
                        "1年": "年排行"
                    }
                    
                    # 如果输入的是简化值，则映射到完整值
                    mapped_indicator = indicator_mapping.get(indicator2, indicator2)
                    call_params["indicator"] = mapped_indicator
                elif not indicator_type and indicator:
                    call_params["indicator"] = indicator
            
            if config.get("requires_date_range", False):
                if start_date:
                    call_params["start_date"] = start_date
                if end_date:
                    call_params["end_date"] = end_date
            
            # 记录最终传递给AKShare的参数，确保只传递需要的参数
            logging.info(f"Final call params for {interface}: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface requires: symbol={config.get('requires_symbol', False)}, market={config.get('requires_market', False)}, indicator={config.get('requires_indicator', False)}, date_range={config.get('requires_date_range', False)}")
            
            # 验证参数数量，确保只传递必要的参数
            expected_params = []
            if config.get("requires_symbol", False):
                expected_params.append("symbol")
            if config.get("requires_market", False):
                expected_params.append("market")
            if config.get("requires_indicator", False):
                expected_params.append("indicator")
            if config.get("requires_date_range", False):
                expected_params.extend(["start_date", "end_date"])
            
            unexpected_params = [k for k in call_params.keys() if k not in expected_params]
            if unexpected_params:
                logging.warning(f"Unexpected parameters passed to {interface}: {unexpected_params}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制
            try:
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            except Exception as e:
                # 检查是否是已知的AKShare接口问题或网络问题
                error_msg = str(e)
                lower_msg = error_msg.lower()
                # 网络相关错误统一提示（与其它工具保持一致关键词）
                if any(k in lower_msg for k in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                    yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {error_msg}")
                    yield self.create_json_message({
                        "error": "network_error",
                        "message": "网络连接中断",
                        "details": error_msg,
                        "suggestion": "请稍后重试或检查网络连接"
                    })
                    return
                if "'noneType' object is not subscriptable" in lower_msg:
                    # 友好提醒：强调检查参数取值是否正确（如股票代码无对应数据）
                    friendly_msg = (
                        "数据源返回为空，无法解析\n\n"
                        "可能原因：\n"
                        "1) 股票代码当前无沪深港通持股数据或代码不存在\n"
                        "2) 数据源暂时不可用或结构变更\n\n"
                        "请检查参数是否正确：\n"
                        "- 股票代码(symbol4) 示例：600519、000001、300750\n"
                        "- 可尝试更换股票代码或稍后重试"
                    )
                    yield self.create_text_message(friendly_msg)
                    yield self.create_json_message({
                        "error": "empty_result_or_invalid_parameter",
                        "message": "返回数据为空或参数无效",
                        "details": error_msg,
                        "suggestion": "请核对股票代码是否存在且有沪深港通持股数据，或稍后重试"
                    })
                    return
                # 其他错误
                yield from handle_akshare_error(e, self, f"接口: {interface}, 类别: {symbol}, 市场: {market}, 指标: {indicator}, 日期范围: {start_date}-{end_date}", str(timeout))
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
            logging.error(f"StockHSGTHoldingsTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

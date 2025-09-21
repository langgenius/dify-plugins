from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, validate_date_format, handle_akshare_error


class StockTechnicalAnalysisTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockTechnicalAnalysisTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            technical_indicator1 = tool_parameters.get("technical_indicator1", "")  # 创新高技术指标类型
            technical_indicator2 = tool_parameters.get("technical_indicator2", "")  # 创新低技术指标类型
            ma_type = tool_parameters.get("ma_type", "")  # 均线类型
            stock_code = tool_parameters.get("stock_code", "")  # 股票代码
            market_type = tool_parameters.get("market_type", "")  # 市场类型
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 120))
            
            logging.info(f"Interface: {interface}, Technical Indicator1: {technical_indicator1}, Technical Indicator2: {technical_indicator2}, MA Type: {ma_type}, Stock Code: {stock_code}, Market Type: {market_type}, Retries: {retries}, Timeout: {timeout}")
            
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
            # 技术指标类接口
            "stock_rank_cxg_ths": {
                "fn": ak.stock_rank_cxg_ths,
                "requires_technical_indicator1": True,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-创新高"
            },
            "stock_rank_cxd_ths": {
                "fn": ak.stock_rank_cxd_ths,
                "requires_technical_indicator2": True,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-创新低"
            },
            "stock_rank_lxsz_ths": {
                "fn": ak.stock_rank_lxsz_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-连续上涨"
            },
            "stock_rank_lxxd_ths": {
                "fn": ak.stock_rank_lxxd_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-连续下跌"
            },
            "stock_rank_cxfl_ths": {
                "fn": ak.stock_rank_cxfl_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-持续放量"
            },
            "stock_rank_cxsl_ths": {
                "fn": ak.stock_rank_cxsl_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-持续缩量"
            },
            "stock_rank_xstp_ths": {
                "fn": ak.stock_rank_xstp_ths,
                "requires_ma_type": True,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-向上突破"
            },
            "stock_rank_xxtp_ths": {
                "fn": ak.stock_rank_xxtp_ths,
                "requires_ma_type": True,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-向下突破"
            },
            "stock_rank_ljqs_ths": {
                "fn": ak.stock_rank_ljqs_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-量价齐升"
            },
            "stock_rank_ljqd_ths": {
                "fn": ak.stock_rank_ljqd_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-量价齐跌"
            },
            "stock_rank_xzjp_ths": {
                "fn": ak.stock_rank_xzjp_ths,
                "requires_technical_indicator": False,
                "timeout": 120,  # 设置为120秒（2分钟）
                "description": "同花顺-技术选股-险资举牌"
            },
            
            # ESG评级类接口
            # 注意：stock_esg_rate_sina 接口处理时间很长（约12分钟），但 Dify 工作流系统超时限制为600秒
            # 暂时禁用该接口，避免超时错误
            # "stock_esg_rate_sina": {
            #     "fn": ak.stock_esg_rate_sina,
            #     "requires_technical_indicator": False,
            #     "timeout": 1800,  # 设置为1800秒（30分钟），因为该接口处理时间很长（约12分钟）
            #     "description": "新浪财经-ESG评级-ESG评级数据"
            # },
            "stock_esg_msci_sina": {
                "fn": ak.stock_esg_msci_sina,
                "requires_technical_indicator": False,
                "timeout": 300,  # 设置为300秒（5分钟）
                "description": "新浪财经-ESG评级-MSCI"
            },
            "stock_esg_rft_sina": {
                "fn": ak.stock_esg_rft_sina,
                "requires_technical_indicator": False,
                "timeout": 300,  # 设置为300秒（5分钟）
                "description": "新浪财经-ESG评级-路孚特"
            },
            
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 参数验证
        try:
            if config.get("requires_technical_indicator1", False) and not technical_indicator1:
                yield self.create_text_message(f"接口 {config['description']} 需要创新高技术指标参数")
                yield self.create_json_message({"error": f"technical_indicator1 required for {interface}"})
                return
            if config.get("requires_technical_indicator2", False) and not technical_indicator2:
                yield self.create_text_message(f"接口 {config['description']} 需要创新低技术指标参数")
                yield self.create_json_message({"error": f"technical_indicator2 required for {interface}"})
                return
            if config.get("requires_ma_type", False) and not ma_type:
                yield self.create_text_message(f"接口 {config['description']} 需要均线类型参数")
                yield self.create_json_message({"error": f"ma_type required for {interface}"})
                return
            if config.get("requires_stock_code", False) and not stock_code:
                yield self.create_text_message(f"接口 {config['description']} 需要股票代码参数")
                yield self.create_json_message({"error": f"stock_code required for {interface}"})
                return
            if config.get("requires_market_type", False) and not market_type:
                yield self.create_text_message(f"接口 {config['description']} 需要市场类型参数")
                yield self.create_json_message({"error": f"market_type required for {interface}"})
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
            if config.get("requires_technical_indicator1", False) and technical_indicator1:
                call_params["symbol"] = technical_indicator1
            if config.get("requires_technical_indicator2", False) and technical_indicator2:
                call_params["symbol"] = technical_indicator2
            if config.get("requires_ma_type", False) and ma_type:
                call_params["symbol"] = ma_type
            if config.get("requires_stock_code", False) and stock_code:
                call_params["symbol"] = stock_code
            if config.get("requires_market_type", False) and market_type:
                call_params["symbol"] = market_type
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            logging.info(f"Final call params: {call_params}")
            logging.info(f"Using timeout: {interface_timeout}")
            
        except Exception as e:
            logging.error(f"Error in parameter building: {e}")
            yield self.create_text_message(f"参数构建错误: {e}")
            yield self.create_json_message({"error": f"parameter building error: {e}"})
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
                yield from handle_akshare_error(e, self, f"接口: {interface}", str(interface_timeout))
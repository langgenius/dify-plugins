from typing import Any, Callable, Tuple, List
import logging
import time
import requests
from requests import exceptions as req_exc
import threading
import subprocess
import json
import sys
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# 设置全局网络超时
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置默认超时
import socket
socket.setdefaulttimeout(1800)  # 30分钟超时，与主进程保持一致

from dify_plugin import ToolProvider


class AkshareStockdataProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # AKShare 接口无需 Token，提供方级别不做鉴权
        return


def classify_network_error(exc: Exception) -> Tuple[str, List[str]]:
    """Classify common network-related exceptions and provide actionable hints."""
    hints_base = [
        "升级 certifi（pip install -U certifi）",
        "设置 SSL_CERT_FILE 为本机 cacert.pem",
        "确认/移除系统或会话代理，或正确配置 HTTPS_PROXY",
        "放行域名 push2.eastmoney.com:443 与 82.push2.eastmoney.com:443",
        "适当增大 timeout 或稍后重试",
    ]
    
    hints_ssl = [
        "SSL握手失败，通常是网络不稳定或服务器问题",
        "尝试增加重试次数和超时时间",
        "检查网络连接是否稳定",
        "稍后重试，服务器可能暂时不可用",
        "如果问题持续，请联系技术支持",
    ]

    # 检查SSL相关错误
    error_msg = str(exc).lower()
    if (isinstance(exc, req_exc.SSLError) or 
        "ssl" in error_msg or 
        "eof" in error_msg or 
        "unexpected_eof" in error_msg or
        "certificate" in error_msg):
        return "SSL_ERROR", hints_ssl
    
    if isinstance(exc, (req_exc.ProxyError,)):
        return "PROXY_ERROR", hints_base
    if isinstance(exc, (req_exc.ConnectTimeout, req_exc.ReadTimeout, req_exc.Timeout)):
        return "TIMEOUT", hints_base
    if isinstance(exc, (req_exc.ConnectionError,)):
        return "CONNECTION_ERROR", hints_base
    if isinstance(exc, req_exc.HTTPError):
        return "HTTP_ERROR", hints_base
    return "NETWORK_ERROR", hints_base


# 接口超时配置 - 根据接口类型设置不同的默认超时时间
INTERFACE_TIMEOUT_CONFIG = {
    # 实时行情接口 - 数据量大，需要15分钟
    'realtime_market': {
        'interfaces': [
            'stock_zh_a_spot_em', 'stock_sh_a_spot_em', 'stock_sz_a_spot_em',
            'stock_bj_a_spot_em', 'stock_new_a_spot_em', 'stock_cy_a_spot_em',
            'stock_kc_a_spot_em', 'stock_hk_spot_em', 'stock_hk_main_board_spot_em',
            'stock_zh_ah_spot_em', 'stock_zh_ab_comparison_em',
            'stock_zh_a_new', 'stock_zh_a_new_em', 'stock_xgsr_ths',
            'stock_hsgt_sh_hk_spot_em'  # 沪深港通实时行情
        ],
        'timeout': 900.0  # 15分钟
    },
    # 财务数据接口 - 复杂查询，需要10分钟
    'financial_data': {
        'interfaces': [
            'stock_balance_sheet_by_report_em', 'stock_financial_abstract', 'stock_research_report_em'
        ],
        'timeout': 600.0  # 10分钟
    },
    # 财务分析接口 - 新增财务数据分析TOOL相关接口
    'financial_analysis': {
        'interfaces': [
            'stock_lrb_em', 'stock_xjll_em', 'stock_zcfz_em', 'stock_zcfz_bj_em',
            'stock_financial_debt_ths', 'stock_financial_benefit_ths', 'stock_financial_cash_ths',
            'stock_financial_abstract_ths', 'stock_financial_analysis_indicator'
        ],
        'timeout': 300.0  # 5分钟
    },
    # 数据密集型接口 - 大量历史数据，需要5分钟
    'data_intensive': {
        'interfaces': [
            'stock_gpzy_profile_em', 'stock_account_statistics_em', 'stock_comment_em',
            # （已移除）stock_hsgt_hold_stock_em
            'stock_hsgt_board_rank_em',  # 沪深港通板块排行
            'stock_hsgt_hist_em',  # 沪深港通历史数据
            'stock_hsgt_individual_em'  # 沪深港通个股详情
        ],
        'timeout': 300.0  # 5分钟
    },
    # 历史数据接口 - 中等数据量，需要5分钟
    'historical_data': {
        'interfaces': [
            'stock_hist_quotations',  # 所有历史行情相关接口
            'stock_hsgt_fund_min_em'  # 沪深港通分时数据
        ],
        'timeout': 300.0  # 5分钟
    },
    # 基础接口 - 数据量小，需要2分钟
    'basic': {
        'interfaces': [],  # 默认类型
        'timeout': 120.0  # 2分钟
    }
}

def get_interface_timeout(function_name: str, user_timeout: float | None = None) -> float:
    """根据接口类型获取合适的超时时间"""
    if user_timeout is not None:
        # 用户设置了超时，使用用户设置（最大30分钟）
        return min(float(user_timeout), 1800.0)
    
    # 根据接口名称匹配超时配置
    for config_type, config in INTERFACE_TIMEOUT_CONFIG.items():
        if config_type == 'basic':
            continue  # 基础类型最后处理
        
        for interface_pattern in config['interfaces']:
            if function_name == interface_pattern or function_name.startswith(interface_pattern):
                return config['timeout']
    
    # 默认使用基础接口的超时时间
    return INTERFACE_TIMEOUT_CONFIG['basic']['timeout']

def safe_ak_call(
    fn: Callable[..., Any],
    *,
    retries: int = 5,  # 增加默认重试次数
    backoff: float = 1.5,
    timeout: float | None = None,  # 改为None，让函数自动决定
    **kwargs: Any,
) -> Any:
    """
    Call AKShare API with exponential backoff retries in a separate process.
    - Uses subprocess to completely avoid gevent blocking issues
    - timeout parameter controls subprocess execution time, not AKShare interface timeout
    - Re-raise the last exception for the caller to handle.
    """
    attempt = 0
    last_exc: Exception | None = None
    
    # 获取函数名称
    function_name = fn.__name__
    
    # 准备调用参数 - timeout不再作为AKShare接口参数传递
    call_kwargs = dict(kwargs)
    # 注意：timeout参数现在仅用于子进程超时控制，不作为AKShare接口参数

    # 获取工作进程脚本路径
    worker_script = os.path.join(os.path.dirname(__file__), "akshare_worker.py")
    
    while attempt < max(1, retries):
        try:
            # 使用子进程避免gevent冲突
            # 尝试使用临时文件，如果失败则回退到命令行参数
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8', newline='') as f:
                    json.dump(call_kwargs, f, ensure_ascii=False, indent=None, separators=(',', ':'))
                    temp_file = f.name
                
                cmd = [sys.executable, worker_script, function_name, temp_file]
            except Exception as e:
                # 如果临时文件创建失败，回退到命令行参数方式
                logging.warning(f"Failed to create temp file: {e}, using command line args")
                cmd = [sys.executable, worker_script, function_name, json.dumps(call_kwargs, ensure_ascii=False)]
            
            # 设置子进程超时 - 根据接口类型自动选择超时时间
            actual_timeout = get_interface_timeout(function_name, timeout)
            logging.info(f"Using subprocess timeout: {actual_timeout}s for {function_name} (user_set: {timeout is not None})")
            
            # 执行子进程 - 使用UTF-8编码避免GBK编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            # 强制设置系统编码环境变量
            env['LANG'] = 'en_US.UTF-8'
            env['LC_ALL'] = 'en_US.UTF-8'
            
            # 在Windows上额外设置编码相关环境变量
            if os.name == 'nt':  # Windows
                env['PYTHONLEGACYWINDOWSSTDIO'] = '1'
                env['PYTHONIOENCODING'] = 'utf-8:replace'
            
            # 使用二进制模式避免gevent编码问题
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,  # 使用二进制模式
                timeout=actual_timeout,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=env
            )
            
            # 手动解码输出，处理编码问题
            try:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    stdout_text = result.stdout.decode('gbk', errors='replace')
                except UnicodeDecodeError:
                    stdout_text = result.stdout.decode('latin1', errors='replace')
            
            try:
                stderr_text = result.stderr.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                try:
                    stderr_text = result.stderr.decode('gbk', errors='replace')
                except UnicodeDecodeError:
                    stderr_text = result.stderr.decode('latin1', errors='replace')
            
            # 创建类似subprocess.run结果的命名元组
            class SubprocessResult:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            result = SubprocessResult(result.returncode, stdout_text, stderr_text)
            
            # 记录子进程的stderr输出用于调试
            if result.stderr:
                logging.warning(f"Subprocess stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise RuntimeError(f"Subprocess failed with return code {result.returncode}: {result.stderr}")
            
            # 解析结果
            try:
                result_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse subprocess output: {e}")
            
            if not result_data.get("success", False):
                error_msg = result_data.get("error", "Unknown error")
                raise RuntimeError(f"AKShare call failed: {error_msg}")
            
            # 重建DataFrame
            if result_data.get("type") == "dataframe":
                df = pd.DataFrame(result_data["data"])
                return df
            else:
                return result_data.get("data", "")
                
        except TypeError as e:
            # Unexpected keyword 'timeout': retry without timeout in subsequent attempts
            if "unexpected keyword argument 'timeout'" in str(e) or "got an unexpected keyword argument 'timeout'" in str(e):
                logging.debug("safe_ak_call: removing unsupported 'timeout' argument and retrying once")
                call_kwargs.pop("timeout", None)
                last_exc = e
            else:
                last_exc = e
        except subprocess.TimeoutExpired as e:
            last_exc = e
            logging.warning("AKShare call timeout (attempt %s/%s): %s", attempt + 1, retries, e)
            # 对于慢接口，提供更友好的错误信息
            if function_name in ['stock_balance_sheet_by_report_em', 'stock_financial_abstract', 'stock_research_report_em']:
                logging.info(f"Slow interface {function_name} timed out after {actual_timeout}s, this is normal for financial data interfaces")
            elif function_name in ['stock_zh_a_spot_em', 'stock_sh_a_spot_em', 'stock_sz_a_spot_em', 
                                 'stock_bj_a_spot_em', 'stock_new_a_spot_em', 'stock_cy_a_spot_em', 
                                 'stock_kc_a_spot_em', 'stock_hk_spot_em', 'stock_hk_main_board_spot_em',
                                 'stock_zh_ah_spot_em', 'stock_zh_ab_comparison_em',
                                 'stock_zh_a_new', 'stock_zh_a_new_em', 'stock_xgsr_ths']:
                logging.info(f"Real-time market data interface {function_name} timed out after {actual_timeout}s, this is normal for large market data requests")
            
            # 设置超时错误的重试等待时间
            sleep_s = min(8.0, backoff ** attempt)
        except Exception as e:  # network or other
            last_exc = e
            code, _ = classify_network_error(e)
            logging.warning("AKShare call failed (attempt %s/%s, code=%s): %s", attempt + 1, retries, code, e)
            
            # 对于SSL错误，增加更长的等待时间
            if isinstance(e, (req_exc.SSLError,)) or "SSL" in str(e) or "EOF" in str(e):
                logging.info("SSL error detected, using extended backoff")
                sleep_s = min(15.0, backoff ** attempt * 2)  # SSL错误使用更长的等待时间
            else:
                sleep_s = min(8.0, backoff ** attempt)
        
        attempt += 1
        if attempt < retries:
            time.sleep(sleep_s)
    
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("safe_ak_call: unknown error")


def build_error_payload(exc: Exception) -> tuple[str, dict[str, Any]]:
    code, hints = classify_network_error(exc)
    message = str(exc)
    text = f"网络错误({code}): {message}\n建议: " + "; ".join(hints)
    return text, {"error_code": code, "message": message, "hints": hints}


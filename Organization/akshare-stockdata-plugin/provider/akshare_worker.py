#!/usr/bin/env python3
"""
AKShare工作进程 - 在独立进程中执行AKShare调用，避免gevent冲突
"""
import sys
import json
import os
import traceback

# 设置环境变量强制使用UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
# 在Windows上设置额外的编码环境变量
if os.name == 'nt':  # Windows
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['LC_ALL'] = 'en_US.UTF-8'

# 解决SSL问题 - 必须在导入akshare之前设置
import ssl
import urllib3
import requests
import socket
import os

# 设置环境变量
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# 设置socket超时
socket.setdefaulttimeout(1800)  # 30分钟超时，与主进程保持一致

# 创建更宽松的SSL上下文 - 针对东方财富网等金融网站优化
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')

# 添加更多SSL配置以处理EOF错误
try:
    ssl_context.options |= ssl.OP_LEGACY_SERVER_CONNECT
    ssl_context.options |= ssl.OP_NO_SSLv2
    ssl_context.options |= ssl.OP_NO_SSLv3
    # 移除已弃用的TLS版本选项，使用minimum_version和maximum_version代替
    # ssl_context.options |= ssl.OP_NO_TLSv1
    # ssl_context.options |= ssl.OP_NO_TLSv1_1
    
    # 设置SSL协议版本
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
    
    # 禁用SSL会话缓存
    ssl_context.options |= ssl.OP_NO_TICKET
    
    # 添加更多选项来处理EOF错误
    ssl_context.options |= ssl.OP_SINGLE_DH_USE
    ssl_context.options |= ssl.OP_SINGLE_ECDH_USE
    
    # 设置更宽松的SSL选项
    ssl_context.options |= ssl.OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION
    
except AttributeError:
    # 某些SSL选项可能不可用，忽略错误
    pass

# 设置默认SSL上下文
ssl._create_default_https_context = lambda: ssl_context

# 禁用urllib3的SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置requests的SSL配置
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 设置urllib3的SSL配置
urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT@SECLEVEL=1'

# 创建自定义的urllib3 SSL上下文
import urllib3.util.ssl_
urllib3.util.ssl_.create_urllib3_context = lambda: ssl_context

# 设置urllib3的连接池配置
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT@SECLEVEL=1'

# 强制urllib3使用我们的SSL上下文
import urllib3.poolmanager
original_poolmanager_init = urllib3.poolmanager.PoolManager.__init__

def patched_poolmanager_init(self, *args, **kwargs):
    kwargs['ssl_context'] = ssl_context
    # 添加连接池配置以处理EOF错误
    kwargs.setdefault('retries', urllib3.Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=['GET', 'POST']
    ))
    kwargs.setdefault('timeout', urllib3.Timeout(connect=30, read=1800))
    return original_poolmanager_init(self, *args, **kwargs)

urllib3.poolmanager.PoolManager.__init__ = patched_poolmanager_init

# 设置requests的默认超时
requests.adapters.DEFAULT_TIMEOUT = 1800  # 30分钟超时

# 强制设置requests的超时配置
import requests.adapters
requests.adapters.DEFAULT_TIMEOUT = 1800  # 30分钟超时

# 设置urllib3的连接池超时
urllib3.util.timeout.DEFAULT_TIMEOUT = 1800  # 30分钟超时

# 强制设置socket默认超时 - 关键配置！
socket.setdefaulttimeout(1800)  # 30分钟超时，与主进程保持一致

# 强制设置requests的默认超时 - 通过monkey patching
def patch_requests_timeout():
    """强制设置requests的超时配置"""
    import requests
    import requests.adapters
    import urllib3
    import requests.sessions
    import akshare.utils.func
    
    # 设置默认超时
    requests.adapters.DEFAULT_TIMEOUT = 1800  # 30分钟超时
    
    # 重写requests.Session的request方法
    original_request = requests.Session.request
    
    def patched_request(self, method, url, **kwargs):
        # 强制设置超时 - 使用更细粒度的超时控制
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (30, 1800)  # (连接超时, 读取超时)
        elif isinstance(kwargs['timeout'], (int, float)):
            # 如果只设置了单个超时值，转换为元组
            kwargs['timeout'] = (30, min(float(kwargs['timeout']), 1800))
        elif isinstance(kwargs['timeout'], tuple) and len(kwargs['timeout']) == 2:
            # 如果已经是元组，确保连接超时不超过30秒
            connect_timeout, read_timeout = kwargs['timeout']
            kwargs['timeout'] = (min(connect_timeout, 30), min(read_timeout, 1800))
        
        # 强制设置SSL配置
        kwargs['verify'] = False
        
        # 注意：requests的Session.request方法不支持retries参数
        # 重试逻辑由urllib3的连接池处理
            
        return original_request(self, method, url, **kwargs)
    
    requests.Session.request = patched_request
    
    # 重写requests.get, post等方法
    original_get = requests.get
    original_post = requests.post
    
    def patched_get(url, **kwargs):
        # 强制设置超时 - 使用更细粒度的超时控制
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (30, 1800)  # (连接超时, 读取超时)
        elif isinstance(kwargs['timeout'], (int, float)):
            kwargs['timeout'] = (30, min(float(kwargs['timeout']), 1800))
        
        # 强制设置SSL配置
        kwargs['verify'] = False
            
        return original_get(url, **kwargs)
    
    def patched_post(url, **kwargs):
        # 强制设置超时 - 使用更细粒度的超时控制
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (30, 1800)  # (连接超时, 读取超时)
        elif isinstance(kwargs['timeout'], (int, float)):
            kwargs['timeout'] = (30, min(float(kwargs['timeout']), 1800))
        
        # 强制设置SSL配置
        kwargs['verify'] = False
            
        return original_post(url, **kwargs)
    
    requests.get = patched_get
    requests.post = patched_post
    
    # 重写akshare.utils.func.fetch_paginated_data函数
    def patched_fetch_paginated_data(url, params=None, timeout=1800, **kwargs):
        """重写fetch_paginated_data函数，使用更长的超时时间"""
        if params is None:
            params = {}
        
        # 使用patched的requests.get，确保超时设置正确
        r = patched_get(url, params=params, timeout=timeout, **kwargs)
        return r
    
    # 应用fetch_paginated_data patch
    akshare.utils.func.fetch_paginated_data = patched_fetch_paginated_data

# 应用超时补丁
patch_requests_timeout()

# 现在导入akshare
import akshare as ak

# 接口超时配置 - 与主进程保持一致
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

def get_interface_timeout_for_worker(function_name: str) -> float:
    """根据接口类型获取合适的超时时间（工作进程版本）"""
    # 根据接口名称匹配超时配置
    for config_type, config in INTERFACE_TIMEOUT_CONFIG.items():
        if config_type == 'basic':
            continue  # 基础类型最后处理
        
        for interface_pattern in config['interfaces']:
            if function_name == interface_pattern or function_name.startswith(interface_pattern):
                return config['timeout']
    
    # 默认使用基础接口的超时时间
    return INTERFACE_TIMEOUT_CONFIG['basic']['timeout']
import pandas as pd

def call_akshare_function(function_name, **kwargs):
    """调用指定的AKShare函数"""
    try:
        # 获取函数对象
        if hasattr(ak, function_name):
            func = getattr(ak, function_name)
        else:
            raise ValueError(f"Function {function_name} not found in akshare")
        
        # 调用函数
        result = func(**kwargs)
        
        # 处理结果
        if isinstance(result, pd.DataFrame):
            # 将DataFrame转换为JSON可序列化的格式
            # 处理日期和其他不可序列化的类型
            df_clean = result.copy()
            for col in df_clean.columns:
                # 将所有列转换为字符串，处理NaT、NaN等特殊值
                df_clean[col] = df_clean[col].astype(str)
                # 将NaN、NaT等特殊值替换为空字符串
                df_clean[col] = df_clean[col].replace(['nan', 'NaT', 'None'], '')
            
            return {
                "success": True,
                "type": "dataframe",
                "data": df_clean.to_dict('records'),
                "columns": list(result.columns),
                "shape": result.shape
            }
        else:
            # 其他类型的结果
            return {
                "success": True,
                "type": "other",
                "data": str(result)
            }
            
    except Exception as e:
        error_info = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        # 同时输出到stderr用于调试
        print(f"ERROR in call_akshare_function: {error_info}", file=sys.stderr)
        return error_info

def main():
    """主函数 - 从命令行参数读取调用信息"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "No function name provided"
        }))
        sys.exit(1)
    
    # 添加调试信息
    # 调试信息（仅在调试模式下输出）
    if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes'):
        print(f"DEBUG: Received {len(sys.argv)} arguments: {sys.argv}", file=sys.stderr)
    
    try:
        # 解析输入
        function_name = sys.argv[1]
        
        # 解析JSON参数
        if len(sys.argv) > 2:
            try:
                # 检查第二个参数是否是文件路径
                if os.path.exists(sys.argv[2]):
                    # 从文件读取JSON参数
                    with open(sys.argv[2], 'r', encoding='utf-8', newline='') as f:
                        kwargs = json.load(f)
                    # 删除临时文件
                    try:
                        os.unlink(sys.argv[2])
                    except:
                        pass
                else:
                    # 直接从命令行参数解析JSON
                    kwargs = json.loads(sys.argv[2])
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "success": False,
                    "error": f"JSON decode error: {e}",
                    "error_type": "JSONDecodeError",
                    "input": sys.argv[2] if len(sys.argv) > 2 else "None"
                }))
                sys.exit(1)
            except Exception as e:
                print(json.dumps({
                    "success": False,
                    "error": f"Parameter parsing error: {e}",
                    "error_type": type(e).__name__
                }))
                sys.exit(1)
        else:
            kwargs = {}
        
        # 调用函数
        result = call_akshare_function(function_name, **kwargs)
        
        # 输出结果 - 处理编码问题
        try:
            # 尝试使用UTF-8输出
            output = json.dumps(result, ensure_ascii=False)
            print(output)
        except UnicodeEncodeError:
            # 如果UTF-8输出失败，使用ASCII安全模式
            output = json.dumps(result, ensure_ascii=True)
            print(output)
        
    except Exception as e:
        error_info = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        # 处理错误输出的编码问题
        try:
            print(json.dumps(error_info, ensure_ascii=False))
        except UnicodeEncodeError:
            print(json.dumps(error_info, ensure_ascii=True))
        
        try:
            print(f"ERROR in main: {error_info}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"ERROR in main: {error_info}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

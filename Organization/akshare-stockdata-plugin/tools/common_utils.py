"""
公共工具函数，用于避免代码重复
"""
import logging
import numpy as np
import pandas as pd
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage


def clean_nan_values(obj: Any) -> Any:
    """
    递归清理对象中的NaN值，将NaN转换为None
    
    Args:
        obj: 需要清理的对象（dict, list, 或其他类型）
        
    Returns:
        清理后的对象
    """
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, tuple):
        # 处理元组，确保所有元素都被清理
        return tuple(clean_nan_values(item) for item in obj)
    elif isinstance(obj, float):
        if np.isnan(obj):
            return None
        # 检查是否为无穷大
        elif np.isinf(obj):
            return None
        # 检查是否为整数形式的浮点数，如果是则转换为整数
        elif obj.is_integer():
            return int(obj)
        else:
            return obj
    elif isinstance(obj, (np.integer, np.floating)):
        # 处理numpy数值类型
        try:
            if np.isnan(obj):
                return None
            elif np.isinf(obj):
                return None
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating) and obj.is_integer():
                return int(obj)
            else:
                return float(obj)
        except (ValueError, TypeError, OverflowError):
            return str(obj)
    elif hasattr(obj, 'dtype') and hasattr(obj, 'item'):
        # 处理numpy标量
        try:
            if np.isnan(obj):
                return None
            elif np.isinf(obj):
                return None
            elif np.issubdtype(obj.dtype, np.integer):
                return int(obj)
            elif np.issubdtype(obj.dtype, np.floating):
                if obj.is_integer():
                    return int(obj)
                else:
                    return float(obj)
            else:
                return obj.item()
        except (ValueError, TypeError):
            return str(obj)
    else:
        return obj


def process_dataframe_output(result: pd.DataFrame, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    处理DataFrame输出，生成TEXT和JSON消息
    JSON保持AKShare原始数据不变，TEXT使用Markdown格式
    
    Args:
        result: pandas DataFrame
        tool_instance: 工具实例，用于调用create_text_message和create_json_message
        
    Yields:
        ToolInvokeMessage: TEXT和JSON消息
    """
    # 对于键值对格式的数据（如买卖盘口），使用Markdown表格格式
    if len(result.columns) == 2 and 'item' in result.columns and 'value' in result.columns:
        text_output = "## 股票实时数据\n\n"
        text_output += "| 项目 | 数值 |\n"
        text_output += "|------|------|\n"
        for _, row in result.iterrows():
            text_output += f"| {row['item']} | {row['value']} |\n"
    else:
        # 普通表格格式，TEXT输出标准Markdown表格格式，符合Dify工作流要求
        try:
            # 检查DataFrame是否为空
            if result.empty:
                text_output = "暂无数据"
            else:
                # 使用pandas的to_markdown方法生成标准Markdown表格
                text_output = result.to_markdown(index=True, tablefmt='pipe')
        except Exception as e:
            logging.warning(f"to_markdown failed: {e}, using manual markdown generation")
            try:
                # 如果to_markdown失败，手动构建Markdown表格
                if result.empty:
                    text_output = "暂无数据"
                else:
                    # 获取列名
                    columns = result.columns.tolist()
                    
                    # 构建表头
                    text_output = "| " + " | ".join(columns) + " |\n"
                    text_output += "| " + " | ".join(["---"] * len(columns)) + " |\n"
                    
                    # 构建数据行
                    for idx, row in result.iterrows():
                        row_data = []
                        for col in columns:
                            value = row[col]
                            # 处理NaN值
                            if pd.isna(value):
                                value = ""
                            else:
                                value = str(value)
                            row_data.append(value)
                        text_output += "| " + " | ".join(row_data) + " |\n"
                    
            except Exception as e2:
                logging.warning(f"Manual markdown generation failed: {e2}, using simple format")
                # 如果都失败，使用简单的格式
                text_output = str(result)
    
    yield tool_instance.create_text_message(text_output)
    
    # 处理JSON序列化，保持原始数据完整性
    try:
        # 重置索引以避免浮点数索引问题
        df_reset = result.reset_index(drop=True)
        
        # 确保所有列的数据类型都是JSON可序列化的，但保持原始数据
        df_clean = df_reset.copy()
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                # 对于对象类型，转换为字符串并处理特殊值
                df_clean[col] = df_clean[col].astype(str)
                # 替换常见的非JSON值
                df_clean[col] = df_clean[col].replace(['nan', 'NaT', 'None', 'null'], '')
            elif np.issubdtype(df_clean[col].dtype, np.integer):
                # 对于整数类型，确保是Python整数
                df_clean[col] = df_clean[col].astype('int64')
            elif np.issubdtype(df_clean[col].dtype, np.floating):
                # 对于浮点数类型，处理NaN值
                df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
                # 将NaN替换为空字符串
                df_clean[col] = df_clean[col].fillna('')
        
        # 先将DataFrame转换为字典，然后手动处理NaN值
        json_data = df_clean.to_dict(orient="records")
        json_data = clean_nan_values(json_data)
        
        # 构建输出数据
        output_data = {"data": json_data}
        
        # 确保最终的JSON数据是有效的
        import json
        try:
            # 测试JSON序列化
            json_str = json.dumps(output_data, ensure_ascii=False)
            # 如果成功，创建JSON消息，保持原始数据完整性
            yield tool_instance.create_json_message(output_data)
        except (TypeError, ValueError) as json_error:
            logging.warning(f"JSON serialization failed: {json_error}")
            # 如果JSON序列化失败，使用更安全的方式
            safe_data = []
            for record in json_data:
                safe_record = {}
                for key, value in record.items():
                    try:
                        # 测试每个值是否可以JSON序列化
                        json.dumps(value)
                        safe_record[key] = value
                    except (TypeError, ValueError):
                        # 如果不能序列化，转换为字符串
                        safe_record[key] = str(value) if value is not None else ""
                safe_data.append(safe_record)
            
            safe_output = {"data": safe_data}
            yield tool_instance.create_json_message(safe_output)
    except Exception as e:
        logging.warning(f"Failed to serialize DataFrame to JSON: {e}")
        # 如果还是失败，尝试更简单的方式
        try:
            # 将所有数据转换为字符串，然后替换NaN
            df_str = result.astype(str).replace('nan', 'null').replace('NaN', 'null').replace('inf', 'null').replace('-inf', 'null')
            df_reset = df_str.reset_index(drop=True)
            json_data = df_reset.to_dict(orient="records")
            
            output_data = {"data": json_data}
            yield tool_instance.create_json_message(output_data)
        except Exception as e2:
            logging.warning(f"Failed to serialize DataFrame to JSON (fallback): {e2}")
            # 最后的降级方案：只返回列名和数据类型信息
            try:
                fallback_data = {
                    "columns": result.columns.tolist(),
                    "shape": [int(x) for x in result.shape],  # 确保shape中的元素是Python整数
                    "dtypes": result.dtypes.astype(str).to_dict(),
                    "message": "数据序列化失败，请查看TEXT输出获取详细信息"
                }
                
                output_data = {"data": [fallback_data]}
                yield tool_instance.create_json_message(output_data)
            except Exception as e3:
                logging.warning(f"Failed to create fallback JSON: {e3}")
                output_data = {"data": []}
                yield tool_instance.create_json_message(output_data)


def process_other_output(result: Any, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    处理非DataFrame输出，生成TEXT和JSON消息
    
    Args:
        result: 非DataFrame结果
        tool_instance: 工具实例，用于调用create_text_message和create_json_message
        
    Yields:
        ToolInvokeMessage: TEXT和JSON消息
    """
    text_output = str(result)
    yield tool_instance.create_text_message(text_output)
    
    # 清理结果中的NaN值和其他不可序列化的值
    try:
        cleaned_result = clean_nan_values(result)
        yield tool_instance.create_json_message({"data": cleaned_result})
    except Exception as e:
        logging.warning(f"Failed to serialize non-DataFrame result to JSON: {e}")
        # 如果清理失败，尝试转换为字符串
        try:
            yield tool_instance.create_json_message({"data": str(result)})
        except Exception as e2:
            logging.warning(f"Failed to serialize result as string: {e2}")
            yield tool_instance.create_json_message({"data": "数据序列化失败"})


def handle_empty_result(tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    处理空结果，生成TEXT和JSON消息
    
    Args:
        tool_instance: 工具实例，用于调用create_text_message和create_json_message
        
    Yields:
        ToolInvokeMessage: TEXT和JSON消息
    """
    yield tool_instance.create_text_message("暂无数据")
    yield tool_instance.create_json_message({"data": []})


def validate_required_params(tool_parameters: dict[str, Any], required_params: list[str], tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证必需参数
    
    Args:
        tool_parameters: 工具参数
        required_params: 必需参数列表
        tool_instance: 工具实例
        
    Yields:
        ToolInvokeMessage: 错误消息（如果有缺失参数）
        
    Returns:
        bool: 是否验证通过
    """
    missing_params = []
    for param in required_params:
        if not tool_parameters.get(param):
            missing_params.append(param)
    
    if missing_params:
        error_msg = f"缺少必需参数: {', '.join(missing_params)}"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "missing_required_params", "missing": missing_params})
        return False
    
    return True


def validate_date_format(date: str, expected_format: str, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证日期格式
    
    Args:
        date: 日期字符串
        expected_format: 期望格式 ("YYYYMMDD" 或 "YYYYMM")
        tool_instance: 工具实例
        
    Yields:
        ToolInvokeMessage: 错误消息（如果格式不正确）
        
    Returns:
        bool: 是否验证通过
    """
    if expected_format == "YYYYMMDD" and len(date) != 8:
        error_msg = f"日期格式不正确。需要YYYYMMDD格式的日期，如'20240101'。"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_date_format", "message": "Date format should be YYYYMMDD"})
        return False
    elif expected_format == "YYYYMM" and len(date) != 6:
        error_msg = f"日期格式不正确。需要YYYYMM格式的日期，如'202412'。"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_date_format", "message": "Date format should be YYYYMM"})
        return False
    
    # 验证日期是否为纯数字
    if not date.isdigit():
        error_msg = f"日期格式不正确。日期必须为纯数字，如'20240101'。"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_date_format", "message": "Date must be numeric"})
        return False
    
    # 验证日期范围（基本合理性检查）
    if expected_format == "YYYYMMDD":
        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:8])
        if year < 2000 or year > 2030:
            error_msg = f"日期年份超出合理范围。年份应在2000-2030之间。"
            yield tool_instance.create_text_message(error_msg)
            yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Year out of range"})
            return False
        if month < 1 or month > 12:
            error_msg = f"日期月份超出合理范围。月份应在01-12之间。"
            yield tool_instance.create_text_message(error_msg)
            yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Month out of range"})
            return False
        if day < 1 or day > 31:
            error_msg = f"日期天数超出合理范围。天数应在01-31之间。"
            yield tool_instance.create_text_message(error_msg)
            yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Day out of range"})
            return False
    elif expected_format == "YYYYMM":
        year = int(date[:4])
        month = int(date[4:6])
        if year < 2000 or year > 2030:
            error_msg = f"日期年份超出合理范围。年份应在2000-2030之间。"
            yield tool_instance.create_text_message(error_msg)
            yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Year out of range"})
            return False
        if month < 1 or month > 12:
            error_msg = f"日期月份超出合理范围。月份应在01-12之间。"
            yield tool_instance.create_text_message(error_msg)
            yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Month out of range"})
            return False
    
    return True


def validate_stock_symbol(symbol: str, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证股票代码格式
    
    Args:
        symbol: 股票代码
        tool_instance: 工具实例
        
    Yields:
        ToolInvokeMessage: 错误消息（如果格式不正确）或验证结果
    """
    if not symbol or not symbol.strip():
        error_msg = "股票代码不能为空。"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "empty_symbol", "message": "Stock symbol cannot be empty"})
        yield False
        return
    
    symbol = symbol.strip().upper()
    
    # 检查是否包含非法字符
    if not symbol.replace('SH', '').replace('SZ', '').replace('HK', '').replace('-', '').replace('.', '').isalnum():
        error_msg = f"股票代码包含非法字符。支持的格式：\n- A股：600519、000001、SH600519、SZ000001\n- 港股：00700、03900、HK00700（系统会自动转换为0700、3900格式）\n- 美股：AAPL、MSFT"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_symbol_format", "message": "Stock symbol contains invalid characters"})
        yield False
        return
    
    # 检查长度是否合理
    if len(symbol) < 2 or len(symbol) > 10:
        error_msg = f"股票代码长度不合理。支持的格式：\n- A股：600519、000001、SH600519、SZ000001\n- 港股：00700、03900、HK00700（系统会自动转换为0700、3900格式）\n- 美股：AAPL、MSFT"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_symbol_length", "message": "Stock symbol length is invalid"})
        yield False
        return
    
    yield True


def handle_akshare_error(error: Exception, tool_instance, context: str = "", timeout_value: str = None) -> Generator[ToolInvokeMessage, None, None]:
    """
    统一处理AKShare接口错误
    
    Args:
        error: 异常对象
        tool_instance: 工具实例
        context: 错误上下文信息
        
    Yields:
        ToolInvokeMessage: 错误消息
    """
    error_msg = str(error)
    
    # 1. 数据结构不匹配错误（AKShare库问题）
    if "Length mismatch" in error_msg and "Expected axis has" in error_msg and "new values have" in error_msg:
        yield tool_instance.create_text_message(f"数据源结构不匹配错误：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 数据源更新了数据结构，但AKShare库尚未适配\n2. 请求的数据格式与预期不符\n3. 数据源暂时不可用\n\n建议：\n1. 检查参数格式是否正确\n2. 稍后重试\n3. 检查AKShare库是否为最新版本")
        yield tool_instance.create_json_message({
            "error": "data_structure_mismatch",
            "message": "数据源结构不匹配，可能是数据源更新或参数问题",
            "details": error_msg,
            "suggestion": "检查参数格式或稍后重试"
        })
        return
    
    # 2. 网络相关错误
    elif any(keyword in error_msg.lower() for keyword in ["timeout", "connection", "network", "ssl", "proxy"]):
        # 构建超时错误信息
        timeout_info = ""
        if timeout_value:
            timeout_info = f"\n\n当前超时设置: {timeout_value}秒\n如果仍然超时，建议将超时时间设置为更大的值（如1200秒或1800秒）"
        
        yield tool_instance.create_text_message(f"网络连接错误：\n\n{error_msg}{timeout_info}\n\n建议：\n1. 检查网络连接\n2. 稍后重试\n3. 增加超时时间")
        yield tool_instance.create_json_message({
            "error": "network_error",
            "message": "网络连接问题",
            "details": error_msg,
            "timeout_value": timeout_value,
            "suggestion": "检查网络连接或稍后重试"
        })
        return
    
    # 3. 数据结构错误（AKShare内部问题）
    elif ("'NoneType' object is not subscriptable" in error_msg or 
          "NoneType" in error_msg):
        yield tool_instance.create_text_message(f"数据源结构错误：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 数据源返回的数据结构不符合预期\n2. 该股票代码可能没有相关数据\n3. 数据源暂时不可用或结构发生变化\n\n建议：\n1. 检查股票代码是否正确\n2. 稍后重试\n3. 尝试其他股票代码")
        yield tool_instance.create_json_message({
            "error": "data_structure_error",
            "message": "数据源结构错误",
            "details": error_msg,
            "suggestion": "检查股票代码或稍后重试"
        })
        return
    
    # 4. 股票代码格式错误
    elif ("'zygcfx'" in error_msg or
          error_msg.strip() in ["'zygcfx'", "zygcfx"]):
        yield tool_instance.create_text_message(f"股票代码格式错误：\n\n{error_msg}\n\n建议：\n1. 检查股票代码格式：\n   - A股：600519、000001、SH600519、SZ000001\n   - 港股：00700、03900、HK00700（系统会自动转换为0700、3900格式）\n   - 美股：AAPL、MSFT\n2. 确认股票代码是否存在于对应市场\n3. 检查接口是否支持该股票代码")
        yield tool_instance.create_json_message({
            "error": "symbol_format_error",
            "message": "股票代码格式不正确",
            "details": error_msg,
            "suggestion": "检查股票代码格式，确保使用正确的市场代码"
        })
        return
    
    # 5. 参数错误
    elif any(keyword in error_msg.lower() for keyword in ["invalid", "parameter", "argument", "unexpected"]):
        yield tool_instance.create_text_message(f"参数错误：\n\n{error_msg}\n\n建议：\n1. 检查参数格式是否正确\n2. 确认参数值是否有效")
        yield tool_instance.create_json_message({
            "error": "parameter_error",
            "message": "参数格式或值不正确",
            "details": error_msg,
            "suggestion": "检查参数格式和值"
        })
        return
    
    # 5. 其他错误
    else:
        yield tool_instance.create_text_message(f"接口调用错误：\n\n{error_msg}\n\n建议：\n1. 检查参数是否正确\n2. 稍后重试\n3. 联系技术支持")
        yield tool_instance.create_json_message({
            "error": "api_error",
            "message": "接口调用失败",
            "details": error_msg,
            "suggestion": "检查参数或稍后重试"
        })
        return


def validate_period(period: str, tool_instance, interface: str = None) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证周期参数
    
    Args:
        period: 周期参数
        tool_instance: 工具实例
        interface: 接口名称，用于确定验证规则
        
    Yields:
        ToolInvokeMessage: 错误消息（如果格式不正确）
        
    Returns:
        bool: 是否验证通过
    """
    # 分时行情接口的周期参数
    minute_interfaces = [
        "stock_zh_a_hist_min_em",
        "stock_hk_hist_min_em",
        "stock_us_hist_min_em"
    ]
    
    if interface in minute_interfaces:
        # 分时行情接口支持分钟级别和日线级别参数
        valid_periods = ['daily', 'weekly', 'monthly', '1', '5', '15', '30', '60']
    else:
        # 历史行情接口只支持日线级别参数
        valid_periods = ['daily', 'weekly', 'monthly']
    
    if period not in valid_periods:
        error_msg = f"周期参数错误。支持的周期：{', '.join(valid_periods)}"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_period", "valid_periods": valid_periods})
        return False
    
    return True


def validate_date_range(start_date: str, end_date: str, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        tool_instance: 工具实例
        
    Yields:
        ToolInvokeMessage: 错误消息（如果格式不正确）
        
    Returns:
        bool: 是否验证通过
    """
    # 验证日期格式
    validation_result = None
    for result in validate_date_format(start_date, "YYYYMMDD", tool_instance):
        if isinstance(result, bool):
            validation_result = result
        else:
            yield result
    if validation_result is False:
        return False
    
    validation_result = None
    for result in validate_date_format(end_date, "YYYYMMDD", tool_instance):
        if isinstance(result, bool):
            validation_result = result
        else:
            yield result
    if validation_result is False:
        return False
    
    # 验证日期范围
    if start_date > end_date:
        error_msg = "开始日期不能晚于结束日期"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_date_range", "message": "Start date cannot be later than end date"})
        return False
    
    # 验证日期范围是否过大（超过5年）
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    if end_year - start_year > 5:
        error_msg = f"日期范围过大。当前范围：{end_year - start_year}年，建议不超过5年"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "date_range_too_large", "message": "Date range too large, suggest within 5 years"})
        return False
    
    return True


def validate_adjust(adjust: str, tool_instance) -> Generator[ToolInvokeMessage, None, None]:
    """
    验证调整参数
    
    Args:
        adjust: 调整参数
        tool_instance: 工具实例
        
    Yields:
        ToolInvokeMessage: 错误消息（如果格式不正确）
        
    Returns:
        bool: 是否验证通过
    """
    valid_adjusts = ['qfq', 'hfq', 'none', '']
    if adjust not in valid_adjusts:
        error_msg = f"调整参数错误。支持的调整：{', '.join(valid_adjusts)}"
        yield tool_instance.create_text_message(error_msg)
        yield tool_instance.create_json_message({"error": "invalid_adjust", "valid_adjusts": valid_adjusts})
        return False
    
    return True


def process_symbol_format(symbol: str, interface: str) -> str:
    """
    处理股票代码格式，根据接口要求进行转换
    
    Args:
        symbol: 原始股票代码
        interface: 接口名称
        
    Returns:
        str: 处理后的股票代码
    """
    if not symbol:
        return symbol
    
    # 需要带市场前缀的接口
    prefix_required_interfaces = [
        # "stock_zh_a_hist",  # A股历史数据不需要SH/SZ前缀
    ]
    
    # 港股接口需要特殊格式处理
    hk_interfaces = [
        "stock_hk_hist",  # 港股历史数据
    ]
    
    # 美股接口需要特殊格式处理
    us_interfaces = [
        "stock_us_hist",  # 美股历史数据
        "stock_us_hist_min_em",  # 美股分时数据
    ]
    
    # 科创板接口需要特殊格式处理
    kcb_interfaces = [
        "stock_zh_kcb_daily",  # 科创板历史数据
    ]
    
    # 处理科创板接口的代码格式
    if interface in kcb_interfaces:
        # 科创板代码需要sh前缀
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith('68'):  # 科创板代码以68开头
                return f"sh{symbol}"
        return symbol
    
    # 处理港股接口的代码格式
    elif interface in hk_interfaces:
        # 移除HK前缀（如果有）
        if symbol.upper().startswith('HK'):
            symbol = symbol[2:]
        
        # 港股代码保持原始格式，不进行转换
        # 因为ak.stock_hk_hist需要00700格式，而不是0700格式
        return symbol
    
    # 处理美股接口的代码格式
    elif interface in us_interfaces:
        # 美股代码需要特殊格式处理
        # 如果输入的是简单代码（如MSFT, AAPL），需要查找对应的完整代码
        if symbol.isalpha() and len(symbol) <= 5:
            # 常见美股代码映射
            us_stock_mapping = {
                'MSFT': '105.MSFT',
                'AAPL': '105.AAPL', 
                'GOOGL': '105.GOOGL',
                'AMZN': '105.AMZN',
                'TSLA': '105.TSLA',
                'NVDA': '105.NVDA',
                'META': '105.META',
                'NFLX': '105.NFLX',
                'GOOG': '105.GOOG',
                'BRK.A': '105.BRK.A',
                'BRK.B': '105.BRK.B'
            }
            return us_stock_mapping.get(symbol.upper(), symbol.upper())
        return symbol.upper()
    
    # 如果接口需要前缀且当前代码没有前缀
    if interface in prefix_required_interfaces and not any(symbol.upper().startswith(prefix) for prefix in ['SH', 'SZ', 'HK']):
        # 根据代码判断市场
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith(('60', '68')):
                return f"SH{symbol}"
            elif symbol.startswith(('00', '30')):
                return f"SZ{symbol}"
    
    return symbol

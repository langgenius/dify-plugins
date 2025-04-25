import base64
import hashlib
import time
import os
import binascii
import requests
from collections.abc import Generator
from typing import Any, Dict, List, Optional, Tuple, Union

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 引入MD2算法和其他必要模块
from Crypto.Hash import MD2

class ResponseFormatter:
    """
    响应格式化工具类，处理标准化的API响应
    """
    # 状态码定义
    STATUS_SUCCESS = 0        # 成功
    STATUS_INVALID_PARAM = 400  # 参数错误
    STATUS_NOT_FOUND = 404      # 资源未找到
    STATUS_ERROR = 500        # 服务器错误
    
    @classmethod
    def success(cls, data: Any, message: str = "操作成功") -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            
        Returns:
            标准化的成功响应
        """
        return {
            "code": ResponseFormatter.STATUS_SUCCESS,
            "data": data,
            "message": message
        }
    
    @classmethod
    def error(cls, message: str, code: int = None, error_type: str = "general_error", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            message: 错误消息
            code: 错误状态码
            error_type: 错误类型
            details: 错误详情
            
        Returns:
            标准化的错误响应
        """
        if code is None:
            code = ResponseFormatter.STATUS_ERROR
            
        response = {
            "code": code,
            "message": message,
            "error_type": error_type
        }
        
        if details:
            response["details"] = details
            
        return response
    
    @classmethod
    def progress(cls, progress: int, message: str = None) -> Dict[str, Any]:
        """
        创建进度响应
        
        Args:
            progress: 进度百分比
            message: 进度消息
            
        Returns:
            标准化的进度响应
        """
        response = {
            "code": ResponseFormatter.STATUS_SUCCESS,
            "status": "processing",
            "progress": progress
        }
        
        if message:
            response["message"] = message
            
        return response


class HashAlgorithmFactory:
    """
    哈希算法工厂类，负责创建和管理不同的哈希算法
    """
    # 算法安全性评级
    ALGORITHM_SECURITY = {
        "MD2": {"rating": "危险", "description": "已被破解，不应用于安全场景"},
        "MD5": {"rating": "不安全", "description": "已被破解，仅用于完整性检查"},
        "SHA-1": {"rating": "弱", "description": "不推荐用于安全用途"},
        "SHA-256": {"rating": "强", "description": "推荐用于一般安全用途"},
        "SHA-384": {"rating": "强", "description": "推荐用于一般安全用途"},
        "SHA-512": {"rating": "强", "description": "推荐用于一般安全用途"},
        "SHA3-256": {"rating": "非常强", "description": "现代算法，推荐用于高安全性场景"},
        "BLAKE2b": {"rating": "非常强", "description": "现代算法，性能优异"}
    }
    
    @classmethod
    def get_algorithm_security(cls, algorithm: str) -> Dict[str, str]:
        """
        获取指定算法的安全性评级
        
        Args:
            algorithm: 哈希算法名称
            
        Returns:
            包含算法安全性评级的字典
        """
        return cls.ALGORITHM_SECURITY.get(algorithm, {"rating": "未知", "description": ""})
    
    @classmethod
    def create_hash_object(cls, algorithm: str) -> Optional[Any]:
        """
        创建指定算法的哈希对象
        
        Args:
            algorithm: 哈希算法名称
            
        Returns:
            哈希对象，如果不支持则返回None
        """
        # 特殊处理MD2算法
        if algorithm == "MD2":
            return MD2.new()
            
        # 处理hashlib支持的标准算法
        algorithm_mapping = {
            "MD5": hashlib.md5,
            "SHA-1": hashlib.sha1,
            "SHA-256": hashlib.sha256,
            "SHA-384": hashlib.sha384,
            "SHA-512": hashlib.sha512,
            "SHA3-256": hashlib.sha3_256,
            "BLAKE2b": hashlib.blake2b
        }
        
        if algorithm in algorithm_mapping:
            return algorithm_mapping[algorithm]()
        
        return None
    
    @classmethod
    def get_supported_algorithms(cls) -> List[str]:
        """
        获取所有支持的哈希算法列表
        
        Returns:
            支持的算法列表
        """
        return list(cls.ALGORITHM_SECURITY.keys())
    
    @classmethod
    def is_algorithm_supported(cls, algorithm: str) -> bool:
        """
        检查指定算法是否受支持
        
        Args:
            algorithm: 哈希算法名称
            
        Returns:
            是否支持该算法
        """
        return algorithm in cls.ALGORITHM_SECURITY


class HashFormatter:
    """
    哈希值格式化工具类，负责不同格式的转换
    """
    @staticmethod
    def format_hash(hash_bytes: bytes, output_format: str) -> str:
        """
        将哈希字节值转换为指定格式的字符串
        
        Args:
            hash_bytes: 原始哈希字节
            output_format: 输出格式（hex, base64, binary）
            
        Returns:
            格式化后的哈希字符串
        """
        if output_format == 'hex':
            return binascii.hexlify(hash_bytes).decode('ascii')
        elif output_format == 'base64':
            return base64.b64encode(hash_bytes).decode('ascii')
        elif output_format == 'binary':
            # 将二进制转为01字符串，仅用于显示
            return ''.join(format(b, '08b') for b in hash_bytes)
        else:
            # 默认十六进制
            return binascii.hexlify(hash_bytes).decode('ascii')


class FileHashTool(Tool):
    """
    文件哈希计算工具，支持多种算法和格式
    """
    # 块大小，用于分块处理大文件 (8MB)
    CHUNK_SIZE = 8 * 1024 * 1024
    
    def _get_attribute_safely(self, obj: Any, attr_name: str, default: Any = None) -> Any:
        """
        安全地获取对象的属性，无论对象是字典还是其他类型
        
        Args:
            obj: 目标对象
            attr_name: 属性名称
            default: 默认值（如果属性不存在）
            
        Returns:
            属性值或默认值
        """
        if isinstance(obj, dict):
            return obj.get(attr_name, default)
        elif hasattr(obj, attr_name):
            return getattr(obj, attr_name)
        else:
            return default
    
    def _download_file_from_url(self, url: str) -> Tuple[bytes, bool, str]:
        """
        从URL下载文件内容
        
        Args:
            url: 文件下载URL
            
        Returns:
            元组(文件内容, 是否成功, 错误信息)
        """
        try:
            # 处理不包含http前缀的URL
            if url and not url.startswith(('http://', 'https://')):
                # 从环境变量获取FILES_URL作为基础URL
                base_url = os.environ.get('FILES_URL')
                if not base_url:
                    return None, False, "未配置FILES_URL环境变量，无法处理相对URL。请在环境变量中设置FILES_URL指向Dify文件服务地址。"
                
                # 确保基础URL没有尾部斜杠
                if base_url.endswith('/'):
                    base_url = base_url[:-1]
                
                # 确保URL路径以/开头
                if not url.startswith('/'):
                    url = '/' + url
                
                url = f"{base_url}{url}"
                print(f"转换相对URL为绝对URL: {url}")
            
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code != 200:
                return None, False, f"下载失败，HTTP状态码: {response.status_code}"
            
            # 获取文件内容
            file_content = response.content
            return file_content, True, ""
            
        except Exception as e:
            return None, False, f"下载文件时出错: {str(e)}"
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        处理文件哈希计算请求
        
        Args:
            tool_parameters: 工具参数，包含文件、算法选择等
            
        Yields:
            处理结果或进度信息
        """
        # 获取参数
        file_param = tool_parameters.get('file')
        algorithm = tool_parameters.get('algorithm', 'SHA-256')
        output_format = tool_parameters.get('format', 'hex')
        expected_hash = tool_parameters.get('expected_hash', '')
        
        try:
            # 检查算法是否支持
            if not HashAlgorithmFactory.is_algorithm_supported(algorithm):
                yield self.create_json_message(
                    ResponseFormatter.error(
                        message=f"不支持的哈希算法: {algorithm}",
                        code=ResponseFormatter.STATUS_INVALID_PARAM,
                        error_type="algorithm_error",
                        details={"supported_algorithms": HashAlgorithmFactory.get_supported_algorithms()}
                    )
                )
                return
            
            # 处理文件参数，支持多文件输入
            files_list = []
            
            # 判断是单文件还是多文件格式
            if isinstance(file_param, list):
                # 新格式：多文件列表
                files_list = file_param
            elif isinstance(file_param, dict):
                # 旧格式：单个文件
                files_list = [file_param]
            else:
                yield self.create_json_message(
                    ResponseFormatter.error(
                        message="未提供有效的文件",
                        code=ResponseFormatter.STATUS_INVALID_PARAM,
                        error_type="invalid_file"
                    )
                )
                return
            
            # 文件列表为空
            if not files_list:
                yield self.create_json_message(
                    ResponseFormatter.error(
                        message="文件列表为空",
                        code=ResponseFormatter.STATUS_INVALID_PARAM,
                        error_type="empty_file_list"
                    )
                )
                return
            
            # 处理进度追踪
            total_files = len(files_list)
            processed_files = 0
            hash_results = []
            
            # 开始处理消息
            if total_files > 1:
                yield self.create_json_message(
                    ResponseFormatter.progress(
                        progress=0,
                        message=f"开始处理 {total_files} 个文件的哈希计算..."
                    )
                )
            
            # 逐个处理文件
            for file_item in files_list:
                try:
                    # 检查是否有URL，优先使用URL下载文件
                    has_url = False
                    url = self._get_attribute_safely(file_item, "url")
                    if url:
                        has_url = True
                    
                    file_data = None
                    filename = self._get_attribute_safely(file_item, "name", 
                               self._get_attribute_safely(file_item, "filename", "未命名文件"))
                    
                    if has_url:
                        # 从URL下载文件
                        yield self.create_json_message(
                            ResponseFormatter.progress(
                                progress=processed_files * 90 // total_files,
                                message=f"正在下载文件 {filename}..."
                            )
                        )
                        file_content, success, error_msg = self._download_file_from_url(url)
                        
                        if not success:
                            hash_results.append({
                                "file": {
                                    "name": filename
                                },
                                "status": "error",
                                "error": error_msg
                            })
                            continue
                            
                        file_data = file_content
                    else:
                        # 使用直接提供的文件内容
                        file_data = self._get_attribute_safely(file_item, "content")
                        
                        # 如果没有content属性，尝试检查是否有可能是File对象的情况
                        if file_data is None and hasattr(file_item, "read"):
                            # 可能是类似文件对象，尝试读取
                            try:
                                file_data = file_item.read()
                            except Exception as e:
                                print(f"尝试读取文件对象时出错: {str(e)}")
                    
                    if not file_data:
                        hash_results.append({
                            "file": {
                                "name": filename
                            },
                            "status": "error",
                            "error": "文件内容为空"
                        })
                        continue
                    
                    # 获取文件字节内容 
                    file_bytes = file_data
                    
                    # 获取文件大小
                    file_size = len(file_bytes)
                    
                    # 处理文件哈希计算
                    start_time = time.time()
                    
                    # 对大文件使用分块处理，但在多文件模式下不报告进度以简化处理
                    if file_size > self.CHUNK_SIZE:
                        # 大文件分块处理，不报告进度
                        hash_result_generator = self._calculate_hash_chunked(file_bytes, algorithm, yield_progress=False)
                        hash_result = next(hash_result_generator)
                        for _ in hash_result_generator:
                            pass  # 消耗生成器中的所有内容
                    else:
                        # 小文件直接处理
                        hash_result = self._calculate_hash(file_bytes, algorithm)
                    
                    end_time = time.time()
                    
                    # 如果计算失败
                    if not hash_result.get("success", False):
                        hash_results.append({
                            "file": {
                                "name": filename
                            },
                            "status": "error",
                            "error": hash_result.get("error", "哈希计算失败")
                        })
                        continue
                    
                    # 格式化哈希值
                    hash_value = hash_result["hash_value"]
                    formatted_hash = HashFormatter.format_hash(hash_value, output_format)
                    
                    # 验证哈希值（如果提供了预期值，仅对单文件模式有效）
                    verification_result = None
                    verification_status = None
                    if expected_hash and total_files == 1:
                        # 规范化预期哈希值以进行比较
                        expected_hash = expected_hash.lower().strip()
                        actual_hash = formatted_hash.lower() if output_format == 'hex' else formatted_hash
                        
                        is_verified = expected_hash == actual_hash
                        verification_status = "匹配" if is_verified else "不匹配"
                        verification_result = {
                            "verified": is_verified,
                            "expected": expected_hash,
                            "actual": actual_hash,
                            "status": verification_status
                        }
                    
                    # 构建单个文件的结果数据
                    file_result = {
                        "file": {
                            "name": filename,
                            "size": {
                                "bytes": file_size,
                                "readable": self._format_size(file_size)
                            }
                        },
                        "hash": {
                            "value": formatted_hash,
                            "algorithm": algorithm,
                            "format": output_format,
                            "security": HashAlgorithmFactory.get_algorithm_security(algorithm)
                        },
                        "status": "success",
                        "processing_time_ms": round((end_time - start_time) * 1000, 2)
                    }
                    
                    # 添加验证结果（如果有）
                    if verification_result:
                        file_result["verification"] = verification_result
                    
                    hash_results.append(file_result)
                
                except Exception as e:
                    error_msg = f"计算哈希时出错: {str(e)}"
                    print(f"处理文件时出错: {error_msg}")
                    filename = "未命名文件"
                    try:
                        filename = self._get_attribute_safely(file_item, "name", 
                                   self._get_attribute_safely(file_item, "filename", "未命名文件"))
                    except:
                        pass
                    
                    hash_results.append({
                        "file": {
                            "name": filename
                        },
                        "status": "error",
                        "error": error_msg
                    })
                
                # 更新处理进度
                processed_files += 1
                if total_files > 1:
                    progress_percent = min(95, int((processed_files / total_files) * 100))
                    
                    # 发送进度更新
                    yield self.create_json_message(
                        ResponseFormatter.progress(
                            progress=progress_percent,
                            message=f"已处理 {processed_files}/{total_files} 个文件..."
                        )
                    )
            
            # 创建最终响应
            if total_files == 1:
                # 单文件模式，保持与旧接口兼容
                result_data = hash_results[0]
                success_message = "哈希计算完成"
                if verification_status:
                    success_message += f"，验证结果: {verification_status}"
            else:
                # 多文件模式，返回聚合结果
                result_data = {
                    "files_count": total_files,
                    "successful_count": sum(1 for r in hash_results if r.get("status") == "success"),
                    "failed_count": sum(1 for r in hash_results if r.get("status") == "error"),
                    "results": hash_results,
                    "algorithm": algorithm,
                    "format": output_format
                }
                success_message = f"已完成 {total_files} 个文件的哈希计算"
            
            # 发送成功响应
            yield self.create_json_message(
                ResponseFormatter.success(
                    data=result_data,
                    message=success_message
                )
            )
            
        except Exception as e:
            yield self.create_json_message(
                ResponseFormatter.error(
                    message=f"计算文件哈希时出错: {str(e)}",
                    error_type="general_error",
                    details={
                        "exception_type": type(e).__name__,
                        "algorithm": algorithm
                    }
                )
            )
    
    def _calculate_hash(self, file_bytes: bytes, algorithm: str) -> Dict[str, Any]:
        """
        根据指定算法计算哈希值（适用于小文件）
        
        Args:
            file_bytes: 文件内容字节
            algorithm: 哈希算法名称
            
        Returns:
            哈希计算结果
        """
        try:
            # 使用工厂创建哈希对象
            hash_obj = HashAlgorithmFactory.create_hash_object(algorithm)
            
            if not hash_obj:
                return {
                    "success": False,
                    "error": f"不支持的哈希算法: {algorithm}",
                    "error_type": "algorithm_error"
                }
            
            # 计算哈希值
            hash_obj.update(file_bytes)
            
            # 获取原始字节形式的哈希值
            hash_value = hash_obj.digest()
            
            return {
                "success": True,
                "hash_value": hash_value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"计算哈希值时出错: {str(e)}",
                "error_type": "hash_calculation_error"
            }
    
    def _calculate_hash_chunked(self, file_bytes: bytes, algorithm: str, yield_progress: bool = False) -> Generator[Dict[str, Any], None, None]:
        """
        分块计算哈希值，适用于大文件，可选择是否报告进度
        
        Args:
            file_bytes: 文件内容字节
            algorithm: 哈希算法名称
            yield_progress: 是否报告进度
            
        Yields:
            进度信息或最终哈希结果
        """
        try:
            # 使用工厂创建哈希对象
            hash_obj = HashAlgorithmFactory.create_hash_object(algorithm)
            
            if not hash_obj:
                yield {
                    "success": False,
                    "error": f"不支持的哈希算法: {algorithm}",
                    "error_type": "algorithm_error"
                }
                return
            
            # 计算总块数
            total_size = len(file_bytes)
            total_chunks = (total_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            # 分块处理
            for i in range(0, total_size, self.CHUNK_SIZE):
                # 获取当前块
                chunk = file_bytes[i:i+self.CHUNK_SIZE]
                # 更新哈希
                hash_obj.update(chunk)
                
                # 报告进度
                if yield_progress and total_chunks > 1:
                    chunk_number = i // self.CHUNK_SIZE + 1
                    progress_percent = min(100, round(chunk_number * 100 / total_chunks))
                    yield {"progress": progress_percent}
            
            # 获取最终哈希值
            hash_value = hash_obj.digest()
            
            yield {
                "success": True,
                "hash_value": hash_value
            }
            
        except Exception as e:
            yield {
                "success": False,
                "error": f"计算哈希值时出错: {str(e)}",
                "error_type": "hash_calculation_error"
            }
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化后的大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.2f} MB"
        elif size_bytes < 1024 * 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
        else:
            return f"{size_bytes/(1024*1024*1024*1024):.2f} TB"

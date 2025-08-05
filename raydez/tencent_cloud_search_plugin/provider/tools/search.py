# 首先导入 dify_plugin 以确保 monkey patching 在其他模块之前完成
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

# 然后导入其他模块
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from typing import Any, Dict, List, Union
import requests


class TencentCloudSearchTool(Tool):
    """
    腾讯云联网搜索API工具
    Tencent Cloud Networked Search API Tool
    """
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> Union[ToolInvokeMessage, List[ToolInvokeMessage]]:
        """
        调用腾讯云联网搜索API
        """
        try:
            # 获取认证信息
            secret_id = self.runtime.credentials.get('secret_id')
            secret_key = self.runtime.credentials.get('secret_key')
            
            if not secret_id or not secret_key:
                return self._create_error_result("缺少腾讯云API密钥配置")
            
            # 获取参数
            query = tool_parameters.get('query', '').strip()
            if not query:
                return self._create_error_result("搜索关键词不能为空")
            
            if len(query.encode('utf-8')) > 1500:
                return self._create_error_result("搜索关键词过长，请限制在500个字符以内")
            
            # 构建请求参数
            params = self._build_request_params(tool_parameters)
            
            # 发送API请求
            response = self._send_api_request(secret_id, secret_key, params)
            
            # 解析响应
            return self._parse_response(response, tool_parameters.get('mode', '0'))
            
        except Exception as e:
            return self._create_error_result(f"搜索请求失败: {str(e)}")
    
    def _build_request_params(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """构建API请求参数"""
        params = {
            "Query": tool_parameters.get('query', '').strip()
        }
        
        # 可选参数
        mode = tool_parameters.get('mode')
        if mode is not None:
            params["Mode"] = int(mode)
        
        site = tool_parameters.get('site', '').strip()
        if site:
            params["Site"] = site
        
        count = tool_parameters.get('count')
        if count is not None and count > 0:
            params["Cnt"] = min(int(count), 50)
        
        from_time = tool_parameters.get('from_time')
        to_time = tool_parameters.get('to_time')
        if from_time is not None and to_time is not None:
            params["FromTime"] = int(from_time)
            params["ToTime"] = int(to_time)
        
        industry = tool_parameters.get('industry', '').strip()
        if industry:
            params["industry"] = industry
        
        return params
    
    def _send_api_request(self, secret_id: str, secret_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送腾讯云API请求"""
        # API配置
        service = "wsa"
        version = "2025-05-08"
        action = "SearchPro"
        endpoint = "wsa.tencentcloudapi.com"
        region = ""
        
        # 当前时间戳
        timestamp = int(time.time())
        date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
        
        # 请求体
        payload = json.dumps(params, separators=(',', ':'))
        
        # 构建签名
        authorization = self._build_authorization(
            secret_id, secret_key, service, action, version,
            timestamp, date, payload, endpoint, region
        )
        
        # 构建请求头
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': endpoint,
            'X-TC-Action': action,
            'X-TC-Timestamp': str(timestamp),
            'X-TC-Version': version,
        }
        
        if region:
            headers['X-TC-Region'] = region
        
        # 发送请求
        url = f"https://{endpoint}"
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def _build_authorization(self, secret_id: str, secret_key: str, service: str, 
                           action: str, version: str, timestamp: int, date: str,
                           payload: str, endpoint: str, region: str) -> str:
        """构建腾讯云API v3签名"""
        
        # 步骤1：拼接规范请求串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{endpoint}\n"
        signed_headers = "content-type;host"
        hashed_request_payload = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
        
        # 步骤2：拼接待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = f"{date}/{service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # 步骤3：计算签名
        def sign(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        secret_date = sign(f"TC3{secret_key}".encode('utf-8'), date)
        secret_service = sign(secret_date, service)
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 步骤4：拼接Authorization
        authorization = f"{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        return authorization
    
    def _parse_response(self, response: Dict[str, Any], mode: str) -> List[ToolInvokeMessage]:
        """解析API响应"""
        if 'Response' not in response:
            return self._create_error_result("API响应格式错误")
        
        response_data = response['Response']
        
        # 检查错误
        if 'Error' in response_data:
            error_info = response_data['Error']
            error_msg = f"API错误: {error_info.get('Message', '未知错误')} (Code: {error_info.get('Code', 'Unknown')})"
            return self._create_error_result(error_msg)
        
        # 解析搜索结果
        pages = response_data.get('Pages', [])
        if not pages:
            return [ToolInvokeMessage(
                type=ToolInvokeMessage.MessageType.TEXT,
                message=ToolInvokeMessage.TextMessage(text=f"未找到相关搜索结果，查询词：{response_data.get('Query', '')}")
            )]
        
        results = []
        
        # 添加搜索摘要
        query = response_data.get('Query', '')
        results.append(ToolInvokeMessage(
            type=ToolInvokeMessage.MessageType.TEXT,
            message=ToolInvokeMessage.TextMessage(text=f"🔍 搜索结果 - 关键词：{query}\n找到 {len(pages)} 条相关结果\n")
        ))
        
        # 解析每个搜索结果
        for i, page_str in enumerate(pages, 1):
            try:
                page_data = json.loads(page_str)
                result = self._format_search_result(page_data, i, mode)
                if result:
                    results.append(result)
            except json.JSONDecodeError:
                continue
        
        return results
    
    def _format_search_result(self, page_data: Dict[str, Any], index: int, mode: str) -> ToolInvokeMessage:
        """格式化单个搜索结果"""
        
        # 检查是否为VR卡结果
        is_vr = page_data.get('vr', False)
        
        if is_vr:
            return self._format_vr_result(page_data, index)
        else:
            return self._format_natural_result(page_data, index)
    
    def _format_natural_result(self, page_data: Dict[str, Any], index: int) -> ToolInvokeMessage:
        """格式化自然搜索结果"""
        title = page_data.get('title', '无标题')
        url = page_data.get('url', '')
        passage = page_data.get('passage', '')
        content = page_data.get('content', '')
        date = page_data.get('date', '')
        site = page_data.get('site', '')
        score = page_data.get('score', 0)
        
        # 选择摘要内容
        summary = passage if passage else (content[:200] + '...' if len(content) > 200 else content)
        
        text_parts = [f"📄 **结果 {index}**"]
        text_parts.append(f"**标题**: {title}")
        
        if summary:
            text_parts.append(f"**摘要**: {summary}")
        
        if url:
            text_parts.append(f"**链接**: {url}")
        
        if site:
            text_parts.append(f"**来源**: {site}")
        
        if date:
            text_parts.append(f"**发布时间**: {date}")
        
        if score > 0:
            text_parts.append(f"**相关性**: {score:.2f}")
        
        return ToolInvokeMessage(
            type=ToolInvokeMessage.MessageType.TEXT,
            message=ToolInvokeMessage.TextMessage(text='\n'.join(text_parts) + '\n')
        )
    
    def _format_vr_result(self, page_data: Dict[str, Any], index: int) -> ToolInvokeMessage:
        """格式化VR卡结果"""
        vr_category = page_data.get('vr_category', '')
        vrid = page_data.get('vrid', '')
        
        text_parts = [f"🎯 **VR卡结果 {index}** ({vr_category})"]
        
        # 解析display信息
        display = page_data.get('display', {})
        if display.get('title'):
            text_parts.append(f"**标题**: {display['title']}")
        
        # 解析jsonData
        json_data = page_data.get('jsonData', {})
        if json_data:
            # 基础信息
            base_info = json_data.get('base_info', {})
            if base_info.get('title'):
                text_parts.append(f"**名称**: {base_info['title']}")
            if base_info.get('url'):
                text_parts.append(f"**详情链接**: {base_info['url']}")
            
            # 显示信息
            display_info = json_data.get('display_info', {})
            if display_info:
                text_parts.append(f"**详细信息**: {json.dumps(display_info, ensure_ascii=False, indent=2)}")
        
        text_parts.append(f"**VR ID**: {vrid}")
        
        return ToolInvokeMessage(
            type=ToolInvokeMessage.MessageType.TEXT,
            message=ToolInvokeMessage.TextMessage(text='\n'.join(text_parts) + '\n')
        )
    
    def _create_error_result(self, error_message: str) -> List[ToolInvokeMessage]:
        """创建错误结果"""
        return [ToolInvokeMessage(
            type=ToolInvokeMessage.MessageType.TEXT,
            message=ToolInvokeMessage.TextMessage(text=f"❌ 错误: {error_message}")
        )]
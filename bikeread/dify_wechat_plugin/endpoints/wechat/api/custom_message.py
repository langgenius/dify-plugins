import json
import logging
import requests
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WechatCustomMessageSender:
    """微信客服消息发送器"""
    
    TOKEN_CACHE = {}  # 用于缓存访问令牌
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化客服消息发送器
        
        参数:
            app_id: 微信公众号的AppID
            app_secret: 微信公众号的AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret
    
    def _get_access_token(self) -> str:
        """
        获取微信接口访问令牌
        
        返回:
            有效的access_token字符串
        
        异常:
            Exception: 当获取令牌失败时
        """
        # 检查缓存中是否有有效的令牌
        cache_key = f"{self.app_id}_{self.app_secret}"
        if cache_key in self.TOKEN_CACHE:
            token_info = self.TOKEN_CACHE[cache_key]
            # 检查令牌是否过期（提前5分钟刷新）
            if token_info['expires_at'] > time.time() + 300:
                return token_info['token']
        
        # 请求新的访问令牌
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if 'access_token' in result:
                # 计算过期时间 (令牌有效期通常为7200秒)
                expires_at = time.time() + result.get('expires_in', 7200)
                # 保存到缓存
                self.TOKEN_CACHE[cache_key] = {
                    'token': result['access_token'],
                    'expires_at': expires_at
                }
                return result['access_token']
            else:
                error_msg = f"获取访问令牌失败: {result.get('errmsg', '未知错误')}"
                logger.error(error_msg)
                raise Exception(error_msg)
        
        except Exception as e:
            logger.error(f"请求访问令牌异常: {str(e)}")
            raise
    
    def send_text_message(self, open_id: str, content: str) -> Dict[str, Any]:
        """
        发送文本客服消息
        
        参数:
            open_id: 接收消息用户的OpenID
            content: 文本消息内容
            
        返回:
            API响应结果
            
        异常:
            Exception: 当发送失败时
        """
        try:
            # 获取访问令牌
            access_token = self._get_access_token()
            
            # 构建请求URL
            url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
            
            # 构建请求数据
            data = {
                "touser": open_id,
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            # 发送请求
            response = requests.post(
                url=url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # 解析响应
            result = response.json()
            
            if result.get('errcode', 0) != 0:
                error_msg = f"发送客服消息失败: {result.get('errmsg', '未知错误')}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'raw_response': result
                }
            
            return {
                'success': True,
                'raw_response': result
            }
            
        except Exception as e:
            logger.error(f"发送客服消息异常: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 
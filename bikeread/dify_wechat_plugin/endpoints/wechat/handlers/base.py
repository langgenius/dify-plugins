from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from ..models import WechatMessage

logger = logging.getLogger(__name__)

class MessageHandler(ABC):
    """消息处理器抽象基类"""
    @abstractmethod
    def handle(self, message: WechatMessage, session: Any, app_settings: Dict[str, Any]) -> str:
        """
        处理消息并返回回复内容
        
        参数:
            message: 要处理的微信消息对象
            session: 当前会话对象，用于访问存储和AI接口
            app_settings: 应用设置字典
            
        返回:
            处理后的回复内容字符串
        """
        pass 
        
    def clear_cache(self, session: Any, user_id: str) -> bool:
        """
        清除指定用户的会话缓存
        
        参数:
            session: 当前会话对象，用于访问存储
            user_id: 用户标识（如微信用户的OpenID）
            
        返回:
            bool: 是否成功清除缓存
        """
        try:
            # 构造存储键
            storage_key = f"wechat_conv_{user_id}"
            logger.info(f"准备清除用户 '{user_id}' 的会话缓存，存储键: '{storage_key}'")
            
            # 删除会话数据
            session.storage.delete(storage_key)
            logger.info(f"已成功清除用户 '{user_id}' 的会话缓存")
            return True
        except Exception as e:
            logger.error(f"清除用户 '{user_id}' 的会话缓存失败: {str(e)}")
            return False
            
    def get_storage_key(self, user_id: str) -> str:
        """
        获取用户会话的存储键
        
        参数:
            user_id: 用户标识（如微信用户的OpenID）
            
        返回:
            str: 存储键
        """
        return f"wechat_conv_{user_id}"
        
    def _get_conversation_id(self, session: Any, storage_key: str) -> Optional[str]:
        """
        获取存储的会话ID
        
        参数:
            session: 当前会话对象，用于访问存储
            storage_key: 存储键
            
        返回:
            Optional[str]: 会话ID，如果不存在则返回None
        """
        try:
            stored_data = session.storage.get(storage_key)
            if stored_data:
                conversation_id = stored_data.decode('utf-8')
                logger.debug(f"使用已存在的会话ID: {conversation_id[:8]}...")
                return conversation_id
            logger.debug(f"未找到存储的会话ID(键:{storage_key})，将创建新对话")
            return None
        except Exception as e:
            logger.warning(f"获取存储的会话ID失败: {str(e)}")
            return None
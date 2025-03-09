from typing import Dict, Type

from .handlers.base import MessageHandler
from .handlers.text import TextMessageHandler
from .handlers.unsupported import UnsupportedMessageHandler
from .handlers.image import ImageMessageHandler
from .handlers.voice import VoiceMessageHandler
from .handlers.link import LinkMessageHandler

class MessageHandlerFactory:
    """消息处理器工厂"""
    _handlers: Dict[str, Type[MessageHandler]] = {
        'text': TextMessageHandler,
        'image': ImageMessageHandler,
        'voice': VoiceMessageHandler,
        'link': LinkMessageHandler,
        'default': UnsupportedMessageHandler
    }
    
    @classmethod
    def get_handler(cls, msg_type: str) -> MessageHandler:
        """
        获取对应类型的消息处理器
        
        参数:
            msg_type: 消息类型
            
        返回:
            对应类型的消息处理器实例
        """
        handler_class = cls._handlers.get(msg_type, cls._handlers['default'])
        return handler_class()
    
    @classmethod
    def register_handler(cls, msg_type: str, handler_class: Type[MessageHandler]) -> None:
        """
        注册新的消息处理器
        
        参数:
            msg_type: 消息类型
            handler_class: 对应的处理器类
        """
        cls._handlers[msg_type] = handler_class 
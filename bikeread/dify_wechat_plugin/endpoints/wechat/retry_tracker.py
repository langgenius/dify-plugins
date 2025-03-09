import logging
import threading
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MessageStatusTracker:
    """
    消息状态跟踪器
    用于跟踪微信消息处理状态和重试机制
    """
    # 类变量，用于存储所有正在处理的消息状态
    _messages: Dict[str, Dict[str, Any]] = {}
    
    # 字典操作锁
    _messages_lock = threading.Lock()
    
    @classmethod
    def track_message(cls, msg_id: str) -> Dict[str, Any]:
        """
        跟踪一个消息，如果消息已存在则更新重试计数并返回其状态，否则创建新状态
        """
        if not msg_id:
            return cls._create_temp_status()
        
        with cls._messages_lock:
            # 检查消息是否已存在
            if msg_id in cls._messages:
                # 增加重试计数
                cls._messages[msg_id]['retry_count'] = cls._messages[msg_id].get('retry_count', 0) + 1
                retry_count = cls._messages[msg_id]['retry_count']
                logger.info(f"检测到重试请求: {msg_id}, 当前重试次数: {retry_count}")
                return cls._messages[msg_id]
            
            # 新消息，创建状态
            status = cls._create_status()
            cls._messages[msg_id] = status
            
            # 启动清理线程（如果未启动）
            cls._ensure_cleanup_thread()
            
            return status
    
    @classmethod
    def update_status(cls, msg_id: str, result: Optional[str] = None, 
                     is_completed: bool = False, error: Optional[str] = None) -> None:
        """
        更新消息处理状态
        """
        if not msg_id:
            return
        
        with cls._messages_lock:
            if msg_id not in cls._messages:
                cls._messages[msg_id] = cls._create_status()
            
            status = cls._messages[msg_id]
            
            # 使用消息独立锁更新状态
            with status['lock']:
                # 更新状态
                if result is not None:
                    status['result'] = result
                
                if error is not None:
                    status['error'] = error
                
                if is_completed:
                    status['is_completed'] = True
                    # 设置完成事件
                    if 'completion_event' in status and not status['completion_event'].is_set():
                        status['completion_event'].set()
    
    @classmethod
    def mark_result_returned(cls, msg_id: str) -> bool:
        """
        原子操作：标记结果已返回
        如果结果已经被标记为返回，则返回False
        如果成功标记，则返回True
        """
        if not msg_id:
            return False
        
        with cls._messages_lock:
            if msg_id not in cls._messages:
                return False
            
            status = cls._messages[msg_id]
            
            # 使用消息独立锁更新状态
            with status['lock']:
                if status.get('result_returned', False):
                    logger.debug(f"结果已标记为已返回，跳过处理: {msg_id}")
                    return False
                
                status['result_returned'] = True
                return True
    
    @classmethod
    def get_status(cls, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        获取消息处理状态
        """
        if not msg_id:
            return None
        
        with cls._messages_lock:
            if msg_id not in cls._messages:
                return None
            
            # 返回状态的浅拷贝，排除锁对象
            return {k: v for k, v in cls._messages[msg_id].items() 
                   if k not in ('lock', 'completion_event')}
    
    @classmethod
    def wait_for_completion(cls, msg_id: str, timeout: Optional[float] = None) -> bool:
        """
        等待消息处理完成
        """
        if not msg_id:
            return False
        
        completion_event = None
        
        with cls._messages_lock:
            if msg_id not in cls._messages:
                return False
            
            status = cls._messages[msg_id]
            
            # 如果已完成，直接返回
            if status.get('is_completed', False):
                return True
            
            # 获取完成事件
            completion_event = status.get('completion_event')
        
        # 在锁外等待完成
        if completion_event:
            return completion_event.wait(timeout=timeout)
        
        return False
    
    @classmethod
    def _create_status(cls) -> Dict[str, Any]:
        """创建新的状态对象"""
        return {
            'result': None,
            'is_completed': False,
            'error': None,
            'start_time': time.time(),
            'completion_event': threading.Event(),
            'retry_count': 0,
            'result_returned': False,  # 标记是否已发送结果
            'lock': threading.Lock()   # 每个消息独立的锁
        }
    
    @classmethod
    def _create_temp_status(cls) -> Dict[str, Any]:
        """创建临时状态对象（不会被跟踪）"""
        return cls._create_status()
    
    @classmethod
    def _ensure_cleanup_thread(cls) -> None:
        """确保清理线程已启动"""
        if not hasattr(cls, '_cleanup_thread_started') or not cls._cleanup_thread_started:
            cls._cleanup_thread_started = True
            thread = threading.Thread(
                target=cls._cleanup_expired_messages,
                daemon=True,
                name="MessageCleanupThread"
            )
            thread.start()
    
    @classmethod
    def _cleanup_expired_messages(cls) -> None:
        """定期清理过期的消息"""
        try:
            while True:
                # 每60秒清理一次
                time.sleep(60)
                
                with cls._messages_lock:
                    now = time.time()
                    # 清理超过10分钟的已完成消息
                    expired_keys = [
                        msg_id for msg_id, status in cls._messages.items()
                        if status.get('is_completed', False) and 
                           now - status.get('start_time', now) > 600  # 10分钟
                    ]
                    
                    # 删除过期消息
                    for msg_id in expired_keys:
                        cls._messages.pop(msg_id, None)
                    
                    if expired_keys:
                        logger.info(f"已清理 {len(expired_keys)} 条过期消息，剩余消息: {len(cls._messages)}")
        except Exception as e:
            logger.error(f"消息清理线程异常退出: {str(e)}")
            cls._cleanup_thread_started = False

# 向后兼容的别名
MessageRetryTracker = MessageStatusTracker 
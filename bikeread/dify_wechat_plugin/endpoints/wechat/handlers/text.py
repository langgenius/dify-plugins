import logging
from typing import Dict, Any, Optional
import time
import threading
import json
import traceback

from .base import MessageHandler
from ..models import WechatMessage

logger = logging.getLogger(__name__)

# 定义超时常量
STREAM_CHUNK_TIMEOUT = 30  # 接收单个chunk的最大等待时间(秒)
MAX_TOTAL_STREAM_TIME = 240  # 流式处理的最大总时间(秒)

class TextMessageHandler(MessageHandler):
    """文本消息处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.initial_conversation_id = None
        self.new_conversation_id = None
    
    def handle(self, message: WechatMessage, session: Any, app_settings: Dict[str, Any]) -> str:
        """
        处理文本消息并返回回复内容
        
        参数:
            message: 要处理的微信文本消息对象
            session: 当前会话对象，用于访问存储和AI接口
            app_settings: 应用设置字典
            
        返回:
            处理后的回复内容字符串
        """
        try:
            # 记录开始处理
            logger.info(f"开始处理用户'{message.from_user}'的文本消息: '{message.content[:50]}...'")
            
            # 1. 获取存储键（基于用户OpenID）
            storage_key = self.get_storage_key(message.from_user)
            
            # 2. 获取会话ID（如果存在）
            conversation_id = self._get_conversation_id(session, storage_key)
            
            # 3. 调用AI（流式响应）
            app = app_settings.get("app", {})
            response_generator = self._invoke_ai(session, app, message.content, conversation_id)
            
            # 3.1 如果是新会话且获得了新的conversation_id，保存以便后续对话
            if self.new_conversation_id and not self.initial_conversation_id:
                try:
                    session.storage.set(storage_key, self.new_conversation_id.encode('utf-8'))
                    logger.info(f"为用户'{message.from_user}'保存新会话ID: {self.new_conversation_id[:8]}...")
                except Exception as e:
                    logger.error(f"保存会话ID失败: {str(e)}")
            
            # 4. 处理AI响应
            response = self._process_ai_response(response_generator)
            logger.info(f"处理完成，响应长度: {len(response)}")
            
            return response
        except Exception as e:
            logger.error(f"处理文本消息失败: {str(e)}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return f"抱歉，处理您的消息时出现了问题: {str(e)}"
    
    def _invoke_ai(self, session: Any, app: Dict[str, Any], content: str, conversation_id: Optional[str]) -> Any:
        """调用AI接口，获取流式响应生成器"""
        # 记录初始状态的conversation_id
        self.initial_conversation_id = conversation_id
        self.new_conversation_id = None
        
        # 准备调用参数
        invoke_params = {
            "app_id": app.get("app_id"),
            "query": content,
            "inputs": {},
            "response_mode": "streaming"
        }
        
        # 检查app_id是否存在
        if not invoke_params["app_id"]:
            logger.error("未配置app_id，这是调用Dify API的必要参数")
        
        # 只有当获取到有效的conversation_id时才添加到参数中
        if conversation_id:
            invoke_params["conversation_id"] = conversation_id
        
        try:
            # 调用AI接口
            logger.info(f"调用Dify API，参数: app_id={invoke_params['app_id']}" +
                      (f", conversation_id={conversation_id[:8]}..." if conversation_id else ", 新对话"))
            
            try:
                response_generator = session.app.chat.invoke(**invoke_params)
            except Exception as e:
                logger.error(f"调用Dify API失败: {str(e)}")
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    logger.error(f"API错误响应: {e.response.text}")
                raise
            
            # 尝试从第一个响应块中提取conversation_id
            try:
                # 获取第一个响应块
                first_chunk = next(response_generator)
                
                # 检查是否包含conversation_id
                if isinstance(first_chunk, dict) and 'conversation_id' in first_chunk:
                    self.new_conversation_id = first_chunk['conversation_id']
                    logger.debug(f"获取到新会话ID: {self.new_conversation_id[:8]}...")
                
                # 创建一个新的生成器，首先返回第一个块，然后返回原始生成器的其余部分
                def combined_generator():
                    yield first_chunk
                    yield from response_generator
                
                return combined_generator()
            except StopIteration:
                logger.warning("AI响应生成器为空")
                return (x for x in [])
            except Exception as e:
                logger.error(f"获取会话ID时出错: {str(e)}")
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    logger.error(f"API错误响应: {e.response.text}")
                return response_generator
        except Exception as e:
            logger.error(f"调用AI接口失败: {str(e)}")
            return (x for x in [])
    
    def _process_ai_response(self, response_generator: Any) -> str:
        """处理AI接口流式响应"""
        if not response_generator:
            return "系统处理中，请稍后再试"
        
        start_time = time.time()
        message_end_received = False
        chunk_count = 0
        full_content = ""
        
        try:
            # 遍历流式响应
            for chunk in self._safe_iterate(response_generator):
                chunk_count += 1
                
                # 检查块是否有效
                if not isinstance(chunk, dict):
                    continue
                
                # 处理消息内容
                if 'answer' in chunk:
                    full_content += chunk.get('answer', '')
                
                # 检查消息结束事件
                if chunk.get('event') == 'message_end':
                    message_end_received = True
                    break  # 收到结束事件后直接退出循环
            
            # 计算处理总时间
            total_time = time.time() - start_time
            
            logger.info(f"流式响应处理完成，共{chunk_count}个响应块，耗时: {total_time:.2f}秒")
            
            # 返回完整回复内容
            return full_content or "AI没有给出回复"
        except Exception as e:
            logger.error(f"处理流式响应时出错: {str(e)}")
            return f"处理AI回复时出现问题: {str(e)}"
    
    def _safe_iterate(self, response_generator):
        """安全地遍历生成器，添加超时保护"""
        done = False

        while not done:
            try:
                # 使用超时线程来防止无限阻塞
                chunk_received = [None]
                iteration_done = [False]
                exception_caught = [None]
                
                def get_next_chunk():
                    try:
                        chunk_received[0] = next(response_generator)
                    except StopIteration:
                        iteration_done[0] = True
                    except Exception as e:
                        exception_caught[0] = e
                
                # 创建获取下一个chunk的线程
                thread = threading.Thread(target=get_next_chunk)
                thread.daemon = True
                thread.start()
                
                # 等待线程完成或超时
                thread.join(timeout=STREAM_CHUNK_TIMEOUT)
                
                # 检查线程是否仍在运行（超时）
                if thread.is_alive():
                    logger.warning(f"获取流式响应块超时(已等待{STREAM_CHUNK_TIMEOUT}秒)")
                    done = True
                    break
                
                # 检查是否迭代结束
                if iteration_done[0]:
                    done = True
                    break
                
                # 检查是否有异常
                if exception_caught[0]:
                    logger.error(f"流式响应迭代出错: {exception_caught[0]}")
                    if hasattr(exception_caught[0], 'response') and hasattr(exception_caught[0].response, 'text'):
                        logger.error(f"API错误响应: {exception_caught[0].response.text}")
                    raise exception_caught[0]
                
                # 返回获取到的chunk
                yield chunk_received[0]
                
            except Exception as e:
                logger.error(f"迭代流式响应时出错: {str(e)}")
                done = True
                break 
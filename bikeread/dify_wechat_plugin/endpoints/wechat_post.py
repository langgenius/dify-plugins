import logging
import threading
import time
import json
from typing import Mapping, Optional, Dict, Any
from werkzeug import Request, Response
from dify_plugin import Endpoint

from endpoints.wechat.handlers import MessageHandler
# 导入拆分后的组件
from endpoints.wechat.parsers import MessageParser
from endpoints.wechat.factory import MessageHandlerFactory
from endpoints.wechat.formatters import ResponseFormatter
from endpoints.wechat.crypto import WechatMessageCryptoAdapter
from endpoints.wechat.api import WechatCustomMessageSender
# 导入重试跟踪器
from endpoints.wechat.retry_tracker import MessageStatusTracker

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 默认超时和响应设置
DEFAULT_HANDLER_TIMEOUT = 5.0  # 默认超时时间5.0秒，固定值
DEFAULT_TEMP_RESPONSE = "内容生成耗时较长，请稍等..."  # 默认临时响应消息
# 重试等待时间为正常超时时间的一半
RETRY_WAIT_TIMEOUT = DEFAULT_HANDLER_TIMEOUT * 0.8  # 重试时使用较短的等待时间
# 清除历史标识消息
CLEAR_HISTORY_MESSAGE = "清除历史聊天记录"


class WechatPost(Endpoint):
    """微信公众号消息处理端点"""
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """处理微信请求"""
        # 记录请求信息
        logger.info("===== 微信请求信息 =====")
        logger.debug(f"请求方法: {r.method}, URL: {r.url}")
        logger.debug(f"请求头: {dict(r.headers)}")
        
        # 记录查询参数和表单数据(如果有)
        if r.args:
            logger.debug(f"查询参数: {dict(r.args)}")
        
        # 获取请求体 - 减少单独的try-catch
        body = ""
        try:
            body = r.get_data(as_text=True)
        except Exception as e:
            logger.warning(f"读取请求体时出错: {str(e)}")
        
        # 记录插件配置 - 减少单独的try-catch
        if 'app' in settings:
            app_config = settings.get('app', {})
            logger.debug(f"应用配置: app_id={app_config.get('app_id', '未配置')}")
        
        # 1. 获取配置的临时响应消息
        temp_response_message = settings.get('WECHAT_TEMP_RESPONSE', DEFAULT_TEMP_RESPONSE)
        
        try:
            # 2. 创建加密适配器
            crypto_adapter = WechatMessageCryptoAdapter(settings)
            
            # 3. 解密消息
            try:
                decrypted_data = crypto_adapter.decrypt_message(r)
                logger.debug(f"解密后数据: {decrypted_data}")
            except Exception as e:
                logger.error(f"解密消息失败: {str(e)}")
                return Response('解密失败', status=400)
                
            # 4. 解析消息内容
            message = MessageParser.parse_xml(decrypted_data)
            # 创建处理器并调用清除缓存方法
            handler = MessageHandlerFactory.get_handler(message.msg_type)
            # 如果收到清除历史记录的指令
            if message.content == CLEAR_HISTORY_MESSAGE:
                success = handler.clear_cache(self.session, message.from_user)
                
                # 返回清除结果
                result_message = "已清除历史聊天记录" if success else "清除历史记录失败，请稍后再试"
                logger.info(f"清除历史记录操作: {result_message}")
                
                # 返回响应
                response_xml = ResponseFormatter.format_xml(message, result_message)
                encrypted_response = crypto_adapter.encrypt_message(response_xml, r)
                return Response(encrypted_response, status=200, content_type="application/xml")
                
            # 5. 使用MessageStatusTracker跟踪消息状态
            message_status = MessageStatusTracker.track_message(message.msg_id)
            retry_count = message_status.get('retry_count', 0)
            
            # 初始化结果已返回标志
            message_status['result_returned'] = False
            
            # 6. 处理重试请求
            if retry_count > 0:
                logger.info(f"检测到重试请求，当前重试次数: {retry_count}")
                return self._handle_retry(message, message_status, retry_count, 
                                        temp_response_message, crypto_adapter, r)
            
            # 7. 处理首次请求
            return self._handle_first_request(message, message_status, settings, 
                                            handler, crypto_adapter, r)
        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}")
            return Response("", status=200, content_type="application/xml")
    
    def _handle_retry(self, message, message_status, retry_count, 
                     temp_message, crypto_adapter, request):
        """处理重试请求"""
        # 获取完成事件
        completion_event = message_status.get('completion_event')
        
        # 直接等待处理完成或超时
        # 如果已完成，wait会立即返回True；如果未完成，才会等待指定时间
        is_completed = False
        if completion_event:
            is_completed = completion_event.wait(timeout=RETRY_WAIT_TIMEOUT)
        
        if is_completed or message_status.get('is_completed', False):
            # 处理已完成，返回结果
            logger.debug(f"重试请求: 处理已完成或等待期间完成，直接返回结果")
            response_content = message_status.get('result', '') or "抱歉，处理结果为空"
            
            # 使用原子操作标记结果已返回
            if not MessageStatusTracker.mark_result_returned(message.msg_id):
                logger.debug(f"重试请求: 结果已被其他线程返回，跳过处理")
                return Response("", status=200)
            
            # HTTP返回了完整结果，显式设置skip_custom_message标记
            # 这样比只设置retry_completion_event更明确
            message_status['skip_custom_message'] = True
            
            # 设置重试完成事件，同时也通知客服消息线程
            retry_completion_event = message_status.get('retry_completion_event')
            if retry_completion_event:
                logger.debug(f"重试请求: HTTP已返回完整结果，通知客服消息线程跳过发送")
                retry_completion_event.set()
            
            # 格式化并返回响应
            response_xml = ResponseFormatter.format_xml(message, response_content)
            encrypted_response = crypto_adapter.encrypt_message(response_xml, request)
            return Response(encrypted_response, status=200, content_type="application/xml")
        
        # 等待后仍未完成，继续原有的重试策略
        logger.debug(f"重试请求: 处理未完成，第{retry_count}次重试")
        if retry_count < 2:  # 前两次重试返回500状态码
            logger.debug(f"重试请求: 返回500状态码以触发后续重试")
            return Response("", status=500)
        else:  # 最后一次重试，返回临时消息
            logger.info(f"重试请求: 最后一次重试，返回临时消息")
            
            # 获取重试完成事件并设置，通知客服消息线程可以开始发送
            # 但不设置skip_custom_message，表示需要通过客服消息发送完整结果
            retry_completion_event = message_status.get('retry_completion_event')
            if retry_completion_event:
                logger.debug(f"重试请求: 最后一次重试完成，通知客服消息线程可以开始发送")
                retry_completion_event.set()
            
            response_xml = ResponseFormatter.format_xml(message, temp_message)
            encrypted_response = crypto_adapter.encrypt_message(response_xml, request)
            return Response(encrypted_response, status=200, content_type="application/xml")
    
    def _handle_first_request(self, message, message_status, settings, 
                             handler: MessageHandler, crypto_adapter, request):
        
        # 创建完成事件
        completion_event = threading.Event()
        message_status['completion_event'] = completion_event
        
        # 创建重试完成事件，用于通知客服消息线程
        retry_completion_event = threading.Event()
        message_status['retry_completion_event'] = retry_completion_event
        
        # 初始化客服消息跳过标记为False
        message_status['skip_custom_message'] = False
        
        # 启动异步处理线程
        thread = threading.Thread(
            target=self._async_process_message,
            args=(handler, message, settings, message_status, completion_event),
            daemon=True,
            name=f"Msg-{message.msg_id}-Processor"
        )
        
        # 记录处理开始时间并启动线程
        thread.start()
        
        # 等待处理完成或超时
        is_completed = completion_event.wait(timeout=DEFAULT_HANDLER_TIMEOUT)
        
        if is_completed:
            # 处理已完成，直接返回结果
            response_content = message_status.get('result', '') or "抱歉，处理结果为空"
            
            # 首次请求直接标记结果已返回，不存在竞争情况
            MessageStatusTracker.mark_result_returned(message.msg_id)
            
            # 格式化并返回响应
            response_xml = ResponseFormatter.format_xml(message, response_content)
            encrypted_response = crypto_adapter.encrypt_message(response_xml, request)
            return Response(encrypted_response, status=200, content_type="application/xml")
        else:
            # 处理超时，发送临时响应并继续异步处理
            logger.info(f"首次请求: 处理超时，转为异步处理")
            
            # 启动异步发送客服消息线程
            async_thread = threading.Thread(
                target=self._wait_and_send_custom_message,
                args=(message, message_status, settings, completion_event),
                daemon=True,
                name=f"Msg-{message.msg_id}-CustomerMsgSender"
            )
            async_thread.start()
            
            return Response("", status=500)
    
    def _async_process_message(self, handler, message, settings, message_status, completion_event):
        """异步处理消息"""
        start_time = time.time()
        
        try:
            logger.debug(f"异步处理: 开始处理消息 {message.msg_id}")
            
            # 使用处理器处理消息
            result = handler.handle(message, self.session, settings)
            
            # 打印完整结果（debug级别）
            logger.debug(f"异步处理: 获取到完整结果:\n{result}")
            
            # 更新状态
            message_status['result'] = result
            message_status['is_completed'] = True
            
            # 更新跟踪器
            MessageStatusTracker.update_status(
                message.msg_id,
                result=result,
                is_completed=True
            )
        except Exception as e:
            logger.error(f"异步处理: 处理消息时出错: {str(e)}")
            
            # 更新错误状态
            error_msg = f"处理失败: {str(e)}"
            message_status['result'] = error_msg
            message_status['error'] = error_msg
            message_status['is_completed'] = True
            
            # 更新跟踪器
            MessageStatusTracker.update_status(
                message.msg_id,
                result=error_msg,
                is_completed=True,
                error=error_msg
            )
        finally:
            # 设置完成事件
            completion_event.set()
            
            # 记录处理耗时
            elapsed = time.time() - start_time
            logger.info(f"异步处理: 消息 {message.msg_id} 处理完成，耗时 {elapsed:.2f}秒")
    
    def _wait_and_send_custom_message(self, message, message_status, settings, completion_event):
        """等待处理完成并发送客服消息"""
        try:
            # 首先等待处理完成（最多5分钟）
            is_completed = completion_event.wait(timeout=300)
            
            if not is_completed:
                logger.warning(f"客服消息: 等待处理超时(>5分钟)，强制结束等待")
                MessageStatusTracker.update_status(
                    message.msg_id,
                    result="处理超时，请重试",
                    is_completed=True,
                    error="处理超时(>5分钟)"
                )
                return
            
            # 等待重试流程完成（使用事件而不是轮询）
            retry_completion_event = message_status.get('retry_completion_event')
            if retry_completion_event:
                logger.debug(f"客服消息: 等待重试流程完成...")
                # 设置一个合理的超时时间，例如20秒
                retry_completed = retry_completion_event.wait(timeout=20)
                
                if not retry_completed:
                    logger.warning(f"客服消息: 等待重试完成超时(>20秒)")
                else:
                    logger.debug(f"客服消息: 重试流程已完成")
            
            # 检查是否应该跳过客服消息发送
            if message_status.get('skip_custom_message', False):
                logger.debug(f"客服消息: HTTP已返回完整结果，跳过客服消息发送")
                return
            
            # 使用原子操作标记结果已返回，如果标记失败则说明结果已由HTTP返回
            if not MessageStatusTracker.mark_result_returned(message.msg_id):
                logger.debug(f"客服消息: 结果已被其他途径返回，跳过客服消息发送")
                return
                
            # 获取处理结果
            content = message_status.get('result', '') or "抱歉，无法获取处理结果"
            
            # 打印完整内容（debug级别）
            logger.debug(f"消息完整内容:\n{content}")
            
            # 检查配置中是否有客服消息所需的参数
            app_id = settings.get('app_id')
            app_secret = settings.get('app_secret')
            
            if not app_id or not app_secret:
                logger.error("客服消息: 缺少app_id或app_secret配置")
                return
            
            # 初始化客服消息发送器并发送消息
            sender = WechatCustomMessageSender(app_id, app_secret)
            logger.debug(f"客服消息: 发送给用户 {message.from_user}，内容长度: {len(content)}")
            
            send_result = sender.send_text_message(
                open_id=message.from_user,
                content=content
            )
            
            if send_result.get('success'):
                logger.info("客服消息: 发送成功")
            else:
                error_msg = send_result.get('error', '未知错误')
                logger.error(f"客服消息: 发送失败: {error_msg}")
        except Exception as e:
            logger.error(f"客服消息: 处理过程中出错: {str(e)}")

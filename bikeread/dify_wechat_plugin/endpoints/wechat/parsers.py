import logging
import xml.etree.ElementTree as ET
from .models import WechatMessage

logger = logging.getLogger(__name__)

class MessageParser:
    """消息解析器"""
    @staticmethod
    def parse_xml(raw_data: str) -> WechatMessage:
        """
        解析XML数据为WechatMessage对象
        
        参数:
            raw_data: XML格式的原始数据
            
        返回:
            WechatMessage对象
            
        异常:
            ValueError: 当XML解析失败时
        """
        try:
            xml_data = ET.fromstring(raw_data)
            
            # 提取公共字段
            msg_type = xml_data.find('MsgType').text
            from_user = xml_data.find('FromUserName').text
            to_user = xml_data.find('ToUserName').text
            create_time = xml_data.find('CreateTime').text
            
             # 提取消息ID（如果存在）
            msg_id_elem = xml_data.find('MsgId')
            msg_id = msg_id_elem.text if msg_id_elem is not None else None

            
            # 根据不同消息类型提取特定字段
            if msg_type == 'text':
                content = xml_data.find('Content').text
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    content=content
                )
            
            elif msg_type == 'image':
                pic_url = xml_data.find('PicUrl').text
                media_id = xml_data.find('MediaId').text
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    pic_url=pic_url,
                    media_id=media_id
                )
            
            elif msg_type == 'voice':
                media_id = xml_data.find('MediaId').text
                format_elem = xml_data.find('Format')
                format = format_elem.text if format_elem is not None else None
                
                # 语音识别结果（可能不存在）
                recognition_elem = xml_data.find('Recognition')
                recognition = recognition_elem.text if recognition_elem is not None else None
                
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    media_id=media_id,
                    format=format,
                    recognition=recognition
                )
            
            elif msg_type == 'video' or msg_type == 'shortvideo':
                media_id = xml_data.find('MediaId').text
                thumb_media_id = xml_data.find('ThumbMediaId').text
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    media_id=media_id,
                    thumb_media_id=thumb_media_id
                )
            
            elif msg_type == 'location':
                location_x = xml_data.find('Location_X').text
                location_y = xml_data.find('Location_Y').text
                scale = xml_data.find('Scale').text
                label = xml_data.find('Label').text
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    location_x=location_x,
                    location_y=location_y,
                    scale=scale,
                    label=label
                )
            
            elif msg_type == 'link':
                title = xml_data.find('Title').text
                description = xml_data.find('Description').text
                url = xml_data.find('Url').text
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id,
                    title=title,
                    description=description,
                    url=url
                )
            
            elif msg_type == 'event':
                # 事件类型消息
                event = xml_data.find('Event').text
                event_key_elem = xml_data.find('EventKey')
                event_key = event_key_elem.text if event_key_elem is not None else None
                
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    content=f"event:{event}:{event_key}"
                )
            
            else:
                # 默认构造基本消息对象
                logger.warning(f"未知消息类型: {msg_type}")
                return WechatMessage(
                    msg_type=msg_type,
                    from_user=from_user,
                    to_user=to_user,
                    create_time=create_time,
                    msg_id=msg_id
                )
                
        except Exception as e:
            logger.error(f"XML解析失败: {str(e)}")
            raise ValueError(f"无法解析XML: {str(e)}") 
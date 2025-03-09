from typing import Optional, Dict, Any, List

class WechatMessage:
    """微信消息实体类"""
    def __init__(self, 
                 msg_type: str, 
                 from_user: str, 
                 to_user: str, 
                 create_time: str, 
                 msg_id: Optional[str] = None,
                 content: Optional[str] = None,
                 pic_url: Optional[str] = None,
                 media_id: Optional[str] = None,
                 format: Optional[str] = None,
                 recognition: Optional[str] = None,
                 thumb_media_id: Optional[str] = None,
                 location_x: Optional[str] = None,
                 location_y: Optional[str] = None,
                 scale: Optional[str] = None,
                 label: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 url: Optional[str] = None):
        """
        初始化微信消息对象
        
        参数:
            msg_type: 消息类型 (如 'text', 'image', 'voice', 'link' 等)
            from_user: 发送者的OpenID
            to_user: 接收者的ID (公众号原始ID)
            create_time: 消息创建时间
            msg_id: 消息ID
            content: 文本消息内容 (对文本消息有效)
            pic_url: 图片链接 (对图片消息有效)
            media_id: 图片或语音的媒体ID
            format: 语音格式 (对语音消息有效)
            recognition: 语音识别结果 (对语音消息有效)
            thumb_media_id: 视频消息缩略图的媒体ID
            location_x: 地理位置纬度
            location_y: 地理位置经度
            scale: 地图缩放大小
            label: 地理位置信息
            title: 消息标题 (对链接消息有效)
            description: 消息描述 (对链接消息有效)
            url: 消息链接 (对链接消息有效)
        """
        self.msg_type = msg_type
        self.from_user = from_user
        self.to_user = to_user
        self.create_time = create_time
        self.msg_id = msg_id
        
        # 文本消息特有属性
        self.content = content
        
        # 图片消息特有属性
        self.pic_url = pic_url
        self.media_id = media_id
        
        # 语音消息特有属性
        self.format = format
        self.recognition = recognition
        
        # 视频消息特有属性
        self.thumb_media_id = thumb_media_id
        
        # 地理位置消息特有属性
        self.location_x = location_x
        self.location_y = location_y
        self.scale = scale
        self.label = label
        
        # 链接消息特有属性
        self.title = title
        self.description = description
        self.url = url
    
    def __str__(self) -> str:
        """返回消息的字符串表示"""
        if self.msg_type == 'text':
            return f"WechatMessage(type={self.msg_type}, from={self.from_user}, content={self.content})"
        elif self.msg_type == 'image':
            return f"WechatMessage(type={self.msg_type}, from={self.from_user}, pic_url={self.pic_url})"
        elif self.msg_type == 'voice':
            return f"WechatMessage(type={self.msg_type}, from={self.from_user}, format={self.format})"
        elif self.msg_type == 'link':
            return f"WechatMessage(type={self.msg_type}, from={self.from_user}, title={self.title}, url={self.url})"
        else:
            return f"WechatMessage(type={self.msg_type}, from={self.from_user})" 
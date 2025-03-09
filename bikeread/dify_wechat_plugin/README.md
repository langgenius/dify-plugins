# Dify微信公众号插件

**作者:** bikeread  
**版本:** 0.1.4  
**类型:** extension  

## 项目概述

Dify微信公众号插件允许将Dify AI应用与微信公众号无缝集成，使用户能够通过微信公众号与AI进行对话交互。该插件处理微信公众号的消息接收和回复，支持会话记忆功能，确保连续对话的上下文保持。

## 功能特点

- 支持微信公众号服务器配置验证（token验证）
- 支持明文模式和加密模式（自动识别）
- 接收并处理多种类型的用户消息：
  - 文本消息：直接处理用户发送的文字内容 
  - 图片消息：处理用户发送的图片，提取图片URL -待开发
  - 语音消息：支持语音识别结果（如果公众号已开启语音识别功能）-待开发
  - 链接消息：处理用户分享的链接，提取标题、描述和URL -待开发
- 调用Dify AI应用进行智能回复 支持聊天助手、ChatFlow、Agent
- 支持会话记忆，保持对话连续性
- 处理微信5秒超时限制，利用微信三次重试回调，延长消息回复至15秒，如还未生成完整答复，会异步调用客服消息接口发送回复
- 支持Dify流式(streaming)响应，在插件内部组装完整回复内容，返回用户

## 配置说明

### 微信公众号配置

1. 登录微信公众平台（https://mp.weixin.qq.com/）
2. 进入"设置与开发" -> "基本配置"
3. 在"服务器配置"部分：
   - URL设置为您的Dify插件访问地址，例如：`http://your-domain.com/wechat/input`
   - Token设置一个自定义的安全令牌（需要记住此令牌）
   - 消息加解密方式：选择明文模式、兼容模式或安全模式
   - 如果选择兼容模式或安全模式，需要设置EncodingAESKey（点击"随机生成"按钮自动生成）
   - 点击启用配置
4. 如需启用语音识别功能，请在"接口权限" -> "接口设置" -> "接收语音识别结果"中开启
5. 如需启用客服消息功能（用于处理长耗时请求），请确保已获得该接口的调用权限

### 插件配置

在Dify平台配置此插件时，需要设置以下参数：

- `wechat_token`: 与公众号平台配置相同的Token

如果您的公众号启用了加密模式（兼容模式或安全模式），还需要添加以下配置：

- `encoding_aes_key`: 与公众号平台配置的EncodingAESKey相同
- `app_id`: 公众号的AppID（在公众号平台的基本配置中可以找到）

对于支持异步客服消息功能（处理长耗时请求），还需要添加：

- `app_secret`: 公众号的AppSecret（在公众号平台的基本配置中可以找到）

可选配置参数：

- `timeout_message`: 超时时发送的临时响应消息，默认为"内容生成耗时较长，请稍等..."

系统会根据`encoding_aes_key`是否存在自动判断是否使用加密模式。

## 加密模式说明

微信公众平台支持三种消息加解密方式：

1. **明文模式**：消息以明文方式传输，不进行加密。
   - 配置简单，但安全性较低
   - 只需配置`wechat_token`，无需设置`encoding_aes_key`和`app_id`

2. **兼容模式/安全模式**：消息需要加密处理。
   - 安全性更高，需要额外的加解密处理
   - 需要配置：`wechat_token`, `encoding_aes_key`, `app_id`


## 使用方法

### 基本使用流程

1. 安装插件后，完成上述配置保存
2. 用户关注您的微信公众号
3. 用户发送消息（文本、图片、语音或链接），目前只处理了文本消息
4. 系统自动调用配置的Dify AI应用处理消息
5. 将AI回复转发给用户

### 支持的消息类型及处理方式

1. **文本消息**：
   - 直接将用户发送的文本内容传递给AI进行处理
   - 示例：用户发送"你好，请介绍一下你自己"

2. **图片消息**：待调整
   - 将图片URL提取并以文本形式传递给AI
   - 格式：`[图片] URL: http://example.com/image.jpg`
   - AI可以根据URL描述图片内容

3. **语音消息**：待调整
   - 如果公众号开启了语音识别功能，将使用识别结果作为文本输入
   - 如果未开启语音识别，会提示用户无法识别语音内容
   - 格式：`您的语音内容：[语音识别结果]`

4. **链接消息**：待调整
   - 提取链接的标题、描述和URL，传递给AI处理
   - 格式：`[链接] 标题: [标题]\n描述: [描述]\nURL: [URL]`

### 处理微信5秒超时限制

微信公众号要求在5秒内必须回复用户消息，否则用户会收到"该公众号暂时无法提供服务"的提示。针对AI处理耗时较长的情况，本插件采用以下策略：

1. **渐进式响应机制**：
   - 首次请求：如AI在4秒内完成，直接返回完整结果
   - 未完成时：返回状态码触发微信自动重试（最多2次）
   - 最后一次重试：如仍未完成，返回临时提示信息

2. **客服消息兜底**：
   - 当所有重试机会用尽后，通过客服消息API发送完整结果
   - 确保即使超出15秒限制，用户也能收到完整回复

3. **防重复机制**：
   - 使用原子化标记和事件通知，确保每条消息只发送一次
   - 无论是HTTP响应还是客服消息，只有一种方式会生效

4. **配置要求**：使用客服消息功能需提供公众号的`app_id`和`app_secret`

## 架构说明

本插件采用模块化设计，主要组件包括：

### 目录结构
```
endpoints/
├── wechat/                    # 微信处理核心模块
│   ├── __init__.py            # 包初始化文件
│   ├── models.py              # 定义WechatMessage消息模型
│   ├── parsers.py             # 定义XML解析器
│   ├── formatters.py          # 定义响应格式化器
│   ├── factory.py             # 定义消息处理器工厂
│   ├── crypto.py              # 微信消息加解密工具
│   ├── retry_tracker.py       # 消息重试跟踪器
│   ├── api/                   # API调用相关
│   │   ├── __init__.py        # API包初始化
│   │   └── custom_message.py  # 客服消息发送器
│   └── handlers/              # 消息处理器
│       ├── __init__.py        # 处理器包初始化
│       ├── base.py            # 定义处理器抽象基类
│       ├── text.py            # 文本消息处理器
│       ├── image.py           # 图片消息处理器
│       ├── voice.py           # 语音消息处理器
│       ├── link.py            # 链接消息处理器
│       └── unsupported.py     # 不支持的消息类型处理器
├── wechat_get.py              # 处理微信服务器验证请求
└── wechat_post.py             # 处理用户发送的消息
```

### 消息处理流程

1. **消息接收**：`wechat_post.py` 接收微信服务器发来的消息
2. **消息解析**：使用 `MessageParser` 解析XML格式的消息
3. **重试检测**：使用 `MessageStatusTracker` 判断是否为重试请求
4. **消息处理**：
   - 首次请求：启动异步线程处理，等待一定时间（默认5.0秒）
   - 重试请求：先等待一段较短时间（默认4.0秒），然后根据处理状态返回适当响应
5. **响应返回**：使用 `ResponseFormatter` 格式化回复，加密后返回
6. **后台处理**：如果处理超时，通过客服消息发送完整回复

### 设计模式

本插件使用了多种设计模式：

1. **策略模式**: 通过`MessageHandler`抽象类定义统一接口，不同消息类型使用不同的实现
2. **工厂模式**: 使用`MessageHandlerFactory`根据消息类型创建相应处理器
3. **适配器模式**: 使用解析器和格式化器转换不同格式的数据
4. **装饰器模式**: 使用装饰器处理消息的加解密
5. **观察者模式**: 使用线程和事件通知机制监控处理完成
6. **异步处理模式**: 使用子线程处理长耗时请求，避免微信超时
7. **单例模式**: `MessageStatusTracker`使用类变量实现单例状态跟踪

## 扩展开发指南

### 添加新的消息类型支持

要添加对新消息类型（如视频、小程序消息等）的支持，按以下步骤操作：

1. 在`handlers`目录下创建新的处理器类，继承`MessageHandler`：

```python
# handlers/video.py
from typing import Dict, Any
from .base import MessageHandler
from ..models import WechatMessage

class VideoMessageHandler(MessageHandler):
    def handle(self, message: WechatMessage, session: Any, app_settings: Dict[str, Any]) -> str:
        # 实现视频消息处理逻辑
        # ...
        return "收到您的视频，正在处理..."
```

2. 在`MessageHandlerFactory`中注册新的处理器：

```python
# 在项目初始化时注册
from endpoints.wechat.factory import MessageHandlerFactory
from endpoints.wechat.handlers.video import VideoMessageHandler

MessageHandlerFactory.register_handler('video', VideoMessageHandler)
```

### 自定义响应格式

要支持更复杂的响应格式（如图文消息），可以扩展`ResponseFormatter`：

```python
@staticmethod
def format_news_xml(message: WechatMessage, articles: list) -> str:
    # 实现图文消息XML格式化
    # ...
```

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。




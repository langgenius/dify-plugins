import base64
import string
import random
import hashlib
import time
import struct
import json
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET
import socket
import logging

logger = logging.getLogger(__name__)

class PKCS7Encoder:
    """提供基于PKCS7算法的加解密接口"""
    block_size = 32  # 微信官方AES加密使用32字节块大小

    @staticmethod
    def encode(text):
        """对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文(bytes)
        @return: 补齐明文字符串(bytes)
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = PKCS7Encoder.block_size - (text_length % PKCS7Encoder.block_size)
        if amount_to_pad == 0:
            amount_to_pad = PKCS7Encoder.block_size
        # 获得补位所用的字符
        pad_byte = bytes([amount_to_pad])
        padding = pad_byte * amount_to_pad
        # 返回补齐明文的bytes
        return text + padding

    @staticmethod
    def decode(decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文(bytes)
        @return: 删除补位字符后的明文(bytes)
        """
        # Python 3中bytes的最后一个字节直接就是数字，不需要ord()
        pad = decrypted[-1]
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class WechatCrypto:
    """微信消息加解密工具类"""
    
    def __init__(self, token, encoding_aes_key, app_id):
        """
        初始化加密工具
        
        参数:
            token: 微信公众号配置的Token
            encoding_aes_key: 微信公众号的EncodingAESKey
            app_id: 微信公众号的AppID
        """
        self.token = token
        self.app_id = app_id
        # EncodingAESKey需要额外添加一个等号进行Base64解码
        self.aes_key = base64.b64decode(encoding_aes_key + "=")
        if len(self.aes_key) != 32:
            raise ValueError("无效的EncodingAESKey，解码后长度必须为32字节")
        
    def encrypt_message(self, reply_msg, nonce, timestamp=None, format='xml'):
        """
        加密回复消息
        
        参数:
            reply_msg: 回复消息字符串
            nonce: 随机字符串
            timestamp: 时间戳（如果为None则使用当前时间）
            format: 返回格式，'xml'或'json'
            
        返回:
            加密后的消息字符串
        """
        if timestamp is None:
            timestamp = str(int(time.time()))
            
        # 加密消息内容
        encrypt = self._encrypt(reply_msg)
        
        # 生成安全签名
        signature = self._gen_signature(timestamp, nonce, encrypt)
        
        # 根据指定格式构造结果
        if format == 'json':
            result = self._gen_encrypted_json(encrypt, signature, timestamp, nonce)
        else:
            result = self._gen_encrypted_xml(encrypt, signature, timestamp, nonce)
        
        return result
        
    def decrypt_message(self, post_data, msg_signature, timestamp, nonce):
        """
        解密微信消息
        
        参数:
            post_data: 接收到的XML消息数据
            msg_signature: 消息签名
            timestamp: 时间戳
            nonce: 随机字符串
            
        返回:
            解密后的消息字符串
        """
        try:
            # 判断是XML还是JSON
            if post_data.startswith('<'):
                # XML格式
                xml_tree = ET.fromstring(post_data)
                encrypt = xml_tree.find("Encrypt").text
            else:
                # JSON格式
                try:
                    json_data = json.loads(post_data)
                    encrypt = json_data.get("Encrypt", "")
                except:
                    logger.error("无法解析JSON数据")
                    raise ValueError("无法解析的数据格式")
            
            # 验证安全签名
            signature = self._gen_signature(timestamp, nonce, encrypt)
            if signature != msg_signature:
                raise ValueError("签名验证失败")
            
            # 解密
            decrypted = self._decrypt(encrypt)
            
            return decrypted
        except Exception as e:
            logger.error(f"解密消息失败: {str(e)}")
            raise
    
    def _encrypt(self, text):
        """
        对消息进行加密
        """
        # 确保text是字节类型
        text_bytes = text.encode('utf-8') if isinstance(text, str) else text
        
        # 16位随机字符串添加到明文开头
        random_str_bytes = self._get_random_str().encode('utf-8')
        
        # 使用网络字节序处理内容长度
        network_order = struct.pack("I", socket.htonl(len(text_bytes)))
        
        # 拼接明文
        app_id_bytes = self.app_id.encode('utf-8')
        content = random_str_bytes + network_order + text_bytes + app_id_bytes
        
        # 使用PKCS7填充
        padded_content = PKCS7Encoder.encode(content)
        
        # 加密
        cryptor = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        encrypted = cryptor.encrypt(padded_content)
        
        # Base64编码
        return base64.b64encode(encrypted).decode('utf-8')
    
    def _decrypt(self, encrypted_text):
        """
        对加密消息进行解密
        """
        try:
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_text)
            
            # 解密
            cryptor = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            decrypted_data = cryptor.decrypt(encrypted_data)
            
            # 使用PKCS7去除填充
            plain_bytes = PKCS7Encoder.decode(decrypted_data)
            
            # 提取消息内容
            content = plain_bytes[16:]  # 去除16位随机字符串
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4:xml_len+4]
            from_appid = content[xml_len+4:].decode('utf-8')
            
            # 校验AppID
            if from_appid != self.app_id:
                raise ValueError(f"AppID校验失败: {from_appid} != {self.app_id}")
            
            return xml_content.decode('utf-8')
        except Exception as e:
            logger.error(f"解密失败: {str(e)}")
            raise
    
    def _gen_signature(self, timestamp, nonce, encrypt):
        """
        生成安全签名
        """
        sign_list = [self.token, timestamp, nonce, encrypt]
        sign_list.sort()
        sign_str = ''.join(sign_list)
        
        # SHA1加密
        sha = hashlib.sha1()
        sha.update(sign_str.encode('utf-8'))
        return sha.hexdigest()
    
    def _gen_encrypted_xml(self, encrypt, signature, timestamp, nonce):
        """
        生成加密XML
        """
        xml = f"""<xml>
<Encrypt><![CDATA[{encrypt}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        return xml
    
    def _gen_encrypted_json(self, encrypt, signature, timestamp, nonce):
        """
        生成加密JSON
        """
        json_data = {
            "Encrypt": encrypt,
            "MsgSignature": signature,
            "TimeStamp": timestamp,
            "Nonce": nonce
        }
        return json.dumps(json_data)
    
    def _get_random_str(self, length=16):
        """
        生成随机字符串
        """
        rule = string.ascii_letters + string.digits
        return ''.join(random.sample(rule, length))


class WechatMessageCryptoAdapter:
    """微信消息加解密适配器"""
    
    def __init__(self, settings):
        """
        初始化适配器
        
        参数:
            settings: 插件配置
        """
        # 从配置中获取加密所需参数
        self.encoding_aes_key = settings.get('encoding_aes_key', '')
        self.app_id = settings.get('app_id', '')
        self.token = settings.get('wechat_token', '')
        
        # 根据是否有encoding_aes_key判断是否需要加密
        self.is_encrypted_mode = bool(self.encoding_aes_key)
        
        # 如果是加密模式，初始化加密工具
        if self.is_encrypted_mode:
            if not self.token or not self.app_id:
                raise ValueError("加密模式下必须提供token和app_id")
            
            self.crypto = WechatCrypto(self.token, self.encoding_aes_key, self.app_id)
        else:
            self.crypto = None
    
    def decrypt_message(self, request):
        """
        解密请求消息
        
        参数:
            request: 请求对象
            
        返回:
            解密后的XML字符串
        """
        raw_data = request.get_data(as_text=True)
        
        # 明文模式直接返回
        if not self.is_encrypted_mode:
            logger.info("未启用加密模式，返回明文")
            return raw_data
            
        # 检查是否有encrypt_type参数
        encrypt_type = request.args.get('encrypt_type', '')
        if encrypt_type != 'aes' and not request.args.get('msg_signature', ''):
            # 未指定加密类型且没有msg_signature参数，视为明文
            logger.info("未指定加密类型且没有msg_signature参数，视为明文")
            return raw_data
            
        # 加密模式需要解密
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        
        # 检查参数完整性
        if not msg_signature or not timestamp or not nonce:
            logger.warning("缺少解密所需的参数")
            return raw_data
            
        # 检查是否有msg_signature
        if not msg_signature:
            # 兼容模式下，可能是明文消息
            # 通过检查XML中是否有Encrypt节点或JSON中是否有Encrypt字段来判断
            try:
                if raw_data.startswith('<'):
                    # XML格式
                    xml_tree = ET.fromstring(raw_data)
                    encrypt_node = xml_tree.find("Encrypt")
                    if encrypt_node is None:
                        # 没有Encrypt节点，认为是明文
                        return raw_data
                else:
                    # 可能是JSON格式
                    try:
                        json_data = json.loads(raw_data)
                        if 'Encrypt' not in json_data:
                            # 没有Encrypt字段，认为是明文
                            return raw_data
                    except:
                        # 不是有效JSON，当作明文处理
                        return raw_data
            except:
                # 解析出错，当作明文处理
                return raw_data
            
        # 解密消息
        try:
            logger.info("开始解密消息")
            return self.crypto.decrypt_message(raw_data, msg_signature, timestamp, nonce)
        except Exception as e:
            logger.error(f"解密消息失败: {str(e)}")
            # 解密失败时返回明文，避免整个请求处理失败
            return raw_data
    
    def encrypt_message(self, reply_msg, request):
        """
        加密回复消息
        
        参数:
            reply_msg: 回复消息字符串
            request: 请求对象
            
        返回:
            加密后的XML或JSON字符串
        """
        # 明文模式直接返回
        if not self.is_encrypted_mode:
            return reply_msg
            
        # 检查是否需要加密(检查URL中的encrypt_type参数)
        encrypt_type = request.args.get('encrypt_type', '')
        if encrypt_type != 'aes':
            # 未指定加密类型，返回明文
            return reply_msg
            
        # 确定返回格式
        content_type = request.headers.get('Content-Type', '')
        format = 'json' if 'application/json' in content_type else 'xml'
        
        # 加密模式需要加密
        nonce = request.args.get('nonce', '')
        timestamp = request.args.get('timestamp', '')
        
        # 检查参数完整性
        if not nonce or not timestamp:
            logger.warning("缺少加密所需的参数，返回明文")
            return reply_msg
            
        try:
            return self.crypto.encrypt_message(reply_msg, nonce, timestamp, format)
        except Exception as e:
            logger.error(f"加密消息失败: {str(e)}")
            # 加密失败时返回明文，避免响应失败
            return reply_msg 
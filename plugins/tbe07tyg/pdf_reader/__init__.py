from typing import Any, Dict
from plugins import Plugin, PluginDescriptor

class PDFReaderPlugin(Plugin):
    """
    @description PDF阅读器插件类
    """
    def __init__(self, context: Dict[str, Any] = None):
        super().__init__(context)
        
    @classmethod
    def description(cls) -> PluginDescriptor:
        """
        @description 返回插件描述信息
        @return PluginDescriptor 插件描述对象
        """
        return PluginDescriptor(
            name="pdf_reader",
            description="用于读取和处理PDF文件的插件",
            version="0.1.0",
            author="Your Name",
            contributors=[],
            url="https://github.com/yourusername/dify-pdf-plugin",
            tags=["pdf", "document", "reader"],
            type="python"
        ) 
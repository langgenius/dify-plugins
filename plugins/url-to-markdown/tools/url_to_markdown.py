from collections.abc import Generator
from typing import Any
import asyncio
import logging
from crawl4ai import AsyncWebCrawler

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class UrlToMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        url = tool_parameters.get("url", "")
        
        if not url:
            yield self.create_text_message("错误：URL是必需的")
            return
            
        try:
            # 使用asyncio运行异步爬虫
            result = asyncio.run(self._crawl_url(url))
            
            # 返回Markdown结果
            yield self.create_text_message(result)
            
        except Exception as e:
            logging.error(f"处理URL时出错: {str(e)}")
            yield self.create_text_message(f"处理URL时出错: {str(e)}")
    
    async def _crawl_url(self, url: str) -> str:
        """使用crawl4ai爬取URL并转换为Markdown"""
        # 创建爬虫实例
        async with AsyncWebCrawler(verbose=False) as crawler:
            # 爬取URL
            result = await crawler.arun(
                url=url,
                bypass_cache=True  # 绕过缓存，每次都重新爬取
            )
            
            # 构建完整的Markdown内容
            markdown_content = result.markdown
            
            # 添加元数据
            title = result.metadata.get('title', 'No Title')
            description = result.metadata.get('description', '')
            
            # 构建完整的Markdown文档
            full_markdown = f"# {title}\n\n"
            
            if description:
                full_markdown += f"_{description}_\n\n"
                
            full_markdown += f"**Source URL**: {url}\n\n"
            full_markdown += "---\n\n"
            full_markdown += markdown_content
            
            # 添加图片和链接信息（如果有）
            images = getattr(result, 'images', [])
            if images:
                full_markdown += "\n\n## 图片链接\n\n"
                for i, img in enumerate(images[:10]):  # 最多显示10个图片
                    full_markdown += f"{i+1}. {img}\n"
            
            external_links = getattr(result, 'external_links', [])
            if external_links:
                full_markdown += "\n\n## 外部链接\n\n"
                for i, link in enumerate(external_links[:10]):  # 最多显示10个链接
                    full_markdown += f"{i+1}. {link}\n"
            
            return full_markdown

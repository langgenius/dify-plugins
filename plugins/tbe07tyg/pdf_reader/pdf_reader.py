import PyPDF2
import requests
import io
import magic
from typing import Dict, Any, Optional
import os

class PDFReader:
    """
    @description PDF处理核心类，提供PDF文件读取和文本提取功能
    """
    
    def __init__(self):
        """
        @description 初始化PDF阅读器
        """
        self.mime = magic.Magic(mime=True)
    
    def validate_pdf(self, file_content: bytes) -> bool:
        """
        @description 验证文件是否为PDF
        @param file_content 文件内容
        @return bool 是否为PDF文件
        """
        mime_type = self.mime.from_buffer(file_content)
        return mime_type == 'application/pdf'

    def read_pdf_from_url(self, url: str) -> str:
        """
        @description 从URL读取PDF内容
        @param url PDF文件的URL
        @return str PDF文本内容
        """
        try:
            # 确保URL包含协议
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            # 下载PDF文件
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 验证是否为PDF
            if not self.validate_pdf(response.content):
                raise ValueError("The provided URL does not point to a valid PDF file")
            
            return self._extract_text_from_bytes(response.content)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error downloading PDF: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def read_pdf_from_file(self, file_path: str) -> str:
        """
        @description 从本地文件读取PDF内容
        @param file_path PDF文件路径
        @return str PDF文本内容
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, 'rb') as file:
                content = file.read()
                
                # 验证是否为PDF
                if not self.validate_pdf(content):
                    raise ValueError("The provided file is not a valid PDF")
                
                return self._extract_text_from_bytes(content)
                
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")

    def _extract_text_from_bytes(self, content: bytes) -> str:
        """
        @description 从字节内容中提取PDF文本
        @param content PDF文件的字节内容
        @return str 提取的文本内容
        """
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = []
            
            # 提取所有页面的文本
            for page in pdf_reader.pages:
                text.append(page.extract_text())
                
            return "\n".join(text)
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def get_pdf_metadata(self, content: bytes) -> Dict[str, Any]:
        """
        @description 获取PDF元数据
        @param content PDF文件的字节内容
        @return Dict 元数据字典
        """
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            return {
                "num_pages": len(pdf_reader.pages),
                "metadata": pdf_reader.metadata
            }
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}") 
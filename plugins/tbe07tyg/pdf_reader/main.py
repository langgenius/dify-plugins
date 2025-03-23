from typing import Dict, Any
from .pdf_reader import PDFReader

def pdf_to_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    @description 将PDF转换为文本的主函数
    @param params 包含PDF URL或文件路径的参数字典
    @return Dict 包含处理结果的字典
    """
    try:
        reader = PDFReader()
        
        if 'url' in params:
            content = reader.read_pdf_from_url(params['url'])
            metadata = None  # URL模式暂不支持元数据
        elif 'file_path' in params:
            with open(params['file_path'], 'rb') as f:
                file_content = f.read()
                content = reader.read_pdf_from_file(params['file_path'])
                metadata = reader.get_pdf_metadata(file_content)
        else:
            raise ValueError("Neither URL nor file path provided")
            
        return {
            "success": True,
            "content": content,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 
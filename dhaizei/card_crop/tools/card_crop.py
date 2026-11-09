from collections.abc import Generator
import io
from pathlib import PurePosixPath

from PIL import Image, UnidentifiedImageError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.processor import MAX_FILE_BYTES, process_image


class CardCropTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        image = tool_parameters.get('image')
        if image is None:
            raise ValueError('Please upload a source image.')
        blob = image.blob
        if not blob or len(blob) > MAX_FILE_BYTES:
            raise ValueError('The image must be non-empty and no larger than 30 MiB.')
        preset = str(tool_parameters.get('preset') or '')
        try:
            # 解码前检查像素数，限制高压缩率图片的内存占用。
            with Image.open(io.BytesIO(blob)) as opened:
                if opened.width * opened.height > 16_000_000:
                    raise ValueError('Source images must not exceed 16 megapixels.')
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
            raise ValueError('The source file is not a supported, valid image.') from exc
        # 保留原始文件名，批量工作流可按输入顺序对应结果。
        name = PurePosixPath(str(image.filename or 'card').replace('\\', '/')).stem[:80] or 'card'
        content, extension = process_image(blob, preset)
        yield self.create_blob_message(content, meta={
            'filename': f'{name}_{preset}{extension}',
            'mime_type': 'image/png',
        })

"""独立校验发布包的图片输入边界与真实 SDK 文件输出。"""
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / 'package' if (ROOT / 'package').is_dir() else ROOT
sys.path.insert(0, str(PACKAGE))
from tools.card_crop import CardCropTool
from tools.processor import load_presets


def png(size=(600, 800), mode='RGBA'):
    image = Image.new(mode, size, '#76c5ba')
    ImageDraw.Draw(image).ellipse((120, 160, 450, 500), fill='#fff1db')
    output = io.BytesIO()
    image.save(output, 'PNG')
    return output.getvalue()


class CardCropCheck(unittest.TestCase):
    def setUp(self):
        self.tool = CardCropTool.from_credentials({})

    def invoke(self, blob, preset='rounded_rectangle_181x234', filename='source.png'):
        return list(self.tool._invoke({'image': SimpleNamespace(blob=blob, filename=filename), 'preset': preset}))

    def test_all_presets_return_png_files(self):
        for mode in ('RGB', 'RGBA'):
            for preset, settings in load_presets().items():
                with self.subTest(mode=mode, preset=preset):
                    messages = self.invoke(png(mode=mode), preset, 'folder/source.png')
                    self.assertEqual(len(messages), 1)
                    message = messages[0]
                    self.assertEqual(message.meta['filename'], f'source_{preset}.png')
                    self.assertEqual(message.meta['mime_type'], 'image/png')
                    with Image.open(io.BytesIO(message.message.blob)) as image:
                        self.assertEqual(image.size, (settings['width'], settings['height']))
                        self.assertEqual(image.mode, 'RGBA')
                        self.assertEqual(image.getpixel((0, 0))[3], 0)
                        self.assertEqual(image.getpixel((image.width // 2, image.height // 2))[3], 255)

    def test_rejects_invalid_inputs(self):
        for blob in (b'', b'not-an-image', b'x' * (30 * 1024 * 1024 + 1)):
            with self.subTest(size=len(blob)), self.assertRaises(ValueError):
                self.invoke(blob)
        with self.assertRaisesRegex(ValueError, 'Unknown card preset'):
            self.invoke(png(), 'invalid')
        with self.assertRaisesRegex(ValueError, '16 megapixels'):
            self.invoke(png((4001, 4000)))
        with self.assertRaisesRegex(ValueError, 'upload'):
            list(self.tool._invoke({}))


if __name__ == '__main__':
    unittest.main()

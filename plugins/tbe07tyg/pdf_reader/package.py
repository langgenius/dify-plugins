import os
import zipfile

def create_plugin_package():
    """
    @description 创建插件包
    """
    # 定义要打包的文件
    files_to_package = [
        '__init__.py',
        'main.py',
        'pdf_reader.py',
        'config.json',
        'requirements.txt',
        'manifest.yaml',
        'endpoints/pdf_reader.yaml'
    ]
    
    # 创建zip文件
    with zipfile.ZipFile('pdf_reader.difypkg', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_package:
            if os.path.exists(file):
                zipf.write(file)
            else:
                print(f"Warning: {file} not found")

if __name__ == '__main__':
    create_plugin_package() 
#!/usr/bin/env python3
"""
腾讯云联网搜索API插件测试脚本
"""

import json
import os
from tools.search import TencentCloudSearchTool


class MockRuntime:
    """模拟Dify运行时环境"""
    def __init__(self, secret_id: str, secret_key: str):
        self.credentials = {
            'secret_id': secret_id,
            'secret_key': secret_key
        }


def test_search():
    """测试搜索功能"""
    # 从环境变量获取密钥（请设置您的腾讯云密钥）
    secret_id = os.getenv('TENCENT_SECRET_ID', 'your_secret_id_here')
    secret_key = os.getenv('TENCENT_SECRET_KEY', 'your_secret_key_here')
    
    if secret_id == 'your_secret_id_here' or secret_key == 'your_secret_key_here':
        print("❌ 请设置环境变量 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY")
        print("   export TENCENT_SECRET_ID='your_actual_secret_id'")
        print("   export TENCENT_SECRET_KEY='your_actual_secret_key'")
        return
    
    # 创建工具实例
    tool = TencentCloudSearchTool()
    tool.runtime = MockRuntime(secret_id, secret_key)
    
    # 测试用例
    test_cases = [
        {
            "name": "基础搜索测试",
            "params": {
                "query": "人工智能"
            }
        },
        {
            "name": "指定网站搜索测试", 
            "params": {
                "query": "机器学习",
                "site": "github.com",
                "mode": "0"
            }
        },
        {
            "name": "多模态VR卡测试",
            "params": {
                "query": "北京天气",
                "mode": "1"
            }
        },
        {
            "name": "混合结果测试",
            "params": {
                "query": "腾讯股价",
                "mode": "2"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试 {i}: {test_case['name']}")
        print(f"参数: {json.dumps(test_case['params'], ensure_ascii=False, indent=2)}")
        print(f"{'='*50}")
        
        try:
            result = tool._invoke("test_user", test_case['params'])
            
            if isinstance(result, list):
                for j, item in enumerate(result):
                    print(f"\n结果 {j+1}:")
                    if item.get('type') == 'text':
                        print(item.get('text', ''))
                    else:
                        print(json.dumps(item, ensure_ascii=False, indent=2))
            else:
                print(f"结果: {result}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print(f"\n{'='*50}")


if __name__ == "__main__":
    print("🚀 腾讯云联网搜索API插件测试")
    print("请确保已设置正确的腾讯云API密钥环境变量")
    test_search()
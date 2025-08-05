#!/usr/bin/env python3
"""
腾讯云联网搜索API插件使用示例
Usage Examples for Tencent Cloud Search API Plugin
"""

# 示例1: 基础搜索
def basic_search_example():
    """基础搜索示例"""
    return {
        "query": "人工智能最新发展"
    }

# 示例2: 指定网站搜索
def site_specific_search_example():
    """指定网站搜索示例"""
    return {
        "query": "开源项目",
        "site": "github.com",
        "mode": "0"
    }

# 示例3: 多模态VR卡搜索
def vr_card_search_example():
    """多模态VR卡搜索示例"""
    return {
        "query": "北京天气",
        "mode": "1"  # 只返回VR卡结果
    }

# 示例4: 混合搜索结果
def mixed_search_example():
    """混合搜索结果示例"""
    return {
        "query": "腾讯股价",
        "mode": "2",  # 返回自然结果+VR卡
        "count": 20
    }

# 示例5: 时间范围搜索
def time_range_search_example():
    """时间范围搜索示例"""
    import time
    
    # 搜索最近30天的内容
    current_time = int(time.time())
    thirty_days_ago = current_time - (30 * 24 * 60 * 60)
    
    return {
        "query": "ChatGPT更新",
        "from_time": thirty_days_ago,
        "to_time": current_time,
        "mode": "0"
    }

# 示例6: 政府信息搜索（尊享版功能）
def government_search_example():
    """政府信息搜索示例（尊享版）"""
    return {
        "query": "政策解读",
        "industry": "gov",
        "mode": "0",
        "count": 30
    }

# 示例7: 新闻媒体搜索（尊享版功能）
def news_search_example():
    """新闻媒体搜索示例（尊享版）"""
    return {
        "query": "科技新闻",
        "industry": "news",
        "mode": "2",
        "count": 25
    }

# 在Dify工作流中的使用示例
DIFY_WORKFLOW_EXAMPLES = {
    "知识问答助手": {
        "description": "用于回答用户问题时搜索最新信息",
        "parameters": {
            "query": "{{user_question}}",
            "mode": "2",
            "count": 10
        }
    },
    
    "新闻摘要生成": {
        "description": "搜索特定主题的最新新闻",
        "parameters": {
            "query": "{{news_topic}}",
            "industry": "news",
            "mode": "0",
            "count": 20
        }
    },
    
    "技术文档搜索": {
        "description": "在特定技术网站搜索文档",
        "parameters": {
            "query": "{{tech_keyword}}",
            "site": "{{target_site}}",
            "mode": "0"
        }
    },
    
    "实时信息查询": {
        "description": "查询天气、股价等实时信息",
        "parameters": {
            "query": "{{real_time_query}}",
            "mode": "1"  # 优先返回VR卡结果
        }
    }
}

if __name__ == "__main__":
    print("腾讯云联网搜索API插件使用示例")
    print("="*50)
    
    examples = [
        ("基础搜索", basic_search_example()),
        ("指定网站搜索", site_specific_search_example()),
        ("VR卡搜索", vr_card_search_example()),
        ("混合搜索", mixed_search_example()),
        ("时间范围搜索", time_range_search_example()),
        ("政府信息搜索", government_search_example()),
        ("新闻媒体搜索", news_search_example())
    ]
    
    for name, params in examples:
        print(f"\n{name}:")
        print(f"参数: {params}")
    
    print(f"\n\nDify工作流使用示例:")
    for name, config in DIFY_WORKFLOW_EXAMPLES.items():
        print(f"\n{name}:")
        print(f"说明: {config['description']}")
        print(f"参数: {config['parameters']}")
"""Alt 文本 SEO 评分工具 — 纯本地计算，不调用外部 API。"""
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def _score_alt_text(alt_text: str, product_type: str = "") -> dict:
    """对 Alt 文本进行 SEO 规则评分（0-100 分）。

    与后端 pixseo/app/routes/api_v1.py 的 score_alt_text_local 保持一致：
    四个维度各 25 分：length / keywords / natural_language / descriptiveness。
    """
    suggestions = []
    text = alt_text.strip()
    text_lower = text.lower()

    if not text:
        return {
            "score": 0,
            "total_score": 0,
            "max_score": 100,
            "grade": "差",
            "dimensions": {
                "length": {"score": 0, "max": 25, "feedback": "Alt 文本为空"},
                "keywords": {"score": 0, "max": 25, "feedback": "Alt 文本为空"},
                "natural_language": {"score": 0, "max": 25, "feedback": "Alt 文本为空"},
                "descriptiveness": {"score": 0, "max": 25, "feedback": "Alt 文本为空"},
            },
            "suggestions": ["Alt 文本为空，请提供有效的图片描述"],
        }

    # ── 维度 1: 长度 (25 分) ──
    char_count = len(text)
    word_count = len(text.split())

    if 30 <= char_count <= 125:
        if 5 <= word_count <= 16:
            length_score = 25
            length_feedback = "长度和词数都在理想范围内"
        else:
            length_score = 20
            length_feedback = f"字符数理想 ({char_count})，但词数 ({word_count}) 可优化至 5-16 词"
    elif char_count < 30:
        length_score = max(5, char_count // 2)
        length_feedback = f"太短 ({char_count} 字符)，建议 30-125 字符"
        suggestions.append(f"Alt 文本过短（{char_count} 字符），建议扩充至 30-125 字符，增加描述细节")
    elif char_count > 125:
        length_score = max(5, 25 - (char_count - 125) // 10)
        length_feedback = f"偏长 ({char_count} 字符)，建议 30-125 字符"
        suggestions.append(f"Alt 文本偏长（{char_count} 字符），建议精简至 125 字符以内")
    else:
        length_score = 15
        length_feedback = "长度基本合格"

    # ── 维度 2: 关键词覆盖 (25 分) ──
    if product_type:
        keywords = [
            kw.strip().lower()
            for kw in product_type.replace("/", " ").replace("&", " ").split()
            if len(kw.strip()) > 1
        ]
    else:
        keywords = []

    if keywords:
        matched = sum(1 for kw in keywords if kw in text_lower)
        keyword_score = min(25, int(matched / len(keywords) * 25)) if len(keywords) > 0 else 15
        if matched == 0:
            keyword_feedback = f"未包含品类关键词：{', '.join(keywords)}"
            suggestions.append(f"建议在 Alt 文本中自然融入品类关键词：{', '.join(keywords)}")
        elif matched < len(keywords):
            keyword_feedback = f"覆盖了 {matched}/{len(keywords)} 个品类关键词"
            missing = [kw for kw in keywords if kw not in text_lower]
            if missing:
                suggestions.append(f"可补充关键词：{', '.join(missing)}")
        else:
            keyword_feedback = f"完整覆盖了所有品类关键词 ({matched}/{len(keywords)})"
    else:
        keyword_score = 15
        keyword_feedback = "未提供品类信息，无法评估关键词覆盖"

    # ── 维度 3: 自然语言 (25 分) ──
    words = text_lower.split()
    stuffing_signals = 0
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            stuffing_signals += 1

    ends_with_period = text.rstrip().endswith((".", "。", "!", "！"))
    has_connectors = any(
        w in words for w in ["with", "and", "in", "on", "for", "of", "featuring", "showing", "的", "和", "在"]
    )

    if stuffing_signals == 0 and (ends_with_period or has_connectors):
        nl_score = 25
        nl_feedback = "读起来像自然语言描述，流畅无堆砌"
    elif stuffing_signals == 0:
        nl_score = 20
        nl_feedback = "无明显关键词堆砌，但可增加连接词使描述更自然"
    elif stuffing_signals <= 2:
        nl_score = 15
        nl_feedback = f"检测到 {stuffing_signals} 处重复，略显堆砌感"
        suggestions.append("避免关键词堆砌，用自然语言描述图片内容")
    else:
        nl_score = 8
        nl_feedback = f"检测到 {stuffing_signals} 处关键词堆砌，严重影响可读性"
        suggestions.append("严重关键词堆砌，请改写为自然描述句")

    # ── 维度 4: 描述性 (25 分) ──
    color_words = [
        "white", "black", "red", "blue", "green", "yellow", "pink", "purple",
        "gray", "grey", "brown", "orange", "gold", "silver",
        "白色", "黑色", "红色", "蓝色", "绿色", "黄色", "粉色", "紫色", "灰色", "棕色", "橙色", "金色", "银色",
    ]
    material_words = [
        "cotton", "leather", "metal", "plastic", "wood", "glass", "steel",
        "aluminum", "ceramic", "rubber", "silicone",
        "棉", "皮", "金属", "塑料", "木", "玻璃", "钢", "铝", "陶瓷", "橡胶", "硅胶",
    ]
    shape_words = [
        "round", "square", "rectangular", "oval", "circular", "flat", "curved", "straight",
        "圆形", "方形", "矩形", "椭圆", "扁平", "弯曲", "直",
    ]

    has_color = any(w in text_lower for w in color_words)
    has_material = any(w in text_lower for w in material_words)
    has_shape = any(w in text_lower for w in shape_words)

    desc_categories = sum([has_color, has_material, has_shape])

    if desc_categories >= 3:
        desc_score = 25
        desc_feedback = "描述丰富，涵盖颜色、材质、形状等多维度"
    elif desc_categories == 2:
        desc_score = 20
        desc_feedback = f"包含 {desc_categories} 类描述维度，可再丰富"
        if not has_color:
            suggestions.append("建议添加颜色描述（如 white, black, red）")
        if not has_material:
            suggestions.append("建议添加材质描述（如 leather, metal, cotton）")
        if not has_shape:
            suggestions.append("建议添加形状描述（如 round, square, compact）")
    elif desc_categories == 1:
        desc_score = 12
        desc_feedback = f"仅包含 {desc_categories} 类描述维度，过于简单"
        suggestions.append("Alt 文本描述不够丰富，建议至少包含颜色和材质信息")
    else:
        desc_score = 5
        desc_feedback = "缺少颜色、材质、形状等描述性词汇"
        suggestions.append("Alt 文本缺乏描述性，请添加颜色、材质、形状等细节")

    total_score = length_score + keyword_score + nl_score + desc_score

    if total_score >= 90:
        grade = "优秀"
    elif total_score >= 75:
        grade = "良好"
    elif total_score >= 60:
        grade = "一般"
    elif total_score >= 40:
        grade = "较差"
    else:
        grade = "差"

    return {
        "score": total_score,
        "total_score": total_score,
        "max_score": 100,
        "grade": grade,
        "dimensions": {
            "length": {"score": length_score, "max": 25, "feedback": length_feedback},
            "keywords": {"score": keyword_score, "max": 25, "feedback": keyword_feedback},
            "natural_language": {"score": nl_score, "max": 25, "feedback": nl_feedback},
            "descriptiveness": {"score": desc_score, "max": 25, "feedback": desc_feedback},
        },
        "suggestions": suggestions[:5],
    }


class ScoreAltTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        alt_text = tool_parameters.get("alt_text", "")
        product_type = tool_parameters.get("product_type", "")

        if not alt_text or not alt_text.strip():
            yield self.create_text_message("错误：alt_text 不能为空")
            return

        result = _score_alt_text(alt_text, product_type=product_type)

        yield self.create_json_message(result)
        yield self.create_text_message(
            f"Alt 文本评分：{result['score']}/{result['max_score']}（{result['grade']}）。"
            f"改进建议：{', '.join(result['suggestions']) if result['suggestions'] else '无'}"
        )

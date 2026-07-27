"""Alt 文本 SEO 评分工具 — 纯本地计算，不调用外部 API。"""
from collections.abc import Generator
import re
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Google Alt 文本最佳实践参考
_ALT_TEXT_MAX_LEN = 125
_ALT_TEXT_MIN_LEN = 20
_ALT_TEXT_IDEAL_MIN = 40
_ALT_TEXT_IDEAL_MAX = 100

# 描述性词汇（颜色、材质、形状、尺寸等）
_DESCRIPTIVE_PATTERNS = [
    "色", "白", "黑", "红", "蓝", "绿", "黄", "灰", "金", "银", "粉",
    "不锈钢", "铝", "塑料", "木质", "皮质", "硅胶", "金属", "玻璃", "陶瓷",
    "圆形", "方形", "长方形", "椭圆", "三角",
    "大", "中", "小", "迷你", "便携", "紧凑",
    "mm", "cm", "英寸", "inch",
    "wireless", "bluetooth", "portable", "premium", "professional",
    "adjustable", "foldable", "lightweight", "waterproof", "rechargeable",
    "stainless", "aluminum", "plastic", "wooden", "leather", "silicone",
    "metal", "glass", "ceramic", "carbon",
    "round", "square", "rectangular", "oval", "triangular",
    "white", "black", "red", "blue", "green", "yellow", "grey", "gold", "silver", "pink",
    "mini", "compact", "large",
]


def _extract_keywords(text: str) -> set:
    """提取关键词。英文按空格分词并过滤短词；中文按连续非空白字符/标点的 token 提取。"""
    if not text:
        return set()

    keywords = set()
    for word in re.findall(r"[a-zA-Z0-9]+", text):
        if len(word) > 2:
            keywords.add(word.lower())
    for token in re.findall(r"[\u4e00-\u9fa5]{2,}", text):
        keywords.add(token.lower())
    return keywords


def _score_alt_text(alt_text: str, title: str = "", lang: str = "en") -> dict:
    """对 Alt 文本进行 SEO 规则评分（0-100 分）。"""
    if not alt_text or not alt_text.strip():
        return {
            "score": 0,
            "max_score": 100,
            "grade": "差",
            "dimensions": {},
            "suggestions": ["Alt 文本为空，请提供有效的图片描述"],
        }

    text = alt_text.strip()
    text_len = len(text)
    scores = {}
    suggestions = []

    # 1. 长度评分（30 分）
    if _ALT_TEXT_IDEAL_MIN <= text_len <= _ALT_TEXT_IDEAL_MAX:
        scores["length"] = 30
    elif _ALT_TEXT_MIN_LEN <= text_len < _ALT_TEXT_IDEAL_MIN:
        scores["length"] = 20
        suggestions.append(
            f"Alt 文本偏短（{text_len} 字符），建议扩充到 {_ALT_TEXT_IDEAL_MIN}-{_ALT_TEXT_IDEAL_MAX} 字符"
        )
    elif _ALT_TEXT_IDEAL_MAX < text_len <= _ALT_TEXT_MAX_LEN:
        scores["length"] = 25
        suggestions.append(
            f"Alt 文本略长（{text_len} 字符），建议控制在 {_ALT_TEXT_IDEAL_MAX} 字符以内"
        )
    elif text_len > _ALT_TEXT_MAX_LEN:
        scores["length"] = 10
        suggestions.append(
            f"Alt 文本过长（{text_len} 字符），超过 Google 截断上限 {_ALT_TEXT_MAX_LEN} 字符"
        )
    else:
        scores["length"] = 10
        suggestions.append(
            f"Alt 文本过短（{text_len} 字符），建议至少 {_ALT_TEXT_MIN_LEN} 字符"
        )

    # 2. 关键词覆盖（25 分）
    title_words = _extract_keywords(title)
    if title_words:
        text_lower = text.lower()
        matched = [w for w in title_words if w in text_lower]
        if matched:
            coverage = len(matched) / max(len(title_words), 1)
            if coverage >= 0.8:
                scores["keyword_coverage"] = 25
            elif coverage >= 0.5:
                scores["keyword_coverage"] = 18
                suggestions.append(
                    f"Alt 文本覆盖了 {len(matched)}/{len(title_words)} 个标题关键词，建议补充更多"
                )
            else:
                scores["keyword_coverage"] = 10
                suggestions.append(
                    f"Alt 文本仅覆盖了 {len(matched)}/{len(title_words)} 个标题关键词，关键词覆盖不足"
                )
        else:
            scores["keyword_coverage"] = 5
            suggestions.append("Alt 文本未包含商品标题中的关键词")
    else:
        scores["keyword_coverage"] = 15

    # 3. 自然语言（20 分）
    if text.startswith(("http", "www", "IMG", "图片", "image", "DSC")):
        scores["natural_language"] = 0
        suggestions.append("Alt 文本是文件名/URL，不是自然语言描述")
    elif "," in text and text.count(",") >= 3 and len(text.split(",")[0].strip()) < 15:
        scores["natural_language"] = 5
        suggestions.append("Alt 文本疑似关键词堆砌，建议改为完整描述句")
    elif any(kw in text for kw in ["是", "is", "with", "featuring", "showing", "displaying"]):
        scores["natural_language"] = 20
    elif len(text.split()) >= 4:
        scores["natural_language"] = 15
    else:
        scores["natural_language"] = 10
        suggestions.append("Alt 文本建议使用完整描述句而非关键词罗列")

    # 4. 描述性（25 分）
    desc_count = sum(1 for pat in _DESCRIPTIVE_PATTERNS if pat.lower() in text.lower())
    if desc_count >= 3:
        scores["descriptiveness"] = 25
    elif desc_count >= 2:
        scores["descriptiveness"] = 20
    elif desc_count >= 1:
        scores["descriptiveness"] = 15
        suggestions.append("Alt 文本可增加更多描述性细节（颜色、材质、形状等）")
    else:
        scores["descriptiveness"] = 5
        suggestions.append("Alt 文本缺少描述性细节，建议补充颜色、材质、形状等特征")

    total = sum(scores.values())

    if total >= 90:
        grade = "优秀"
    elif total >= 75:
        grade = "良好"
    elif total >= 60:
        grade = "一般"
    elif total >= 40:
        grade = "较差"
    else:
        grade = "差"

    return {
        "score": total,
        "max_score": 100,
        "grade": grade,
        "dimensions": scores,
        "suggestions": suggestions,
    }


class ScoreAltTextTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        alt_text = tool_parameters.get("alt_text", "")
        title = tool_parameters.get("title", "")
        lang = tool_parameters.get("lang", "en")

        if not alt_text or not alt_text.strip():
            yield self.create_text_message("Error: alt_text is required.")
            return

        result = _score_alt_text(alt_text, title=title, lang=lang)

        yield self.create_json_message(result)
        yield self.create_text_message(
            f"Alt text score: {result['score']}/{result['max_score']} ({result['grade']}). "
            f"Suggestions: {', '.join(result['suggestions']) if result['suggestions'] else 'None'}"
        )

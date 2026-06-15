"""
KG Chunk Generator
将 Markdown 文档切分为带实体-关系标注的图谱化分块。
核心逻辑全部在本地完成，无需调用 LLM，不依赖外部网络。
"""

import re
import ssl
import certifi
import urllib.request
from collections.abc import Generator
from io import BytesIO
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


# ───────────────────────────────────────────────
# SSL 双模式下载（兼容 Dify 内部自签名 URL + 公网）
# ───────────────────────────────────────────────
def _download(url: str) -> BytesIO:
    is_dify_internal = any(x in url for x in [
        "/files/", "/console/api/", "127.0.0.1", "localhost", "dify"
    ])
    if is_dify_internal:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=ctx, timeout=60) as resp:
        return BytesIO(resp.read())


# ───────────────────────────────────────────────
# 图谱化分块模板
# ───────────────────────────────────────────────
CHUNK_TEMPLATE = """\
## 【图谱块 {idx:02d}】{entity_name}

**【实体】** {entity_name}
**【类型】** {entity_type}
**【关系-上游】** {upstream}
**【关系-下游】** {downstream}
**【关联实体】** {related}

---

{content}

"""

TRAP_TEMPLATE = """\
## 【图谱块 TRAP】常见混淆点与规则纠错

**【实体】** 规程混淆陷阱
**【类型】** 知识陷阱 / 规则澄清
**【关系-上游】** 全部规则块 → 本块作补充说明
**【关系-下游】** 本块 → 提升 LLM 判断精度
**【关联实体】** 所有含数值阈值的规则块

---

{traps}

"""


# ───────────────────────────────────────────────
# 解析器：提取章节、识别实体和关系
# ───────────────────────────────────────────────

def _split_sections(text: str) -> list[dict]:
    """
    将 Markdown 按二级标题（##）切分为章节列表。
    返回: [{"title": str, "content": str}, ...]
    """
    sections = []
    # 匹配 ## 或 ### 标题
    pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return [{"title": "全文", "content": text.strip()}]

    for i, m in enumerate(matches):
        level = len(m.group(1))
        if level > 2:
            continue  # 跳过三级以下标题（作为内容保留）
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # 找下一个同级或上级标题
        for j in range(i + 1, len(matches)):
            if len(matches[j].group(1)) <= level:
                end = matches[j].start()
                break
        content = text[start:end].strip()
        if content:
            sections.append({"title": title, "content": content, "level": level})

    # 一级标题作为文档标题，不单独成块
    return [s for s in sections if s["level"] >= 2 or len(sections) == 1]


def _extract_numbers(text: str) -> list[str]:
    """提取文本中出现的关键数值（百分比、数字+单位等）"""
    patterns = [
        r'\d+(?:\.\d+)?%',          # 百分比
        r'\d+\s*(?:kV|kWh|V|A|W)',  # 电气单位
        r'\d+\s*(?:个工作日|小时|天|月|年)',  # 时限
        r'[±]\d+(?:\.\d+)?%',       # 误差范围
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text))
    return list(dict.fromkeys(found))  # 去重保序


def _detect_traps(sections: list[dict]) -> list[str]:
    """
    识别文档中的「陷阱」：
    - 明确纠正旧版本说法的语句
    - 含「不是」「非」「注意」「重要」的否定/警示
    - 含「以本规程为准」「不超过」「不得」的强制条款
    """
    trap_keywords = [
        r'以本规程.*为准',
        r'非\s*\d+',
        r'不(?:是|得|能|超过|属于)',
        r'注意[：:]',
        r'重要(?:说明|提示)[：:]',
        r'不(?:在|纳入|输出)',
        r'修订版',
        r'早期规程.*写.*以本',
    ]
    traps = []
    for sec in sections:
        combined = sec["title"] + "\n" + sec["content"]
        for kw in trap_keywords:
            for m in re.finditer(kw, combined):
                # 提取该句（向前后各找句号/换行）
                start = max(0, m.start() - 80)
                end = min(len(combined), m.end() + 120)
                snippet = combined[start:end].strip()
                snippet = re.sub(r'\s+', ' ', snippet)
                entry = f"- **[{sec['title']}]** {snippet}"
                if entry not in traps:
                    traps.append(entry)
    return traps


def _infer_entity_type(title: str, content: str) -> str:
    """根据标题和内容推断实体类型"""
    combined = title + content
    rules = [
        (r'分级|预警|级别|范围', '管理标准'),
        (r'原因|故障|缺陷|误差|缺抄', '异常原因'),
        (r'流程|步骤|排查|程序', '操作流程'),
        (r'计算|公式|系数|退补|更正', '计算规则'),
        (r'装置|设备|终端|表计|互感器', '设备管理'),
        (r'电压|低电压|电压偏差|治理', '电能质量'),
        (r'数据|系统|比对|完整率|营销|量测', '数据管理'),
        (r'定义|基本|总则|目的|适用', '基础定义'),
        (r'周期|轮换|到期', '周期管理'),
    ]
    for pattern, etype in rules:
        if re.search(pattern, combined):
            return etype
    return '规程条款'


def _infer_relations(idx: int, title: str, content: str,
                     all_titles: list[str]) -> tuple[str, str, str]:
    """
    推断上下游关系和关联实体。
    返回: (upstream, downstream, related)
    """
    upstream_hints = {
        '分级': ['线损率计算'],
        '原因': ['线损率分级'],
        '排查': ['线损率分级', '异常原因'],
        '退补': ['失压判定', '采集终端故障'],
        '数据': ['线损率计算', '台变关系'],
        '低电压': ['独立领域'],
        '失压': ['采集终端故障'],
        '轮换': ['计量装置误差'],
    }
    downstream_hints = {
        '计算': ['线损率分级管理'],
        '分级': ['排查流程', '责任人追责'],
        '原因': ['针对性整改措施'],
        '失压': ['退补电量计算'],
        '低电压': ['治理方案实施'],
        '数据': ['异常台区核查'],
    }
    related_hints = {
        '缺抄': ['修正线损率公式', '营销系统'],
        '台变': ['营销系统', '量测系统'],
        '终端': ['失压更正系数K', '附录C'],
        '误差': ['退补电量', '电能计量规程'],
        '退补': ['供电营业规则第81条'],
        '低电压': ['附录B', '六类成因表'],
    }

    def _match(hints: dict) -> list[str]:
        found = []
        for kw, vals in hints.items():
            if kw in title or kw in content[:200]:
                found.extend(vals)
        return list(dict.fromkeys(found))

    up = _match(upstream_hints)
    down = _match(downstream_hints)
    rel = _match(related_hints)

    # 邻近章节关联
    if idx > 0:
        prev = all_titles[idx - 1]
        if prev not in up:
            up = [prev] + up
    if idx < len(all_titles) - 1:
        nxt = all_titles[idx + 1]
        if nxt not in down:
            down = down + [nxt]

    upstream_str = ' → '.join(up[:3]) if up else '（文档起始节）'
    downstream_str = ' → '.join(down[:3]) if down else '（独立规则）'
    related_str = '、'.join(rel[:4]) if rel else '—'
    return upstream_str, downstream_str, related_str


def _extract_key_numbers(content: str) -> str:
    """提取关键数值，格式化为可读说明"""
    nums = _extract_numbers(content)
    if not nums:
        return ''
    return '\n\n> 📌 **本块关键数值：** ' + '　'.join(nums)


# ───────────────────────────────────────────────
# 主转换函数
# ───────────────────────────────────────────────

def build_kg_chunks(markdown_text: str, domain: str = '通用',
                    trap_mode: str = 'on') -> str:
    """
    将 Markdown 文本转换为图谱化分块 Markdown。
    """
    sections = _split_sections(markdown_text)
    all_titles = [s["title"] for s in sections]

    output_parts = []

    # 文档头部说明
    # 提取一级标题作为文档名
    title_match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else '未知文档'

    header = f"""# 知识图谱化分块输出

> **源文档：** {doc_title}
> **领域：** {domain}
> **分块数：** {len(sections)} 个主题块{' + 1 个陷阱纠错块' if trap_mode == 'on' else ''}
> **用途：** 直接导入 Dify 知识库，每个分块独立检索

---

"""
    output_parts.append(header)

    # 逐章节生成图谱化分块
    for idx, sec in enumerate(sections):
        title = sec["title"]
        content = sec["content"]

        entity_type = _infer_entity_type(title, content)
        upstream, downstream, related = _infer_relations(
            idx, title, content, all_titles
        )
        key_nums = _extract_key_numbers(content)

        # 清理内容中的多余空行
        clean_content = re.sub(r'\n{3,}', '\n\n', content)
        if key_nums:
            clean_content = clean_content + key_nums

        chunk = CHUNK_TEMPLATE.format(
            idx=idx + 1,
            entity_name=title,
            entity_type=entity_type,
            upstream=upstream,
            downstream=downstream,
            related=related,
            content=clean_content,
        )
        output_parts.append(chunk)

    # 陷阱纠错块
    if trap_mode == 'on':
        traps = _detect_traps(sections)
        if traps:
            trap_content = '\n'.join(traps)
        else:
            trap_content = '- 本文档未检测到明确的纠错声明，建议人工审核易混淆数值。'
        output_parts.append(TRAP_TEMPLATE.format(traps=trap_content))

    # 尾部：关系索引表
    relation_index = _build_relation_index(sections, all_titles)
    output_parts.append(relation_index)

    return '\n'.join(output_parts)


def _build_relation_index(sections: list[dict], all_titles: list[str]) -> str:
    """生成关系索引总表，辅助人工审核"""
    lines = [
        "---\n",
        "## 附：实体关系索引（辅助审核）\n",
        "| 序号 | 实体名称 | 类型 | 关键数值 |",
        "|---|---|---|---|",
    ]
    for idx, sec in enumerate(sections):
        etype = _infer_entity_type(sec["title"], sec["content"])
        nums = _extract_numbers(sec["content"])
        nums_str = '　'.join(nums[:3]) if nums else '—'
        lines.append(f"| {idx + 1:02d} | {sec['title']} | {etype} | {nums_str} |")
    lines.append('\n')
    return '\n'.join(lines)


# ───────────────────────────────────────────────
# Dify Tool 入口
# ───────────────────────────────────────────────

class KgChunkTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        file_meta = tool_parameters.get('file')
        domain = tool_parameters.get('domain', '通用') or '通用'
        trap_mode = tool_parameters.get('trap_mode', 'on') or 'on'

        if not file_meta:
            raise Exception('请上传 Markdown 文档文件。')

        try:
            file_bytes = _download(file_meta.url)
            file_bytes.seek(0)
            raw_text = file_bytes.read().decode('utf-8', errors='replace')
        except Exception as e:
            raise Exception(f'文件读取失败：{str(e)}')

        if not raw_text.strip():
            raise Exception('文件内容为空，请检查上传的文档。')

        try:
            kg_output = build_kg_chunks(raw_text, domain=domain, trap_mode=trap_mode)
        except Exception as e:
            raise Exception(f'图谱化分块失败：{str(e)}')

        # 输出 1：统计摘要（文本消息）
        sections = _split_sections(raw_text)
        traps = _detect_traps(sections) if trap_mode == 'on' else []
        summary = (
            f"✅ 图谱化分块完成\n\n"
            f"- 源文档字符数：{len(raw_text):,}\n"
            f"- 生成主题块：{len(sections)} 个\n"
            f"- 检测到陷阱条目：{len(traps)} 条\n"
            f"- 领域标注：{domain}\n\n"
            f"请下载输出文件，直接导入 Dify 知识库。"
        )
        yield self.create_text_message(summary)

        # 输出 2：图谱化分块 Markdown 文件
        output_bytes = kg_output.encode('utf-8')
        yield self.create_blob_message(
            blob=output_bytes,
            meta={
                "mime_type": "text/markdown",
                "filename": "kg_chunks_output.md"
            }
        )

"""
tools/clean_md/clean_md.py  —  MD 文档清洗工具（通用 RAG 增强版 v3.6）

设计原则
────────
• 零业务硬编码：不含任何特定领域词汇（南网/线损/台区等），适用于
  法规、技术手册、合同、产品文档、学术文档等各类 MD 文件。
• 防御性设计：每步操作均有前置条件判断和异常捕获，单步失败不影响
  其余步骤。
• 可观测：stats 字典记录每步前后字符数，方便排查问题。
• 顺序敏感：步骤严格按依赖顺序排列，注释说明原因。

十一步清洗流程
──────────────
  Step 1  标准文号保护          白名单占位，防止去噪误删
  Step 2  噪声清除              页码、水印、版本号、密级等
  Step 3  封面/元数据行剥离     文件号行、发布日期行、版本印发行
  Step 4  PDF 分页符 --- 清除   行首/行末粘连的 ---（非表格分隔行）
  Step 5  表格列拆行修复        PDF 转换导致最后一列换行分离
  Step 6  标题格式归一化        ##无空格、多余空格、孤儿条文号合并
  Step 7  表格结构修复          表格末行粘连、表格前后空行保障
  Step 8  行内折行空格修复      汉字间 PDF 折行空格（跳过标题/表格行）
  Step 9  表格单元格折行清理    单元格内汉字间空格
  Step 10 跨行断句续接          不跨越标题行；不合并新段落起始行
  Step 11 MD5 去重（标题级）    按标题行切分后去重
  Step 12 表格行展开为段落      父子结构优化：每行展开为键值对段落，形成独立子块
"""

import hashlib
import re
import ssl
import certifi
import urllib.request
from collections.abc import Generator
from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


# ════════════════════════════════════════════════════════════
# 常量 & 预编译正则
# ════════════════════════════════════════════════════════════

# 中文数字（含百/零，用于条文号）
_CN_NUM = r"[一二三四五六七八九十百零]+"

# 条文/章/节/款/项 通用前缀
_CLAUSE_PREFIX = rf"第{_CN_NUM}[条章节款项]"

# 标题行识别
_RE_HEADING    = re.compile(r"^(#{1,6})\s")
# 表格行识别
_RE_TABLE_ROW  = re.compile(r"^\s*\|")
# blockquote 行
_RE_BLOCKQUOTE = re.compile(r"^\s*>")

# 中文孤儿条文号：整行只有"第X条/章"
_RE_ORPHAN_CLAUSE = re.compile(
    rf"^({_CLAUSE_PREFIX})\s*$",
    re.MULTILINE,
)
# 标题候选行：2-25 字符，纯中文/字母/数字/括号，无句末标点
_RE_TITLE_CAND = re.compile(
    r"^[\u4e00-\u9fff\w（）()／【】〔〕]{2,25}$"
)

# 句子终止符（行末不续接下一行）
_RE_SENT_END = re.compile(
    r"[。！？；…\.!?;\u201d\u2019」』】）\)]$"
)

# 新段落起始特征（不参与续接）
_RE_NEW_PARA = re.compile(
    rf"^(?:"
    rf"#{1,6}\s"               # Markdown 标题
    rf"|\|"                    # 表格行
    rf"|>"                     # blockquote
    rf"|\s*$"                  # 空行
    rf"|{_CLAUSE_PREFIX}"      # 中文条文/章节
    rf"|附录\s*[A-Z\d]"        # 附录
    rf"|[（(][一二三四五六七八九十\d]+[）)]"  # 括号序号
    rf"|\d+[\.、。]"           # 数字列表
    rf"|步骤\s*[\d一二三四五六七八九十]"     # 步骤
    rf"|注\s*[：:$]"           # 注释
    rf"|重要说明"              # 重要说明
    rf")"
)


# ════════════════════════════════════════════════════════════
# Step 1  标准文号白名单保护
# ════════════════════════════════════════════════════════════

# 匹配常见标准文号格式，去噪前先占位，去噪后还原
_RE_STD_REF = re.compile(
    r"(?:"
    # 国标/行标：GB、GB/T、DL/T、NB/T、SJ、YD、HJ 等
    r"(?:GB|DL|NB|SJ|YD|JB|HJ|SH|CJ|JT|NY|QX)(?:/[A-Z])?\s*/?\s*T?\s*[\d][\d.\-— /]*"
    r"|ISO(?:/IEC)?\s*[\d][\d.\-:/ ]*"
    # 企业标准：Q/XXX
    r"|Q/[A-Z][A-Z0-9]*[\s\-—./\d]*"
    # IEEE、NEMA 等英文标准
    r"|(?:IEEE|NEMA|ANSI|ASTM)\s*[\d][\d.\-/]*"
    r")",
    re.IGNORECASE,
)

_std_store: list[str] = []   # 模块级，可在函数间传递


def _protect_std_refs(text: str) -> str:
    """将标准文号替换为占位符，防止后续规则误删。"""
    _std_store.clear()

    def _ph(m: re.Match) -> str:
        _std_store.append(m.group(0))
        return f"\x00STD{len(_std_store)-1}\x00"

    return _RE_STD_REF.sub(_ph, text)


def _restore_std_refs(text: str) -> str:
    """还原标准文号占位符。"""
    for i, original in enumerate(_std_store):
        text = text.replace(f"\x00STD{i}\x00", original)
    return text


# ════════════════════════════════════════════════════════════
# Step 2  噪声清除
# ════════════════════════════════════════════════════════════

# 每项：(pattern, replacement, flags)
_NOISE_RULES: list[tuple[str, str, int]] = [
    # 中文页码
    (r"第\s*\d+\s*页\s*共\s*\d+\s*页",           "",  0),
    # 英文页码（整行）
    (r"(?m)^[ \t]*(?i:page)\s+\d+(?:\s+of\s+\d+)?[ \t]*$", "", re.MULTILINE),
    # 纯数字页码行
    (r"(?m)^[ \t]*\d{1,4}[ \t]*$",               "",  re.MULTILINE),
    # 装饰性页码  — 1 —  或  - 15 -
    (r"(?m)^[ \t]*[—\-–]{1,3}[ \t]*\d+[ \t]*[—\-–]{1,3}[ \t]*$", "", re.MULTILINE),
    # 版本号独立行：版本：V2.1 / Ver 3.0 / V2.1（行首行尾均为版本信息）
    (r"(?m)^[ \t]*(?:版本[：:\s]*|[Vv]er(?:sion)?[.:\s]?)[Vv]?\d+[\.\d]*[ \t]*$", "", re.MULTILINE),
    # 密级标记
    (r"(?:内部资料|内部文件|机密|绝密|秘密|confidential)\s*(?:请勿外传|不得外传|do not distribute)?",
     "", re.IGNORECASE),
    # 打印日期行
    (r"(?m)^[ \t]*打印日期[：:\s]\s*\d{4}[-/]\d{1,2}[-/]\d{1,2}[ \t]*$", "", re.MULTILINE),
    # 归档编号行
    (r"(?m)^[ \t]*归档编号[：:].+$",               "",  re.MULTILINE),
    # 目录引导符  ···3  或  .....5
    (r"[·…\.]{4,}[ \t]*\d+[ \t]*$",              "",  0),
    # 企业名称水印（独立整行，不删内嵌的）
    (r"(?m)^[ \t]*(?:中国南方电网|国家电网|中国电力建设|中国华电|中国大唐|中国华能)"
     r"(?:有限责任公司|股份有限公司|集团公司|集团)?[ \t]*$", "", re.MULTILINE),
    # 多余空行 → 最多保留 2 个换行
    (r"\n{3,}",                                    "\n\n", 0),
]


def _remove_noise(text: str, extra_patterns: list[str]) -> str:
    # 合并内置规则与用户自定义规则
    rules = _NOISE_RULES + [(p, "", 0) for p in extra_patterns if p.strip()]
    for pattern, repl, flags in rules:
        try:
            text = re.sub(pattern, repl, text, flags=flags)
        except re.error:
            pass  # 用户自定义规则有误时跳过
    return text.strip()


# ════════════════════════════════════════════════════════════
# Step 3  封面 / 元数据行剥离
# ════════════════════════════════════════════════════════════

# 匹配高置信度封面/元数据行（整行）
_COVER_PATTERNS: list[re.Pattern] = [
    # 文件号行（Q/XX-YWGL-YYYY-NNN 格式）
    re.compile(r"^[A-Z]/[A-Z]+-[\w-]+-\d{4}-\d+\s"),
    # 发布日期行
    re.compile(r"^(?:发布|实施|修订|审核|批准|颁布)日期[：:\s]"),
    # 打印/生效/版本信息行
    re.compile(r"^版本[：:\s]"),
    re.compile(r"^供内部使用$"),
    # "注：本文件为...管理规程" 类说明行
    re.compile(r"^注[：:]本(?:文件|规程|标准|制度)(?:为|是|属于)"),
    # 尾部印发行：如"版本V2.1 2024年3月1日印发"
    re.compile(r"\d{4}\s*年\s*\d+\s*月\s*\d+\s*日\s*(?:发布|印发|施行|实施)\s*$"),
    # 文件号+日期三段粘连行
    re.compile(r"(?:文件号|编号)[：:].+(?:发布|实施)日期[：:]"),
]


def _strip_cover_lines(text: str) -> str:
    """逐行检查，剥离封面/元数据行。"""
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        s = line.strip()
        if s and any(p.search(s) for p in _COVER_PATTERNS):
            continue
        result.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(result)).strip()


# ════════════════════════════════════════════════════════════
# Step 3b  目录（TOC）剥离
# ════════════════════════════════════════════════════════════

# 目录项：以点引导符 + 页码结尾（如 "第一章 总则 ········· 1"），
# 或 "第X章/节 标题 + 末尾数字页码"。点引导符已被 Step 2 部分清理，
# 故两种形态都覆盖。
_RE_TOC_DOTLEADER = re.compile(r"[·…\.\u2024\u2025\u2026]{2,}\s*\d{1,4}\s*$")
_RE_TOC_CLAUSE = re.compile(
    rf"^(?:{_CLAUSE_PREFIX})\s+\S.*?\s+\d{{1,4}}\s*$"
)
# 独立的"目录"标记行
_RE_TOC_HEADER = re.compile(r"^\s*(?:目\s*录|目录|contents|table of contents)\s*$", re.IGNORECASE)


def _strip_toc(text: str) -> str:
    """
    剥离目录区：
      • 独立"目录"标题行；
      • 形如"第X章 标题 …… N"或"第X章 标题  N"的目录项（点引导符或末尾页码）。
    仅删除高置信度目录行，避免误删正文。
    """
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            result.append(line)
            continue
        if _RE_TOC_HEADER.match(s):
            continue
        if _RE_TOC_DOTLEADER.search(s) or _RE_TOC_CLAUSE.match(s):
            continue
        result.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(result)).strip()


# ════════════════════════════════════════════════════════════
# Step 4  标题格式归一化 & 孤儿条文号合并
# ════════════════════════════════════════════════════════════

def _normalize_headings(text: str) -> str:
    """
    4a. 标题格式归一化：
        ##标题   → ## 标题
        ##  标题 → ## 标题（多余空格）
        ###  多  空  格  → ### 多 空 格
    4b. 孤儿条文/章节号合并：
        第一条           第一条 目的
        目的         →   （升级为 ## 标题）
        （空行间隔也合并）
    4c. 有标题名的条文行升级为 ##：
        第一条 目的  →  ## 第一条 目的
    """
    # ── 4a: 标题格式归一化 ────────────────────────────────────────
    def _fix_heading(m: re.Match) -> str:
        hashes = m.group(1)
        title  = re.sub(r"\s{2,}", " ", m.group(2)).strip()
        return f"{hashes} {title}" if title else hashes

    text = re.sub(r"^(#{1,6})\s*(.*?)\s*$", _fix_heading, text, flags=re.MULTILINE)

    # ── 4b & 4c: 条文/章节标题处理 ────────────────────────────────
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        raw  = lines[i]
        s    = raw.strip()

        # 已是 Markdown 标题 → 不处理
        if _RE_HEADING.match(s):
            result.append(raw)
            i += 1
            continue

        # 匹配"第X条/章/节…"开头的行
        clause_m = re.match(rf"^({_CLAUSE_PREFIX})(.*)", s)
        if clause_m:
            prefix = clause_m.group(1)   # "第一条"
            rest   = clause_m.group(2).strip()  # 可能为空 / 标题名 / 内容

            if not rest:
                # 孤儿：整行只有"第X条"，向后找标题候选（允许跳过 1 个空行）
                j = i + 1
                if j < len(lines) and not lines[j].strip():
                    j += 1  # 跳过一个空行
                if (j < len(lines)
                        and _RE_TITLE_CAND.match(lines[j].strip())
                        and not _RE_HEADING.match(lines[j].strip())):
                    result.append(f"## {prefix} {lines[j].strip()}")
                    i = j + 1
                    continue
                else:
                    # 孤儿但找不到标题名 → 单独升级
                    result.append(f"## {prefix}")
                    i += 1
                    continue
            elif len(rest) <= 25 and not _RE_SENT_END.search(rest):
                # "第X条 标题名"（标题名短且无终止标点）→ 升级为标题
                # 但需排除「跨页截断的正文首行」：若下一非空行是续接正文
                # （非空、不以标题/表格/列表等新块特征开头），则说明 rest 只是
                # 被页面截断的正文上半句，不应升级。
                nxt = ""
                k = i + 1
                if k < len(lines) and not lines[k].strip():
                    k += 1  # 允许跨一个空行
                if k < len(lines):
                    nxt = lines[k].strip()
                is_continuation = bool(nxt) and not _RE_NEW_PARA.match(nxt)
                if not is_continuation:
                    result.append(f"## {prefix} {rest}")
                    i += 1
                    continue
                # else: 跨页截断的正文 → 保持原样（交给后续续接步骤处理）

        result.append(raw)
        i += 1

    return "\n".join(result)



# ════════════════════════════════════════════════════════════
# Step 4  PDF 分页符 --- 清除
# ════════════════════════════════════════════════════════════

def _fix_stray_hrules(text: str) -> str:
    """
    清除 PDF 转 MD 时产生的跨页分隔符 --- 残留。
    三种形态：
      行首粘连：---正文内容  →  正文内容
      行末粘连：正文内容---  →  正文内容（含 | 内容 |--- 形式）
      独立行：  ---（非表格分隔行）→ 删除
    保留：表格内的合法 | --- | 分隔行。
    """
    # 1. 行首粘连（--- 后接非 - 非 | 字符）
    text = re.sub(r"^---(?=[^-|])", r"", text, flags=re.MULTILINE)
    # 2. 行末粘连（任何行末的连续 ---）
    text = re.sub(r"-{3,}\s*$", "", text, flags=re.MULTILINE)
    # 3. 独立 --- 行：只删非表格环境中的
    lines = text.split("\n")
    result: list[str] = []
    for i, line in enumerate(lines):
        if re.match(r"^\s*-{3,}\s*$", line):
            prev_pipe = i > 0 and "|" in lines[i - 1]
            next_pipe = i < len(lines) - 1 and "|" in lines[i + 1]
            if prev_pipe or next_pipe:
                result.append(line)   # 保留表格内分隔行
            # else: 删除
        else:
            result.append(line)
    return "\n".join(result)


# ════════════════════════════════════════════════════════════
# Step 5  表格列拆行修复
# ════════════════════════════════════════════════════════════

def _fix_table_split_columns(text: str) -> str:
    """
    修复 PDF 转换时表格被换行/跨页分离的两类问题：

    (A) 最后一列被换行分离（原逻辑）：
      | col1 | col2 |          | col1 | col2 | col3 |
      （空行）             →
       col3 |

    (B) 单元格在跨页处被截断（新增）：
      | 2 | 缺陷记录 | 当班运        | 2 | 缺陷记录 | 当班运维员 | 实时 |
      （空行/被页码隔断）     →
      维员 | 实时 |
      —— 上一行是表格数据行但【不以 | 结尾】（被截断），
         下一非空行又以 | 收尾（断裂的后半截），二者重连。

    反复执行直到无匹配（应对多列同时被拆的极端情况）。
    """
    # (A) 行以 | 结尾，空行后接以 | 结尾的续行
    pat_a = re.compile(
        r"(\|[^\n]*\|)\n\n( {0,4}(?:[^\n|]{1,120})\|)",
        re.MULTILINE,
    )
    # (B) 表格数据行被截断（行内有 | 但不以 | 结尾），其后（允许跨一个空行）
    #     紧跟一段以 | 收尾的断裂残片 → 直接拼回，不加空格（汉字单元格被折断）
    pat_b = re.compile(
        r"(?m)^([ \t]*\|[^\n]*[^|\s])[ \t]*\n\n?([^\n|][^\n]*\|[^\n]*)$"
    )
    prev = None
    while prev != text:
        prev = text
        text = pat_a.sub(lambda m: m.group(1) + " " + m.group(2).strip(), text)
        text = pat_b.sub(lambda m: m.group(1).rstrip() + m.group(2).strip(), text)
    return text


# ════════════════════════════════════════════════════════════
# Step 7  表格结构修复
# ════════════════════════════════════════════════════════════

# 表格末行与紧接内容粘连：| xxx |内容
# 只匹配行末 | 后（跨行）紧接非表格行内容的真正粘连，不误匹配行内 | 分隔符
_RE_TABLE_FUSE = re.compile(r"(\|)\s*$\s*^([^\n|])", re.MULTILINE)


def _fix_table_structure(text: str) -> str:
    """
    5a. 表格末行粘连修复：| xxx |第三章  →  | xxx |\n\n第三章
    5b. 确保表格块前后各有空行（Dify 解析要求）
    """
    # 5a: 粘连修复
    text = _RE_TABLE_FUSE.sub(r"\1\n\n\2", text)

    # 5b: 表格前后空行保障（逐行扫描，效率可接受）
    lines = text.split("\n")
    result: list[str] = []
    for i, line in enumerate(lines):
        is_table  = bool(_RE_TABLE_ROW.match(line))
        prev_empty = (i == 0) or (not lines[i-1].strip())
        prev_table = (i > 0) and bool(_RE_TABLE_ROW.match(lines[i-1]))
        next_empty = (i == len(lines)-1) or (not lines[i+1].strip())
        next_table = (i < len(lines)-1) and bool(_RE_TABLE_ROW.match(lines[i+1]))

        # 表格块首行：前面无空行则补一个
        if is_table and not prev_table and not prev_empty:
            result.append("")
        result.append(line)
        # 表格块末行：后面无空行且有内容则补一个
        if is_table and not next_table and not next_empty:
            result.append("")

    text = "\n".join(result)

    # 5c. 删除连续表格行之间的孤立空行（PDF 跨页表格产物）
    #     | 行A |\n\n| 行B |  →  | 行A |\n| 行B |
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"(\|[^\n]*\|)\n\n(\|)", r"\1\n\2", text)

    return text


# ════════════════════════════════════════════════════════════
# Step 8  行内折行空格修复（汉字间）
# ════════════════════════════════════════════════════════════

# PDF 折行遗留：汉字 + 空格 + 汉字/括号
_RE_HAN_SPACE = re.compile(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff（【《〔])")


def _fix_han_spaces(text: str) -> str:
    """
    跳过以 #  |  > 开头的行（标题/表格/引用），
    仅在正文行中消除汉字间折行空格。
    """
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        s = line.strip()
        if _RE_HEADING.match(s) or _RE_TABLE_ROW.match(s) or _RE_BLOCKQUOTE.match(s):
            result.append(line)
        else:
            result.append(_RE_HAN_SPACE.sub(r"\1\2", line))
    return "\n".join(result)


# ════════════════════════════════════════════════════════════
# Step 7  表格单元格内折行清理
# ════════════════════════════════════════════════════════════

_RE_CELL_SPACE = re.compile(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])")


def _fix_table_cell_spaces(text: str) -> str:
    """仅对表格行做汉字间空格清理（Step 6 跳过了表格行，这里补充）。"""
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        if _RE_TABLE_ROW.match(line.strip()):
            result.append(_RE_CELL_SPACE.sub(r"\1\2", line))
        else:
            result.append(line)
    return "\n".join(result)


# ════════════════════════════════════════════════════════════
# Step 10 跨行断句续接
# ════════════════════════════════════════════════════════════

def _fix_cross_line_breaks(text: str) -> str:
    """
    将 PDF 排版折断的行（行末无终止标点、下一行不是新段落）续接。
    不续接：
      • 当前行是标题/表格/引用行
      • 下一行是标题/表格/引用/新段落起始
      • 当前行以终止标点结尾
    """
    lines = text.split("\n")
    merged: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s    = line.rstrip()

        # 当前行是结构行 → 不参与续接
        if (_RE_HEADING.match(s)
                or _RE_TABLE_ROW.match(s)
                or _RE_BLOCKQUOTE.match(s)
                or not s):
            merged.append(line)
            i += 1
            continue

        # 行末是终止标点 → 不续接
        if _RE_SENT_END.search(s):
            merged.append(line)
            i += 1
            continue

        # 尝试续接下一行（允许跳过最多 2 个连续空行）
        j = i + 1
        _skipped = 0
        while j < len(lines) and not lines[j].strip() and _skipped < 2:
            j += 1
            _skipped += 1

        if j < len(lines):
            nxt = lines[j].strip()
            if (nxt
                    and not _RE_HEADING.match(nxt)
                    and not _RE_TABLE_ROW.match(nxt)
                    and not _RE_BLOCKQUOTE.match(nxt)
                    and not _RE_NEW_PARA.match(nxt)):
                merged.append(s + nxt)
                i = j + 1
                continue

        merged.append(line)
        i += 1

    return "\n".join(merged)



# ════════════════════════════════════════════════════════════
# Step 12  表格行展开（父子结构 RAG 优化）
# ════════════════════════════════════════════════════════════

def _should_expand_table(header: list[str], context_before: str = "") -> bool:
    """
    判断表格是否适合展开为键值对段落。
    不展开：公式/计算类表格、列数不足的表格。
    """
    # 公式/计算类列头 → 不展开
    skip_keywords = {"公式", "计算项目", "formula", "equation"}
    if any(h.strip() in skip_keywords for h in header):
        return False
    if any("公式" in h for h in header):
        return False
    # 上下文含"公式汇总"/"计算公式" → 不展开
    if "公式汇总" in context_before or "计算公式" in context_before:
        return False
    # 列数不足
    if len(header) < 2:
        return False
    return True


def _expand_table_rows(header: list[str], rows: list[list[str]]) -> list[str]:
    """
    把表格每行展开为 "列头：值　列头：值…" 格式的自然语言段落。
    每个段落约 40-80 字，在 Dify 父子结构中会成为独立子块。
    """
    expanded: list[str] = []
    for row in rows:
        if not row:
            continue
        parts: list[str] = []
        for i, cell in enumerate(row):
            cell = cell.strip()
            if not cell or cell in ("—", "-", ""):
                continue
            col = header[i].strip() if i < len(header) else ""
            if col and col != cell:
                parts.append(f"{col}：{cell}")
            else:
                parts.append(cell)
        if parts:
            expanded.append("　".join(parts))   # 全角空格分隔各列
    return expanded


def _inject_table_expansions(text: str) -> str:
    """
    在 MD 文本中，找到所有适合展开的表格，
    在原始表格后追加展开的键值对段落。
    
    父块（##标题）里同时包含：
      • 原始 Markdown 表格（供 LLM 阅读）
      • 展开段落（每行一段，供子块向量搜索）
    
    这样既保留了人类可读的表格，又让每行数据成为精准的检索单元。
    """
    lines = text.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        result.append(line)

        # 检测表格起始：| 行 且下一行是分隔行 | --- |
        if (line.strip().startswith("|")
                and "---" not in line
                and i + 1 < len(lines)
                and re.match(r"^\|[\s\-|]+\|", lines[i + 1])):

            header = [c.strip() for c in line.split("|") if c.strip()]

            # 收集表格后续所有行（含分隔行）
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                result.append(lines[j])
                j += 1

            # 收集数据行（跳过分隔行）
            data_rows: list[list[str]] = []
            for k in range(i + 2, j):
                if "---" not in lines[k]:
                    row = [c.strip() for c in lines[k].split("|") if c.strip()]
                    if row:
                        data_rows.append(row)

            # 获取当前父块（最近的 ## 标题行到表格行）作为上下文
            # 确保能检测到如"附录B 常用计算公式汇总"这类父块标题
            _parent_start = i
            for _k in range(i - 1, -1, -1):
                if re.match(r"^##\s", lines[_k]):
                    _parent_start = _k
                    break
            ctx_before = "\n".join(lines[_parent_start: i])

            # 展开
            if data_rows and _should_expand_table(header, ctx_before):
                paragraphs = _expand_table_rows(header, data_rows)
                if paragraphs:
                    result.append("")   # 表格后空行
                    for para in paragraphs:
                        result.append("")
                        result.append(para)

            i = j
            continue

        i += 1

    return "\n".join(result)

# ════════════════════════════════════════════════════════════
# Step 11 MD5 去重（标题级切分）
# ════════════════════════════════════════════════════════════

# 按任意级别标题（#~###）切分，实现"每个标题块独立去重"
_RE_CHUNK_SPLIT = re.compile(r"(?m)^(?=#{1,3}\s)")
# 去重时额外按条文/附录标题切分（条文可能没有被升级为##）
_RE_CHUNK_SPLIT_EXTRA = re.compile(
    rf"(?m)^(?=##\s|第{_CN_NUM}[条章节款项]\s|附录\s*[A-Z\d]\s)"
)


def _deduplicate(text: str, min_chars: int = 8) -> tuple[str, int]:
    # 优先用条文级切分，块更细；降级到标题级
    parts = _RE_CHUNK_SPLIT_EXTRA.split(text)
    if len(parts) <= 1:
        parts = _RE_CHUNK_SPLIT.split(text)
    chunks = [p.strip() for p in parts if len(p.strip()) >= min_chars]
    if not chunks:
        chunks = [text.strip()]

    seen:   set[str]  = set()
    unique: list[str] = []
    removed = 0
    for chunk in chunks:
        fp = hashlib.md5(chunk.encode("utf-8")).hexdigest()
        if fp not in seen:
            seen.add(fp)
            unique.append(chunk)
        else:
            removed += 1

    return "\n\n".join(unique), removed


# ════════════════════════════════════════════════════════════
# 术语归一化（可选，由用户完全控制）
# ════════════════════════════════════════════════════════════

# 仅内置少量无歧义的电工缩写；大部分替换应由用户通过 extra_term_map 提供
_DEFAULT_TERM_MAP: dict[str, str] = {}  # 空默认，避免误替换


def _normalize_terms(text: str, extra_map: dict[str, str]) -> str:
    if not extra_map:
        return text

    sorted_terms = sorted(extra_map.items(), key=lambda x: len(x[0]), reverse=True)

    # 先保护括号内内容，避免误替换说明性文字
    placeholders: list[str] = []

    def _ph(m: re.Match) -> str:
        placeholders.append(m.group(0))
        return f"\x00PH{len(placeholders)-1}\x00"

    protected = re.sub(r"[（(][^）)]{1,80}[）)]", _ph, text)

    for short, full in sorted_terms:
        try:
            pattern = (
                r"(?<![A-Za-z\u4e00-\u9fff])"
                + re.escape(short)
                + r"(?![A-Za-z\u4e00-\u9fff])"
            )
            protected = re.sub(pattern, full, protected)
        except re.error:
            pass

    for i, original in enumerate(placeholders):
        protected = protected.replace(f"\x00PH{i}\x00", original)

    return protected


# ════════════════════════════════════════════════════════════
# 主清洗流程
# ════════════════════════════════════════════════════════════

def _clean(
    text: str,
    extra_noise: list[str],
    extra_terms: dict[str, str],
) -> tuple[str, dict[str, Any]]:

    stats: dict[str, Any] = {"original_chars": len(text)}

    def _step(name: str, fn, *args):
        nonlocal text
        try:
            text = fn(text, *args) if args else fn(text)
        except Exception as exc:
            stats[f"error_{name}"] = str(exc)
        stats[f"after_{name}"] = len(text)

    text = _protect_std_refs(text)           # Step 1（不计入 stats，是装饰器）

    _step("noise",    _remove_noise,          extra_noise)   # Step 2
    _step("cover",    _strip_cover_lines)                    # Step 3
    _step("toc",      _strip_toc)                            # Step 3b ★目录剥离，先于章节升级
    _step("hrules",   _fix_stray_hrules)                     # Step 4 ★先于表格修复
    _step("tbl_cols", _fix_table_split_columns)              # Step 5 ★先于表格空行
    _step("headings", _normalize_headings)                   # Step 6 ★先于折行空格
    _step("tables",   _fix_table_structure)                  # Step 7
    _step("han_sp",   _fix_han_spaces)                       # Step 8
    _step("cell_sp",  _fix_table_cell_spaces)                # Step 9
    _step("breaks",   _fix_cross_line_breaks)                # Step 10
    _step("terms",    _normalize_terms,       extra_terms)   # 术语（可选）
    _step("expand",   _inject_table_expansions)              # Step 12: 表格行展开

    text = _restore_std_refs(text)           # 还原标准文号
    text = re.sub(r"\n{3,}", "\n\n", text)    # Final squeeze：收缩所有多余空行

    text, removed = _deduplicate(text)       # Step 9
    stats["removed_chunks"] = removed
    stats["final_chars"]    = len(text)

    return text, stats


# ════════════════════════════════════════════════════════════
# 参数解析
# ════════════════════════════════════════════════════════════

def _parse_extra_noise(raw: str) -> list[str]:
    """每行一条正则，空行跳过。"""
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _parse_extra_terms(raw: str) -> dict[str, str]:
    """每行格式：简称=全称，忽略无效行。"""
    result: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if "=" in line:
            parts = line.split("=", 1)
            short, full = parts[0].strip(), parts[1].strip()
            if short and full:
                result[short] = full
    return result


# ════════════════════════════════════════════════════════════
# 文件下载（内网 SSL）
# ════════════════════════════════════════════════════════════

def _file_attr(file_meta, name):
    """兼容对象与 dict 两种形态取属性。"""
    if isinstance(file_meta, dict):
        return file_meta.get(name)
    return getattr(file_meta, name, None)


def _read_file_bytes(file_meta) -> BytesIO:
    """
    读取上传文件字节。URL 优先，【绝不访问 file_meta.blob】。
    Dify 内置迭代节点传入的 file 常常只有 remote_url（url 为空甚至为 bool），
    故 url → remote_url 依次尝试，并先判类型；都拿不到才退回 blob 兜底。
    """
    for attr in ("url", "remote_url"):
        u = _file_attr(file_meta, attr)
        if isinstance(u, str) and u.startswith("http"):
            return _download(u)
    blob = _file_attr(file_meta, "blob")  # 仅当拿不到任何 URL 时兜底
    if isinstance(blob, (bytes, bytearray)) and len(blob) > 0:
        return BytesIO(bytes(blob))
    raise RuntimeError("无法获取文件内容：url/remote_url 均无效，且 blob 为空。")


def _download(url: str) -> BytesIO:
    """
    下载到内存。策略：先校验、证书校验失败即回退不校验重试。
    不靠「URL 含 /files/ 等子串」判内外网——那套对内网对象存储(MinIO/S3)、
    自定义域名会漏判，导致去校验内网自签名证书而 CERTIFICATE_VERIFY_FAILED。

    两条分支都不加载系统 CA，故 ARM64 离线容器（/etc/ssl/certs 为空）创建阶段不会崩：
    - 校验分支：用【包内 certifi】的 cacert.pem 建上下文（随 wheel 打进包，必定存在）；
    - 不校验分支：用 ssl._create_unverified_context()（完全不加载任何 CA）。
    http 链接 urllib 不走 SSL，本函数同样适用。
    """
    def _fetch(verify: bool) -> BytesIO:
        if verify:
            ctx = ssl.create_default_context(cafile=certifi.where())
        else:
            ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=ctx, timeout=60) as resp:
            return BytesIO(resp.read())

    # 已知 Dify 内部/本地 URL 直接不校验，省一次失败往返
    if any(x in url for x in ["/files/", "/console/api/", "127.0.0.1", "localhost", "dify"]):
        return _fetch(verify=False)
    try:
        return _fetch(verify=True)
    except Exception as e:
        # 仅证书校验类错误回退到不校验；其它错误（404/拒连等）照常抛出
        if "CERTIFICATE_VERIFY" in str(e) or isinstance(getattr(e, "reason", None), ssl.SSLError):
            return _fetch(verify=False)
        raise


# ════════════════════════════════════════════════════════════
# Dify Tool
# ════════════════════════════════════════════════════════════

class CleanMdTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        file_meta = tool_parameters.get("file")
        if file_meta is None:
            raise ValueError("file 不能为空，请上传 Markdown 文件")

        extra_noise = _parse_extra_noise(tool_parameters.get("extra_noise_patterns") or "")
        extra_terms = _parse_extra_terms(tool_parameters.get("extra_term_map")       or "")

        yield self.create_text_message("⏳ 正在下载文件…")
        try:
            raw_bytes = _read_file_bytes(file_meta)
        except Exception as exc:
            raise RuntimeError(f"文件下载失败：{exc}") from exc

        yield self.create_text_message("⏳ 正在清洗文档（通用 RAG 增强版 v3.6，共 12 步）…")
        try:
            raw_text = raw_bytes.read().decode("utf-8")
            cleaned, stats = _clean(raw_text, extra_noise, extra_terms)
        except Exception as exc:
            raise RuntimeError(f"文档清洗失败：{exc}") from exc

        # 步骤详情摘要
        step_detail = "  →  ".join(
            f"{k.replace('after_','')}: {v}"
            for k, v in stats.items()
            if k.startswith("after_")
        )
        summary = (
            f"✅ 清洗完成（通用 RAG 增强版 v3.6）\n"
            f"- 原始字符数：{stats['original_chars']}\n"
            f"- 最终字符数：{stats['final_chars']}\n"
            f"- 字符变化：{stats['final_chars'] - stats['original_chars']:+d}\n"
            f"- 去除重复分块：{stats['removed_chunks']} 个\n"
            f"- 自定义噪音规则：{len(extra_noise)} 条\n"
            f"- 自定义术语规则：{len(extra_terms)} 条\n"
            f"步骤字符数：{step_detail}"
        )
        yield self.create_text_message(summary)
        yield self.create_text_message(cleaned)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        yield self.create_blob_message(
            blob=cleaned.encode("utf-8"),
            meta={"mime_type": "text/markdown", "filename": f"cleaned_{ts}.md"},
        )

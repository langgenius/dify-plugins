"""
KG Chunk Validator
校验图谱化分块 Markdown 的质量，输出结构化报告。
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


def validate_kg_chunks(text: str) -> dict:
    """
    校验图谱化分块质量。
    返回包含各项指标的字典。
    """
    results = {
        "total_chunks": 0,
        "has_trap_block": False,
        "has_relation_index": False,
        "chunks": [],
        "issues": [],
        "score": 0,
    }

    # 统计总块数
    chunk_headers = re.findall(r'##\s+【图谱块\s*(\w+)】(.+)', text)
    results["total_chunks"] = len(chunk_headers)

    # 是否有陷阱块
    results["has_trap_block"] = '【图谱块 TRAP】' in text

    # 是否有关系索引
    results["has_relation_index"] = '实体关系索引' in text

    # 逐块检查必填字段
    chunk_pattern = re.compile(
        r'##\s+【图谱块[^】]*】(.+?)\n(.*?)(?=##\s+【图谱块|##\s+附：|$)',
        re.DOTALL
    )
    required_fields = ['【实体】', '【类型】', '【关系-上游】', '【关系-下游】', '【关联实体】']

    for m in chunk_pattern.finditer(text):
        chunk_title = m.group(1).strip()
        chunk_body = m.group(2)
        chunk_info = {"title": chunk_title, "missing_fields": [], "has_content": False}

        for field in required_fields:
            if field not in chunk_body:
                chunk_info["missing_fields"].append(field)

        # 检查实际内容是否超过3行（排除标注行）
        content_lines = [
            l for l in chunk_body.split('\n')
            if l.strip() and not l.strip().startswith('**【')
            and not l.strip().startswith('---')
            and not l.strip().startswith('>')
        ]
        chunk_info["has_content"] = len(content_lines) >= 2

        if chunk_info["missing_fields"]:
            results["issues"].append(
                f"块「{chunk_title}」缺少字段：{', '.join(chunk_info['missing_fields'])}"
            )
        if not chunk_info["has_content"]:
            results["issues"].append(f"块「{chunk_title}」正文内容过少（少于2行）")

        results["chunks"].append(chunk_info)

    # 检查关系链连通性（上游引用的实体是否在其他块中出现）
    all_entity_names = re.findall(r'\*\*【实体】\*\*\s*(.+)', text)
    upstream_refs = re.findall(r'\*\*【关系-上游】\*\*\s*(.+)', text)
    dangling_refs = []
    for ref_line in upstream_refs:
        refs = re.split(r'[→、，,]', ref_line)
        for ref in refs:
            ref = ref.strip()
            if ref in ('（文档起始节）', '独立领域', '所有规则块 → 本块补充说明', '—'):
                continue
            if ref and not any(ref in name for name in all_entity_names):
                dangling_refs.append(ref)

    if dangling_refs:
        unique_dangling = list(dict.fromkeys(dangling_refs))[:5]
        results["issues"].append(
            f"以下上游引用未找到对应实体块（可能是跨文档引用，非错误）：{', '.join(unique_dangling)}"
        )

    # 计算质量评分（满分100）
    score = 100
    if results["total_chunks"] == 0:
        return {**results, "score": 0,
                "issues": ["未检测到任何图谱块，请确认文件格式正确。"]}

    # 每个缺字段问题 -5 分
    field_issues = sum(1 for iss in results["issues"] if '缺少字段' in iss)
    score -= field_issues * 5

    # 无陷阱块 -10 分
    if not results["has_trap_block"]:
        score -= 10
        results["issues"].append("未检测到陷阱纠错块（建议开启 trap_mode）")

    # 无关系索引 -5 分
    if not results["has_relation_index"]:
        score -= 5

    # 内容过少 -3 分/块
    thin_chunks = sum(1 for c in results["chunks"] if not c["has_content"])
    score -= thin_chunks * 3

    results["score"] = max(0, score)
    return results


def _format_report(v: dict, filename: str) -> str:
    """将校验结果格式化为可读报告"""
    grade = (
        "🟢 优秀" if v["score"] >= 90
        else "🟡 良好" if v["score"] >= 75
        else "🟠 需改进" if v["score"] >= 60
        else "🔴 不合格"
    )

    report_lines = [
        f"# 图谱化分块质量报告",
        f"",
        f"**文件：** {filename}",
        f"**综合评分：** {v['score']} / 100　{grade}",
        f"",
        f"## 结构统计",
        f"",
        f"| 指标 | 结果 |",
        f"|---|---|",
        f"| 主题块数量 | {v['total_chunks']} 个 |",
        f"| 陷阱纠错块 | {'✅ 存在' if v['has_trap_block'] else '❌ 缺失'} |",
        f"| 实体关系索引 | {'✅ 存在' if v['has_relation_index'] else '❌ 缺失'} |",
        f"| 发现问题数 | {len(v['issues'])} 条 |",
        f"",
    ]

    if v["issues"]:
        report_lines += [
            "## 发现的问题",
            "",
        ]
        for i, iss in enumerate(v["issues"], 1):
            report_lines.append(f"{i}. {iss}")
        report_lines.append("")
    else:
        report_lines += ["## 发现的问题", "", "✅ 无问题，分块质量良好。", ""]

    # 各块详情
    report_lines += ["## 各块检查明细", "", "| 块名称 | 缺失字段 | 内容充实 |", "|---|---|---|"]
    for c in v["chunks"]:
        missing = ', '.join(c["missing_fields"]) if c["missing_fields"] else "—"
        content_ok = "✅" if c["has_content"] else "⚠️ 偏少"
        report_lines.append(f"| {c['title']} | {missing} | {content_ok} |")

    report_lines += [
        "",
        "---",
        "",
        "## 导入建议",
        "",
        "1. 评分 ≥ 90：可直接导入 Dify 知识库",
        "2. 评分 75–89：建议人工检查标注了问题的块后再导入",
        "3. 评分 < 75：建议重新生成或手动修正后再导入",
        "",
        "> 本报告由 KG Chunk Validator 自动生成",
    ]

    return '\n'.join(report_lines)


class KgValidateTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        file_meta = tool_parameters.get('file')
        if not file_meta:
            raise Exception('请上传图谱化分块 Markdown 文件。')

        try:
            file_bytes = _download(file_meta.url)
            file_bytes.seek(0)
            text = file_bytes.read().decode('utf-8', errors='replace')
        except Exception as e:
            raise Exception(f'文件读取失败：{str(e)}')

        if not text.strip():
            raise Exception('文件内容为空。')

        filename = getattr(file_meta, 'filename', 'kg_chunks_output.md') or 'kg_chunks_output.md'

        validation = validate_kg_chunks(text)
        report_md = _format_report(validation, filename)

        # 输出文本摘要
        summary = (
            f"校验完成 | 评分：{validation['score']}/100 | "
            f"块数：{validation['total_chunks']} | "
            f"问题：{len(validation['issues'])} 条"
        )
        yield self.create_text_message(summary)

        # 输出完整报告文件
        yield self.create_blob_message(
            blob=report_md.encode('utf-8'),
            meta={
                "mime_type": "text/markdown",
                "filename": "kg_validation_report.md"
            }
        )

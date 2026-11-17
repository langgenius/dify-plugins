#!/usr/bin/env python3
"""Governance check: near-duplicate plugin detection (three channels).

Motivation (marketplace audit, 1270 unpacked .difypkg files):
  * acedatacloud ships 17 single-purpose wrappers whose shared client module is
    98.6% identical across packages (reskin family).
  * flashdata-dev ships 16 plugins generated from one template (same source
    skeleton), investoday ships 11 data-category splits from one template.
  * 13 cross-author name collisions (volcengine_ai, zendesk, amap, qdrant, ...)
    only surfaced through a post-hoc full-marketplace audit.
  All of these are detectable at pull-request time.

Channels
  1. Name collision  - normalized plugin name (lowercase, alphanumeric only,
     generic suffixes such as "plugin"/"tool"/"dify"/"integration" stripped):
        same author + same normalized name in a different directory -> FAIL
        different author + same normalized name                  -> WARNING
  2. Text similarity - normalized name / label / tags / description:
        name similarity  >= 0.65                                  -> WARNING
        description similarity >= 0.65                            -> WARNING
        tag Jaccard >= 0.65 AND name similarity >= 0.50            -> WARNING
  3. Source skeleton - every source file is normalized (comments, string
     literals and identifiers removed, keywords/operators kept) and the plugin
     is reduced to the set of its normalized lines:
        Jaccard(plugin, other plugin) >= 0.85                     -> WARNING

Warnings never block a merge; they are written to the job summary so that
reviewers can ask the author to explain the difference. Only a same-author name
collision (channel 1) fails the check.

The script is stand-alone (stdlib only; PyYAML used when available) and reads
the whole repository as the comparison corpus, plus the files changed by the PR.

Usage:
    python3 check_near_duplicates.py --changed-files changed_files.json --repo-root .
    python3 check_near_duplicates.py --changed-files all.json --repo-root . --audit-all
"""

from __future__ import annotations

import argparse
import difflib
import io
import json
import keyword
import os
import re
import sys
import tokenize
import zipfile

NAME_SIMILARITY_THRESHOLD = 0.65
DESCRIPTION_SIMILARITY_THRESHOLD = 0.65
TAG_JACCARD_THRESHOLD = 0.65
# Tags alone are weak evidence (80.9% of all tag assignments are utilities or
# productivity), so a tag overlap only counts when the names are similar too.
TAG_JACCARD_MIN_NAME_SIMILARITY = 0.65
SKELETON_JACCARD_THRESHOLD = 0.85
# Descriptions shorter than this carry no signal for text similarity.
MIN_DESCRIPTION_LENGTH = 40

GENERIC_NAME_SUFFIXES = [
    "plugin", "plugins", "tools", "tool", "dify", "integration", "integrations",
    "helper", "official", "unofficial",
]

SOURCE_EXTENSIONS = (".py", ".js", ".ts", ".mjs", ".cjs", ".go", ".java", ".rb", ".php")


# ---------------------------------------------------------------------------
# Minimal YAML subset parser (fallback when PyYAML is not installed)
# ---------------------------------------------------------------------------
def _strip_comment(value: str) -> str:
    quote = None
    for i, ch in enumerate(value):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "#" and i > 0 and value[i - 1] in " \t":
            return value[:i]
    return value


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        inner = value[1:-1]
        if value[0] == "'":
            return inner.replace("''", "'")
        return inner.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")
    return value


def _scalar(value: str):
    value = _strip_comment(value).strip()
    if value in ("{}", "[]"):
        return {} if value == "{}" else []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_unquote(x) for x in inner.split(",")] if inner else []
    return _unquote(value)


def _fold_continuations(lines):
    folded = []
    for indent, content in lines:
        if folded and indent > folded[-1][0]:
            prev_indent, prev = folded[-1]
            m = re.match(r"^([^:]+):(?:\s+(.*))?$", prev)
            if m and (m.group(2) or "").strip():
                value = _strip_comment(m.group(2)).strip()
                quote = value[:1] if value[:1] in ("'", '"') else ""
                if not quote or not value.endswith(quote):
                    folded[-1] = (prev_indent, prev + " " + content)
                    continue
        folded.append((indent, content))
    return folded


def _mini_yaml_load(text: str):
    if text.lstrip()[:1] == "{":
        import json

        try:
            return json.loads(text)
        except Exception:
            pass
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        lines.append((len(raw) - len(raw.lstrip(" ")), raw.strip()))
    lines = _fold_continuations(lines)

    def parse_block(idx, indent):
        if idx >= len(lines):
            return None, idx
        if lines[idx][1].startswith("- "):
            items = []
            while idx < len(lines) and lines[idx][0] == indent and lines[idx][1].startswith("- "):
                items.append(_scalar(lines[idx][1][2:]))
                idx += 1
            return items, idx
        result = {}
        while idx < len(lines):
            ind, content = lines[idx]
            if ind < indent:
                break
            if ind > indent:
                idx += 1
                continue
            if content.startswith("- "):
                break
            m = re.match(r"^([^:#]+):(?:\s+(.*))?$", content)
            if not m:
                idx += 1
                continue
            key = _unquote(m.group(1))
            rest = (m.group(2) or "").strip()
            idx += 1
            if rest:
                block = re.match(r"^([|>])([+-]?\d*)(?:\s+(.*))?$", rest)
                if block:
                    parts = []
                    if block.group(3):
                        parts.append(block.group(3))
                    while idx < len(lines) and lines[idx][0] > ind:
                        parts.append(lines[idx][1])
                        idx += 1
                    result[key] = ("\n" if block.group(1) == "|" else " ").join(parts)
                else:
                    result[key] = _scalar(rest)
            elif idx < len(lines) and lines[idx][0] > ind:
                result[key], idx = parse_block(idx, lines[idx][0])
            elif idx < len(lines) and lines[idx][0] == ind and lines[idx][1].startswith("- "):
                result[key], idx = parse_block(idx, ind)
            else:
                result[key] = None
        return result, idx

    value, _ = parse_block(0, 0)
    return value if isinstance(value, dict) else {}


def load_manifest_text(text: str):
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _mini_yaml_load(text)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
def normalize_author(value) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def normalize_name(value) -> str:
    name = re.sub(r"[^a-z0-9]+", "", (value or "").lower())
    for suffix in GENERIC_NAME_SUFFIXES:
        if name.endswith(suffix) and len(name) > len(suffix) + 3:
            name = name[: -len(suffix)]
    return name


def _text_value(value):
    """Flatten a label/description field (str or {locale: str}) into one string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(str(v) for v in value.values() if isinstance(v, str))
    if isinstance(value, (list, tuple)):
        return " ".join(_text_value(v) for v in value)
    return str(value)


def normalize_text(value) -> str:
    text = _text_value(value).lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_tags(value):
    if not isinstance(value, (list, tuple)):
        return set()
    return {str(t).strip().lower() for t in value if isinstance(t, str) and t.strip()}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    return (len(a & b) / union) if union else 0.0


# ---------------------------------------------------------------------------
# Source skeleton extraction
# ---------------------------------------------------------------------------
def python_skeleton(source: str):
    """Normalized line set for Python source: comments/strings/identifiers removed."""
    lines = set()
    current = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except Exception:
        return None
    for tok in tokens:
        if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                        tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER):
            if current:
                lines.add(" ".join(current))
                current = []
            continue
        if tok.type == tokenize.STRING:
            current.append('"STR"')
        elif tok.type == tokenize.NUMBER:
            current.append("NUM")
        elif tok.type == tokenize.NAME:
            current.append(tok.string if keyword.iskeyword(tok.string) else "ID")
        else:
            current.append(tok.string)
    if current:
        lines.add(" ".join(current))
    lines.discard("")
    return lines or None


_GENERIC_COMMENT = re.compile(r"(#|//)[^\n]*")
_GENERIC_STRING = re.compile(r"(\"(\\.|[^\"\\])*\"|'(\\.|[^'\\])*'|`(\\.|[^`\\])*`)")
_GENERIC_IDENT = re.compile(r"\b[A-Za-z_$][A-Za-z0-9_$]*\b")


def generic_skeleton(source: str):
    """Best-effort normalized line set for non-Python source files."""
    source = _GENERIC_COMMENT.sub(" ", source)
    source = _GENERIC_STRING.sub('"STR"', source)
    lines = set()
    for raw in source.splitlines():
        line = _GENERIC_IDENT.sub("ID", raw).strip()
        line = re.sub(r"\s+", " ", line)
        if line and line not in ("ID", "ID ID"):
            lines.add(line)
    return lines or None


def file_skeleton(name: str, data: bytes):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if name.endswith(".py"):
        return python_skeleton(text)
    if name.endswith(SOURCE_EXTENSIONS):
        return generic_skeleton(text)
    return None


# ---------------------------------------------------------------------------
# Plugin corpus
# ---------------------------------------------------------------------------
class Plugin:
    __slots__ = ("path", "plugin_dir", "author", "name", "version", "tags", "label",
                 "description", "norm_author", "norm_name", "norm_label", "norm_desc",
                 "skeleton", "skeleton_size", "error")

    def __init__(self, path):
        self.path = path
        self.plugin_dir = os.path.dirname(path)
        self.author = ""
        self.name = ""
        self.version = ""
        self.tags = set()
        self.label = ""
        self.description = ""
        self.norm_author = ""
        self.norm_name = ""
        self.norm_label = ""
        self.norm_desc = ""
        self.skeleton = set()
        self.skeleton_size = 0
        self.error = None

    @property
    def identity(self):
        return f"{self.author}/{self.name}"

    def summary(self):
        return f"{self.path} ({self.author}/{self.name} v{self.version})"


def read_plugin(rel_path: str, repo_root: str = ".", with_skeleton: bool = True) -> Plugin:
    plugin = Plugin(rel_path)
    try:
        with zipfile.ZipFile(os.path.join(repo_root, rel_path)) as archive:
            members = [n for n in archive.namelist() if os.path.basename(n) in ("manifest.yaml", "manifest.yml")]
            members.sort(key=lambda n: (n.count("/"), n))
            if members:
                manifest = load_manifest_text(archive.read(members[0]).decode("utf-8", errors="replace"))
                plugin.author = str(manifest.get("author") or "")
                plugin.name = str(manifest.get("name") or "")
                plugin.version = str(manifest.get("version") or "")
                plugin.tags = normalize_tags(manifest.get("tags"))
                plugin.label = _text_value(manifest.get("label"))
                plugin.description = _text_value(manifest.get("description"))
            if with_skeleton:
                skeleton = set()
                for member in archive.namelist():
                    if member.endswith(SOURCE_EXTENSIONS):
                        part = file_skeleton(member, archive.read(member))
                        if part:
                            skeleton |= part
                plugin.skeleton = skeleton
                plugin.skeleton_size = len(skeleton)
    except Exception as exc:  # unreadable package: keep the record, skip comparisons
        plugin.error = str(exc)
    plugin.norm_author = normalize_author(plugin.author)
    plugin.norm_name = normalize_name(plugin.name)
    plugin.norm_label = normalize_text(plugin.label)
    plugin.norm_desc = normalize_text(plugin.description)
    return plugin


def discover_packages(repo_root: str):
    packages = []
    for root, dirs, files in os.walk(repo_root):
        if ".git" in root.split(os.sep):
            continue
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            if name.endswith(".difypkg"):
                packages.append(os.path.relpath(os.path.join(root, name), repo_root))
    return sorted(packages)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------
class Finding:
    def __init__(self, channel, level, changed, other, score, detail):
        self.channel = channel
        self.level = level
        self.changed = changed
        self.other = other
        self.score = score
        self.detail = detail

    def sort_key(self):
        return (-self.score, self.other.path)

    def render(self):
        return (f"- **{self.level}** [{self.channel}] `{self.changed.path}` vs "
                f"`{self.other.path}` (score {self.score:.2f}) - {self.detail}")


def name_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if abs(len(a) - len(b)) > 0.5 * max(len(a), len(b)):
        return 0.0  # cheap upper-bound prefilter
    return difflib.SequenceMatcher(None, a, b).ratio()


def text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if abs(len(a) - len(b)) > 0.5 * max(len(a), len(b)):
        return 0.0  # cheap upper-bound prefilter
    return difflib.SequenceMatcher(None, a, b).ratio()


def compare(changed: Plugin, other: Plugin):
    """Compare one changed plugin against one corpus plugin. Returns a list of Finding."""
    if other.path == changed.path or other.plugin_dir == changed.plugin_dir:
        return []  # same package or another version of the same plugin directory
    if other.error:
        return []

    findings = []

    # Channel 1: normalized name collision.
    if changed.norm_name and changed.norm_name == other.norm_name:
        if changed.norm_author == other.norm_author:
            findings.append(Finding(
                "name-collision", "FAIL", changed, other, 1.0,
                f"same author `{changed.author}` already ships a plugin named `{other.name}` "
                f"in a different directory; normalize the name or consolidate the plugins"))
        else:
            findings.append(Finding(
                "name-collision", "WARNING", changed, other, 1.0,
                f"plugin name `{changed.name}` collides with `{other.identity}` by another author"))

    # Channel 2: name / tags / description text similarity.
    name_sim = name_similarity(changed.norm_name, other.norm_name)
    desc_sim = text_similarity(changed.norm_desc, other.norm_desc)
    label_sim = text_similarity(changed.norm_label, other.norm_label)
    tag_sim = jaccard(changed.tags, other.tags)
    if name_sim >= NAME_SIMILARITY_THRESHOLD:
        findings.append(Finding(
            "text-similarity", "WARNING", changed, other, name_sim,
            f"normalized names are similar (`{changed.name}` vs `{other.name}`)"))
    descriptions_comparable = (
        len(changed.norm_desc) >= MIN_DESCRIPTION_LENGTH
        and len(other.norm_desc) >= MIN_DESCRIPTION_LENGTH
    )
    if descriptions_comparable and desc_sim >= DESCRIPTION_SIMILARITY_THRESHOLD:
        findings.append(Finding(
            "text-similarity", "WARNING", changed, other, desc_sim,
            f"descriptions are {desc_sim:.0%} similar"))
    if tag_sim >= TAG_JACCARD_THRESHOLD and name_sim >= TAG_JACCARD_MIN_NAME_SIMILARITY:
        findings.append(Finding(
            "text-similarity", "WARNING", changed, other, max(tag_sim, name_sim),
            f"tags {sorted(changed.tags)} / {sorted(other.tags)} overlap {tag_sim:.0%} "
            f"and names are similar"))

    # Channel 3: normalized source skeleton Jaccard.
    if changed.skeleton and other.skeleton:
        smaller = min(changed.skeleton_size, other.skeleton_size)
        larger = max(changed.skeleton_size, other.skeleton_size)
        if smaller / larger >= SKELETON_JACCARD_THRESHOLD:  # Jaccard upper bound
            score = jaccard(changed.skeleton, other.skeleton)
            if score >= SKELETON_JACCARD_THRESHOLD:
                findings.append(Finding(
                    "source-skeleton", "WARNING", changed, other, score,
                    f"normalized source line sets are {score:.0%} identical "
                    f"({smaller} shared lines, {larger} lines in the larger plugin)"))
    return findings


def run_checks(corpus, changed_plugins, max_findings_per_plugin=25):
    findings = []
    for changed in changed_plugins:
        if changed.error:
            continue
        per_plugin = []
        for other in corpus:
            per_plugin.extend(compare(changed, other))
        per_plugin.sort(key=Finding.sort_key)
        failures = [f for f in per_plugin if f.level == "FAIL"]
        warnings = [f for f in per_plugin if f.level == "WARNING"]
        findings.extend(failures)
        findings.extend(warnings[:max_findings_per_plugin])
    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def render_summary(findings, checked_count, corpus_count, max_findings_per_plugin=25):
    errors = [f for f in findings if f.level == "FAIL"]
    warnings = [f for f in findings if f.level == "WARNING"]
    by_channel = {}
    for finding in findings:
        by_channel.setdefault(finding.channel, {"FAIL": 0, "WARNING": 0})
        by_channel[finding.channel][finding.level] += 1

    lines = []
    lines.append("## Near-duplicate governance check")
    lines.append("")
    lines.append(f"Checked **{checked_count}** changed package(s) against **{corpus_count}** "
                 f"package(s) in the repository.")
    lines.append("")
    lines.append(f"- same-author name collisions (fail): **{len(errors)}**")
    lines.append(f"- warnings (non-blocking): **{len(warnings)}**")
    lines.append("")
    if by_channel:
        lines.append("| channel | fail | warning |")
        lines.append("|---|---|---|")
        for channel in sorted(by_channel):
            lines.append(f"| {channel} | {by_channel[channel]['FAIL']} | {by_channel[channel]['WARNING']} |")
        lines.append("")
    if errors:
        lines.append("### Blocking findings")
        lines.append("")
        for finding in errors:
            lines.append(finding.render())
        lines.append("")
    if warnings:
        lines.append("### Non-blocking warnings")
        lines.append("")
        lines.append("Warnings do not block the merge. They ask the author to explain in the PR "
                     "how this plugin differs from the listed package(s).")
        lines.append("")
        for finding in warnings[:max_findings_per_plugin]:
            lines.append(finding.render())
        if len(warnings) > max_findings_per_plugin:
            lines.append(f"- ... and {len(warnings) - max_findings_per_plugin} more warning(s) "
                         f"(showing the {max_findings_per_plugin} highest-scoring ones).")
        lines.append("")
    if not findings:
        lines.append("No name collisions, text similarities or source-skeleton matches were found.")
        lines.append("")
    return "\n".join(lines), errors, warnings


def collect_changed_files(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("files", [])
    return [(item["filename"], item.get("status", "modified")) for item in data]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Near-duplicate plugin detection for changed packages.")
    parser.add_argument("--changed-files", required=True,
                        help="JSON file with the PR changed files: [{'filename': ..., 'status': ...}]")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--audit-all", action="store_true",
                        help="audit mode: treat every package in the repository as changed "
                             "(used to validate detection quality against the full marketplace)")
    parser.add_argument("--summary-file", default=None,
                        help="write the markdown summary to this file (default: $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    changed = collect_changed_files(args.changed_files)
    changed_packages = sorted({
        filename for filename, status in changed
        if status != "removed" and filename.endswith(".difypkg")
    })

    all_packages = discover_packages(args.repo_root)
    if args.audit_all:
        changed_packages = all_packages

    if not changed_packages:
        print("No changed .difypkg files: nothing to check.")
        return 0

    print(f"Reading corpus: {len(all_packages)} package(s) ...")
    corpus = [read_plugin(path, args.repo_root) for path in all_packages]
    unreadable = [p for p in corpus if p.error]
    for plugin in unreadable:
        print(f"warning: could not read {plugin.path}: {plugin.error}")
    by_path = {plugin.path: plugin for plugin in corpus}

    missing = [p for p in changed_packages if p not in set(all_packages)]
    for path in missing:
        print(f"warning: changed package not found in working tree: {path}")

    changed_plugins = [by_path[path] for path in changed_packages if path in by_path]
    if not changed_plugins:
        print("Changed packages are not present in the working tree: nothing to check.")
        return 0

    max_findings_per_plugin = 25
    findings = run_checks(corpus, changed_plugins, max_findings_per_plugin)

    summary, errors, warnings = render_summary(findings, len(changed_plugins), len(corpus),
                                                  max_findings_per_plugin)
    print()
    print(summary)

    summary_file = args.summary_file or os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(summary + "\n")

    print(f"Near-duplicate check: {len(errors)} blocking finding(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

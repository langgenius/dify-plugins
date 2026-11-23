#!/usr/bin/env python3
"""Governance check: manifest tags must be non-empty and inside the controlled vocabulary.

Motivation (marketplace audit, 1270 unpacked .difypkg files):
  * 63.2% of packages (803/1270) ship without any tag, so marketplace filtering
    and search cannot cover the majority of the supply.
  * Of the tagged packages, utilities (192) + productivity (186) cover 80.9% of
    all tag assignments, i.e. the vocabulary has collapsed into two catch-all
    buckets and authors have no meaningful tag to choose from.

This script is a stand-alone CI check (stdlib only; PyYAML is used when present).
It inspects only the files changed by a pull request: every changed `.difypkg`
is read as a zip archive and every changed `manifest.yaml` is read from the
working tree.

Usage:
    python3 check_manifest_tags.py --changed-files changed_files.json --repo-root .

`changed_files.json` is a JSON list of objects: {"filename": "...", "status": "..."}.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import zipfile

# ---------------------------------------------------------------------------
# Controlled tag vocabulary
# ---------------------------------------------------------------------------
# Existing 17 marketplace tags.
EXISTING_TAGS = [
    "agent", "business", "design", "education", "entertainment", "finance",
    "image", "news", "other", "productivity", "rag", "search", "social",
    "travel", "utilities", "videos", "weather",
]
# Proposed 8 additions (see governance report P0-1 / P1-1).
PROPOSED_TAGS = [
    "llm", "model_provider", "audio", "document", "devtools", "database",
    "security", "translation",
]
CONTROLLED_TAGS = sorted(set(EXISTING_TAGS) | set(PROPOSED_TAGS))

MANIFEST_NAMES = ("manifest.yaml", "manifest.yml")


# ---------------------------------------------------------------------------
# Minimal YAML subset parser (fallback when PyYAML is not installed)
# ---------------------------------------------------------------------------
def _strip_comment(value: str) -> str:
    """Drop a trailing ``# comment`` that is outside quotes."""
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
    """Fold more-indented continuation lines into the previous scalar value."""
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
    """Parse the manifest.yaml subset: scalars, nested maps, scalar lists, block scalars."""
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
                idx += 1  # defensive: continuations were folded already
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
    """Parse manifest YAML text, preferring PyYAML and falling back to the mini parser."""
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _mini_yaml_load(text)


def read_manifest_from_zip(pkg_path: str):
    """Return (manifest dict, manifest member name) for a .difypkg file."""
    with zipfile.ZipFile(pkg_path) as archive:
        members = [n for n in archive.namelist() if os.path.basename(n) in MANIFEST_NAMES]
        if not members:
            return None, None
        members.sort(key=lambda n: (n.count("/"), n))
        member = members[0]
        raw = archive.read(member)
    return load_manifest_text(raw.decode("utf-8", errors="replace")), member


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
class Finding:
    def __init__(self, level, target, message, hint=None):
        self.level = level
        self.target = target
        self.message = message
        self.hint = hint

    def render(self):
        lines = [f"[{self.level}] {self.target}: {self.message}"]
        if self.hint:
            lines.append(f"    how to fix: {self.hint}")
        return "\n".join(lines)


def check_manifest(manifest, target):
    """Validate the `tags` field of one manifest. Returns a list of Finding."""
    findings = []
    if manifest is None:
        findings.append(Finding("ERROR", target, "manifest.yaml is missing or unreadable inside the package.",
                                "Rebuild the .difypkg so that it contains a valid manifest.yaml at the archive root."))
        return findings

    tags = manifest.get("tags")
    if tags is None:
        findings.append(Finding(
            "ERROR", target,
            "`tags` is missing from manifest.yaml.",
            "Add a non-empty `tags` list to manifest.yaml using values from the controlled vocabulary "
            "(docs/marketplace-curation-policy.md), e.g. `tags:\\n- search`."))
        return findings

    if isinstance(tags, str) or not isinstance(tags, (list, tuple)):
        findings.append(Finding(
            "ERROR", target,
            f"`tags` must be a YAML list, got {type(tags).__name__}.",
            "Use the list form, e.g. `tags:\\n- search\\n- productivity`."))
        return findings

    if len(tags) == 0:
        findings.append(Finding(
            "ERROR", target,
            "`tags` is empty; at least one tag from the controlled vocabulary is required.",
            "Pick 1-3 tags that describe the plugin's function from: " + ", ".join(CONTROLLED_TAGS) + "."))
        return findings

    invalid = []
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            invalid.append(repr(tag))
            continue
        normalized = tag.strip().lower()
        if normalized not in CONTROLLED_TAGS:
            invalid.append(tag.strip())

    if invalid:
        findings.append(Finding(
            "ERROR", target,
            "tag(s) not in the controlled vocabulary: " + ", ".join(sorted(set(invalid))) + ".",
            "Use only tags from the controlled vocabulary: " + ", ".join(CONTROLLED_TAGS) +
            ". If your plugin needs a new tag, open a discussion issue first."))
    return findings


def collect_changed_files(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("files", [])
    return [(item["filename"], item.get("status", "modified")) for item in data]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate manifest tags for changed plugins.")
    parser.add_argument("--changed-files", required=True,
                        help="JSON file with the PR changed files: [{'filename': ..., 'status': ...}]")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    changed = collect_changed_files(args.changed_files)
    targets = []
    for filename, status in changed:
        if status == "removed":
            continue
        if filename.endswith(".difypkg"):
            targets.append(("package", filename))
        elif os.path.basename(filename) in MANIFEST_NAMES:
            targets.append(("manifest", filename))

    if not targets:
        print("No changed .difypkg or manifest.yaml files: nothing to validate.")
        return 0

    findings = []
    for kind, filename in targets:
        full_path = os.path.join(args.repo_root, filename)
        if kind == "package":
            if not os.path.isfile(full_path):
                continue  # renamed/moved away; nothing to validate
            manifest, member = read_manifest_from_zip(full_path)
            target = filename if member is None else f"{filename}:{member}"
        else:
            if not os.path.isfile(full_path):
                continue
            with open(full_path, "r", encoding="utf-8", errors="replace") as handle:
                manifest = load_manifest_text(handle.read())
            target = filename
        findings.extend(check_manifest(manifest, target))

    errors = [f for f in findings if f.level == "ERROR"]
    for finding in findings:
        print(finding.render())
        if finding.level == "ERROR":
            print(f"::error file={finding.target.split(':')[0]}::{finding.message}")

    print()
    print(f"Tag vocabulary check: {len(targets)} changed manifest(s), {len(errors)} error(s).")
    print(f"Controlled vocabulary ({len(CONTROLLED_TAGS)}): {', '.join(CONTROLLED_TAGS)}")
    if errors:
        print()
        print("Merge is blocked until every changed manifest.yaml declares at least one tag")
        print("from the controlled vocabulary. See docs/marketplace-curation-policy.md.")
        return 1
    print("All changed manifests declare tags from the controlled vocabulary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

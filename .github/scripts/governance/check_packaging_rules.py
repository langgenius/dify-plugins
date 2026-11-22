#!/usr/bin/env python3
"""Governance check: packaging rules for changed plugin packages.

Motivation (marketplace audit, 1270 unpacked .difypkg files):
  * 305 packages (24% of all packages, 186 authors) are stale old versions that
    sit next to the current version in the same directory.
  * 17 directories ship versions of the same plugin with contradictory tags, so
    the same plugin appears in the marketplace both tagged and untagged.
  * 153 packages (121 directories) are flattened into the author root directory
    instead of living in one-plugin-per-directory layout.

Rules enforced for the files changed by a pull request (no retro-active
repository-wide cleanup):
  R1 one plugin per directory - the directory of a changed .difypkg must not
     contain packages of a different plugin (different author or name).
  R2 no flattened packages - a .difypkg must not sit directly in the author root
     directory; it must live in its own plugin directory.
  R3 consistent tags across versions - if a directory holds several versions of
     the same plugin, every version must declare the same tags.

The script is stand-alone (stdlib only; PyYAML used when available).

Usage:
    python3 check_packaging_rules.py --changed-files changed_files.json --repo-root .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile

MANIFEST_NAMES = ("manifest.yaml", "manifest.yml")


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


def read_package_meta(pkg_path: str):
    """Return (author, name, version, tags) declared inside a .difypkg."""
    try:
        with zipfile.ZipFile(pkg_path) as archive:
            members = [n for n in archive.namelist() if os.path.basename(n) in MANIFEST_NAMES]
            if not members:
                return None
            members.sort(key=lambda n: (n.count("/"), n))
            manifest = load_manifest_text(archive.read(members[0]).decode("utf-8", errors="replace"))
    except Exception as exc:
        return {"error": str(exc)}
    tags = manifest.get("tags")
    if not isinstance(tags, (list, tuple)):
        tags = []
    return {
        "author": str(manifest.get("author") or ""),
        "name": str(manifest.get("name") or ""),
        "version": str(manifest.get("version") or ""),
        "tags": sorted({str(t).strip().lower() for t in tags if isinstance(t, str) and t.strip()}),
    }


def normalize_identity(author: str, name: str):
    return (re.sub(r"[^a-z0-9]+", "", author.lower()), re.sub(r"[^a-z0-9]+", "", name.lower()))


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
        lines = [f"- **{self.level}** `{self.target}`: {self.message}"]
        if self.hint:
            lines.append(f"  - how to fix: {self.hint}")
        return "\n".join(lines)


def check_directory(repo_root: str, changed_pkg: str):
    findings = []
    rel_parts = changed_pkg.split("/")
    full_pkg = os.path.join(repo_root, changed_pkg)
    directory = os.path.dirname(full_pkg)

    # R2: no flattened packages directly inside the author root directory.
    if len(rel_parts) <= 2:
        findings.append(Finding(
            "FAIL", changed_pkg,
            "the .difypkg sits directly in the author root directory (flattened layout).",
            f"Move it into its own plugin directory, e.g. `{rel_parts[0]}/<plugin-name>/{os.path.basename(changed_pkg)}`."))

    if not os.path.isdir(directory):
        return findings

    siblings = sorted(
        os.path.join(directory, name)
        for name in os.listdir(directory)
        if name.endswith(".difypkg")
    )
    if len(siblings) <= 1:
        return findings  # single package in the directory: R1 and R3 are satisfied

    entries = []
    for sib in siblings:
        meta = read_package_meta(sib)
        rel = os.path.relpath(sib, repo_root)
        if meta is None:
            findings.append(Finding(
                "FAIL", rel, "no manifest.yaml found inside the package.",
                "Rebuild the package so that manifest.yaml is included at the archive root."))
            continue
        if "error" in meta:
            findings.append(Finding(
                "FAIL", rel, f"package could not be read: {meta['error']}",
                "Re-pack the .difypkg (it must be a valid zip archive)."))
            continue
        meta["path"] = rel
        meta["identity"] = normalize_identity(meta["author"], meta["name"])
        entries.append(meta)

    # R1: one plugin per directory.
    identities = {entry["identity"] for entry in entries}
    if len(identities) > 1:
        listing = ", ".join(f"{entry['author']}/{entry['name']} ({os.path.basename(entry['path'])})"
                            for entry in entries)
        findings.append(Finding(
            "FAIL", changed_pkg,
            f"the directory contains packages of {len(identities)} different plugins: {listing}.",
            "Keep exactly one plugin per directory: move every other plugin into its own "
            "<author>/<plugin-name>/ directory."))

    # R3: consistent tags across versions of the same plugin.
    by_identity = {}
    for entry in entries:
        by_identity.setdefault(entry["identity"], []).append(entry)
    for identity, group in by_identity.items():
        if len(group) < 2:
            continue
        tag_sets = {tuple(entry["tags"]) for entry in group}
        if len(tag_sets) > 1:
            detail = "; ".join(
                f"{os.path.basename(entry['path'])} -> {entry['tags'] or 'no tags'}" for entry in group)
            findings.append(Finding(
                "FAIL", changed_pkg,
                f"versions of {group[0]['author']}/{group[0]['name']} in this directory declare "
                f"different tags ({detail}).",
                "Give every version of a plugin the same tags, and keep only the latest version "
                "in the repository (move older versions to GitHub Releases)."))
        else:
            versions = ", ".join(entry["version"] for entry in group)
            findings.append(Finding(
                "WARNING", changed_pkg,
                f"the directory holds {len(group)} versions of {group[0]['author']}/{group[0]['name']} "
                f"({versions}); tags are consistent.",
                "Keep only the latest .difypkg in the repository and publish older versions as "
                "GitHub Releases (see docs/marketplace-curation-policy.md)."))
    return findings


def collect_changed_files(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("files", [])
    return [(item["filename"], item.get("status", "modified")) for item in data]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Packaging rules for changed plugin packages.")
    parser.add_argument("--changed-files", required=True,
                        help="JSON file with the PR changed files: [{'filename': ..., 'status': ...}]")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--summary-file", default=None,
                        help="write the markdown summary to this file (default: $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    changed = collect_changed_files(args.changed_files)
    changed_packages = sorted({
        filename for filename, status in changed
        if status != "removed" and filename.endswith(".difypkg")
    })
    if not changed_packages:
        print("No changed .difypkg files: nothing to check.")
        return 0

    findings = []
    checked = 0
    for pkg in changed_packages:
        if not os.path.isfile(os.path.join(args.repo_root, pkg)):
            continue  # renamed/moved away
        checked += 1
        findings.extend(check_directory(args.repo_root, pkg))

    errors = [f for f in findings if f.level == "FAIL"]
    warnings = [f for f in findings if f.level == "WARNING"]

    lines = ["## Packaging governance check", ""]
    lines.append(f"Checked **{checked}** changed package(s) against the packaging rules "
                 "(one plugin per directory, no flattened packages, consistent tags across versions).")
    lines.append("")
    lines.append(f"- blocking findings: **{len(errors)}**")
    lines.append(f"- warnings (non-blocking): **{len(warnings)}**")
    lines.append("")
    if findings:
        lines.append("| rule | level | package |")
        lines.append("|---|---|---|")
        for finding in findings:
            lines.append(f"| packaging | {finding.level} | `{finding.target}` |")
        lines.append("")
        for finding in findings:
            lines.append(finding.render())
            lines.append("")
    else:
        lines.append("All changed packages satisfy the packaging rules.")
        lines.append("")
    summary = "\n".join(lines)
    print(summary)

    summary_file = args.summary_file or os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(summary + "\n")

    print(f"Packaging check: {len(errors)} blocking finding(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

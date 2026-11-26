"""Offline Marketplace Overview decision engine. No platform writes."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass

PLACEHOLDERS = {"tbd", "todo", "comingsoon", "n/a", "na", "placeholder",
                "aiplugin", "aitool", "待补充", "暂无", "测试"}
COMPLEX = re.compile(r"(?m)^[ ]{0,3}(?:\x60{3,}|~{3,})|"
                     r"\[[^\]\n]*\]\(|"  # links are removed before this check
                     r"\[[^\]\n]+\]\s*\[|^[ ]{0,3}\[[^\]]+\]:|"
                     r"^[ ]{0,3}#{1,6}(?:\s|$)|\n[ ]{0,3}(?:={3,}|-{3,})\s*(?:\n|$)|"
                     r"</?[A-Za-z][^>]*>|<[/!]?[A-Za-z]")
IMAGE = re.compile(r"!\[[^\[\]\n]*\]\((?:[^()\n]|\([^()\n]*\))*\)")
LINK = re.compile(r"\[([^\[\]\n]*)\]\((?:[^()\n]|\([^()\n]*\))*\)")
ANGLE_URL = re.compile(r"<(?:https?://|www\.)[^\s<>]+>", re.I)
URL = re.compile(r"(?:https?://|www\.)[^\s<>\]]+", re.I)
COMMENT = re.compile(r"<!--.*?-->", re.S)
FEEDBACK = "Explain what the plugin does and give one concrete input, output, supported action, or use case, then resubmit."
MAX_CHARS = 40000
POLICY_VERSION = "overview-visible-v2"

@dataclass(frozen=True)
class Policy:
    minimum: int
    review_below: int
    enforce: bool = False

    def __post_init__(self):
        if (type(self.minimum) is not int or type(self.review_below) is not int
                or not 1 <= self.minimum <= self.review_below <= MAX_CHARS
                or type(self.enforce) is not bool):
            raise ValueError("expected 1 <= min-visible <= review-below <= 40000 and a boolean enforce")

def visible(source: str) -> tuple[str, bool]:
    text = unicodedata.normalize("NFKC", html.unescape(COMMENT.sub(" ", source)))
    if "<!--" in text:
        return "", True
    text = IMAGE.sub(" ", text)
    if "![" in text:
        return "", True
    text = ANGLE_URL.sub(" ", LINK.sub(r" \1 ", text))
    # Without delimiters, a Unicode URL can run straight into visible prose.
    if any(not match[0].isascii() for match in URL.finditer(text)):
        return "", True
    text = URL.sub(" ", text)
    if COMPLEX.search(text):
        return "", True
    return text, False

def letters_and_numbers(text: str) -> str:
    return "".join(c for c in text if unicodedata.category(c)[0] in ("L", "N"))

def decide(record: object, policy: Policy) -> dict:
    iid = record.get("id") if isinstance(record, dict) else None
    scalar_id = type(iid) in (str, int) and bool(str(iid).strip())
    base = {
        "id": iid if scalar_id else None, "policy_version": POLICY_VERSION,
        "mode": "enforce" if policy.enforce else "dry_run",
        "min_visible": policy.minimum, "review_below": policy.review_below,
    }

    def output(status: str, reason: str, count=None, proposed=None, feedback=None):
        return {**base, "decision": status, "reason": reason, "visible_count": count,
                "proposed_decision": proposed or status, "feedback": feedback}

    if (not scalar_id or "overview" not in record
            or (record["overview"] is not None and not isinstance(record["overview"], str))
            or ("plugin_name" in record and not isinstance(record["plugin_name"], (str, type(None))))):
        return output("review", "invalid_submission_input")
    raw = record["overview"] or ""
    if len(raw) > MAX_CHARS:
        return output("review", "input_too_large")
    text, uncertain = visible(raw)
    if uncertain:
        return output("review", "complex_markup_requires_review")
    chars = letters_and_numbers(text)
    count = len(chars)
    # Casefold for name/placeholder comparisons only; it can expand Unicode characters.
    key = chars.casefold()
    name = letters_and_numbers(unicodedata.normalize("NFKC", record.get("plugin_name") or "")).casefold()
    reason = None
    if count == 0:
        reason = "no_visible_content"
    elif key in PLACEHOLDERS:
        reason = "placeholder_only"
    elif name and key == name:
        reason = "plugin_name_only"
    elif count < policy.minimum:
        reason = "below_minimum_visible_length"
    if reason:
        return output("reject" if policy.enforce else "review", reason, count, "reject", FEEDBACK)
    if count < policy.review_below:
        return output("review", "borderline_length", count, feedback=FEEDBACK)
    return output("pass", "passes_overview_rule_only", count)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 JSONL file, or - for stdin")
    parser.add_argument("--min-visible", type=int, default=1,
                        help="flag a nonempty Overview for length only if it falls below this count (default: 1)")
    parser.add_argument("--review-below", type=int, help="optional higher threshold for manual review")
    parser.add_argument("--enforce", action="store_true", help="emit reject instead of review for deterministic failures")
    args = parser.parse_args(argv)
    try:
        policy = Policy(args.min_visible, args.min_visible if args.review_below is None else args.review_below, args.enforce)
    except ValueError as exc:
        parser.error(str(exc))

    def process(lines):
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except (ValueError, RecursionError):
                result = {**decide(None, policy), "reason": "invalid_json"}
            else:
                result = decide(record, policy)
            print(json.dumps({"line": number, **result}, ensure_ascii=True))

    try:
        if args.input == "-":
            process(sys.stdin)
        else:
            with open(args.input, encoding="utf-8-sig") as lines:
                process(lines)
    except (OSError, UnicodeError) as exc:
        print(f"Unable to read input: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

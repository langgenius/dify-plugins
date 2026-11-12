"""Validated native tools. Sending is always subject to server-side controls."""

import json
import re
from typing import Any
from uuid import UUID

from lib.client import SentFromAIClient, SentFromAIError

FIELDS = {
    "get_account": set(), "list_inboxes": set(),
    "create_inbox": {"local_part", "display_name", "domain_id"},
    "list_messages": {"query", "inbox_id", "mode", "limit"},
    "get_message": {"message_id"},
    "send_message": {"inbox_id", "to", "cc", "bcc", "subject", "text", "html", "client_id"},
    "reply_to_message": {"message_id", "text", "html", "reply_all", "client_id"},
    "create_draft": {"inbox_id", "to", "cc", "bcc", "subject", "text", "html", "reply_to_message_id"},
    "get_draft": {"draft_id"},
}


def string(p: dict, key: str, *, required: bool = False, maximum: int = 1000) -> str | None:
    value = p.get(key)
    if value is None or value == "":
        if required:
            raise SentFromAIError(f"{key} is required.")
        return None
    if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > maximum:
        raise SentFromAIError(f"{key} must be a nonblank string of at most {maximum} UTF-8 bytes.")
    return value


def identifier(p: dict, key: str, *, required: bool = True) -> str | None:
    value = string(p, key, required=required, maximum=36)
    if value is None:
        return None
    try:
        if str(UUID(value)) != value.lower():
            raise ValueError()
    except ValueError:
        raise SentFromAIError(f"{key} must be a UUID returned by SentFromAI.") from None
    return value.lower()


def recipients(p: dict, key: str, *, required: bool = False) -> list[str]:
    value = string(p, key, required=required, maximum=4096)
    if value is None:
        return []
    try:
        items = json.loads(value) if value.lstrip().startswith("[") else re.split(r"[,\n]", value)
    except ValueError:
        raise SentFromAIError(f"{key} must contain bare email addresses or a JSON string array.") from None
    if not isinstance(items, list) or not all(isinstance(x, str) for x in items):
        raise SentFromAIError(f"{key} must contain bare email addresses or a JSON string array.")
    items = [x.strip() for x in items]
    if any(not re.fullmatch(r"[^\s@<>,;\x00-\x1f]+@[^\s@<>,;\x00-\x1f]+\.[^\s@<>,;\x00-\x1f]+", x)
           or len(x.encode("utf-8")) > 254 for x in items) or (required and not items):
        raise SentFromAIError(f"{key} contains an invalid bare email address.")
    return items


def body_content(p: dict) -> dict:
    content = {key: string(p, key, maximum=1_000_000) for key in ("text", "html")}
    content = {k: v for k, v in content.items() if v is not None}
    if not content:
        raise SentFromAIError("Provide text or html content.")
    return content


def execute(operation: str, p: dict[str, Any], api: SentFromAIClient) -> dict:
    if operation not in FIELDS or not isinstance(p, dict) or set(p) - FIELDS[operation]:
        raise SentFromAIError("Unsupported operation or parameter.")
    if operation in ("get_account", "list_inboxes"):
        return api.request("GET", "/v1/account" if operation == "get_account" else "/v1/inboxes")
    if operation == "create_inbox":
        local = string(p, "local_part", required=True, maximum=64).strip().lower()
        if not re.fullmatch(r"[a-z0-9._-]+", local):
            raise SentFromAIError("local_part may contain letters, numbers, periods, underscores and hyphens.")
        body = {"local_part": local, "display_name": string(p, "display_name", maximum=200),
                "domain_id": identifier(p, "domain_id", required=False)}
        return api.request("POST", "/v1/inboxes", body={k: v for k, v in body.items() if v is not None})
    if operation == "list_messages":
        mode = p.get("mode") or "keyword"
        if mode not in ("keyword", "semantic", "hybrid"):
            raise SentFromAIError("mode must be keyword, semantic or hybrid.")
        limit = p.get("limit")
        limit = 25 if limit is None or limit == "" else limit
        if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not 1 <= limit <= 100 or int(limit) != limit:
            raise SentFromAIError("limit must be a whole number between 1 and 100.")
        params = {"query": string(p, "query", maximum=4000), "mode": mode, "limit": int(limit),
                  "inbox_id": identifier(p, "inbox_id", required=False)}
        return api.request("GET", "/v1/messages", params={k: v for k, v in params.items() if v is not None})
    if operation in ("get_message", "get_draft"):
        kind = "message" if operation == "get_message" else "draft"
        return api.request("GET", f"/v1/{kind}s/{identifier(p, kind + '_id')}")
    body = body_content(p)
    if operation in ("send_message", "reply_to_message"):
        body["client_id"] = string(p, "client_id", required=True, maximum=255)
    if operation == "reply_to_message":
        reply_all = p.get("reply_all", False)
        if reply_all is None:
            reply_all = False
        if not isinstance(reply_all, bool):
            raise SentFromAIError("reply_all must be a boolean.")
        body["reply_all"] = reply_all
        return api.request("POST", f"/v1/messages/{identifier(p, 'message_id')}/reply", body=body)
    body["inbox_id"] = identifier(p, "inbox_id")
    body["subject"] = string(p, "subject", required=operation == "send_message", maximum=998)
    if body["subject"] and any(c in body["subject"] for c in ("\r", "\n", "\x00")):
        raise SentFromAIError("subject must be a single line without control characters.")
    for key in ("to", "cc", "bcc"):
        body[key] = recipients(p, key, required=key == "to" and operation == "send_message")
    if sum(len(body[key]) for key in ("to", "cc", "bcc")) > 10:
        raise SentFromAIError("Use at most 10 recipients across to, cc and bcc; account limits may be lower.")
    if operation == "create_draft":
        body["reply_to_message_id"] = identifier(p, "reply_to_message_id", required=False)
    return api.request("POST", "/v1/drafts" if operation == "create_draft" else "/v1/messages",
                       body={k: v for k, v in body.items() if v is not None})

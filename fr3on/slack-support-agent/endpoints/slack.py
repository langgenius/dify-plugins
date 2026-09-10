"""Slack endpoint for the Support Agent plugin.

Receives Slack Events API webhooks (channel @mentions, direct messages, and
passive channel/group messages used to build thread context), forwards the
conversation to a linked Dify chat app, and posts the answer back to Slack.
"""

import json
import logging
import re
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

import requests
from dify_plugin import Endpoint
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from werkzeug import Request, Response

logger = logging.getLogger(__name__)

MENTION_PATTERN = re.compile(r"<@([A-Za-z0-9]+)>")
LOOSE_MENTION_PATTERN = re.compile(r"<@([^>]+)>")
SLACK_BLOCK_TEXT_LIMIT = 3000  # https://api.slack.com/reference/block-kit/composition-objects#text__fields
DM_CONVERSATION_ANCHOR = "dm-main"


class SlackMarkdownConverter:
    """Converts Markdown text into Slack's mrkdwn format.

    ref: https://github.com/fla9ua/markdown_to_mrkdwn
    """

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding
        self.in_code_block = False
        self.table_replacements: Dict[str, str] = {}
        self.patterns: List[tuple] = [
            (re.compile(r"^(\s*)- \[([ ])\] (.+)", re.MULTILINE), r"\1• ☐ \3"),  # Unchecked task list
            (re.compile(r"^(\s*)- \[([xX])\] (.+)", re.MULTILINE), r"\1• ☑ \3"),  # Checked task list
            (re.compile(r"^(\s*)- (.+)", re.MULTILINE), r"\1• \2"),  # Unordered list
            (re.compile(r"^(\s*)(\d+)\. (.+)", re.MULTILINE), r"\1\2. \3"),  # Ordered list
            (re.compile(r"!\[.*?\]\((.+?)\)", re.MULTILINE), r"<\1>"),  # Images to URL
            (re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", re.MULTILINE), r"_\1_"),  # Italic
            (re.compile(r"^###### (.+)$", re.MULTILINE), r"*\1*"),  # H6 as bold
            (re.compile(r"^##### (.+)$", re.MULTILINE), r"*\1*"),  # H5 as bold
            (re.compile(r"^#### (.+)$", re.MULTILINE), r"*\1*"),  # H4 as bold
            (re.compile(r"^### (.+)$", re.MULTILINE), r"*\1*"),  # H3 as bold
            (re.compile(r"^## (.+)$", re.MULTILINE), r"*\1*"),  # H2 as bold
            (re.compile(r"^# (.+)$", re.MULTILINE), r"*\1*"),  # H1 as bold
            (re.compile(r"(^|\s)~\*\*(.+?)\*\*(\s|$)", re.MULTILINE), r"\1 *\2* \3"),  # Bold with space handling
            (re.compile(r"(?<!\*)\*\*(.+?)\*\*(?!\*)", re.MULTILINE), r"*\1*"),  # Bold
            (re.compile(r"__(.+?)__", re.MULTILINE), r"*\1*"),  # Underline as bold
            (re.compile(r"\[(.+?)\]\((.+?)\)", re.MULTILINE), r"<\2|\1>"),  # Links
            (re.compile(r"`(.+?)`", re.MULTILINE), r"`\1`"),  # Inline code
            (re.compile(r"^> (.+)", re.MULTILINE), r"> \1"),  # Blockquote
            (re.compile(r"^(---|\*\*\*|___)$", re.MULTILINE), r"──────────"),  # Horizontal line
            (re.compile(r"~~(.+?)~~", re.MULTILINE), r"~\1~"),  # Strikethrough
        ]
        self.triple_start = "%%BOLDITALIC_START%%"
        self.triple_end = "%%BOLDITALIC_END%%"

    def convert(self, markdown: str) -> str:
        if not markdown:
            return ""

        try:
            markdown = markdown.strip()
            self.table_replacements = {}
            markdown = self._convert_tables(markdown)

            converted_lines = [self._convert_line(line) for line in markdown.split("\n")]
            result = "\n".join(converted_lines)

            for placeholder, table in self.table_replacements.items():
                result = result.replace(placeholder, table)

            return result.encode(self.encoding).decode(self.encoding)
        except Exception:
            return markdown

    def _convert_tables(self, markdown: str) -> str:
        table_pattern = re.compile(
            r"^\|(.+)\|\s*$\n^\|[-:| ]+\|\s*$(\n^\|.+\|\s*$)*", re.MULTILINE
        )

        def convert_table(match: re.Match) -> str:
            original_table = match.group(0)
            table_lines = original_table.strip().split("\n")
            header_line = table_lines[0]
            data_lines = table_lines[2:] if len(table_lines) > 2 else []

            headers = [cell.strip() for cell in header_line.strip("|").split("|")]
            rows = [
                [cell.strip() for cell in line.strip("|").split("|")]
                for line in data_lines
            ]

            result = [" | ".join(f"*{header}*" for header in headers)]
            result.extend(" | ".join(row) for row in rows)

            placeholder = f"%%TABLE_PLACEHOLDER_{hash(original_table)}%%"
            self.table_replacements[placeholder] = "\n".join(result)
            return placeholder

        return table_pattern.sub(convert_table, markdown)

    def _convert_line(self, line: str) -> str:
        if line.startswith("%%TABLE_PLACEHOLDER_") and line.endswith("%%"):
            return line

        code_block_match = re.match(r"^```(\w*)$", line)
        if code_block_match:
            language = code_block_match.group(1)
            self.in_code_block = not self.in_code_block
            return f"```{language}" if self.in_code_block and language else "```"

        if self.in_code_block:
            return line

        line = re.sub(
            r"(?<!\*)\*\*\*([^*\n]+?)\*\*\*(?!\*)",
            lambda m: f"{self.triple_start}{m.group(1)}{self.triple_end}",
            line,
        )

        for pattern, replacement in self.patterns:
            line = pattern.sub(replacement, line)

        line = re.sub(
            re.escape(self.triple_start) + r"(.*?)" + re.escape(self.triple_end),
            r"*_\1_*",
            line,
            flags=re.MULTILINE,
        )

        return line.rstrip()


@dataclass
class ThreadMessage:
    """One message in a thread/DM, formatted for the linked Dify app."""

    role: str
    participant_id: str
    content: str
    ts: Optional[str] = None
    participant_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        # `ts` is only used internally to filter by context_scope - it's
        # never sent to the linked app.
        return {
            "role": self.role,
            "participant_id": self.participant_id,
            "content": self.content,
            "participant_name": self.participant_name,
        }


@dataclass
class RoutingContext:
    """Where an incoming Slack event routes to, and how the bot should reply.

    For a channel @mention, or a DM reply the user explicitly threaded,
    `raw_thread_ts` is a real Slack thread timestamp and every property below
    is simply that value (or the event's own ts for a brand-new thread).

    For a plain DM message - the common case, since Slack doesn't set
    thread_ts unless the user threads a reply - there's no natural thread to
    anchor to. Anchoring each message to its own ts would start a brand-new
    Dify conversation on every single message, so instead the whole DM
    channel shares one fixed conversation anchor, and replies post as normal
    top-level DM messages rather than a threaded reply under each message.
    """

    channel: str
    event_ts: Optional[str]
    is_dm: bool
    raw_thread_ts: Optional[str]

    @property
    def _is_freeform_dm(self) -> bool:
        return self.is_dm and not self.raw_thread_ts

    @property
    def conversation_ts(self) -> str:
        """Anchors our cache/conversation storage keys."""
        if self._is_freeform_dm:
            return DM_CONVERSATION_ANCHOR
        return self.raw_thread_ts or self.event_ts

    @property
    def reply_thread_ts(self) -> Optional[str]:
        """Value passed to Slack's chat_postMessage/conversations_replies."""
        if self._is_freeform_dm:
            return None
        return self.raw_thread_ts or self.event_ts

    @property
    def slack_thread_ts(self) -> Optional[str]:
        """The real Slack timestamp handed to the linked Dify app as input,
        for use by downstream plugins (e.g. Slack Post) - never our internal
        DM conversation anchor."""
        return self.raw_thread_ts or self.event_ts


class SlackEndpoint(Endpoint):
    CACHE_PREFIX = "thread-cache"
    CONVERSATION_PREFIX = "slack"
    CACHE_DURATION = 60 * 60 * 24  # 1 day

    # ---------------------------------------------------------------- cache

    def _cache_key(self, channel: str, conversation_ts: str) -> str:
        return f"{self.CACHE_PREFIX}-{channel}-{conversation_ts}"

    def _conversation_key(self, channel: str, conversation_ts: str) -> str:
        return f"{self.CONVERSATION_PREFIX}-{channel}-{conversation_ts}"

    def _load_cached_history(self, channel: str, conversation_ts: str) -> List[Dict[str, Any]]:
        key = self._cache_key(channel, conversation_ts)
        try:
            raw = self.session.storage.get(key)
        except Exception:
            return []
        if not raw:
            return []

        try:
            all_messages = json.loads(raw.decode("utf-8")).get("messages", [])
        except Exception:
            return []

        now = time.time()
        active = [m for m in all_messages if now - m.get("saved_at", now) < self.CACHE_DURATION]
        if len(active) != len(all_messages):
            self._write_cache(channel, conversation_ts, active)
        return active

    def _write_cache(self, channel: str, conversation_ts: str, messages: List[Dict[str, Any]]) -> None:
        try:
            self.session.storage.set(
                self._cache_key(channel, conversation_ts),
                json.dumps({"messages": messages}).encode("utf-8"),
            )
        except Exception:
            pass

    def _append_thread_message(self, channel: str, conversation_ts: str, message: Mapping) -> None:
        messages = self._load_cached_history(channel, conversation_ts)
        msg = dict(message)
        msg["saved_at"] = time.time()
        messages.append(msg)
        self._write_cache(channel, conversation_ts, messages)

    def _get_conversation_id(self, channel: str, conversation_ts: str) -> Optional[str]:
        try:
            raw = self.session.storage.get(self._conversation_key(channel, conversation_ts))
        except Exception:
            return None
        return raw.decode("utf-8") if raw else None

    def _set_conversation_id(self, channel: str, conversation_ts: str, conversation_id: str) -> None:
        try:
            self.session.storage.set(
                self._conversation_key(channel, conversation_ts),
                conversation_id.encode("utf-8"),
            )
        except Exception:
            pass

    # -------------------------------------------------------------- routing

    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        if self._is_ignorable_retry(r, settings):
            return Response(status=200, response="ok")

        data = r.get_json(silent=True) or {}

        if data.get("type") == "url_verification":
            return Response(
                response=json.dumps({"challenge": data.get("challenge")}),
                status=200,
                content_type="application/json",
            )

        if data.get("type") != "event_callback":
            return Response(status=200, response="ok")

        event = data.get("event") or {}
        is_dm = self._is_dm_message(event)

        if event.get("type") == "app_mention" or is_dm:
            return self._handle_reply(event, settings, is_dm)
        if event.get("type") == "message":
            return self._handle_passive_message(event)
        return Response(status=200, response="ok")

    @staticmethod
    def _is_ignorable_retry(r: Request, settings: Mapping) -> bool:
        if settings.get("allow_retry"):
            return False
        retry_num = r.headers.get("X-Slack-Retry-Num")
        return bool(
            r.headers.get("X-Slack-Retry-Reason") == "http_timeout"
            or (retry_num is not None and int(retry_num) > 0)
        )

    @staticmethod
    def _is_dm_message(event: Mapping) -> bool:
        """Slack sends type="message" with channel_type="im" for a DM (no
        app_mention fires in a DM, since there's no one else to @-mention).
        Guard against bot_id/subtype so we never reply to our own posts or to
        edits/deletes - either would otherwise create a reply loop."""
        return bool(
            event.get("type") == "message"
            and event.get("channel_type") == "im"
            and not event.get("bot_id")
            and not event.get("subtype")
            and event.get("text")
        )

    @staticmethod
    def _event_to_cache_entry(event: Mapping) -> Dict[str, Any]:
        return {
            "ts": event.get("ts"),
            "text": event.get("text", ""),
            "user": event.get("user"),
            "bot_id": event.get("bot_id"),
        }

    # ------------------------------------------------- passive caching path

    def _handle_passive_message(self, event: Mapping) -> Response:
        """Messages that aren't a mention or a DM (e.g. other people replying
        in a channel thread the bot is already tracking) are cached silently,
        without invoking the linked app, so full thread context is available
        next time the bot is mentioned in that thread."""
        channel = event.get("channel", "")
        thread_ts = event.get("thread_ts") or event.get("ts")
        if self._is_thread_recognized(channel, thread_ts):
            self._append_thread_message(channel, thread_ts, self._event_to_cache_entry(event))
        return Response(status=200, response="ok")

    def _is_thread_recognized(self, channel: str, thread_ts: str) -> bool:
        for key in (
            self._conversation_key(channel, thread_ts),
            self._cache_key(channel, thread_ts),
        ):
            try:
                if self.session.storage.get(key):
                    return True
            except Exception:
                pass
        return False

    # ----------------------------------------------------- mention -> reply

    def _handle_reply(self, event: Mapping, settings: Mapping, is_dm: bool) -> Response:
        ctx = RoutingContext(
            channel=event.get("channel", ""),
            event_ts=event.get("ts"),
            is_dm=is_dm,
            raw_thread_ts=event.get("thread_ts"),
        )
        client = WebClient(token=settings.get("bot_token"))
        message_text = self._extract_message_text(event)

        self._append_thread_message(ctx.channel, ctx.conversation_ts, self._event_to_cache_entry(event))

        blocked = self._enforce_allowed_channel(client, ctx, settings, is_dm)
        if blocked is not None:
            return blocked

        try:
            return self._respond(client, ctx, settings, event, message_text)
        except Exception as e:
            return self._handle_invoke_error(client, ctx, settings, e)

    @staticmethod
    def _extract_message_text(event: Mapping) -> str:
        text = event.get("text", "")
        if event.get("type") == "app_mention":
            # Remove the leading bot mention, e.g. "<@U123> what's up" -> "what's up".
            # DMs carry no leading mention, so nothing to strip there.
            return re.sub(r"^<@[^>]+>\s*", "", text)
        return text

    def _enforce_allowed_channel(
        self, client: WebClient, ctx: RoutingContext, settings: Mapping, is_dm: bool
    ) -> Optional[Response]:
        """Returns a short-circuit Response if this channel isn't allowed (or
        the check itself failed), else None to continue. DMs have no channel
        name to compare against - the restriction is a channel-scoping
        feature, so it's skipped for DMs entirely."""
        allowed_channel = settings.get("allowed_channel", "").strip()
        if not allowed_channel or is_dm:
            return None

        try:
            channel_info = client.conversations_info(channel=ctx.channel)
            actual_channel = f"#{channel_info['channel']['name']}"
        except SlackApiError as e:
            logger.warning("Error getting channel info: %s", e)
            self._safe_post(client, ctx, f"Failed to retrieve channel info. SlackApiError: {e}")
            return Response(status=200, response="ok", content_type="text/plain")
        except Exception as e:
            logger.warning("Unexpected error getting channel info: %s", e)
            self._safe_post(
                client, ctx, f"An unexpected error occurred while retrieving channel info. Error: {e}"
            )
            return Response(status=200, response="ok", content_type="text/plain")

        if actual_channel == allowed_channel:
            return None

        self._safe_post(client, ctx, f"Current channel: {actual_channel} is not allowed.")
        return Response(status=200, response="ok", content_type="text/plain")

    @staticmethod
    def _safe_post(client: WebClient, ctx: RoutingContext, text: str) -> None:
        try:
            client.chat_postMessage(channel=ctx.channel, thread_ts=ctx.reply_thread_ts, text=text)
        except SlackApiError:
            pass

    # ------------------------------------------------------- app invocation

    def _respond(
        self, client: WebClient, ctx: RoutingContext, settings: Mapping, event: Mapping, message_text: str
    ) -> Response:
        conversation_id = self._get_conversation_id(ctx.channel, ctx.conversation_ts)

        raw_messages = self._fetch_thread_messages(client, ctx)
        user_display_names = self._resolve_display_names(client, raw_messages)
        thread_history, is_first_message = self._build_thread_history(raw_messages, user_display_names)
        thread_history = self._apply_context_scope(
            thread_history, settings.get("context_scope", "full_thread"), ctx.event_ts
        )

        uploaded_files = self._upload_slack_files(
            client, ctx, settings.get("bot_token"), event.get("files", [])
        )

        invoke_params: Dict[str, Any] = {
            "app_id": settings["app"]["app_id"],
            "query": self._substitute_mentions(message_text, user_display_names),
            "inputs": self._build_invoke_inputs(ctx, thread_history, user_display_names, uploaded_files),
            "response_mode": "blocking",
        }
        if conversation_id is not None:
            invoke_params["conversation_id"] = conversation_id

        response = self.session.app.chat.invoke(**invoke_params)
        answer = response.get("answer")

        new_conversation_id = response.get("conversation_id")
        if new_conversation_id:
            self._set_conversation_id(ctx.channel, ctx.conversation_ts, new_conversation_id)

        try:
            return self._post_answer(client, ctx, answer, settings, is_first_message)
        except SlackApiError as e:
            return Response(
                status=200, response=f"Error sending message to Slack: {e}", content_type="text/plain"
            )

    def _fetch_thread_messages(self, client: WebClient, ctx: RoutingContext) -> List[Dict[str, Any]]:
        """Raw Slack messages for this thread/DM, from cache if present, else
        fetched from Slack. Only falls back to Slack's API when we have a
        real thread ts - the synthetic DM anchor isn't one, and the cache is
        never empty here anyway since the triggering message was already
        appended to it in `_handle_reply`."""
        messages = self._load_cached_history(ctx.channel, ctx.conversation_ts)
        if messages or not ctx.reply_thread_ts:
            return messages

        messages = self._fetch_replies_with_retry(client, ctx)
        for m in messages:
            self._append_thread_message(ctx.channel, ctx.conversation_ts, m)
        return messages

    def _fetch_replies_with_retry(self, client: WebClient, ctx: RoutingContext) -> List[Dict[str, Any]]:
        try:
            return client.conversations_replies(channel=ctx.channel, ts=ctx.reply_thread_ts).get("messages", [])
        except SlackApiError as e:
            if e.response.get("error") != "ratelimited":
                logger.warning("Error getting thread history: %s", e)
                return []

            retry_after = int(e.response.get("headers", {}).get("Retry-After", 60))
            self._safe_post(
                client, ctx, f"Rate limit reached when retrieving thread. Retrying in {retry_after} seconds..."
            )
            time.sleep(retry_after)
            try:
                return client.conversations_replies(channel=ctx.channel, ts=ctx.reply_thread_ts).get("messages", [])
            except SlackApiError as retry_error:
                logger.warning("Error getting thread history after retry: %s", retry_error)
                return []

    def _resolve_display_names(self, client: WebClient, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        user_ids: List[str] = []
        for msg in messages:
            user_id = msg.get("user", "unknown")
            if user_id != "unknown" and user_id not in user_ids:
                user_ids.append(user_id)
            for mentioned_id in LOOSE_MENTION_PATTERN.findall(msg.get("text") or ""):
                if mentioned_id not in user_ids:
                    user_ids.append(mentioned_id)

        display_names: Dict[str, str] = {}
        try:
            for user_id in user_ids:
                info = client.users_info(user=user_id).get("user", {})
                name, real_name = info.get("name", ""), info.get("real_name", "")
                display_names[user_id] = f"{real_name} ({name})" if name else real_name
        except SlackApiError as e:
            logger.warning("Error getting user info: %s", e)
        return display_names

    def _build_thread_history(
        self, messages: List[Dict[str, Any]], user_display_names: Dict[str, str]
    ) -> tuple:
        thread_history = [
            ThreadMessage(
                role="assistant" if msg.get("bot_id") else "user",
                participant_id=(participant_id := msg.get("user", "unknown")),
                content=self._substitute_mentions(msg.get("text", ""), user_display_names),
                ts=msg.get("ts"),
                participant_name=user_display_names.get(participant_id, "unknown"),
            )
            for msg in messages
        ]
        # Decided from the untrimmed history, before _apply_context_scope
        # shrinks it down to 0-1 items regardless of the thread's real length.
        is_first_message = len(thread_history) == 1
        return thread_history, is_first_message

    @staticmethod
    def _apply_context_scope(
        thread_history: List[ThreadMessage], scope: str, trigger_ts: Optional[str]
    ) -> List[ThreadMessage]:
        """Trims thread_history down to the configured scope. The triggering
        message itself is excluded from the trimmed scopes since it's already
        sent separately as the query."""
        if scope == "full_thread":
            return thread_history

        without_trigger = [m for m in thread_history if m.ts != trigger_ts]
        if scope == "parent_message":
            return without_trigger[:1]
        if scope == "last_message":
            return without_trigger[-1:]
        return thread_history

    @staticmethod
    def _substitute_mentions(text: str, user_display_names: Mapping[str, str]) -> str:
        def replace(match: re.Match) -> str:
            user_id = match.group(1)
            return f"@{user_display_names[user_id]}" if user_id in user_display_names else match.group(0)

        return MENTION_PATTERN.sub(replace, text)

    def _upload_slack_files(
        self, client: WebClient, ctx: RoutingContext, token: str, slack_files: List[Dict[str, Any]]
    ) -> List[Any]:
        uploaded = []
        for f in slack_files:
            file_name = f.get("name")
            file_url = f.get("url_private_download")
            mimetype = f.get("mimetype", "application/octet-stream")
            if not file_url or not file_name:
                continue

            resp = requests.get(file_url, headers={"Authorization": f"Bearer {token}"})
            if resp.status_code != 200:
                logger.warning(
                    "Failed to download file from Slack: %s, status code=%s", file_name, resp.status_code
                )
                continue

            try:
                storage_file = self.session.file.upload(filename=file_name, content=resp.content, mimetype=mimetype)
                if storage_file:
                    uploaded.append(storage_file)
            except Exception as e:
                self._safe_post(
                    client,
                    ctx,
                    f"Error uploading file: {e}\n\n"
                    "This may be caused by an unconfigured `FILES_URL` in your `dify/docker/.env` .\n"
                    "Please set `FILES_URL` properly and restart( `docker compose down && docker compose up -d` ) "
                    "your Dify environment, then try again.",
                )
                logger.warning("Error uploading file via session.file.upload: %s", e)
        return uploaded

    @staticmethod
    def _build_invoke_inputs(
        ctx: RoutingContext,
        thread_history: List[ThreadMessage],
        user_display_names: Dict[str, str],
        uploaded_files: List[Any],
    ) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {
            "thread_history": json.dumps([m.to_dict() for m in thread_history], indent=4, ensure_ascii=False),
            "thread_users": json.dumps(user_display_names, indent=4, ensure_ascii=False),
            "thread_ts": ctx.slack_thread_ts,
            "channel_id": ctx.channel,
        }
        if uploaded_files:
            inputs["files"] = [
                {"type": f.type, "transfer_method": "remote_url", "url": f.preview_url}
                for f in uploaded_files
            ]
        return inputs

    def _handle_invoke_error(
        self, client: WebClient, ctx: RoutingContext, settings: Mapping, error: Exception
    ) -> Response:
        err_msg = str(error)
        err_trace = traceback.format_exc()

        skip_timeout_error = settings.get("skip_timeout_error", False)
        if skip_timeout_error and "invocation exited without response" in err_msg.lower():
            return Response(status=200, response="ok", content_type="text/plain")

        self._safe_post(
            client, ctx, f"Sorry, I'm having trouble processing your request. Please try again later. Error: {err_msg}"
        )
        return Response(
            status=200, response=f"An error occurred: {err_msg}\n{err_trace}", content_type="text/plain"
        )

    # ------------------------------------------------------------- replying

    def _post_answer(
        self, client: WebClient, ctx: RoutingContext, answer: str, settings: Mapping, is_first_message: bool
    ) -> Response:
        converted_answer = SlackMarkdownConverter().convert(answer)
        chunks = self._split_into_chunks(converted_answer, SLACK_BLOCK_TEXT_LIMIT)
        reply_broadcast = settings.get("first_reply_broadcast", False) and is_first_message

        for i, chunk in enumerate(chunks):
            resp = client.chat_postMessage(
                channel=ctx.channel,
                text=chunk,  # fallback text
                thread_ts=ctx.reply_thread_ts,
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": chunk}}],
                # Only broadcast the first chunk - broadcasting every chunk
                # would flood the channel outside the thread.
                reply_broadcast=reply_broadcast if i == 0 else False,
            )
            self._append_thread_message(
                ctx.channel,
                ctx.conversation_ts,
                {
                    "ts": resp.get("ts"),
                    "text": chunk,
                    "user": resp.get("message", {}).get("user"),
                    "bot_id": resp.get("message", {}).get("bot_id"),
                },
            )

        return Response(status=200, response="ok", content_type="text/plain")

    @staticmethod
    def _split_into_chunks(text: str, max_len: int) -> List[str]:
        """Greedily packs lines into chunks up to `max_len` characters,
        splitting any single line that's longer than max_len on its own."""
        if len(text) <= max_len:
            return [text]

        def pieces(line: str):
            if len(line) <= max_len:
                yield line
            else:
                for i in range(0, len(line), max_len):
                    yield line[i : i + max_len]

        chunks: List[str] = []
        current = ""
        for line in text.split("\n"):
            for piece in pieces(line):
                added_len = len(piece) + (1 if current else 0)
                if len(current) + added_len <= max_len:
                    current = f"{current}\n{piece}" if current else piece
                else:
                    if current:
                        chunks.append(current)
                    current = piece
        if current:
            chunks.append(current)
        return chunks

## Slack Support Agent

**Version:** 0.0.1
**Type:** extension

Connects Slack to a Dify chat app: reply within Slack threads and to direct messages sent straight to the bot, with conversation history, user info, file uploads, and `mrkdwn` formatting handled for you.

### Contents

- [Features](#features)
- [Settings](#settings)
- [Install](#install)
- [Setup](#setup)
- [Usage in your Dify app](#usage-in-your-dify-app)
- [Support](#support)

### Features

- **Threads** - reply within Slack threads, with an optional setting to also post the first reply to the channel
- **Direct messages** - reply to DMs sent straight to the bot, with the conversation continuing turn-to-turn just like Dify's own chat UI, not just @mentions in channels
- **File uploads** - Slack file attachments are downloaded and passed to the linked app automatically
- **`mrkdwn` formatting** - the app's Markdown answer is converted to Slack's `mrkdwn` and split across multiple messages if it exceeds Slack's block text limit
- **Context, your way** - the linked app receives thread/DM conversation history and a resolved user list; how much history it gets is configurable (see [Settings](#settings))
- **Channel restriction** - optionally lock the bot to a single Slack channel

> [!NOTE]
> The app also receives `channel_id` and `thread_ts` as inputs. These are for advanced use cases - e.g. a linked plugin posting follow-up messages to a specific channel or thread - and most setups won't need them.

### Settings

| Setting | Required | Description |
| --- | --- | --- |
| App | Yes | The Dify chat app that answers Slack messages. |
| Bot Token | Yes | Your Slack bot's `xoxb-...` token. |
| Allowed Channel | No | Restrict the bot to one channel, in `#channel` format. Leave blank to allow all channels. Doesn't apply to DMs. |
| Thread Context Sent to App | No | How much thread history to send with each reply: **Full thread** (default), **Root message only**, or **Message right before the mention**. |
| Broadcast First Reply | No | Also post the bot's first reply in a thread to the channel itself, not just the thread. |
| Allow Retry | No | Process Slack's automatic retries of a webhook delivery instead of ignoring them. Off by default to avoid duplicate replies. |
| Skip App Timeout Error Notifications | No | If the linked app times out, stay silent instead of posting an error message to Slack. |

### Install

To install this plugin, specify the following GitHub repository when selecting "Install Plugin":

https://github.com/fr3on/slack-support-agent

### Setup

Follow the same setup procedure as the official SlackBot plugin, but with this plugin's scopes and events.

**Bot token scopes:**

```text
app_mentions:read, users:read, channels:history, groups:history, im:history, chat:write, groups:write, channels:read,
groups:read, im:read, files:read
```

**Subscribe to bot events:**

| Event | Purpose |
| --- | --- |
| `app_mention` | Reply when someone @-mentions the bot in a channel |
| `message.im` | Reply to direct messages sent to the bot |
| `message.channels` | Cache messages in public channel threads |
| `message.groups` | Cache messages in private channel threads |

The `message.channels`/`message.groups` events feed a caching layer that keeps thread context available without repeatedly hitting Slack's thread-history endpoint, which is rate-limited to about 1 request per minute.

For details on setting up the official SlackBot plugin, see:

https://github.com/langgenius/dify-official-plugins/blob/main/extensions/slack_bot/README.md

### Usage in your Dify app

In the start node of the chat flow app you link to this plugin, add these input fields to receive Slack context:

| Input field | Field type |
| --- | --- |
| `thread_history` | Paragraph, max length e.g. 65535 |
| `thread_users` | Paragraph, max length e.g. 65535 |
| `files` | File List |
| `thread_ts` | Short Text, max length e.g. 48 |
| `channel_id` | Short Text, max length e.g. 48 |

Example prompt (LLM node in the chat flow app):

```text
You are an assistant on Slack who answers user questions.
Refer to the recent conversation history and provide an appropriate response.

If you need to mention a specific user, refer to the user list and mention them in the format `<@ID>`.

# Recent conversation history
Start.thread_history
# User list
Start.thread_users
```

### Support

- Source repository: https://github.com/fr3on/slack-support-agent
- Issues / questions: https://github.com/fr3on/slack-support-agent/issues
- Contact: [@fr3on](https://github.com/fr3on) on GitHub

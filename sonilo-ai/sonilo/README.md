# Sonilo Plugin for Dify

Licensed AI music, video-to-music soundtracks, and frame-accurate sound
effects for [Dify](https://dify.ai) workflows and agents, backed by the
[Sonilo API](https://sonilo.com) (`api.sonilo.com`). One provider, four
tools, bring your own Sonilo API key.

## Tools

| Tool | Endpoint | Purpose |
|---|---|---|
| **Text to Music** (`text_to_music`) | `POST /v1/text-to-music` | Original, licensed music from a text prompt. |
| **Video to Music** (`video_to_music`) | `POST /v1/video-to-music` | A soundtrack generated from and matched to a video's pacing/mood. |
| **Text to Sound Effects** (`text_to_sfx`) | `POST /v1/text-to-sfx` | Isolated SFX/Foley/impacts/ambience/UI sounds from a text prompt. |
| **Video to Sound Effects** (`video_to_sfx`) | `POST /v1/video-to-sfx` | Frame-accurate SFX aligned to a video's cuts, motion, and on-screen moments. |

All four tools:

- Return a `json` artifact (`success`, `audio_url`, `task_id`, `status`,
  `duration`, `raw`) so results are easy to chain in Workflow nodes.
- Return a short text summary.
- Attach the generated audio as a downloadable file (`blob` message) when a
  URL is available, so the audio also shows up directly in chat.
- Transparently poll `GET /v1/tasks/{task_id}` when Sonilo answers with an
  async task instead of a finished result, so tool callers never have to
  handle polling themselves.

## Setup

1. Install this plugin from the Dify Marketplace (or import the packaged
   `.difypkg` file directly).
2. Open the **Sonilo** provider settings in Dify.
3. Paste your Sonilo API key into **Sonilo API Key**. Dify stores it as an
   encrypted secret and validates it with one read-only request
   (`GET /v1/account/usage`) that does not consume generation credits.
4. Save, then add any of the four Sonilo tools to an Agent or Workflow.

Each Dify workspace supplies its own Sonilo API key — this plugin ships
with **no** default key, and the Sonilo team never sees your key.

### Get a Sonilo API key

Create an account and an API key at <https://platform.sonilo.com>. See the
API docs at <https://platform.sonilo.com/docs> and the spec at
<https://sonilo.com/openapi.json>.

## Scope of this version

- **Video tools take a `video_url`, not a file upload.** `video_to_music`
  and `video_to_sfx` submit the JSON `video_url` request variant described
  in Sonilo's OpenAPI spec (`VideoUrlRequest`) — the URL must be a public
  or signed HTTPS location Sonilo's servers can fetch directly. The
  multipart binary-upload variant (`VideoInputRequest`, uploading raw video
  bytes) is not implemented in this version; host the video first (e.g. in
  object storage) and pass its URL.
- **Segment-level control is not exposed.** The API supports an optional
  `segments` array (per-segment start/end/prompt) on the video endpoints.
  This version does not expose it as a tool parameter, since Dify tool
  parameter forms don't map cleanly onto nested arrays; the whole-video
  prompt/mode/output_format controls are exposed instead.
- **`audio-ducking` is not included.** Sonilo's API also exposes
  `POST /v1/audio-ducking` (mixing speech with background music). It's out
  of scope for this initial submission, which focuses on the four
  generation endpoints named in the plugin's tool list.

## How it works

Each tool calls the Sonilo REST API directly over HTTPS with `Authorization:
Bearer <your key>`, built from Sonilo's published OpenAPI spec
(<https://sonilo.com/openapi.json>) rather than through a third-party SDK.
For an endpoint that returns an async task, the shared client
(`tools/_client.py`) polls `GET /v1/tasks/{task_id}` until the task reaches
a terminal status (`completed`, `failed`, or `canceled`, per the spec) or a
10-minute timeout elapses.

## Testing status

Unit-level request/response shaping was checked against Sonilo's published
OpenAPI spec. **No live call against `api.sonilo.com` has been made from
the environment that built this plugin** — no API key was available there.
Before relying on this in production, run one real generation with a live
key against each of the four tools (a short text-to-music and text-to-sfx
call, plus a short video-to-music and video-to-sfx call against a small
public test video) and confirm the response shape matches what
`tools/_client.py` expects (`extract_audio_url` is written defensively for
this reason, but hasn't been exercised against a real payload).

## Privacy

See [PRIVACY.md](PRIVACY.md). Short version: the plugin forwards your
prompt / video URL / generation options, plus your configured API key, to
`api.sonilo.com`. It does not persist prompts, video URLs, generated audio,
or credentials anywhere outside of a single tool invocation.

## Source and support

- Source for this plugin: this directory
  (`sonilo-ai/sonilo/`) in
  [`langgenius/dify-plugins`](https://github.com/langgenius/dify-plugins/tree/main/sonilo-ai/sonilo).
- Sonilo API / product: <https://sonilo.com>
- Official SDKs (used as the reference for field names and request/response
  shapes while building this plugin):
  [`sonilo-ai/sonilo-python`](https://github.com/sonilo-ai/sonilo-python),
  [`sonilo-ai/sonilo-js`](https://github.com/sonilo-ai/sonilo-js).
- Support: <https://sonilo.com/contact-sales> or <info@sonilo.com>.
- Security reports: follow Dify's
  [security disclosure process](https://github.com/langgenius/dify-plugins#security-disclosure).

## License

MIT for this plugin's code (see [LICENSE](LICENSE)). Generated audio is
subject to Sonilo's own terms of service.

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

- Submit the request as `multipart/form-data` (required — see "How it
  works" below) and always run the task-polling path: the two SFX
  endpoints are unconditionally async on Sonilo's side, and this plugin
  always requests `mode=async` on the two music endpoints too.
- Return a `json` artifact (`success`, `audio_url`, `content_type`,
  `task_id`, `status`, `duration_seconds`, `cost`, `raw`) so results are
  easy to chain in Workflow nodes.
- Return a short text summary.
- Attach the generated audio as a downloadable file (`blob` message) when a
  URL is available, so the audio also shows up directly in chat.

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
API docs at <https://platform.sonilo.com/docs>.

## Scope of this version

- **Video tools take a `video_url`, not a file upload.** `video_to_music`
  and `video_to_sfx` send `video_url` as a `multipart/form-data` field —
  it must be a public or signed HTTPS location Sonilo's servers can fetch
  directly. Uploading raw video bytes (a `video` file field on the same
  endpoints) is not implemented in this version; host the video first
  (e.g. in object storage) and pass its URL.
- **The music endpoints' default streaming mode is not implemented.**
  `text-to-music` and `video-to-music` accept `mode="stream"` (default) or
  `mode="async"`. `stream` returns an NDJSON event stream
  (`audio_chunk`/`title`/`complete`/`error` events) rather than a single
  JSON body. This plugin always sends `mode="async"` instead and polls
  `GET /v1/tasks/{task_id}`, so it never has to parse that streaming
  protocol. A future version could add real streaming support.
- **Segment-level control is not exposed.** The API supports an optional,
  JSON-encoded `segments` field (per-segment start/end/prompt) on the
  video endpoints. This version does not expose it as a tool parameter,
  since Dify tool parameter forms don't map cleanly onto nested arrays.
- **`isolate_vocals` / `preserve_speech` / `ducking` are not exposed** on
  `video_to_music`, and **`audio-ducking` (`POST /v1/audio-ducking`) is
  not included** as a fifth tool. Both are out of scope for this initial
  submission, which focuses on the four generation endpoints named above.

## How it works

Each tool calls the Sonilo REST API directly over HTTPS with `Authorization:
Bearer <your key>`, built directly against the backend's route contract
rather than through a third-party SDK. Two details matter here because they
are easy to get wrong from documentation alone:

- **Requests are `multipart/form-data`, not JSON.** Sonilo's backend binds
  every field on these five POST routes with FastAPI `Form(...)`
  parameters, so a JSON body will not bind — `tools/_client.py` always
  sends fields as multipart form fields (via `requests`' `files={name:
  (None, value)}` construction, which multipart-encodes plain values with
  no attached file).
- **Task status values are `processing` / `succeeded` / `failed`** — not
  the `queued`/`running`/`completed`/`canceled` values an earlier draft of
  this plugin used (see "Testing status" below). `succeeded` is the only
  success terminal state; there is no `canceled` state.

The shared client (`tools/_client.py`) submits the request, then polls
`GET /v1/tasks/{task_id}` until the task reaches `succeeded` or `failed`,
or a 10-minute timeout elapses.

Field names also differ by endpoint family: the music endpoints use
`output_format` (`m4a` default, or `wav`) and accept `mode`; the SFX
endpoints use a differently named `audio_format` field (`wav`/`mp3`/`aac`/
`flac`, no documented default) and accept no `mode` field at all.

## Testing status

**No live call against `api.sonilo.com` has been made from the environment
that built this plugin** — no API key was available there.

An earlier draft of this plugin was built against `sonilo.com/openapi.json`
and used JSON request bodies and a `queued/running/completed/canceled`
status enum. That spec turned out to be significantly wrong — the real
backend requires `multipart/form-data` and uses a
`processing/succeeded/failed` status enum, among other field-level
differences (see "How it works" above). This version has been corrected
against the confirmed backend contract, but that correction itself has
only been checked for internal consistency (unit-level request/response
shaping, YAML/manifest validation, and successful packaging with the
official `dify-plugin` CLI) — **not against a live response from
`api.sonilo.com`**.

Before relying on this in production, run one real generation with a live
key against each of the four tools (a short text-to-music and text-to-sfx
call, plus a short video-to-music and video-to-sfx call against a small
public test video) and confirm the response shape matches what
`tools/_client.py` expects (`extract_audio_media` is written defensively
for this reason, but hasn't been exercised against a real payload).

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
- Official SDKs (used as a reference while building this plugin):
  [`sonilo-ai/sonilo-python`](https://github.com/sonilo-ai/sonilo-python),
  [`sonilo-ai/sonilo-js`](https://github.com/sonilo-ai/sonilo-js).
- Support: <https://sonilo.com/contact-sales> or <info@sonilo.com>.
- Security reports: follow Dify's
  [security disclosure process](https://github.com/langgenius/dify-plugins#security-disclosure).

## License

MIT for this plugin's code (see [LICENSE](LICENSE)). Generated audio is
subject to Sonilo's own terms of service.

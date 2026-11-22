# Privacy Policy — Sonilo Plugin

This plugin connects Dify to the Sonilo API (`https://api.sonilo.com`) using
an API key you configure yourself in the Dify provider credentials.

## Data sent to Sonilo

When you invoke one of this plugin's four tools, the following leaves your
Dify deployment and is sent to `api.sonilo.com` over HTTPS:

- **Text to Music**: the `prompt` text you (or the calling LLM) supply,
  plus `duration` and, if set, `output_format`.
- **Text to Sound Effects**: the `prompt` text, plus `duration` and, if
  set, `audio_format`.
- **Video to Music / Video to Sound Effects**: the `video_url` you supply
  (Sonilo's servers fetch the video content from that URL directly), plus
  any optional style `prompt` and format field. This plugin does not
  upload raw video bytes itself; it only sends the URL.
- **Your Sonilo API key**, sent as a `Bearer` token on every request. Used
  for authentication and billing only.

Requests are sent as `multipart/form-data` (required by Sonilo's backend
for these endpoints) — the plugin does not send anything beyond the
prompt/video URL/generation options and the API key needed to make the
request.

## Data the plugin itself stores

This plugin does **not** persist prompts, video URLs, generated audio, task
IDs, or your API key anywhere outside of a single tool invocation. Async
jobs are polled in-memory for the duration of that invocation only; nothing
is written to disk or to any datastore operated by the plugin.

Dify itself may store tool inputs, outputs, and logs according to your Dify
deployment's own configuration — that is governed by Dify's privacy policy,
not by this plugin.

## Data Sonilo may store

Sonilo processes the prompts, video URLs, and generated audio you submit in
order to run generation and serve the resulting file back to you, and may
retain data and operational logs according to its own terms. Review
Sonilo's own policies before enabling this plugin:

- Sonilo: <https://sonilo.com>
- API documentation: <https://platform.sonilo.com/docs>

This plugin does not control, and is not able to describe on Sonilo's
behalf, Sonilo's internal retention windows; consult the links above or
contact Sonilo directly for that detail.

## Third-party processing

This plugin sends data only to `api.sonilo.com`. It does not transmit data
to any other third party. Downloading the generated audio file (so it can
be returned to you as a file, not just a URL) is a direct HTTPS request to
the URL Sonilo's API returns, which is itself hosted by or on behalf of
Sonilo.

## Credential handling

- The provider credential `api_key` is declared as a Dify `secret-input`.
  Dify encrypts it at rest and does not echo it back to clients.
- The plugin's error messages never include the API key value.
- Each Dify workspace supplies its own Sonilo API key — the plugin
  publisher has no access to other users' keys.

## Contact

For privacy questions about this plugin, contact Sonilo at
<info@sonilo.com> or via <https://sonilo.com/contact-sales>.

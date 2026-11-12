# Release validation: 0.1.0

Checked on 12 November 2026. No customer inbox or customer message content was used in connector validation. The live test used an existing isolated workspace and synthetic mail only between its two approved test addresses. Its API key is not part of source, the archive or the submission.

## Automated validation

- Python 3.12.16, `dify-plugin==0.11.0`, `httpx==0.28.1`, official Dify CLI 0.6.15 (download digest checked).
- `python -m pytest -q`: 69 passed. Network is blocked in unit tests; HTTP interactions use `httpx.MockTransport`.
- All nine routes/payloads, address/UUID/size validation, no scheduled draft input, stable send IDs, duplicate/pending errors, credential validation without writes, sanitized failures, no automatic retries, fixed-host allowlist, TLS/proxy/redirect behavior and oversized responses are covered.
- The actual Dify SDK loads the manifest, provider and all nine tool classes and verifies JSON/named-variable output.
- `python scripts/package.py --cli /path/to/dify`: packages 33 allowlisted runtime files with the official CLI, compares every packaged byte to staged source, and loads all nine tools from the unpacked archive. No virtual environment, tests, local settings, executable or credential is bundled.
- CI repeats unit tests and packaging on Linux/Python 3.12 and retains the package/checksum as a build artifact.

The SDK currently emits a Pydantic deprecation warning; pytest startup can also emit the SDK/gevent late-SSL-import warning. These are dependency/test-process warnings, not hidden test failures. The packaged entrypoint imports the Dify SDK first, as the official scaffold does.

## Live API validation through SDK tool classes

Passed: read-only credential validation; Get account; List inboxes; Create inbox and list it back; Send message; Get message with exact synthetic content; keyword search; receive the sent message; Reply with the expected recipient/thread; receive that reply; create/read a draft that remains `draft` with no schedule.

An identical Send retry returned the same message ID with `idempotent: true`. A changed payload with that ID returned `client_id_conflict`. An identical Reply retry also returned the same message ID. No third-party recipient was used and no repeated send was forced around a restriction.

The isolated account is on Free: semantic/hybrid request shape and returned `mode_used` handling are covered by tests, but paid-plan semantic retrieval was not exercised live for this plugin. Suspensions, quota exhaustion and bounce/complaint events were not deliberately triggered; client behavior is tested with mocked service errors and server controls are documented from deployed code/configuration.

## Hosted-testing limitations

This is **not** a claim that the plugin has been installed or visually tested in Dify Cloud or a full self-hosted Dify Community Edition deployment. Validation used the official SDK locally against both mocked and live API responses, plus the official package format. Workspace installation, credential UI, workflow variable selection, Agent node invocation and a Human Input workflow still need hosted verification. Marketplace review/signing/publication is pending. There is no claim of compatibility with every older Dify/daemon release.

A future creators.dify.ai workflow is a separate follow-up once the plugin is available. An email reply is not, by itself, authenticated human approval. The README explains the Human Input pattern and its trust boundary; no untested workflow template is bundled.

## Operational facts behind the notices

The service source audited was commit `02e9a1cb1b6525bc59c838c072a42687e21244f4`; the same API release was active during the checks. Allowlisted production metadata confirmed Railway API/PostgreSQL in `us-west2`, AWS configured `eu-west-1`, an S3 bucket region response of `eu-west-1`, and embedding/telemetry integrations enabled. No customer S3 objects were fetched for this audit.

The owner confirmed that ordinary email has no automatic expiry: users control deletion or request account deletion. Raw-object deletion and backup purge deadlines were not verified; those limits are disclosed in `PRIVACY.md`. The plugin does not invent a purge promise or claim all processing stays in one jurisdiction.

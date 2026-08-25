# HOL Guard — Dify Tool plugin

A Dify **Tool** plugin for side-effect-free command risk inspection with [HOL Guard](https://github.com/hashgraph-online/hol-guard).

## What it does

**Inspect command with HOL Guard** (`inspect_command`) accepts command text and runs HOL Guard's built-in command safety extensions without executing the command or persisting Guard state. The result includes the matched command classification, risk classes, minimum action, controlling rule, signals, extensions, rules, and parser trace.

Use the returned fields in a Dify Workflow or Agent flow to decide whether to continue, ask for review, or stop.

This plugin is an inspection surface, not a claim of native Dify pre-tool enforcement. For actual runtime blocking, approvals, receipts, and harness protection, install HOL Guard on one of its supported agent/coding harnesses.

## Setup

No API key or external service is required. The plugin runtime installs the `hol-guard` Python package from PyPI through `requirements.txt`.

## Usage

Pass a shell command as `command`, for example:

```text
rm -rf ./build
```

The plugin returns HOL Guard's structured inspection payload. It **never runs** the submitted command.

## Connection requirements

None for inspection. The tool runs locally in the Dify plugin process.

## Source

HOL Guard: https://github.com/hashgraph-online/hol-guard

## Privacy

See [PRIVACY.md](./PRIVACY.md). The plugin does not collect, store, or transmit command text.

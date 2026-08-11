# Privacy Policy — Prompt Template Plugin

This plugin renders prompt templates by substituting `{{variable}}` placeholders with values supplied by the Dify workflow. It performs no network requests, no file operations, and no external calls of any kind.

## Data collected

**None.** This plugin collects, stores, logs, or transmits no user data.

## What happens to your data

Everything runs inside your Dify runtime as a pure string transformation:

* Template inputs (`system_template`, `user_template`) and variable values are processed in-memory for the duration of a single tool invocation.
* The plugin sends **no** data to any external service, because it makes **no** network requests.
* The plugin does not persist anything to disk, database, or any storage backend. `storage` permission is disabled in `manifest.yaml`.

## Third-party processing

None. The plugin does not transmit data to any third party. It has no API endpoints, no external dependencies beyond the Dify plugin SDK, and no telemetry.

## Credential handling

The plugin requires **no credentials**. The `provider/_validate_credentials` method is a no-op, and no secret-input fields are declared.

## Contact

For privacy questions about this plugin, open an issue at https://github.com/tanzhangjia/prompt-template

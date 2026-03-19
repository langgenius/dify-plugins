# Privacy Policy - Prompt Shield Dify Plugin

## Data Processing

All text processing performed by this plugin runs **entirely locally** on the machine where the Dify instance is hosted. No data is transmitted to external servers or third-party services.

## What This Plugin Does

- **Prompt Injection Scan**: Analyzes input text locally using pattern matching and heuristic detection to identify prompt injection attempts.
- **PII Scan**: Detects personally identifiable information using local regex-based pattern matching.
- **PII Redact**: Replaces detected PII with placeholder tokens locally.

## Data Storage

This plugin does not store, log, or persist any input text or scan results beyond the lifetime of a single tool invocation. Any persistence (e.g., attack vault, feedback) is managed by the prompt-shield library itself on local disk.

## Third-Party Services

This plugin makes **no network requests** and communicates with **no external APIs**. All detection logic is self-contained within the prompt-shield library.

## Contact

For questions about this privacy policy, please open an issue on the [prompt-shield GitHub repository](https://github.com/mthamil107/prompt-shield).

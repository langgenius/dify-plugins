# Prompt Shield - Dify Plugin

A Dify tool plugin that provides local prompt injection detection and PII redaction powered by [prompt-shield](https://github.com/mthamil107/prompt-shield).

## Tools

### Prompt Injection Scan (`scan`)

Scans text for prompt injection attacks using multiple detection strategies. Returns a risk score (0.0-1.0), a recommended action (`pass`, `log`, `flag`, or `block`), and details about detected threats.

### PII Scan (`pii_scan`)

Detects personally identifiable information in text, including email addresses, phone numbers, SSNs, credit card numbers, IP addresses, and more. Returns entity types and counts without modifying the text.

### PII Redact (`pii_redact`)

Redacts PII from text by replacing sensitive data with entity-type-aware placeholders (e.g., `[EMAIL_REDACTED]`, `[PHONE_REDACTED]`). Returns the redacted text along with counts of what was redacted.

## Installation

1. Ensure `prompt-shield-ai` is installed in your Dify plugin runtime environment:

   ```bash
   pip install prompt-shield-ai>=0.3.0
   ```

2. Package and install the plugin into your Dify instance following the [Dify plugin development guide](https://docs.dify.ai/plugins/develop-plugins/tool-plugin).

## Configuration

No API keys or credentials are required. All processing runs locally using the prompt-shield library.

## Privacy

All text analysis is performed locally. No data is sent to external services. See [privacy.md](privacy.md) for details.

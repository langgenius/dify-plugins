# Privacy Policy — x402 Pay-Per-Call Plugin

This plugin lets a Dify workflow, chatflow, or agent call a third-party HTTP endpoint that you specify, optionally attaching a Nano (XNO) payment proof.

## Data sent by this plugin

When the **x402 Call** tool is invoked, the plugin sends, to the URL you (or the calling LLM) supply:

- The **URL**, HTTP method, and any query parameters or JSON body you provide.
- If you supply one, the **payment proof** you provide: either a settled Nano block hash (`X-PAYMENT` header) or a public `nano_...` account address (`X-BALANCE` header).

The plugin does not add any tracking identifiers, and does not send Dify workspace, user, or conversation identifiers to the target endpoint. A fixed `User-Agent: dify-x402-pay-per-call` header is sent so target servers can identify plugin traffic.

## What this plugin never collects, stores, or transmits

- **No wallet seed or private key.** The plugin has no input field for one, and never asks for one. A settled block hash or a public account address is not secret material — it cannot be used to spend funds.
- **No API key or account for this plugin's publisher.** There is no signup and no provider-level credential.
- The plugin does not persist request URLs, payment proofs, or response bodies beyond the single tool invocation. Everything happens in-memory for the duration of one call.

## Data the target endpoint may collect

The third-party endpoint you point this tool at is outside this plugin's control. It receives the URL, method, parameters, and (if supplied) payment proof for each call, and may log or retain that data according to its own policies. Review the target service's own privacy policy before sending it sensitive data.

## Data Dify itself may store

Dify may store tool inputs, outputs, and logs according to your own Dify deployment's configuration. That is governed by Dify's privacy policy, not by this plugin.

## Contact

For privacy questions about this plugin, open an issue at:
https://github.com/langgenius/dify-plugins/issues

# x402 Pay-Per-Call

Call third-party HTTP endpoints that use the [x402](https://www.x402.org/) pay-per-call scheme, settled in Nano (XNO). Nano settles on-chain in about a second at zero fee, which makes per-call micropayments practical.

## What it does

The plugin provides one tool, **x402 Call**:

- Calls a URL you (or the calling LLM) supply.
- If the endpoint responds `200 OK`, the response body is returned as-is.
- If the endpoint responds `402 Payment Required`, the plugin **does not pay anything** — it parses and relays the payment challenge (price, pay-to account, accepted networks) so the price can be quoted to the human user.
- Once the human has settled the payment themselves, in their own Nano wallet, they provide the resulting **settled block hash** back to the tool as payment proof, and the tool retries the call with that proof attached.

## What it does NOT do

- It never holds, generates, or requests a wallet seed or private key.
- It never initiates a payment on your behalf. You settle payments yourself, outside of Dify, in your own wallet.
- It only relays a settled block hash (public, on-chain, already-spent proof) or a public `nano_...` account address — never secret material.

## Configuration

No provider-level credentials or account are required. Each call to the **x402 Call** tool takes:

| Parameter | Required | Description |
| --- | --- | --- |
| `url` | Yes | The full `https://` or `http://` URL of the endpoint to call. |
| `method` | No | `GET` (default) or `POST`. |
| `query_params` | No | JSON object of query parameters. |
| `json_body` | No | JSON request body (POST only). |
| `payment_header` | No | A settled Nano (XNO) payment block hash, sent as the `X-PAYMENT` header. Leave empty on the first call. |
| `balance_account` | No | A `nano_...` account with a prepaid balance on the target server, sent as the `X-BALANCE` header. |
| `timeout` | No | Request timeout in seconds (default 30). |

## Usage

### Chatflow / Workflow

Add the **x402 Call** tool node, wire the `URL` input, and route the tool's JSON output (which includes a `payment_required` flag on HTTP 402) into your flow logic. On a 402 response, surface the quoted `price` / `pay_to` fields to the end user so they can settle the payment; on their next turn, pass the resulting block hash back in as `payment_header`.

### Agent applications

Add the **x402 Call** tool to an Agent. The tool's LLM-facing description explains the two-step flow (quote, then retry with proof), so the agent can ask the user for a settled Nano payment before retrying automatically.

## Requirements

- No API key or account signup with this plugin's publisher.
- To settle payments, you need a Nano (XNO) wallet capable of sending a transaction and reading back the resulting block hash (e.g. any standard Nano wallet).
- The target endpoint must implement the x402 HTTP 402 challenge/response scheme.

## Source

https://github.com/langgenius/dify-plugins (this directory)

Issue and design discussion: https://github.com/langgenius/dify-plugins/issues/3148

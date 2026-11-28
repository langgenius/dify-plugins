# KontoCSV for Dify

Convert bank, card, and payment statements or transaction CSV files into accounting-ready exports using the official KontoCSV MCP service. The plugin exposes **eight existing server-side tools**; it does not parse statements, move money, or implement a second conversion or credit system.

## Setup and account linking

1. Install the KontoCSV Tool plugin in Dify (version 1.7.1 or later).
2. Register a confidential OAuth 2.0 client with KontoCSV for the **exact callback URL shown by Dify**. The registration must allow the resource `https://www.kontocsv.de/api/mcp/claude`, the `mcp:tools` scope, authorization-code and refresh-token grants, PKCE S256, and `client_secret_basic` token authentication. KontoCSV integration support can assist with this registration.
3. In Dify's Tool Provider OAuth Client configuration, enter the client ID and client secret. Do **not** paste credentials into a workflow prompt.
4. Select Authorize, then sign in or sign up on KontoCSV and consent to the requested MCP access.
5. Use the eight KontoCSV tools with the authenticated account. If no conversion credits remain, purchase credits separately through the KontoCSV website; this plugin does not provide paid checkout tools.

The Dify ToolProvider uses a fresh PKCE verifier for each authorization. A ten-minute encrypted state token binds the verifier to the registered confidential OAuth client and the exact HTTPS callback. OAuth tokens are handled by Dify's credentials storage; they are not stored independently by the plugin.

## Recommended workflow

1. **create_browser_upload_session**: ask whether the document is a PDF or CSV, then give the user the short-lived browserUploadUrl.
2. The user opens that link and uploads the file **directly on KontoCSV**. The Dify plugin never retrieves files from Dify conversations or workflows.
3. **complete_browser_upload**: after user upload, use the returned uploadSessionId to obtain a sourceId.
4. **inspect_bank_statement**: inspect document scope, account structure, balances and compatible export profiles.
5. **get_credit_balance** (optional) and **prepare_bank_statement_conversion**: use the returned sourceId and a supported exportProfile. Preparation never charges credits and does not create a checkout.
6. Present the exact required credits, available credits and target profile, then ask the **human user for explicit confirmation**. Only when explicitly confirmed use **convert_bank_statement_for_accounting** with the original quoteId and `confirmedByUser=true`. KontoCSV atomically reserves existing credits; billing and outcomes are enforced server-side.
7. **get_conversion_status**: inspect the conversion's quality status, including incomplete or failed states. **download_accounting_export** returns a short-lived URL only when a valid export is actually ready.

Do not invent source IDs, quote IDs, job IDs, successful conversion results or file readiness. Do not call confirmation-gated conversion without explicit human consent. If credits are insufficient, direct the user to `https://www.kontocsv.de`; do not create a checkout through Dify.

## Scope, privacy and security

- All tool calls use HTTPS to a fixed `https://www.kontocsv.de/api/mcp/claude` endpoint. Redirects are disabled. No arbitrary third-party API calls, SSH, shell, SQL, or remote file fetching.
- Authentication is per user through KontoCSV OAuth. KontoCSV enforces source/job ownership, quotas, atomic credit holds and quality validation. The plugin does not have privileged administration access.
- PDFs and CSVs are uploaded on KontoCSV, not sent through Dify. Tool inputs, metadata and results may be processed by the Dify workspace, workflow and LLMs selected by the user.
- No payment-card collection, payment links or monetary quote/checkout actions are exposed in this plugin.
- See [PRIVACY.md](PRIVACY.md), [KontoCSV connector documentation](https://www.kontocsv.de/en/claude-connector), [privacy policy](https://www.kontocsv.de/en/privacy/claude) and [terms](https://www.kontocsv.de/en/terms).
- Public source: https://github.com/world-discovery-llp/dify-plugins

Support: support@kontocsv.de.

## Verification and limitations

The eight input schemas are generated from the live public KontoCSV MCP catalog endpoint and checked for parity. Offline tests cover argument validation, confirmation gating, JSON and SSE transport, OAuth PKCE and token rotation. The Dify Marketplace validator is run on the packaged artifact. **An authenticated Dify Cloud OAuth and conversion E2E must be performed with a registered OAuth client and test account before claiming live validation.** The Dify plugin itself is free to install; KontoCSV credits are required to perform paid conversions.

# KontoCSV Dify Tool Plugin — Privacy Notice

Updated 28 November 2026.

KontoCSV, operated by World Discovery LLP, provides document conversion services behind a user-authenticated OAuth 2.0 MCP endpoint.

## Data transmitted

The plugin sends tool parameters, including temporary source/session/quote/job identifiers, export choices and conversion-confirmation flags, to KontoCSV at https://www.kontocsv.de/api/mcp/claude. Responses may contain account/statement metadata, balance evidence, credit balance information, conversion status and time-limited export links.

Bank PDFs and CSV files are uploaded directly through a secure browser session on the KontoCSV website. The plugin does not download attachments from Dify, read unrelated Dify files or send raw document bytes through a Dify tool call. The user may still enter sensitive text into Dify workflows independently.

OAuth credentials, including access and refresh tokens, are provided to and stored by the Dify host. The plugin handles them only for authentication and does not independently persist or log tokens. It transmits tokens only as Bearer credentials to the fixed KontoCSV MCP endpoint and as token credentials to the fixed KontoCSV OAuth issuer. A short-lived encrypted OAuth PKCE state does not contain access tokens.

## Storage, recipients and control

Data uploaded to KontoCSV is stored and processed according to KontoCSV's service and privacy policies. Dify and any workflow-connected models or services may separately process tool arguments and results under the Dify user's configuration and terms. The plugin does not implement its own database, logging or storage of documents, prompts or API results. KontoCSV enforces user-level source/job isolation and existing-credit billing; users can disconnect the integration in Dify and manage KontoCSV authorization in their account.

No bank login details, TANs, payment-card data or bank passwords should be entered in tool arguments.

Privacy: https://www.kontocsv.de/en/privacy/claude

Terms: https://www.kontocsv.de/en/terms

Support: support@kontocsv.de

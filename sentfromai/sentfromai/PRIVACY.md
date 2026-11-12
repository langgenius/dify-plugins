# SentFromAI Dify plugin privacy notice

Version 0.1.0 — operational facts checked 12 November 2026.

This notice describes the plugin and the SentFromAI service it connects to. SentFromAI is operated by Brightboard AI Ltd (UK company 16832757). Contact support@sentfrom.ai for privacy, access, deletion or security questions. The service policy is https://sentfrom.ai/privacy and terms are https://sentfrom.ai/terms. This notice adds integration-specific detail; it does not promise an unverified storage location, retention period, certification or processor agreement.

## Data flow and purposes

1. You put a SentFromAI workspace API key into Dify's provider credential field. Dify stores/manages that credential under your Dify deployment's policies. The running plugin receives it and sends it only as an HTTPS Bearer credential to the fixed host `api.sentfrom.ai`. It is not an input parameter offered to the LLM.
2. Tool calls transmit the selected arguments to SentFromAI: mailbox names/IDs, recipients (including CC/BCC), subjects, plain-text/HTML content, search queries, message/draft IDs and stable send-operation IDs. SentFromAI uses them to operate inboxes, deliver and receive mail, keep threads/drafts, search, meter usage and enforce security/abuse controls.
3. Results return through the plugin to Dify. They can include account IDs/status/limits, inbox addresses, email headers and content, correspondent addresses, timestamps, labels, attachment metadata and time-limited signed attachment URLs. Returned email may contain personal, confidential, authentication, financial, health, location or other sensitive information. The plugin does not inspect or certify it as nonsensitive. Users must have authority to process the mail; do not use it for prohibited data under SentFromAI's terms.
4. Your Dify workflow decides what reaches its LLMs, later nodes, logs, exports and users. Dify Cloud, self-hosted Dify, and your configured model/tool providers have separate data-processing and retention arrangements. Installing this plugin does not control those arrangements. Grant access only to appropriate workspace members and minimize email content included in prompts or exports.

The plugin itself creates no separate database, local message archive, analytics stream or persistent plugin storage. It holds request/response data in process memory while running, does not intentionally log credentials or message bodies, and replaces upstream error content with sanitized errors. This does **not** mean no data is collected: SentFromAI stores/processes mail, and Dify/hosting infrastructure may retain workflow data or diagnostics. The plugin verifies TLS, follows no redirects, has fixed API routes and performs no arbitrary URL fetch, browser action or attachment download.

## SentFromAI storage and locations

The production API and PostgreSQL database are hosted on **Railway in the United States (`us-west2`)**. Stored records include inboxes, messages, addresses/headers, threads, drafts, attachment metadata, account/usage state and derived search vectors. Raw inbound mail and attachment objects are handled by **Amazon S3**; the configured bucket's region was verified as **Europe (Ireland), `eu-west-1`**, using its region response header. Amazon SES/SNS email infrastructure is also configured for `eu-west-1`.

These are service/configuration locations, not a promise that all processing, support, backups, recipient mail systems or subprocessors stay in one country. Email delivery transfers content to the recipients' email providers wherever they operate. Backup retention/locations and regional processing guarantees for other vendors have not been verified for this release. This integration must not be represented as US-only or EU-only processing.

## Email indexing and model processing

SentFromAI currently sends message **subjects and plain-text bodies** to **OpenRouter**, using the `openai/text-embedding-3-small` model, to create search vectors for inbound and outbound mail. The vectors are stored in PostgreSQL. This server-side indexing can occur on all plans and does not stop merely because a Dify tool uses keyword search. Semantic/hybrid searches also send their query text for embedding.

OpenRouter routes requests to an underlying model provider. The checked configuration does not pin a provider or geography; routing may involve OpenAI or Azure. We have not verified a contractual zero-retention/no-training setting or a fixed processing region for this route, so this notice makes no such claim. There is no per-call “disable server indexing” switch in this plugin. It does not send attachments directly to an embedding service. Your own Dify model steps may separately receive email text or attachment data if you configure them to do so.

## Service providers and access

| Provider/service | Relevant processing |
| --- | --- |
| Railway | API/database hosting, stored email and derived search records, operational infrastructure |
| Amazon Web Services (SES, SNS, S3) | Mail transport/events, raw mail and attachment objects |
| OpenRouter and its selected model provider | Subject/plain-text and search-query embeddings as described above |
| PostHog | Product analytics/error telemetry through the configured EU ingestion host; event data can include account identifiers and message subjects (up to 200 characters), along with delivery/usage metadata |
| Clerk | Console identity, workspace ownership and authentication |
| Stripe | Subscription, payment and usage/billing data; the plugin does not call Stripe or request card data |
| Cloudflare | DNS/domain configuration and support-address routing |
| Vercel / Ploy | Console / marketing-site hosting respectively; the plugin calls the API, not those sites |
| Google | Business/support correspondence when communicating with the team |

This table distinguishes mail-processing vendors from ancillary website/account/support services; it does not imply every vendor receives every email body. Authorized SentFromAI personnel and operational systems may access relevant mail and metadata for support, delivery diagnosis and abuse investigation. Do not include customer mail in a public GitHub issue; contact support privately and share only what is needed.

## Retention, deletion and backups

**There is no automatic age-based deletion policy for ordinary stored email.** Customers keep their email until they use the service's available deletion controls or request deletion of their account. Do not assume a 7/30/90-day purge. Raw objects, derived records and backups need to be considered separately in the deletion process, as explained below. Separate short-lived unclaimed-account cleanup rules do not establish a general retention period for claimed accounts or all objects.

The API's inbox-deletion path cascades related database message/thread/attachment-metadata records and associated vectors. It does **not** establish that corresponding S3 raw mail/attachment objects or backups have been erased. This plugin exposes no deletion tool. Disconnecting it from Dify or revoking its API key stops that credential's future access; it does not delete SentFromAI mail or Dify's past workflow executions.

For access, correction, export, objection or erasure requests, contact support@sentfrom.ai with the relevant account and scope. Identity/authority may need verification; where SentFromAI processes data for a customer's organization, requests may need coordination with that organization. Do not send an API key with the request. Account deletion is available by request. A universal deletion completion time, raw-object expiry and backup purge period have not been confirmed; contact support before relying on a particular deadline. Legal, billing and abuse-investigation records can have different retention requirements from mail content. Copies already delivered to recipients and records held by Dify or other vendors require their own deletion processes.

## Operator choices

Use a separate workspace for synthetic testing, store keys only as Dify credentials, limit who can run tools/read results, restrict sending tools to authorized workflows and review retention settings in your Dify deployment. Signed attachment URLs should be treated as temporary access credentials. For sensitive workflows, confirm the processing/retention arrangements with support before connecting production mail. Policy changes will be reflected in future plugin releases and the service policy.

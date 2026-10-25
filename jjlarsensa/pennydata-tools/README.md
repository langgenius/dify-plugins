# PennyData Tools for Dify

Three Dify tools backed by public pay-per-event actors from the `pennydata` account on Apify:

| Tool | Actor | What it returns | Apify price (check the actor page) |
|---|---|---|---|
| Detect Website Tech Stack | [website-tech-stack-detector](https://apify.com/pennydata/website-tech-stack-detector) | CMS, e-commerce platform, analytics, CDN, JS frameworks, with evidence | about $0.0015 per analyzed URL |
| Validate Emails in Bulk | [bulk-email-validator-no-smtp](https://apify.com/pennydata/bulk-email-validator-no-smtp) | syntax, MX, disposable, role-account, free-provider flags (no SMTP probe; does not prove a mailbox exists) | about $0.0004 per email |
| Domain WHOIS and DNS Lookup | [bulk-domain-whois-dns-lookup](https://apify.com/pennydata/bulk-domain-whois-dns-lookup) | availability, registrar, created/expiry, age, nameservers, MX, TXT via RDAP | about $0.001 per domain |

## Paid external service (disclosure)

The plugin itself is free. The tools run on Apify and are billed by Apify to **your** Apify account per result (pay-per-event), at the prices on each actor page. Each call is capped at 100 items and at $1.00 of charges. New Apify accounts include free monthly platform credit.

## Setup

1. Create an Apify account and copy an API token from https://console.apify.com/settings/integrations.
2. In Dify, install this plugin, open **Tools > PennyData Tools > Authorize** and paste the token. The plugin validates it against `https://api.apify.com/v2/users/me`.
3. Add a tool to a workflow, chatflow, or agent. Each tool takes one text input: a list separated by commas or newlines (max 100 items per call).

## Output

Each tool returns JSON: `{"count": N, "results": [...]}` with one object per item. See the actor pages for field descriptions.

## Connection requirements

Outbound HTTPS to `api.apify.com`. A call waits for the run synchronously (up to 5 minutes).

## Source, contact, and notes

- Source: https://github.com/jjlarsensa/bulk-whois-dns-api/tree/main/dify-plugin
- Contact / issues: https://github.com/jjlarsensa/bulk-whois-dns-api/issues
- Privacy: see [PRIVACY.md](PRIVACY.md). The plugin stores and logs nothing.
- Not affiliated with Apify or Dify. Built with AI assistance (Claude) and published by the maintainer account.

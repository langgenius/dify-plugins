# Sending limits and abuse controls

Verified against the deployed API and configuration on 12 November 2026. These are current operational controls, not a guarantee that abusive messages can never pass detection. Limits and entitlements can change; use Get account and the API's actual response for the connected workspace.

## Account boundary

- A workspace API key authenticates all plugin calls. An agent-created account cannot send until claimed by a verified human owner. The plugin cannot sign up, claim, unsuspend, unblock, upgrade or alter entitlements.
- Tenant suspensions, sending pauses, owner blocks, recipient suppression/block lists and account entitlements are checked by the sending service. The same service handles new mail and replies.
- Verified owners' free workspaces share sending allowances, so a fresh free workspace does not reset that owner's allowance. Owner blocks cover linked workspaces and subsequent claims. This is based on verified account ownership, not a claim that all unrelated identities can be automatically linked. Paid workspaces retain their own plan allowances and still respect owner blocks.

## Current default limits

| Effective plan | Sends per rolling hour | First 24-hour sends | Monthly hard ceiling |
| --- | ---: | ---: | ---: |
| Free | 100 | 200 | 5,000 |
| Pro | 2,000 | 5,000 | 100,000 |
| Scale | 20,000 | 50,000 | 1,000,000 |
| Business | 60,000 | 150,000 | 3,000,000 |

Enterprise limits are configured by agreement. Included paid quotas differ from these hard ceilings; overage billing may apply. Operator-set daily limits or holds may be more restrictive. Existing tenant quota checks use database counts and can overshoot by in-flight requests under concurrency; this table is not a claim of an atomic reservation for every quota. The pooled free-owner sending budget uses reservations before dispatch.

The plugin caps To+CC+BCC at 10 recipients per send/draft; server controls also apply, including to server-derived reply recipients. Message text/HTML fields are each capped at 1,000,000 UTF-8 bytes in the plugin. These are implementation limits, not additional purchased allowances.

## Abuse detection and enforcement

- Repeated-content detection normally blocks further identical sends once a tenant has sent the same fingerprint to 20 distinct recipients within 24 hours. This is separate from normal hourly/monthly quotas.
- A confirmed-abuse library blocks exact matches and eligible high-similarity message bodies across accounts. Body-length/evidence checks help avoid relying on a generic subject alone. Similarity detection is not a guarantee that reworded or novel abuse is recognized.
- Delivery feedback is used for progressive warnings, throttling and pauses. Current sustained thresholds over a two-day window are 3%/4%/5% permanent bounce/complaint rates after at least 100 sends. Throttled accounts are limited to 10 sends/hour; quarantined accounts to 5/hour. Egregious bounce behavior can suspend an account and revoke its keys (current trigger: 25% after at least 20 sends).
- Recipient suppression and tenant block lists can remove individual recipients; the API refuses a send if no deliverable To recipient remains. Inspect send results; a successful request is not proof that every original recipient was included.
- Operators can investigate, warn, suspend/revoke keys, block verified owners, and add confirmed-abuse examples. These are server/operator capabilities, not privileges granted to the Dify plugin.

Sending unsolicited spam, phishing, deceptive messages, purchased-list mail or evading restrictions violates the service terms. A send hold must be resolved with the account owner/support, not by rotating identities, varying content or creating additional accounts.

## Agent and workflow safeguards

Send and Reply perform real external actions immediately. Only expose them where autonomous email is intended, or put them after an authenticated Human Input approval branch. Incoming email is untrusted content; never treat it as instructions to reveal credentials or authorization to change recipients. Keep an approved message fixed through dispatch.

The plugin requires durable `client_id` values for Send/Reply, preserves server errors without auto-retries, uses a fixed HTTPS host and does not expose arbitrary requests or account administration. These controls reduce accidental duplicate sends; they do not replace account abuse enforcement, recipient authorization or workflow access controls. There is no claimed general requests-per-second API quota: the limits above concern sending.

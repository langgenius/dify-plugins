# SupraWall Email System

This directory contains the core logic for the SupraWall Enterprise Email System, integrated via Brevo.

## Components
- `brevo.ts`: Low-level API client for Brevo Transactional API.
- `base.html`: The "Technical Noir" base template (Dark mode, Neon Lime `#B8FF00` accents).
- `phase1.ts`: Content and metadata for the 15 critical Phase 1 emails.
- `sync.ts`: Batch registration script to upload/update templates in Brevo.
- `dispatcher.ts`: High-level utility to send emails by tag (e.g., `SW-HITL-001`).

## Sending Emails
Use the `dispatchEmail` function:
```typescript
import { dispatchEmail } from '@/lib/emails/dispatcher';

await dispatchEmail("SW-HITL-001", "user@example.com", {
  agent_name: "SecurityAgent",
  action_summary: "Delete Database"
});
```

## Syncing Templates
To register templates in Brevo, run:
```bash
npx jiti packages/dashboard/src/lib/emails/sync.ts
```

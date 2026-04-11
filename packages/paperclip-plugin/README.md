# suprawall-vault

**Secure credential vault for Paperclip AI companies.**

Every agent gets only the credentials it's authorized to use, for only as long as it needs them — with every access logged. No more raw API keys in env variables.

```bash
paperclipai plugin install suprawall-vault
```

---

## What it does

When you install SupraWall Vault on your Paperclip company:

1. **Your agents get role-based credential access** — CEO agents can read everything, marketing agents get LinkedIn/Twitter/Google Ads, engineering gets GitHub/Supabase/Vercel, finance gets Stripe.
2. **Credentials are never stored in env vars** — they live in SupraWall's encrypted vault and are injected at runtime for the duration of a single task.
3. **Every access is logged** — who accessed what, when, and why. Tamper-proof audit trail.
4. **Agents lose access the moment they're fired** — webhooks revoke all credentials immediately.

---

## Install & Setup

### Step 1: Install the plugin

```bash
paperclipai plugin install suprawall-vault
```

The terminal will print:

```
✅  SupraWall Vault installed successfully!
🔑  Temp API key (Developer tier): sw_temp_xxxxx
🚀  Activate your account: https://supra-wall.com/activate?token=sw_temp_xxxxx
📖  Docs: https://docs.supra-wall.com/paperclip
```

### Step 2: Store your SupraWall API key in Paperclip

```bash
curl -X POST http://localhost:3100/api/companies/{YOUR_COMPANY_ID}/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SUPRAWALL_API_KEY",
    "value": "sw_temp_xxxxx",
    "provider": "local_encrypted"
  }'
```

Replace `sw_temp_xxxxx` with the key printed during install.

### Step 3: Register the SupraWall webhook in Paperclip

Generate a shared secret first:

```bash
openssl rand -hex 32
# → e.g. a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5...
```

Then register the webhook:

```bash
curl -X POST http://localhost:3100/api/companies/{YOUR_COMPANY_ID}/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.supra-wall.com/v1/paperclip/webhooks",
    "secret": "YOUR_GENERATED_SECRET_ABOVE",
    "events": ["agent.hired", "agent.fired", "run.completed"]
  }'
```

Add the same secret to your SupraWall environment:

```bash
# In your SupraWall server .env or Vercel environment variables:
PAPERCLIP_WEBHOOK_SECRET=YOUR_GENERATED_SECRET_ABOVE
```

### Step 4: Configure your agents to use SupraWall

In each agent's configuration, add the SupraWall adapter:

```json
{
  "adapterType": "http",
  "adapterConfig": {
    "url": "https://api.supra-wall.com/v1/agent/invoke",
    "method": "POST",
    "headers": {
      "x-api-key": "{{SUPRAWALL_API_KEY}}",
      "Content-Type": "application/json"
    },
    "body": {
      "agentId": "{{agent.id}}",
      "companyId": "{{company.id}}",
      "role": "{{agent.role}}",
      "runId": "{{run.id}}"
    }
  }
}
```

### Step 5: Activate your account

Visit the activation URL from Step 1 to capture your email and optionally upgrade to a paid tier. Your `sw_temp_*` key works immediately — activation is optional for the free Developer tier.

---

## Role → Credentials Mapping

| Role | Credentials Granted |
|---|---|
| `ceo` | `read:all` |
| `marketing` | `linkedin`, `twitter`, `google_ads` |
| `engineering` | `github`, `supabase`, `vercel` |
| `finance` | `stripe` |
| `hr` | `read:all` |
| `legal` | `read:all` |

Custom roles and credentials can be configured in your [SupraWall dashboard](https://supra-wall.com/dashboard).

---

## Understanding Operations (Billing)

SupraWall bills by **operations** (evaluations):

| Paperclip concept | SupraWall operation |
|---|---|
| 1 agent heartbeat | 1 operation |
| 1 agent task run | 1–N operations (depends on secrets accessed) |

**Example:** 10 agents × 3 tasks/day = ~900 ops/day = ~27,000 ops/month → fits the **Developer free tier** (25K ops/mo) or **Team** ($149/mo, 250K ops).

---

## Pricing

| Tier | Price | Agents | Ops/mo |
|---|---|---|---|
| Developer | Free | 5 | 25K |
| Team | $149/mo | 25 | 250K + AI semantic analysis |
| Business | $499/mo | Unlimited | 2M + behavioral anomaly detection |
| Enterprise | Custom | Unlimited | Unlimited + EU AI Act compliance |

Upgrade at: [supra-wall.com/pricing](https://supra-wall.com/pricing)

---

## Programmatic Usage

```typescript
import { createPlugin, SupraWallClient } from 'suprawall-vault';

// Use in your Paperclip plugin config
const plugin = createPlugin({
  apiKey: process.env.SUPRAWALL_API_KEY,
  apiUrl: 'https://api.supra-wall.com', // or your self-hosted URL
});

// Or use the client directly
const client = new SupraWallClient({ apiKey: 'sw_temp_xxx' });
const result = await client.invoke({
  agentId: 'agent_ceo',
  companyId: 'my-company',
  role: 'ceo',
  runId: 'run_001',
});
// result.credentials → { LINKEDIN_TOKEN: '...', TWITTER_TOKEN: '...' }
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPRAWALL_API_KEY` | Yes | Your SupraWall API key (auto-generated on install) |
| `SUPRAWALL_API_URL` | No | Override for self-hosted deployments. Default: `https://api.supra-wall.com` |

---

## Links

- **Docs:** [docs.supra-wall.com/paperclip](https://docs.supra-wall.com/paperclip)
- **Dashboard:** [supra-wall.com/dashboard](https://supra-wall.com/dashboard)
- **Pricing:** [supra-wall.com/pricing](https://supra-wall.com/pricing)
- **Support:** support@wiserautomation.agency
- **Issues:** [github.com/wiserautomation/suprawall-plugins-/issues](https://github.com/wiserautomation/suprawall-plugins-/issues)

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

SupraWall Does It All
SupraWall handles three things in this integration:

Vault — stores the actual credentials (LinkedIn token, X token, Stripe key, etc.)

Identity — knows who each Paperclip agent is (agentId + role)

Access Control — decides which agent can use which credential

There's no separate AgentGate. Every endpoint, every policy, every token issuance lives under api.supra-wall.com.

Revised Architecture
text
Paperclip Agent Fleet
        │
        │  HTTP POST (agentId, companyId, role, runId)
        ▼
┌───────────────────────────────────┐
│         supra-wall.com            │
│                                   │
│  /v1/agent/invoke                 │
│    → Identify agent               │
│    → Check role permissions       │  ← All in SupraWall
│    → Issue scoped token from Vault│
│    → Log: who, what, when         │
│                                   │
│  /v1/paperclip/onboard            │
│    → Sync Paperclip org on install│
│                                   │
│  /v1/paperclip/webhooks           │
│    → agent.hired → auto-policy    │
│    → agent.fired → revoke all     │
└───────────────────────────────────┘
Corrected Code — Everything Under SupraWall
Phase 1: Agent Invocation Endpoint
typescript
// /api/v1/agent/invoke — the only endpoint Paperclip calls
export async function POST(req: Request) {
  const { agentId, companyId, role, runId } = await req.json();

  // SupraWall: identify + authorize
  const policy = await suprawall.policies.get({ agentId, companyId });
  if (!policy) return Response.json({ error: "Agent not registered in SupraWall" }, { status: 403 });

  // SupraWall Vault: issue scoped credentials
  const credentials = await suprawall.vault.issueScopedToken({
    agentId,
    companyId,
    allowedCredentials: policy.allowedCredentials, // e.g. ["linkedin", "twitter"]
    ttlSeconds: 3600,
    runId
  });

  // SupraWall Audit: log the access event
  await suprawall.audit.log({
    event: "credential_issued",
    agentId, companyId, role, runId,
    credentials: policy.allowedCredentials,
    timestamp: new Date()
  });

  return Response.json({ status: "accepted", credentials }, { status: 202 });
}
Phase 2: Org Sync on Paperclip Install
typescript
// /api/v1/paperclip/onboard
// Fires when user runs: paperclipai skill install suprawall-vault

const ROLE_POLICIES = {
  ceo:         ["read:all"],
  marketing:   ["linkedin", "twitter", "google_ads"],
  engineering: ["github", "supabase", "vercel"],
  finance:     ["stripe"],
};

export async function POST(req: Request) {
  const { paperclipApiKey, companyId } = await req.json();

  const agents = await fetch("https://your-paperclip.com/api/agents", {
    headers: { Authorization: `Bearer ${paperclipApiKey}` }
  }).then(r => r.json());

  for (const agent of agents) {
    await suprawall.policies.upsert({
      agentId:             agent.id,
      companyId,
      role:                agent.role,
      allowedCredentials:  ROLE_POLICIES[agent.role] ?? []
    });
  }

  return Response.json({ synced: agents.length });
}
Phase 3: Lifecycle Webhooks
typescript
// /api/v1/paperclip/webhooks

export async function POST(req: Request) {
  const { event, agent } = await req.json();

  if (event === "agent.hired") {
    await suprawall.policies.create({
      agentId:            agent.id,
      companyId:          agent.companyId,
      allowedCredentials: ROLE_POLICIES[agent.role] ?? []
    });
  }

  if (event === "agent.fired") {
    await suprawall.policies.delete({ agentId: agent.id });
    await suprawall.vault.revokeAllTokens({ agentId: agent.id }); // immediate wipe
  }

  if (event === "run.completed") {
    await suprawall.vault.revokeToken({ runId: agent.runId }); // clean up scoped token
  }
}
What to Tell Users
When someone installs SupraWall on their Paperclip company, the value proposition is dead simple:

Your agents were running with raw API keys sitting in env variables. SupraWall gives every agent only the credentials it's authorized to use, for only as long as it needs them — and logs every access.

No separate product. One install. SupraWall does the vault, the identity, and the audit trail.

Prepared using Claude Sonnet 4.6 Thinking
This is our actual pricing structure: Listed directory SW-Private
Listed directory SupraWall
Viewed TIER_SYSTEM_FIXES_SUMMARY.md:1-122
Ran command: `find . -name "tier-config.ts"`
Viewed tier-config.ts:1-237
Searched for "\\$/month"
Searched for "developer|team|business|enterprise"
Listed directory packages
Ran command: `find packages/dashboard -name "*pricing*" -o -name "*Pricing*"`
Viewed PricingClient.tsx:1-640
Ran command: `find packages/dashboard -name "en.json"`
Viewed en.json:1-784

The current pricing structure of SupraWall is built on an **Open Core** model, ranging from a free self-hosted tier to a high-compliance Enterprise suite. The system is designed with "Natural Upgrade Walls" that transition users from basic regex-based security to advanced AI-powered semantic analysis.

### 💰 Pricing Overview

| Tier | Price | Best For | Key Limitations |
| :--- | :--- | :--- | :--- |
| **Developer (Free)** | $0 | Solo builders & Research | 3 agents, 10 secrets, 10K ops/mo, 7-day logs |
| **Cloud - Starter** | **$49**/mo | Small production apps | 50K ops/mo included, then $0.002/eval |
| **Cloud - Team** | **$149**/mo | Teams scaling AI fleets | 500K ops/mo, AI Policies, Team plugins, 90-day logs |
| **Cloud - Business** | **$499**/mo | High-volume production | 5M ops/mo, Behavioral detection, SSO, 3-year logs |
| **Enterprise** | **Custom** | Article 9 compliance | Unlimited everything, Air-gapped/VPC, 7+ year logs |

---

### 🛠️ Detailed Plan Limitations & Features

#### 1. Developer (Free / Open Source)
*Target: Individual developers and self-hosted research.*
* **Core Limits:** 3 Agents, 10 Vault Secrets, 10,000 Operations/month.
* **Security:** Layer 1 only (Deterministic Regex-based rules).
* **Compliance:** JSON-only audit logs (7-day retention). No PDF reporting.
* **Integrations:** Limited to LangChain and Vercel AI SDK; PostgreSQL adapter only.
* **Support:** Community-based (GitHub Issues).

#### 2. Cloud Tier (Starter, Team, Business)
*Target: Production startups and scaling businesses.*
* **Consumption Model:** Monthly base fee + Usage-based overages (starting at $0.002/eval).
* **Security Evolution:**
* **Starter:** Standard Regex protection.
* **Team+:** Unlocks **Layer 2: AI Semantic Analysis** (analyzing intent, not just patterns).
* **Business+:** Unlocks **Behavioral Anomaly Detection** and Budget Enforcement.
* **Compliance:** 90-day to 3-year log retention + Branded PDF Compliance Reports.
* **Advanced Features:** Slack & Dashboard approval workflows, all framework plugins (CrewAI, AutoGen, etc.), and AWS Marketplace fulfillment.

#### 3. Enterprise Suite
*Target: Finance, Healthcare, and Government (Article 9 High-Risk AI).*
* **Pricing:** Custom contracts (typically starting at $25,000/year).
* **Infrastructure:** Support for VPC, Air-gapped deployments, and AWS Marketplace Containers (EKS).
* **Compliance:** Full **EU AI Act Compliance Suite** (Article 9 Risk Templates, Article 12 Logging, Article 14 Human Oversight), SOC 2 Type II certified.
* **Security:** Custom fine-tuned threat models, Dedicated HSM for vault secrets, and 7+ year audit retention.
* **SLA:** 99.99% uptime with financial penalties and 1-hour dedicated support response.

---

### 🚧 The "Natural Upgrade Walls"
The platform is architected to trigger upgrades at critical business growth moments:
1. **Agent Scaling:** When you move to your **4th agent**, the Developer tier caps out.
2. **Regex Fatigue:** When regex rules can't catch complex semantic attacks, users upgrade to **Team** for AI-powered policies.
3. **Audit Pressure:** When a legal or compliance audit requires **PDF evidence** instead of raw JSON, users move to **Cloud/Enterprise**.
4. **Retention Gaps:** When a **7-day log** is insufficient for tracking production incidents, users upgrade for 90-day+ history.
5. **Security Complexity:** When users need **PII Scrubbing** or **Budget Caps** to prevent runaway LLM costs.

> [!NOTE]
> **Overage Rates:** Monthly volume is billed on a sliding scale:
> * 10K – 500K ops: **$0.002** / eval
> * 500K – 2M ops: **$0.0015** / eval
> * 2M – 10M ops: **$0.001** / eval
> * 10M+ ops: **$0.0005** / eval

Does it work well with paperclip?
And how the payment process works? How they go from installing our soft in paperclip to paying us? we need to change something in our process?

Great — now I can give you a precise answer with your actual tiers in mind. Two parts: fit analysis + the exact payment flow you need to build.

How Well Your Pricing Fits Paperclip
It fits almost perfectly — with one gap to fix.

What Already Works
Your pricing unit is agents and your free tier gives 3 agents [user pricing]. The average Paperclip company starts with 5–8 agents (CEO, CMO, CFO, dev, marketing). This means every single Paperclip user hits your first upgrade wall immediately — they can't even run a minimal Paperclip company on your free tier. That's a natural funnel into Starter at $49/mo.

The upgrade path from there maps cleanly:

Paperclip Growth Stage	SupraWall Tier Triggered	Why
First company setup (5–8 agents)	Starter $49	Exceeds 3-agent free limit
Scaling to 15–20 agents with AI tasks	Team $149	500K ops, AI Semantic Analysis for intent-based attacks
Running 50+ agents 24/7 autonomously	Business $499	5M ops, Behavioral Anomaly Detection catches rogue agents
Finance/healthcare AI compliance	Enterprise	EU AI Act Article 9, air-gapped VPC
Your Regex Fatigue upgrade wall is particularly powerful here [user pricing]. Paperclip agents do complex, open-ended tasks — regex alone will miss semantic attacks like prompt injection through task descriptions. The moment a user's CMO agent gets jailbroken via a crafted LinkedIn message, they'll upgrade to Team for AI Semantic Analysis immediately.

The One Gap: Operations Mapping
Your ops unit is "evaluations" — you need to define this clearly for Paperclip users because Paperclip thinks in heartbeats and runs. Define it explicitly in your Paperclip-facing docs:

text
1 Paperclip heartbeat = 1 SupraWall operation
1 agent run (task execution) = 1–N operations depending on secrets accessed
A Paperclip company with 10 agents running 3 tasks/day = ~900 ops/day = ~27,000/mo. That fits Starter comfortably. Once they hit 20 agents running continuously, they approach 500K ops — clean upgrade trigger to Team.

The Payment Flow — What You Need to Build
This is the critical gap. Paperclip is a self-hosted CLI tool. There's no built-in marketplace payment layer yet. The user installs via terminal, never touches a browser unless you force it. Here's the full funnel you need:

Step 1 — The Install Hook (CLI → Email Capture)
When a user runs paperclipai plugin install suprawall-vault, your onInstall endpoint fires. This is your only guaranteed moment of contact. It must:

typescript
// POST /api/v1/paperclip/onboard  ← fires on plugin install
export async function POST(req: Request) {
  const { companyId, paperclipVersion, agentCount } = await req.json();

  // Create a pending account in SupraWall
  const account = await suprawall.accounts.createPending({
    source: "paperclip_install",
    companyId,
    agentCount
  });

  // Return an activation URL — printed in the user's terminal
  return Response.json({
    status: "activation_required",
    message: "SupraWall installed. Activate your free account:",
    activationUrl: `https://supra-wall.com/activate?token=${account.token}`,
    // Also allow API key to work immediately (frictionless start)
    tempApiKey: account.tempKey,  // Works for 3 agents on Developer tier, no email needed
    docsUrl: "https://docs.supra-wall.com/paperclip"
  });
}
The terminal prints:

text
✅ SupraWall Vault installed
🔑 Temp API key (Developer tier, 3 agents): sw_temp_xxxxx
🚀 Activate full account: https://supra-wall.com/activate?token=abc123
The tempApiKey means they can start immediately without leaving the terminal — zero friction. The activation URL converts them into a real account later.

Step 2 — The Activation Page (/activate)
This is the moment you capture email and start the Stripe subscription flow. Keep it to one screen:

text
┌─────────────────────────────────────┐
│  You installed SupraWall on         │
│  Paperclip company: [companyId]     │
│                                     │
│  3 agents detected → Free tier      │
│                                     │
│  Email: [________________]          │
│                                     │
│  [Activate Free Account →]          │
│                                     │
│  Need more than 3 agents?           │
│  [Start Starter — $49/mo]           │
└─────────────────────────────────────┘
You already have Stripe integrated. The Starter CTA goes directly to a Stripe Checkout session with the companyId as metadata.

Step 3 — In-Plugin Upgrade Prompts (The Upgrade Walls in Action)
When an agent hits a limit, SupraWall's API response itself triggers the upgrade prompt — no dashboard visit needed. The agent runtime sees this and surfaces it:

typescript
// When 4th agent tries to register (free tier limit)
return Response.json({
  error: "agent_limit_reached",
  currentTier: "developer",
  currentAgents: 3,
  message: "Developer tier supports 3 agents. Upgrade to Starter for up to unlimited agents.",
  upgradeUrl: "https://supra-wall.com/upgrade?plan=starter&source=agent_limit",
  upgradePrice: "$49/mo"
}, { status: 402 });  // 402 Payment Required — the correct HTTP status for this
Paperclip surfaces this in its dashboard UI automatically because it handles HTTP errors from adapters natively.

Step 4 — Usage Alerts via Discord (You Already Have This)
Since your n8n setup reports to Discord — wire SupraWall's usage alerts there too:

text
⚠️ [SupraWall] Company abc123 at 78% of monthly ops (390K/500K)
   Current plan: Starter ($49/mo)
   Upgrade to Team for 500K ops + AI Policies: supra-wall.com/upgrade
This is a warm, contextual upsell at exactly the right moment — right when they feel the limit approaching.

What You Need to Change / Build
Gap	Fix	Effort
No onInstall endpoint exists	Build /v1/paperclip/onboard with temp key issuance	1 day
No /activate page	Add to supra-wall.com dashboard (email capture → Stripe)	1 day
Upgrade walls return generic errors	Return structured 402 with upgradeUrl in JSON	Half day
Ops not defined for Paperclip users	Add "heartbeat = 1 op" definition to docs	2 hours
No Discord usage alerts	Wire SupraWall usage events to Discord webhook	Half day
The core of your product is already built. You're adding 4 glue endpoints that connect the Paperclip install moment to your existing Stripe + dashboard infrastructure — nothing architectural needs to change.

Prepared using Claude Sonnet 4.6 Thinking
right now our OSS is not yet public. We have several plugins our there, but the software itself its still not.
I guess we should wait for the release of the OSS right?

We can just build everything and then make it public jst then?

No — you don't need to wait. The Paperclip integration runs entirely against your cloud API (api.supra-wall.com), not your OSS repo. These are two separate things.

What's Actually Blocking What
text
supra-wall.com cloud API  ← LIVE → Paperclip integration can launch NOW
       │
       │  (separate event)
       ▼
OSS public repo           ← NOT YET PUBLIC → Unrelated to Paperclip plugin
A Paperclip user installing suprawall-vault never touches your source code. They hit your API, get a scoped token, pay via Stripe. The OSS being private is completely invisible to them.

Why Launching Before OSS Is Actually Better
Launching the Paperclip integration before your OSS gives you two separate launch events instead of one:

Launch 1 — Paperclip Plugin (now)

Post on Paperclip's GitHub Discussions, r/AI_Agents, HackerNews

Target: "SupraWall is the first credential vault built natively for Paperclip agent fleets"

Collect real users, real feedback, real usage data

Launch 2 — OSS Release (later)

You launch with: "SupraWall is now open source — already trusted by X Paperclip companies securing Y agents"

Social proof baked in from day one

The Paperclip community already knows you — they become your first GitHub stars

Launching both together collapses two momentum events into one. Splitting them doubles your surface area.

The One Thing to Have Ready Before Paperclip Launch
You don't need the OSS. You do need these 4 things working:

Required	Status to check
api.supra-wall.com/v1/agent/invoke endpoint	Must be live
/activate page with Stripe Checkout	Must be live
Developer free tier (3 agents, no credit card)	Must work on install
skill.json / NPM package published	Build this now
If those four work, you can ship the Paperclip integration this week and the OSS release becomes a power-up to an already-running engine — not the starting gun.
# SupraWall — Final Pre-Launch Security & Quality Review

**Reviewer:** Claude (automated audit)
**Date:** 2026-04-16
**Scope:** Full codebase review of `SW-Private/SupraWall/` — API security, frontend fixes, open-source hygiene, and launch readiness.
**Verdict:** NOT READY for public open-source launch. One critical blocker + one high-severity issue remain.

---

## Verdict Summary

| Area | Status | Notes |
|---|---|---|
| Frontend QA fixes (Cluster A routing) | PASS | All lang-prefix links fixed |
| Frontend QA fixes (Cluster B UX/copy) | PASS | CTA copy updated, beta page fixed |
| Frontend minor fixes (password toggle, email trim, background) | PASS | All verified in code |
| API fixes from Karim's security report (SEC-001..SEC-009) | PARTIAL | The 4 specific endpoints Karim tested are fixed; the rest are not |
| **API auth coverage across all endpoints** | **FAIL — BLOCKER** | **24 of 33 route files have zero authentication** |
| Hardcoded credential in source | FAIL — HIGH | Mock admin key in settings page |
| Open-source documentation | PASS | LICENSE, README, CONTRIBUTING, SECURITY, CHANGELOG all solid |
| CI/CD & publishing | PASS | 5 workflows, CLI publish config ready |
| Secrets in git | PASS | `.env.local` exists locally but is properly `.gitignore`d and not tracked |

---

## BLOCKER: Multi-tenant auth gap (24 of 33 API endpoints unprotected)

This is the single issue that prevents a public launch.

The developer added `verifyAuth` / `requireDashboardAuth` guards to the **specific endpoints Karim tested** (agents/[id], approvals/status/[id], evaluate, threat/log) but did NOT apply the same treatment to the remaining dashboard-facing endpoints. Any user who knows or guesses a `tenantId` string can read, modify, or delete another tenant's data with zero authentication.

### What is protected (8 endpoints — correct)

| Endpoint | Auth method | Status |
|---|---|---|
| `GET/POST/DELETE /agents` | `verifyAuth()` (Firebase JWT) | OK |
| `GET/PATCH/DELETE /agents/[id]` | `requireDashboardAuth()` | OK |
| `GET /approvals/status/[id]` | `requireDashboardAuth()` | OK |
| `GET /audit-logs` | `verifyAuth()` | OK |
| `GET /threat` | `verifyIdToken()` (manual) | OK |
| `POST /evaluate` | apiKey-in-body validation + Zod | OK (SDK endpoint) |
| `POST /threat/log` | apiKey-in-body + rate limit + Zod | OK (SDK endpoint) |
| `POST /vault` (resolve) | apiKey-in-body validation | OK (SDK endpoint) |

### What is NOT protected (24 endpoints — must fix)

Every endpoint below accepts `tenantId` from query params or request body **without verifying the caller owns that tenant.** An unauthenticated attacker can access any tenant's data.

**Vault (6 endpoints — attacker can read/create/delete/rotate secrets):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/vault/secrets` | GET, POST | Read all secrets metadata; create secrets for any tenant |
| `/vault/secrets/[id]` | DELETE, PATCH | Delete or modify any tenant's secrets |
| `/vault/secrets/[id]/rotate` | PUT | Rotate any tenant's secret values |
| `/vault/rules` | GET, POST | Read or create vault access rules |
| `/vault/rules/[id]` | DELETE | Delete vault rules |
| `/vault/log` | GET | Read vault access logs |

**Policies (2 endpoints — attacker can rewrite firewall rules):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/policies` | GET, POST | Read or create policies for any tenant/agent |
| `/policies/[id]` | DELETE | Delete any policy |

**Threat Intelligence (5 endpoints — attacker can read security posture):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/threat/events` | GET | Read all threat events |
| `/threat/aggregate` | POST | Trigger threat score aggregation |
| `/threat/baselines` | GET | Read behavioral baselines |
| `/threat/semantic` | GET | Read semantic analysis results |
| `/threat/summary` | GET | Read threat summaries |

**Compliance (2 endpoints — attacker can read audit data):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/compliance/status` | GET | Read compliance status |
| `/compliance/report` | GET | Generate and read compliance reports |

**Platform / Multi-tenant (4 endpoints — attacker can impersonate tenants):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/platforms` | GET, POST | Read or create platforms for any user |
| `/platforms/keys` | GET, POST, DELETE | Read, create, or delete sub-keys |
| `/tenants/[id]` | GET, POST | Read or modify tenant settings |
| `/stats` | GET | Read usage statistics |

**Other (5 endpoints):**

| Endpoint | Methods | Risk |
|---|---|---|
| `/approvals` | GET | Read pending approvals for any tenant |
| `/approvals/[id]` | PATCH | Approve/deny any approval request |
| `/agents/[id]/assess` | POST | Trigger AI assessment (uses Gemini API — cost risk) |
| `/agents/[id]/guardrails` | GET, PUT | Read or modify agent guardrail configs |
| `/extensions/dify` | POST | Dify plugin endpoint (may be intentionally open) |
| `/scrub` | POST | PII scrubbing (may be intentionally public) |

### Required fix

Add `requireDashboardAuth()` (or `verifyAuth()` + tenant-ownership check) as the **first line** of every handler listed above. The pattern already exists in `agents/[id]/route.ts` and `approvals/status/[id]/route.ts` — it needs to be copy-pasted to the remaining 24 files.

**Estimated effort:** 4–6 hours. It is mechanical work — every file follows the same pattern:

```typescript
// At the top of each handler:
const userId = await verifyAuth(request);
if (!userId) return unauthorizedResponse();

// Then verify the tenantId belongs to this user:
const userDoc = await firestore.collection("users").doc(userId).get();
const allowedTenantId = userDoc.data()?.tenantId || userId;
if (tenantId !== userId && tenantId !== allowedTenantId) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
}
```

**For the two potentially-public endpoints** (`/scrub` and `/extensions/dify`): if they are intentionally unauthenticated, add a code comment `// PUBLIC ENDPOINT — no auth by design` and apply rate limiting.

---

## HIGH: Hardcoded mock admin key in settings page

**File:** `packages/dashboard/src/app/[lang]/dashboard/settings/page.tsx`, line 41
**Content:** `setMasterKey("sw_admin_5f2e8a1b9c3d4e7f");`

This is a `useEffect` that sets a mock admin key as a fallback before the real fetch completes (line 64 does `setMasterKey(data.master_api_key || "")`). The fix is simple: remove the mock `useEffect` entirely. The fetch at line 50-67 already handles the real value, and the initial `useState("")` gives a clean empty state.

This key string will appear in the public GitHub repo's commit history if not removed before the initial public push.

---

## VERIFIED PASS: Karim's QA fixes

Every fix from the remediation plan has been verified in the current code:

**Frontend Cluster A (routing):**
- `HomeWrapper.tsx` line 76: Hero CTA uses `` href={`/${lang}/beta`} `` — PASS
- `VaultClient.tsx` lines 189, 523, 557: All CTAs use lang-prefixed hrefs — PASS
- `BudgetClient.tsx` lines 226, 352, 617: All CTAs use lang-prefixed hrefs — PASS
- `PolicyClient.tsx` lines 76, 351: All CTAs use lang-prefixed hrefs — PASS
- Navbar.tsx line 137: "Deploy on Cloud" uses `prefix("/login")` — PASS (was already correct)

**Frontend individual fixes:**
- `login/page.tsx` lines 146–153: Password visibility toggle with Eye/EyeOff icons — PASS
- `beta/page.tsx` line 52: Email trimmed before submit (`formData.email.trim()`) — PASS
- `beta/page.tsx` lines 88–92: Background orbs constrained with `w-[min(1200px,80vw)]` + overflow-hidden — PASS
- GitHub links: `prefetch={false}` and `rel="noopener noreferrer"` added — PASS

**Backend security fixes (Karim's specific endpoints):**
- `agents/[id]/route.ts`: `requireDashboardAuth` guard added before DB access — PASS
- `approvals/status/[id]/route.ts`: `requireDashboardAuth` guard added — PASS
- `evaluate/route.ts`: Zod validation, 401 + `WWW-Authenticate` header on missing apiKey, 401 on invalid key format — PASS
- `threat/log/route.ts`: New endpoint created with Zod schema, apiKey format validation, 60/min rate limit, 401 + `WWW-Authenticate` — PASS
- `vault/route.ts` (resolve): Endpoint exists with apiKey + secretName validation — PASS
- `vault/secrets/route.ts`: Error messages now list specific missing fields — PASS
- `api-auth.ts`: Supports both Firebase JWT and `sw_admin_*` key authentication — PASS
- `api-errors.ts`: Canonical error helpers with correct HTTP codes and `WWW-Authenticate` header — PASS

**Open-source documentation:**
- `LICENSE`: Apache 2.0, correct copyright — PASS
- `README.md`: Install instructions, feature list, badges — PASS
- `CONTRIBUTING.md`: Bug reporting, PR process, dev setup — PASS
- `CODE_OF_CONDUCT.md`: Contributor Covenant — PASS
- `SECURITY.md`: Disclosure process, email, 48h SLA — PASS
- `CHANGELOG.md`: v1.0.0 release notes, Keep a Changelog format — PASS
- `.gitignore`: Covers `.env*`, `node_modules`, `.vercel`, PEM keys, service accounts — PASS
- `.env.local`: NOT tracked by git (confirmed via `git ls-files`) — PASS

**CI/CD & publishing:**
- 5 GitHub Actions workflows (ci, release, publish-cli, publish-action, dify-plugin) — PASS
- CLI `package.json`: `"version": "0.1.0-beta.1"`, `"publishConfig": {"access": "public", "tag": "beta"}` — PASS

---

## Recommendations (non-blocking but important)

1. **Rate limiting on `/evaluate`** — This is the hot path (every SDK call hits it). Currently no rate limit. Add the same pattern from `/threat/log` (in-memory map, 60/min per key, upgradeable per tier).

2. **Structured logging** — 66 `console.log/error/warn` calls across route files. None leak secrets, but production should use a structured logger (Pino, Winston, or Vercel Log Drain) with `request_id` correlation.

3. **`/threat/route.ts` uses manual `verifyIdToken`** instead of the shared `verifyAuth()` helper. Works correctly but is inconsistent with the pattern in other files. Refactor to use `verifyAuth()`.

4. **Post-launch secret rotation** — After the public repo goes live, rotate: (a) the Firebase service account key, (b) the Neon Postgres password, (c) the MailerLite API key, (d) the Vercel OIDC token. These exist in your local `.env.local` and while they are NOT in git, assume they could have been exposed during the dev process with external testers.

5. **Audit logging for approval decisions** — `approvals/[id]/route.ts` PATCH updates approval status without writing an audit log entry. For a security product, every approval/denial should be immutably logged.

6. **Fire-and-forget writes** — `evaluate/route.ts` (line ~383) and `threat/log/route.ts` (line ~106) use `.catch()` to silently swallow Firestore/Postgres write failures. Consider a dead-letter queue so audit trail entries are never silently lost.

---

## Launch checklist (do these in order)

- [ ] **BLOCKER** — Add `verifyAuth()` + tenant-ownership check to all 24 unprotected dashboard endpoints
- [ ] **HIGH** — Remove mock admin key from `settings/page.tsx` line 41
- [ ] Rotate all secrets listed in recommendation #4
- [ ] Add rate limiting to `/evaluate` endpoint
- [ ] Run Karim's full cURL suite against staging to confirm no regressions
- [ ] Tag the commit, push to public GitHub repo
- [ ] `npm publish` the CLI (`@suprawall/cli@0.1.0-beta.1`)
- [ ] Announce on the channels from the GTM battleplan

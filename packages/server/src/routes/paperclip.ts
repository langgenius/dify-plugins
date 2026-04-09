// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import express, { Request, Response } from "express";
import { pool } from "../db";
import { adminAuth, gatekeeperAuth, AuthenticatedRequest } from "../auth";
import { getFirestore } from "../firebase";
import crypto from "crypto";
import { resolveTier, TieredRequest, tierLimitError, checkEvaluationLimit, recordEvaluation } from "../tier-guard";
import { TIER_LIMITS, Tier } from "../tier-config";
import { logger } from "../logger";
import { rateLimit } from "../rate-limit";

const router = express.Router();

// ---------------------------------------------------------------------------
// Startup guard — fail loudly if critical secrets are absent
// ---------------------------------------------------------------------------

if (!process.env.VAULT_ENCRYPTION_KEY) {
    logger.error("[Paperclip] VAULT_ENCRYPTION_KEY is not set. Vault operations will be disabled.");
}
if (!process.env.PAPERCLIP_WEBHOOK_SECRET) {
    logger.warn("[Paperclip] PAPERCLIP_WEBHOOK_SECRET is not set. Webhook endpoint will reject all requests.");
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Hash an API key with SHA-256 before DB storage.
 * All agent key lookups compare against the hash, never the raw value.
 */
function hashApiKey(rawKey: string): string {
    return crypto.createHash("sha256").update(rawKey).digest("hex");
}

/**
 * Validate that a URL is an allowed Paperclip API endpoint.
 * Blocks SSRF to internal/cloud-metadata addresses.
 */
function isAllowedPaperclipUrl(url: string): boolean {
    let parsed: URL;
    try {
        parsed = new URL(url);
    } catch {
        return false;
    }

    // Only allow https
    if (parsed.protocol !== "https:") return false;

    const hostname = parsed.hostname.toLowerCase();

    // Block RFC 1918, loopback, link-local, and cloud metadata
    const blocked = [
        /^localhost$/,
        /^127\./,
        /^10\./,
        /^172\.(1[6-9]|2\d|3[01])\./,
        /^192\.168\./,
        /^169\.254\./,       // link-local / AWS metadata
        /^::1$/,
        /^0\.0\.0\.0$/,
        /^fd[0-9a-f]{2}:/i,  // ULA IPv6
    ];

    if (blocked.some(r => r.test(hostname))) return false;

    // Allowlist: official Paperclip domains + self-hosted (any public HTTPS is allowed
    // for self-hosted, only internal IPs are blocked)
    return true;
}

// ---------------------------------------------------------------------------
// Role → credential scope mapping
// ---------------------------------------------------------------------------

export const ROLE_POLICIES: Record<string, string[]> = {
    ceo:         ["read:all"],
    marketing:   ["linkedin", "twitter", "google_ads"],
    engineering: ["github", "supabase", "vercel"],
    finance:     ["stripe"],
    hr:          ["read:all"],
    legal:       ["read:all"],
};

// ---------------------------------------------------------------------------
// Key generators (URL-safe base64, no padding)
// ---------------------------------------------------------------------------

const generateTempKey = (): string =>
    "sw_temp_" + crypto.randomBytes(24).toString("base64url");

const generateMasterKey = (): string =>
    "sw_admin_" + crypto.randomBytes(24).toString("base64url");

const generateAgentKey = (): string =>
    "ag_" + crypto.randomBytes(24).toString("base64url");

// ---------------------------------------------------------------------------
// STAGE 2: POST /v1/paperclip/onboard
// Fires when user runs: paperclipai plugin install suprawall-vault
// Unauthenticated — rate-limited aggressively (5 req/min per IP)
// ---------------------------------------------------------------------------

router.post(
    "/onboard",
    rateLimit({ max: 5, windowMs: 60_000, message: "Too many install attempts. Please wait before retrying." }),
    async (req: Request, res: Response) => {
        const { companyId, paperclipApiKey, paperclipVersion, agentCount, apiUrl } = req.body;

        if (!companyId || typeof companyId !== "string") {
            return res.status(400).json({ error: "Missing required field: companyId" });
        }

        const sanitizedCompanyId = companyId.slice(0, 100).trim();

        // Validate apiUrl against SSRF blocklist before making any outbound request
        const resolvedApiUrl = (typeof apiUrl === "string" && isAllowedPaperclipUrl(apiUrl))
            ? apiUrl.slice(0, 500)
            : (process.env.PAPERCLIP_API_URL || "https://api.paperclipai.com");

        try {
            // Check if company already onboarded
            const existing = await pool.query(
                "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
                [sanitizedCompanyId]
            );
            if (existing.rows.length > 0) {
                // Re-issue a fresh temp key instead of erroring out
                const tempKey = generateTempKey();
                const expiresAt = new Date(Date.now() + 72 * 60 * 60 * 1000);
                await pool.query(
                    `INSERT INTO paperclip_tokens (id, token, tenant_id, paperclip_company_id, tier, expires_at)
                     VALUES ($1, $2, $3, $4, $5, $6)`,
                    [crypto.randomUUID(), tempKey, existing.rows[0].tenant_id, sanitizedCompanyId, "developer", expiresAt]
                );
                return res.json({
                    status: "already_onboarded",
                    tempApiKey: tempKey,
                    activationUrl: `https://supra-wall.com/activate?token=${tempKey}`,
                    docsUrl: "https://docs.supra-wall.com/paperclip",
                });
            }
        } catch (e) {
            logger.error("[Paperclip] Onboard re-onboard check error:", { error: e });
            return res.status(500).json({ error: "Internal Server Error during onboarding" });
        }

        // Fetch agent list from Paperclip API if key provided; otherwise use agentCount
        let agents: Array<{ id: string; role: string; name?: string }> = [];

        if (paperclipApiKey && typeof paperclipApiKey === "string") {
            try {
                const resp = await fetch(`${resolvedApiUrl}/api/agents`, {
                    headers: { Authorization: `Bearer ${paperclipApiKey}` },
                    signal: AbortSignal.timeout(5000),
                });
                if (resp.ok) {
                    const data = await resp.json() as any;
                    const rawAgents = Array.isArray(data) ? data : (data.agents || []);
                    
                    // H-3: Validate and sanitize agent data from Paperclip API
                    // Ensure IDs are valid UUIDs and roles/names are sanitized strings
                    agents = rawAgents
                        .filter((a: any) => a && typeof a === "object")
                        .map((a: any) => {
                            const id = (typeof a.id === "string" && a.id.match(/^[0-9a-f-]{36}$/i)) ? a.id : crypto.randomUUID();
                            const role = (typeof a.role === "string" ? a.role.slice(0, 32).replace(/[^a-z0-9_-]/gi, "") : "agent").toLowerCase();
                            const name = (typeof a.name === "string" ? a.name.slice(0, 100).trim() : `${role} Agent`);
                            return { id, role, name };
                        });
                }
            } catch (e) {
                logger.warn("[Paperclip] Failed to fetch agents from Paperclip API:", e);
            }
        }

        // Determine the developer tier limits to enforce during onboard
        const developerLimits = TIER_LIMITS.developer;

        // Fall back: generate placeholder agents based on agentCount
        if (agents.length === 0 && typeof agentCount === "number" && agentCount > 0) {
            const defaultRoles = ["ceo", "marketing", "engineering", "finance", "hr"];
            const cappedCount = Math.min(agentCount, developerLimits.maxAgents);
            for (let i = 0; i < cappedCount; i++) {
                agents.push({ id: crypto.randomUUID(), role: defaultRoles[i % defaultRoles.length], name: `Agent ${i + 1}` });
            }
        }

        // At minimum create 1 placeholder
        if (agents.length === 0) {
            agents.push({ id: crypto.randomUUID(), role: "ceo", name: "CEO Agent" });
        }

        // Enforce tier limit: never create more agents than the developer tier allows on onboard
        if (agents.length > developerLimits.maxAgents) {
            logger.warn(
                `[Paperclip] Onboard truncated agent list from ${agents.length} to ${developerLimits.maxAgents} (developer tier limit)`
            );
            agents = agents.slice(0, developerLimits.maxAgents);
        }

        const tenantId = "pc_" + sanitizedCompanyId.replace(/[^a-zA-Z0-9-_]/g, "_").slice(0, 60);
        const masterKey = generateMasterKey();
        const tempKey = generateTempKey();
        const expiresAt = new Date(Date.now() + 72 * 60 * 60 * 1000); // 72h

        const client = await pool.connect();

        // Collect Firestore writes to execute AFTER the Postgres transaction commits.
        // This avoids leaving a partially-synced state when Firestore is temporarily unavailable.
        const firestoreWrites: Array<() => Promise<void>> = [];

        try {
            await client.query("BEGIN");

            // 1. Create tenant on developer tier
            await client.query(
                `INSERT INTO tenants (id, name, master_api_key, tier)
                 VALUES ($1, $2, $3, $4)
                 ON CONFLICT (id) DO NOTHING`,
                [tenantId, `Paperclip: ${sanitizedCompanyId}`, masterKey, "developer"]
            );

            // 2. Register Paperclip company
            await client.query(
                `INSERT INTO paperclip_companies (id, tenant_id, paperclip_company_id, agent_count, paperclip_version, api_url, status)
                 VALUES ($1, $2, $3, $4, $5, $6, 'active')`,
                [crypto.randomUUID(), tenantId, sanitizedCompanyId, agents.length, paperclipVersion || null, resolvedApiUrl]
            );

            // 3. Create agents with role-based policies
            const createdAgents: Array<{ id: string; name: string; role: string; apiKey: string }> = [];
            for (const agent of agents) {
                const agentId = agent.id || crypto.randomUUID();
                const agentApiKey = generateAgentKey();
                const agentKeyHash = hashApiKey(agentApiKey);
                const agentName = agent.name || `${agent.role} Agent`;
                const allowedCredentials = ROLE_POLICIES[agent.role?.toLowerCase()] ?? [];

                // Store hash, never the raw key
                await client.query(
                    `INSERT INTO agents (id, tenantid, name, apikeyhash, scopes)
                     VALUES ($1, $2, $3, $4, $5)
                     ON CONFLICT (id) DO NOTHING`,
                    [agentId, tenantId, agentName, agentKeyHash, allowedCredentials]
                );

                // Create ALLOW policies for each credential scope
                for (const credential of allowedCredentials) {
                    await client.query(
                        `INSERT INTO policies (tenantid, agentid, name, toolname, ruletype, description)
                         VALUES ($1, $2, $3, $4, $5, $6)
                         ON CONFLICT DO NOTHING`,
                        [
                            tenantId, agentId,
                            `Paperclip: ${credential} for ${agentName}`,
                            credential, "ALLOW",
                            `Auto-created by Paperclip onboard for role: ${agent.role}`
                        ]
                    );
                }

                // Defer Firestore write until after COMMIT
                const capturedId = agentId;
                const capturedName = agentName;
                const capturedRole = agent.role;
                const capturedScopes = allowedCredentials;
                firestoreWrites.push(async () => {
                    const db = getFirestore();
                    if (db) {
                        await db.collection("agents").doc(capturedId).set({
                            name: capturedName,
                            tenantId,
                            apiKeyHash: agentKeyHash, // store hash in Firestore too
                            scopes: capturedScopes,
                            role: capturedRole,
                            status: "active",
                            source: "paperclip",
                            createdAt: new Date(),
                        });
                    }
                });

                // Return the raw key ONCE to the caller — it won't be stored anywhere
                createdAgents.push({ id: agentId, name: agentName, role: agent.role, apiKey: agentApiKey });
            }

            // 4. Issue temporary API key
            await client.query(
                `INSERT INTO paperclip_tokens (id, token, tenant_id, paperclip_company_id, tier, expires_at)
                 VALUES ($1, $2, $3, $4, $5, $6)`,
                [crypto.randomUUID(), tempKey, tenantId, sanitizedCompanyId, "developer", expiresAt]
            );

            await client.query("COMMIT");

            logger.info(`[Paperclip] Onboarded company: ${sanitizedCompanyId} → tenant: ${tenantId}, agents: ${agents.length}`);

            // Execute Firestore writes after successful commit — failures are non-fatal
            for (const write of firestoreWrites) {
                write().catch(err =>
                    logger.error("[Paperclip] Firestore sync failed (non-fatal, reconcile later):", err)
                );
            }

            return res.status(201).json({
                status: "activation_required",
                message: "SupraWall Vault installed. Activate your free account at the URL below.",
                activationUrl: `https://supra-wall.com/activate?token=${tempKey}`,
                tempApiKey: tempKey,
                docsUrl: "https://docs.supra-wall.com/paperclip",
                syncedAgents: createdAgents.length,
                tier: "developer",
                tierLimits: {
                    maxAgents: TIER_LIMITS.developer.maxAgents,
                    maxEvaluationsPerMonth: TIER_LIMITS.developer.maxEvaluationsPerMonth,
                },
            });
        } catch (e) {
            await client.query("ROLLBACK");
            logger.error("[Paperclip] Onboard error:", { error: e });
            return res.status(500).json({ error: "Internal Server Error during onboarding" });
        } finally {
            client.release();
        }
    }
);

// ---------------------------------------------------------------------------
// STAGE 3: POST /v1/agent/invoke
// Hot path — called by every Paperclip agent to get scoped credentials.
// Auth: sw_temp_* key OR ag_* key (via gatekeeperAuth or temp key middleware)
// Returns a run token ID, NOT raw credentials (credentials resolved separately
// via GET /v1/vault/run-token/:runTokenId to avoid secret leakage in logs).
// ---------------------------------------------------------------------------

router.post(
    "/invoke",
    gatekeeperAuth,
    resolveTier,
    async (req: Request, res: Response) => {
        const tenantId = (req as AuthenticatedRequest).tenantId;
        const tierLimits = (req as TieredRequest).tierLimits!;

        const { agentId, companyId, role, runId } = req.body;

        // All fields are required and must be non-empty strings
        if (!agentId || typeof agentId !== "string" || agentId.trim() === "") {
            return res.status(400).json({ error: "Missing required field: agentId" });
        }
        if (!runId || typeof runId !== "string" || runId.trim() === "") {
            return res.status(400).json({ error: "Missing required field: runId" });
        }
        // companyId is validated against the authenticated tenant to prevent cross-tenant access
        if (companyId !== undefined && typeof companyId !== "string") {
            return res.status(400).json({ error: "Invalid field: companyId must be a string" });
        }
        // role is optional but when provided must be a safe string
        const sanitizedRole = typeof role === "string" ? role.slice(0, 64).replace(/[^a-zA-Z0-9_-]/g, "") : "invoke";

        try {
            // 1. Check evaluation limit
            const { allowed, current } = await checkEvaluationLimit(tenantId!, tierLimits);
            if (!allowed) {
                return res.status(402).json({
                    ...tierLimitError("Evaluation", current, tierLimits.maxEvaluationsPerMonth, (req as TieredRequest).tier),
                    status: 402,
                });
            }

            // 2. Verify agent belongs to this tenant
            const agentResult = await pool.query(
                "SELECT id, name, scopes, status FROM agents WHERE id = $1 AND tenantid = $2",
                [agentId.trim(), tenantId]
            );

            if (agentResult.rows.length === 0) {
                // If companyId provided, give a helpful hint — but never reveal cross-tenant data
                if (companyId) {
                    const companyResult = await pool.query(
                        "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
                        [companyId]
                    );
                    if (companyResult.rows.length === 0) {
                        return res.status(403).json({ error: "Agent not registered in SupraWall. Run: paperclipai plugin install suprawall-vault" });
                    }
                }
                return res.status(403).json({ error: "Agent not found for this tenant" });
            }

            const agent = agentResult.rows[0];
            if (agent.status !== "active") {
                return res.status(403).json({ error: `Agent is ${agent.status}` });
            }

            // 3. Load policies for this agent
            const policyResult = await pool.query(
                `SELECT toolname, ruletype FROM policies
                 WHERE tenantid = $1 AND (agentid = $2 OR agentid IS NULL)
                 ORDER BY priority ASC`,
                [tenantId, agentId]
            );

            const allowedTools = policyResult.rows
                .filter((p: any) => p.ruletype === "ALLOW")
                .map((p: any) => p.toolname as string);

            // 4. Resolve vault secrets — requires VAULT_ENCRYPTION_KEY to be set
            const encryptionKey = process.env.VAULT_ENCRYPTION_KEY;
            if (!encryptionKey) {
                logger.error("[Paperclip] Cannot resolve vault secrets: VAULT_ENCRYPTION_KEY not configured");
                return res.status(503).json({ error: "Vault not configured on this server. Contact support." });
            }

            const secretNames: string[] = [];
            const isPostgres = !!process.env.DATABASE_URL && !process.env.DATABASE_URL.includes("sqlite");

            if (isPostgres) {
                // PostgreSQL: use pgp_sym_decrypt — secure at-rest decryption
                const secretResult = await pool.query(
                    `SELECT vs.secret_name, pgp_sym_decrypt(vs.encrypted_value, $1) as value
                     FROM vault_secrets vs
                     JOIN vault_access_rules var ON var.secret_id = vs.id
                     WHERE var.tenant_id = $2 AND var.agent_id = $3
                       AND (vs.expires_at IS NULL OR vs.expires_at > NOW())
                     LIMIT 50`,
                    [encryptionKey, tenantId, agentId]
                );
                for (const row of secretResult.rows) {
                    secretNames.push(row.secret_name);
                }
            } else {
                // SQLite fallback for local dev only
                const secretResult = await pool.query(
                    `SELECT vs.secret_name
                     FROM vault_secrets vs
                     JOIN vault_access_rules var ON var.secret_id = vs.id
                     WHERE var.tenant_id = $1 AND var.agent_id = $2`,
                    [tenantId, agentId]
                );
                for (const row of secretResult.rows) {
                    secretNames.push(row.secret_name);
                }
            }

            // 5. Create run token — store ONLY the list of authorized secret names,
            // NOT the decrypted values. Actual secret values are fetched on-demand
            // via GET /v1/vault/run-token/:runTokenId when the agent needs them.
            const runTokenId = crypto.randomUUID();
            const ttlSeconds = 3600;
            const expiresAt = new Date(Date.now() + ttlSeconds * 1000);

            await pool.query(
                `INSERT INTO paperclip_run_tokens (id, tenant_id, agent_id, run_id, scoped_credentials, ttl_seconds, expires_at)
                 VALUES ($1, $2, $3, $4, $5, $6, $7)
                 ON CONFLICT (tenant_id, agent_id, run_id)
                 DO UPDATE SET issued_at = NOW(), expires_at = $7, revoked = FALSE, revoked_at = NULL`,
                // scoped_credentials stores the authorized secret names only, never decrypted values
                [runTokenId, tenantId, agentId, runId, JSON.stringify({ authorizedSecrets: secretNames }), ttlSeconds, expiresAt]
            );

            // 6. Audit log each authorized secret (not values)
            for (const secretName of secretNames) {
                await pool.query(
                    `INSERT INTO vault_access_log (tenant_id, agent_id, secret_name, tool_name, action, request_metadata)
                     VALUES ($1, $2, $3, $4, $5, $6)`,
                    [
                        tenantId, agentId, secretName.toUpperCase(),
                        sanitizedRole,
                        "ISSUED_RUN_TOKEN",
                        JSON.stringify({ runId, companyId: companyId || null, source: "paperclip_invoke" })
                    ]
                );
            }

            // 7. Record evaluation for metering
            await recordEvaluation(tenantId!, tierLimits);

            // Return the run token ID — agent fetches actual credentials via separate
            // authenticated call to /v1/vault/run-token/:runTokenId
            return res.status(202).json({
                status: "accepted",
                runTokenId,
                expiresAt: expiresAt.toISOString(),
                allowedTools,
                authorizedSecrets: secretNames,  // names only, no values
                resolveUrl: `${process.env.SUPRAWALL_PUBLIC_URL || "https://api.supra-wall.com"}/v1/vault/run-token/${runTokenId}`,
            });
        } catch (e) {
            logger.error("[Paperclip] Invoke error:", { error: e });
            return res.status(500).json({ error: "Internal Server Error" });
        }
    }
);

// ---------------------------------------------------------------------------
// GET /v1/vault/run-token/:runTokenId
// Called by agents after receiving runTokenId to fetch actual secret values.
// Auth: same agent API key that was used to invoke.
// One-time resolution: the token is marked consumed after first decryption.
// ---------------------------------------------------------------------------

router.get(
    "/run-token/:runTokenId",
    gatekeeperAuth,
    async (req: Request, res: Response) => {
        const tenantId = (req as AuthenticatedRequest).tenantId;
        const { runTokenId } = req.params;

        if (!runTokenId || typeof runTokenId !== "string") {
            return res.status(400).json({ error: "Invalid run token ID" });
        }

        const encryptionKey = process.env.VAULT_ENCRYPTION_KEY;
        if (!encryptionKey) {
            return res.status(503).json({ error: "Vault not configured on this server." });
        }

        try {
            // Look up the run token — must belong to this tenant, be valid, and not revoked
            const tokenResult = await pool.query(
                `SELECT id, agent_id, run_id, scoped_credentials, expires_at, revoked, consumed
                 FROM paperclip_run_tokens
                 WHERE id = $1 AND tenant_id = $2`,
                [runTokenId, tenantId]
            );

            if (tokenResult.rows.length === 0) {
                return res.status(404).json({ error: "Run token not found" });
            }

            const tokenRow = tokenResult.rows[0];

            if (tokenRow.revoked) {
                return res.status(410).json({ error: "Run token has been revoked" });
            }

            if (tokenRow.consumed) {
                return res.status(410).json({ error: "Run token has already been used" });
            }

            if (new Date(tokenRow.expires_at) < new Date()) {
                return res.status(410).json({ error: "Run token has expired" });
            }

            // Parse the authorized secret names from the stored JSON
            let authorizedSecrets: string[] = [];
            try {
                const parsed = typeof tokenRow.scoped_credentials === "string"
                    ? JSON.parse(tokenRow.scoped_credentials)
                    : tokenRow.scoped_credentials;
                authorizedSecrets = Array.isArray(parsed?.authorizedSecrets) ? parsed.authorizedSecrets : [];
            } catch {
                return res.status(500).json({ error: "Run token data corrupted" });
            }

            if (authorizedSecrets.length === 0) {
                return res.json({ credentials: {}, runId: tokenRow.run_id });
            }

            // Decrypt only the authorized secrets for this agent
            const isPostgres = !!process.env.DATABASE_URL && !process.env.DATABASE_URL.includes("sqlite");

            // Refuse to serve secrets on unencrypted SQLite in production
            if (!isPostgres && process.env.NODE_ENV === 'production') {
                logger.error("[Paperclip] Refusing to serve vault secrets over unencrypted SQLite in production");
                return res.status(503).json({
                    error: "Vault requires PostgreSQL in production. SQLite is for local development only."
                });
            }

            const credentials: Record<string, string> = {};

            if (isPostgres) {
                // Batch-fetch all authorized secrets in a single query
                const placeholders = authorizedSecrets.map((_, i) => `$${i + 3}`).join(", ");
                const secretResult = await pool.query(
                    `SELECT secret_name, pgp_sym_decrypt(encrypted_value, $1) as value
                     FROM vault_secrets
                     WHERE tenant_id = $2 AND secret_name = ANY(ARRAY[${placeholders}])
                       AND (expires_at IS NULL OR expires_at > NOW())`,
                    [encryptionKey, tenantId, ...authorizedSecrets]
                );
                for (const row of secretResult.rows) {
                    credentials[row.secret_name.toLowerCase()] = row.value;
                }
            } else {
                // SQLite local dev: plain storage (not suitable for production)
                const secretResult = await pool.query(
                    `SELECT secret_name, encrypted_value as value
                     FROM vault_secrets
                     WHERE tenant_id = $1 AND secret_name IN (${authorizedSecrets.map((_, i) => `$${i + 2}`).join(", ")})`,
                    [tenantId, ...authorizedSecrets]
                );
                for (const row of secretResult.rows) {
                    credentials[row.secret_name.toLowerCase()] = row.value;
                }
            }

            // Audit the resolution event
            await pool.query(
                `INSERT INTO vault_access_log (tenant_id, agent_id, secret_name, tool_name, action, request_metadata)
                 VALUES ($1, $2, $3, $4, $5, $6)`,
                [
                    tenantId, tokenRow.agent_id, "MULTIPLE",
                    "run_token_resolve",
                    "INJECTED",
                    JSON.stringify({ runTokenId, runId: tokenRow.run_id, secretCount: Object.keys(credentials).length })
                ]
            );

            // Mark token as consumed (one-time use only)
            await pool.query(
                `UPDATE paperclip_run_tokens
                 SET consumed = TRUE, consumed_at = NOW()
                 WHERE id = $1 AND tenant_id = $2`,
                [runTokenId, tenantId]
            );

            return res.json({
                credentials,
                runId: tokenRow.run_id,
                expiresAt: tokenRow.expires_at,
            });
        } catch (e) {
            logger.error("[Paperclip] Run token resolve error:", { error: e });
            return res.status(500).json({ error: "Internal Server Error" });
        }
    }
);

// ---------------------------------------------------------------------------
// STAGE 4: POST /v1/paperclip/webhooks
// Lifecycle events from Paperclip: agent.hired, agent.fired, run.completed
// Webhook signature is REQUIRED — requests without a valid signature are rejected.
// ---------------------------------------------------------------------------

router.post(
    "/webhooks",
    // Parse raw body for HMAC verification BEFORE express.json() re-serializes it
    express.raw({ type: "application/json" }),
    async (req: Request, res: Response) => {
        const webhookSecret = process.env.PAPERCLIP_WEBHOOK_SECRET;

        // Webhook signing is mandatory. Reject all requests when the secret is not configured.
        if (!webhookSecret) {
            logger.error("[Paperclip] PAPERCLIP_WEBHOOK_SECRET not set — rejecting all webhook traffic");
            return res.status(503).json({
                error: "Webhook signing not configured on this server. Set PAPERCLIP_WEBHOOK_SECRET and redeploy."
            });
        }

        const sig = (req.headers["x-paperclip-signature"] as string) ?? "";
        if (!sig) {
            return res.status(401).json({ error: "Missing X-Paperclip-Signature header" });
        }

        // Compute expected HMAC over the RAW body bytes (not re-serialized JSON)
        const rawBody = req.body as Buffer;
        const expectedSig = "sha256=" + crypto
            .createHmac("sha256", webhookSecret)
            .update(rawBody)
            .digest("hex");

        // Use timingSafeEqual to prevent timing oracle attacks
        const sigBuffer = Buffer.from(sig);
        const expectedBuffer = Buffer.from(expectedSig);
        const isValid =
            sigBuffer.length === expectedBuffer.length &&
            crypto.timingSafeEqual(sigBuffer, expectedBuffer);

        if (!isValid) {
            logger.warn("[Paperclip] Webhook signature mismatch — rejected");
            return res.status(401).json({ error: "Invalid webhook signature" });
        }

        // Parse the verified raw body as JSON
        let parsedBody: any;
        try {
            parsedBody = JSON.parse(rawBody.toString("utf-8"));
        } catch {
            return res.status(400).json({ error: "Invalid JSON body" });
        }

        const { event, agent, run } = parsedBody;

        if (!event || typeof event !== "string") {
            return res.status(400).json({ error: "Missing event type" });
        }

        logger.info(`[Paperclip] Webhook received: ${event}`);

        const client = await pool.connect();
        try {
            // ----------------------------------------------------------------
            // agent.hired → create agent + role-based policies
            // ----------------------------------------------------------------
            if (event === "agent.hired") {
                if (!agent?.id || !agent?.companyId) {
                    return res.status(400).json({ error: "Missing agent.id or agent.companyId" });
                }

                // Look up tenant via Paperclip company
                const companyResult = await client.query(
                    "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
                    [agent.companyId]
                );
                if (companyResult.rows.length === 0) {
                    return res.status(404).json({ error: "Company not found. Install the plugin first." });
                }

                const tenantId = companyResult.rows[0].tenant_id;

                // Tier limit check
                const tierResult = await client.query("SELECT tier FROM tenants WHERE id = $1", [tenantId]);
                const tier = tierResult.rows[0]?.tier || "developer";
                const limits = TIER_LIMITS[tier as Tier] || TIER_LIMITS.developer;

                if (isFinite(limits.maxAgents)) {
                    const countResult = await client.query(
                        "SELECT COUNT(*) FROM agents WHERE tenantid = $1",
                        [tenantId]
                    );
                    const currentCount = parseInt(countResult.rows[0].count, 10);
                    if (currentCount >= limits.maxAgents) {
                        return res.status(402).json({
                            ...tierLimitError("Agent", currentCount, limits.maxAgents, tier),
                            status: 402,
                        });
                    }
                }

                const agentId = agent.id;
                const agentApiKey = generateAgentKey();
                const agentKeyHash = hashApiKey(agentApiKey);
                const agentName = agent.name || `${agent.role || "Agent"} (Paperclip)`;
                const allowedCredentials = ROLE_POLICIES[(agent.role || "").toLowerCase()] ?? [];

                await client.query("BEGIN");

                // Store key hash, never the raw key
                await client.query(
                    `INSERT INTO agents (id, tenantid, name, apikeyhash, scopes)
                     VALUES ($1, $2, $3, $4, $5)
                     ON CONFLICT (id) DO UPDATE SET name = $3, scopes = $5`,
                    [agentId, tenantId, agentName, agentKeyHash, allowedCredentials]
                );

                for (const credential of allowedCredentials) {
                    await client.query(
                        `INSERT INTO policies (tenantid, agentid, name, toolname, ruletype, description)
                         VALUES ($1, $2, $3, $4, $5, $6)
                         ON CONFLICT DO NOTHING`,
                        [
                            tenantId, agentId,
                            `Paperclip: ${credential} for ${agentName}`,
                            credential, "ALLOW",
                            `Auto-created by agent.hired webhook for role: ${agent.role}`
                        ]
                    );
                }

                await client.query("COMMIT");

                // Firestore sync is non-fatal and runs after commit
                (async () => {
                    try {
                        const db = getFirestore();
                        if (db) {
                            await db.collection("agents").doc(agentId).set({
                                name: agentName,
                                tenantId,
                                apiKeyHash: agentKeyHash,
                                scopes: allowedCredentials,
                                role: agent.role,
                                status: "active",
                                source: "paperclip",
                                hiredAt: new Date(),
                            });
                        }
                    } catch (err) {
                        logger.error("[Paperclip] Firestore agent.hired sync failed:", err);
                    }
                })();

                logger.info(`[Paperclip] Agent hired: ${agentId} (${agent.role}) → tenant: ${tenantId}`);
                
                // H-1: Return the raw API key to Paperclip so it can be injected into the agent's environment
                return res.json({ 
                    success: true, 
                    event, 
                    agentId, 
                    agentApiKey, // Raw key returned ONCE
                    credentialsGranted: allowedCredentials 
                });
            }

            // ----------------------------------------------------------------
            // agent.fired → delete agent, revoke all tokens
            // ----------------------------------------------------------------
            if (event === "agent.fired") {
                if (!agent?.id || !agent?.companyId) {
                    return res.status(400).json({ error: "Missing agent.id or agent.companyId" });
                }

                // Verify the company belongs to one of our tenants
                const companyResult = await client.query(
                    "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
                    [agent.companyId]
                );
                if (companyResult.rows.length === 0) {
                    return res.status(404).json({ error: "Company not found" });
                }

                const tenantId = companyResult.rows[0].tenant_id;

                await client.query("BEGIN");

                // Revoke all run tokens immediately
                await client.query(
                    `UPDATE paperclip_run_tokens
                     SET revoked = TRUE, revoked_at = NOW()
                     WHERE agent_id = $1 AND tenant_id = $2 AND revoked = FALSE`,
                    [agent.id, tenantId]
                );

                // Delete vault access rules
                await client.query(
                    "DELETE FROM vault_access_rules WHERE tenant_id = $1 AND agent_id = $2",
                    [tenantId, agent.id]
                );

                // Delete policies
                await client.query(
                    "DELETE FROM policies WHERE tenantid = $1 AND agentid = $2",
                    [tenantId, agent.id]
                );

                // Soft-delete agent (mark inactive rather than hard-delete for audit continuity)
                await client.query(
                    "UPDATE agents SET status = 'revoked' WHERE id = $1 AND tenantid = $2",
                    [agent.id, tenantId]
                );

                await client.query("COMMIT");

                // Audit log the revocation — after commit, non-fatal
                pool.query(
                    `INSERT INTO vault_access_log (tenant_id, agent_id, secret_name, tool_name, action, request_metadata)
                     VALUES ($1, $2, $3, $4, $5, $6)`,
                    [
                        tenantId, agent.id, "ALL_CREDENTIALS",
                        "agent.fired",
                        "REVOKED",
                        JSON.stringify({ reason: "agent.fired webhook", companyId: agent.companyId })
                    ]
                ).catch(err => logger.error("[Paperclip] Failed to write revocation audit log:", err));

                // Firestore sync is non-fatal
                (async () => {
                    try {
                        const db = getFirestore();
                        if (db) {
                            await db.collection("agents").doc(agent.id).update({ status: "revoked", firedAt: new Date() });
                        }
                    } catch (err) {
                        logger.error("[Paperclip] Firestore agent.fired sync failed:", err);
                    }
                })();

                logger.info(`[Paperclip] Agent fired: ${agent.id} → all tokens revoked`);
                return res.json({ success: true, event, agentId: agent.id, tokensRevoked: true });
            }

            // ----------------------------------------------------------------
            // run.completed → revoke scoped run token
            // Validate that the run belongs to this company's tenant
            // ----------------------------------------------------------------
            if (event === "run.completed") {
                const runId = run?.id || agent?.runId;
                if (!runId) {
                    return res.status(400).json({ error: "Missing run.id or agent.runId" });
                }

                // Resolve tenant from the company to prevent cross-tenant revocation
                const companyId = agent?.companyId || run?.companyId;
                if (!companyId) {
                    return res.status(400).json({ error: "Missing companyId to validate run ownership" });
                }

                const companyResult = await client.query(
                    "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
                    [companyId]
                );
                if (companyResult.rows.length === 0) {
                    return res.status(404).json({ error: "Company not found" });
                }

                const tenantId = companyResult.rows[0].tenant_id;

                // Revoke only within the verified tenant scope
                const result = await client.query(
                    `UPDATE paperclip_run_tokens
                     SET revoked = TRUE, revoked_at = NOW()
                     WHERE run_id = $1 AND tenant_id = $2 AND revoked = FALSE
                     RETURNING id, agent_id, tenant_id`,
                    [runId, tenantId]
                );

                logger.info(`[Paperclip] Run completed: ${runId} → ${result.rowCount} token(s) revoked`);
                return res.json({ success: true, event, runId, tokensRevoked: result.rowCount });
            }

            // Unknown event — accept gracefully (future-proof for new Paperclip event types)
            logger.info(`[Paperclip] Unknown webhook event: ${event} — ignoring`);
            return res.json({ success: true, event, message: "Event received but not handled" });

        } catch (e) {
            await client.query("ROLLBACK").catch(() => {});
            logger.error(`[Paperclip] Webhook error (${event}):`, { error: e });
            return res.status(500).json({ error: "Internal Server Error" });
        } finally {
            client.release();
        }
    }
);

// ---------------------------------------------------------------------------
// GET /v1/paperclip/status — Check integration status for a company
// ---------------------------------------------------------------------------

router.get(
    "/status",
    gatekeeperAuth,
    rateLimit({ max: 5, windowMs: 60_000, message: "Too many status checks. Please wait." }),
    async (req: Request, res: Response) => {
        try {
        const tenantId = (req as AuthenticatedRequest).tenantId;

        const [companyResult, agentResult, tokenResult] = await Promise.all([
            pool.query("SELECT * FROM paperclip_companies WHERE tenant_id = $1", [tenantId]),
            pool.query("SELECT COUNT(*) FROM agents WHERE tenantid = $1", [tenantId]),
            pool.query(
                "SELECT COUNT(*) FROM paperclip_run_tokens WHERE tenant_id = $1 AND revoked = FALSE AND expires_at > NOW()",
                [tenantId]
            ),
        ]);

        return res.json({
            company: companyResult.rows[0] || null,
            agentCount: parseInt(agentResult.rows[0].count, 10),
            activeRunTokens: parseInt(tokenResult.rows[0].count, 10),
        });
    } catch (e) {
        logger.error("[Paperclip] Status error:", { error: e });
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

export default router;

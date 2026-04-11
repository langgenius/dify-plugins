// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Router, Request, Response } from "express";
import { pool } from "../db";
import { adminAuth, gatekeeperAuth, AuthenticatedRequest } from "../auth";
import { resolveTier, TieredRequest, tierLimitError } from "../tier-guard";
import { logger } from "../logger";
import { validate, CreateVaultSecretSchema } from "../validation";

const router = Router();

const SECRET_NAME_PATTERN = /^[A-Z][A-Z0-9_]{2,63}$/;

const REDOS_PATTERN = /(\+\+|\*\*|\+\*|\*\+|\{\d+,\d*\}\{|\(\?(?![:=!<]))/;
const MAX_PATTERN_LENGTH = 200;

function safePatternTest(pattern: string, subject: string): boolean {
    if (pattern.length > MAX_PATTERN_LENGTH || REDOS_PATTERN.test(pattern)) {
        return pattern === subject;
    }
    try {
        return new RegExp(pattern).test(subject);
    } catch {
        return pattern === subject;
    }
}

/**
 * Audit log helper for Vault Access
 */
async function logVaultAccess(tenantId: string, agentId: string, secretName: string, toolName: string, action: string, metadata: Record<string, unknown> = {}) {
    try {
        await pool.query(
            `INSERT INTO vault_access_log (tenant_id, agent_id, secret_name, tool_name, action, request_metadata)
             VALUES ($1, $2, $3, $4, $5, $6)`,
            [tenantId, agentId, secretName, toolName || "direct", action, JSON.stringify(metadata)]
        );
    } catch (err) {
        logger.error("Failed to log vault access:", err);
    }
}

/**
 * Shared logic for secret resolution (JIT hydration)
 */
async function handleResolve(req: Request, res: Response) {
    const authReq = req as AuthenticatedRequest;
    const agent = authReq.agent;
    const tenantId = authReq.tenantId;
    
    if (!agent || !tenantId) {
        return res.status(401).json({ error: "Unauthorized: Agent or Tenant not resolved" });
    }

    const agentId = agent.id;
    const secretName = req.body.secretName;
    const { toolName } = req.body;

    try {
        if (!secretName) {
            return res.status(400).json({ error: "Missing required field: secretName" });
        }

        // 2. Resolve Secret (PGP Decrypt)
        const secretResult = await pool.query(
            `SELECT id, expires_at, pgp_sym_decrypt(encrypted_value, $1) as value
             FROM vault_secrets
             WHERE tenant_id = $2 AND secret_name = $3`,
            [process.env.VAULT_ENCRYPTION_KEY, tenantId, secretName]
        );

        if (secretResult.rows.length === 0) {
            await logVaultAccess(tenantId, agentId, secretName, toolName, "NOT_FOUND");
            return res.status(404).json({ error: "Secret not found" });
        }

        const secret = secretResult.rows[0];

        // 3. Expiry Check
        if (secret.expires_at && new Date(secret.expires_at) < new Date()) {
            await logVaultAccess(tenantId, agentId, secretName, toolName, "EXPIRED");
            return res.status(410).json({ error: "Secret expired" });
        }

        // 4. Access Rule Check
        const ruleResult = await pool.query(
            `SELECT allowed_tools FROM vault_access_rules
             WHERE tenant_id = $1 AND agent_id = $2 AND secret_id = $3`,
            [tenantId, agentId, secret.id]
        );

        if (ruleResult.rows.length === 0) {
            await logVaultAccess(tenantId, agentId, secretName, toolName, "DENIED", { reason: "Missing rule" });
            return res.status(403).json({ error: "Access denied: Agent has no rule for this secret" });
        }

        const rule = ruleResult.rows[0];

        // 5. Tool-specific check (if provided)
        if (toolName) {
            const allowedTools: string[] = rule.allowed_tools || [];
            const isAllowed = allowedTools.length === 0 || allowedTools.some(p => safePatternTest(p, toolName));

            if (!isAllowed) {
                await logVaultAccess(tenantId, agentId, secretName, toolName, "DENIED", { reason: "Tool mismatch" });
                return res.status(403).json({ error: `Tool '${toolName}' not allowed for this secret` });
            }
        }

        // 6. Success
        await logVaultAccess(tenantId, agentId, secretName, toolName, "INJECTED");
        res.json({
            success: true,
            secret_name: secretName,
            value: secret.value
        });
    } catch (e: any) {
        logger.error("[Vault Resolve] Internal Error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
}

// POST /v1/vault/secrets — Create a secret (Auth required)
router.post("/secrets", adminAuth, resolveTier, validate(CreateVaultSecretSchema), async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { secretName, secretValue, description, expiresAt, assignedAgents } = req.body;
        const tierLimits = (req as TieredRequest).tierLimits!;

        if (!tenantId || !secretName || !secretValue) {
            return res.status(400).json({ error: "Missing required fields: tenantId, secretName, secretValue" });
        }

        // --- Tier Enforcement: Vault Secret Count ---
        if (isFinite(tierLimits.maxVaultSecrets)) {
            const countResult = await pool.query(
                "SELECT COUNT(*) FROM vault_secrets WHERE tenant_id = $1",
                [tenantId]
            );
            const currentCount = parseInt(countResult.rows[0].count, 10);
            if (currentCount >= tierLimits.maxVaultSecrets) {
                return res.status(403).json(
                    tierLimitError("Vault secrets", currentCount, tierLimits.maxVaultSecrets)
                );
            }
        }

        if (!SECRET_NAME_PATTERN.test(secretName)) {
            return res.status(400).json({ error: "secretName must match pattern: ^[A-Z][A-Z0-9_]{2,63}$" });
        }

        if (!process.env.VAULT_ENCRYPTION_KEY) {
            return res.status(500).json({ error: "Vault encryption key not configured" });
        }

        const result = await pool.query(
            `INSERT INTO vault_secrets (tenant_id, secret_name, encrypted_value, description, expires_at, assigned_agents)
             VALUES ($1, $2, pgp_sym_encrypt($3, $4), $5, $6, $7)
             RETURNING id, secret_name`,
            [tenantId, secretName, secretValue, process.env.VAULT_ENCRYPTION_KEY, description || null, expiresAt || null, assignedAgents || []]
        );

        const secret = result.rows[0];

        // --- Rule Synchronization (parameterized) ---
        if (Array.isArray(assignedAgents) && assignedAgents.length > 0) {
            for (const agId of assignedAgents) {
                await pool.query(
                    `INSERT INTO vault_access_rules (tenant_id, agent_id, secret_id, allowed_tools, max_uses_per_hour, requires_approval)
                     VALUES ($1, $2, $3, '{}', 100, false)
                     ON CONFLICT (tenant_id, agent_id, secret_id) DO NOTHING`,
                    [tenantId, agId, secret.id]
                );
            }
        }

        res.status(201).json(secret);
    } catch (e: any) {
        if (e.code === "23505") {
            return res.status(409).json({ error: `Secret '${req.body.secretName}' already exists` });
        }
        logger.error("Vault create secret error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST /v1/vault/secrets/bulk — Bulk import secrets (Auth required)
router.post("/secrets/bulk", adminAuth, resolveTier, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { secrets } = req.body;
        const tierLimits = (req as TieredRequest).tierLimits!;

        if (!secrets || !Array.isArray(secrets)) {
            return res.status(400).json({ error: "Missing or invalid 'secrets' array" });
        }

        if (secrets.length > 100) {
            return res.status(400).json({ error: "Bulk import limit is 100 secrets per request." });
        }

        const stats = { created: [] as any[], skipped: [] as any[], errors: [] as any[] };

        // Check tier limit once before the loop (prevent race condition)
        const countRes = await pool.query("SELECT COUNT(*) FROM vault_secrets WHERE tenant_id = $1", [tenantId]);
        const currentCount = parseInt(countRes.rows[0].count, 10);
        const remaining = tierLimits.maxVaultSecrets - currentCount;

        if (remaining <= 0) {
            return res.status(403).json({
                error: "Tier secret limit reached",
                maxSecrets: tierLimits.maxVaultSecrets,
                currentCount: currentCount
            });
        }

        let processedCount = 0;

        for (const item of secrets) {
            const { secretName, secretValue, description, expiresAt, assignedAgents } = item;

            if (!SECRET_NAME_PATTERN.test(secretName)) {
                stats.errors.push({ secretName, error: "Invalid name format" });
                continue;
            }

            // Stop processing if we've hit tier limit
            if (processedCount >= remaining) {
                stats.errors.push({ secretName, error: "Tier limit reached" });
                break; 
                }

            try {
                const result = await pool.query(
                    `INSERT INTO vault_secrets (tenant_id, secret_name, encrypted_value, description, expires_at, assigned_agents)
                     VALUES ($1, $2, pgp_sym_encrypt($3, $4), $5, $6, $7)
                     RETURNING id, secret_name`,
                    [tenantId, secretName, secretValue, process.env.VAULT_ENCRYPTION_KEY, description || null, expiresAt || null, assignedAgents || []]
                );

                const secret = result.rows[0];

                // Sync rules
                if (Array.isArray(assignedAgents)) {
                    for (const agId of assignedAgents) {
                        await pool.query(
                            `INSERT INTO vault_access_rules (tenant_id, agent_id, secret_id, allowed_tools, max_uses_per_hour)
                             VALUES ($1, $2, $3, '{}', 100)
                             ON CONFLICT DO NOTHING`,
                            [tenantId, agId, secret.id]
                        );
                    }
                }

                stats.created.push(secret);
                processedCount++;
            } catch (e: any) {
                if (e.code === "23505") {
                    stats.skipped.push({ secretName });
                } else {
                    stats.errors.push({ secretName, error: e.message });
                }
            }
        }

        res.status(207).json(stats);
    } catch (e: any) {
        logger.error("Vault bulk import error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// PATCH /v1/vault/secrets/:id — Update secret metadata and assignments (Auth required)
router.patch("/secrets/:id", adminAuth, resolveTier, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { secretName, description, expiresAt, assignedAgents } = req.body;

        const result = await pool.query(
            `UPDATE vault_secrets
             SET secret_name = COALESCE($1, secret_name),
                 description = COALESCE($2, description),
                 expires_at = $3,
                 assigned_agents = COALESCE($4, assigned_agents)
             WHERE id = $5 AND tenant_id = $6
             RETURNING id, secret_name`,
            [secretName || null, description || null, expiresAt || null, assignedAgents || null, id, tenantId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: "Secret not found" });
        }

        const secret = result.rows[0];

        // Sync rules (parameterized)
        if (Array.isArray(assignedAgents) && assignedAgents.length > 0) {
            for (const agId of assignedAgents) {
                await pool.query(
                    `INSERT INTO vault_access_rules (tenant_id, agent_id, secret_id, allowed_tools, max_uses_per_hour, requires_approval)
                     VALUES ($1, $2, $3, '{}', 100, false)
                     ON CONFLICT (tenant_id, agent_id, secret_id) DO NOTHING`,
                    [tenantId, agId, secret.id]
                );
            }
        }

        res.json(secret);
    } catch (e: any) {
        logger.error("Vault patch error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// GET /v1/vault/secrets — List secrets (Auth required)
router.get("/secrets", adminAuth, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const result = await pool.query(
            `SELECT id, secret_name, description, expires_at, last_rotated_at, created_at, assigned_agents
             FROM vault_secrets WHERE tenant_id = $1 ORDER BY created_at DESC`,
            [tenantId]
        );
        res.json(result.rows);
    } catch (e) {
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// DELETE /v1/vault/secrets/:id — Delete secret (Auth required)
router.delete("/secrets/:id", adminAuth, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        await pool.query("DELETE FROM vault_secrets WHERE id = $1 AND tenant_id = $2", [id, tenantId]);
        res.json({ deleted: true });
    } catch (e) {
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// Rules & Logs
router.post("/rules", adminAuth, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { agentId, secretId, allowedTools, maxUsesPerHour, requiresApproval } = req.body;
        const result = await pool.query(
            `INSERT INTO vault_access_rules (tenant_id, agent_id, secret_id, allowed_tools, max_uses_per_hour, requires_approval)
             VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
            [tenantId, agentId, secretId, allowedTools || [], maxUsesPerHour ?? 100, requiresApproval ?? false]
        );
        res.status(201).json(result.rows[0]);
    } catch (e) { res.status(500).json({ error: "Internal Server Error" }); }
});

router.get("/rules", adminAuth, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { agentId } = req.query;
        const result = await pool.query(
            `SELECT r.*, s.secret_name FROM vault_access_rules r
             JOIN vault_secrets s ON r.secret_id = s.id
             WHERE r.tenant_id = $1 AND ($2::text IS NULL OR r.agent_id = $2)
             ORDER BY r.created_at DESC`,
            [tenantId, agentId || null]
        );
        res.json(result.rows);
    } catch (e) { res.status(500).json({ error: "Internal Server Error" }); }
});

router.delete("/rules/:id", adminAuth, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        await pool.query("DELETE FROM vault_access_rules WHERE id = $1 AND tenant_id = $2", [id, tenantId]);
        res.json({ deleted: true });
    } catch (e) { res.status(500).json({ error: "Internal Server Error" }); }
});

router.get("/log", adminAuth, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId!;
        const { limit = 50, offset = 0 } = req.query;
        const result = await pool.query(
            `SELECT * FROM vault_access_log WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`,
            [tenantId, limit, offset]
        );
        res.json(result.rows);
    } catch (e) { res.status(500).json({ error: "Internal Server Error" }); }
});

// Resolution Endpoints
router.post("/resolve", gatekeeperAuth, handleResolve);
router.post("/", gatekeeperAuth, handleResolve);

export default router;

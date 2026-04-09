// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import express, { Request, Response } from "express";
import { pool } from "../db";
import { adminAuth, AuthenticatedRequest } from "../auth";
import { getFirestore, logToFirestore } from "../firebase";
import crypto from "crypto";
import { resolveTier, TieredRequest, tierLimitError } from "../tier-guard";
import { logger } from "../logger";
import { validate, CreateAgentSchema } from "../validation";

const router = express.Router();

const generateApiKey = () => {
    return "ag_" + crypto.randomBytes(24).toString("base64")
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
};

// GET all agents for a tenant (Admin Protected)
router.get("/", adminAuth, async (req: Request, res: Response) => {
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId;
        const result = await pool.query(
            "SELECT * FROM agents WHERE tenantid = $1 ORDER BY createdat DESC",
            [tenantId]
        );
        res.json(result.rows);
    } catch (e) {
        logger.error("[Agents] Failed to fetch agents:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST create agent (Admin Protected + Tier Enforced)
router.post("/", adminAuth, resolveTier, validate(CreateAgentSchema), async (req: Request, res: Response) => {
    const client = await pool.connect();
    try {
        const tenantId = (req as AuthenticatedRequest).tenantId;
        const { name, scopes, guardrails } = req.body;
        const tierLimits = (req as TieredRequest).tierLimits!;

        if (!name) return res.status(400).json({ error: "Missing agent name" });

        // --- Tier Enforcement: Agent Count ---
        if (isFinite(tierLimits.maxAgents)) {
            const countResult = await pool.query(
                "SELECT COUNT(*) FROM agents WHERE tenantid = $1",
                [tenantId]
            );
            const currentCount = parseInt(countResult.rows[0].count, 10);
            if (currentCount >= tierLimits.maxAgents) {
                return res.status(403).json(
                    tierLimitError("Agent", currentCount, tierLimits.maxAgents)
                );
            }
        }

        const agentId = crypto.randomUUID();
        const apiKey = generateApiKey();
        const apiKeyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
        const finalScopes = scopes || ["*:*"];

        // Guardrails mapping
        const max_cost_usd = guardrails?.budget?.limitUsd || 10;
        const budget_alert_usd = max_cost_usd * 0.8;
        const max_iterations = guardrails?.max_iterations || 50;

        await client.query("BEGIN");

        // 1. Save to Postgres
        const pgResult = await client.query(
            `INSERT INTO agents (id, tenantid, name, apikeyhash, scopes, max_cost_usd, budget_alert_usd, max_iterations)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
             RETURNING id, name, createdat`,
            [agentId, tenantId, name, apiKeyHash, finalScopes, max_cost_usd, budget_alert_usd, max_iterations]
        );

        // 2. Save Blocked Tools as Policies
        if (guardrails?.blockedTools && Array.isArray(guardrails.blockedTools)) {
            for (const tool of guardrails.blockedTools) {
                await client.query(
                    "INSERT INTO policies (tenantid, agentid, name, toolname, ruletype) VALUES ($1, $2, $3, $4, $5)",
                    [tenantId, agentId, `Blocked via API: ${tool}`, tool, "DENY"]
                );
            }
        }

        // 3. Save Custom Policies
        if (guardrails?.policies && Array.isArray(guardrails.policies)) {
            for (const policy of guardrails.policies) {
                await client.query(
                    "INSERT INTO policies (tenantid, agentid, name, toolname, ruletype, description) VALUES ($1, $2, $3, $4, $5, $6)",
                    [tenantId, agentId, policy.name, policy.toolName, policy.ruleType || "DENY", policy.description]
                );
            }
        }

        // 4. Save Vault Access Rules
        if (guardrails?.vault && Array.isArray(guardrails.vault)) {
            for (const rule of guardrails.vault) {
                // Look up secret ID by name
                const secretRes = await client.query(
                    "SELECT id FROM vault_secrets WHERE tenant_id = $1 AND secret_name = $2",
                    [tenantId, rule.secretName]
                );
                
                if (secretRes.rows.length > 0) {
                    const secretId = secretRes.rows[0].id;
                    await client.query(
                        `INSERT INTO vault_access_rules (tenant_id, agent_id, secret_id, allowed_tools, requires_approval)
                         VALUES ($1, $2, $3, $4, $5)`,
                        [tenantId, agentId, secretId, rule.allowedTools || [], rule.requiresApproval || false]
                    );
                }
            }
        }

        // 5. Save to Firestore (for gatekeeper runtime)
        const db = getFirestore();
        if (db) {
            await db.collection("agents").doc(agentId).set({
                name,
                tenantId,
                apiKeyHash,
                scopes: finalScopes,
                status: "active",
                createdAt: new Date(),
                userId: tenantId,
            });
        }

        await client.query("COMMIT");

        res.status(201).json({
            id: agentId,
            apiKey: apiKey,
            name: name,
            createdAt: pgResult.rows[0].createdat
        });
    } catch (e) {
        await client.query("ROLLBACK");
        logger.error("[Agents] Create error:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    } finally {
        client.release();
    }
});

// GET single agent (Admin Protected)
router.get("/:id", adminAuth, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const tenantId = (req as AuthenticatedRequest).tenantId;
        const result = await pool.query("SELECT * FROM agents WHERE id = $1 AND tenantid = $2", [id, tenantId]);
        if (result.rows.length === 0) return res.status(404).json({ error: "Agent not found" });
        res.json(result.rows[0]);
    } catch (e) {
        logger.error("[Agents] Fetch agent error:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// DELETE single agent (Admin Protected)
router.delete("/:id", adminAuth, async (req: Request, res: Response) => {
    const client = await pool.connect();
    try {
        const id = req.params.id as string;
        const tenantId = (req as AuthenticatedRequest).tenantId as string;

        await client.query("BEGIN");

        // 1. Delete from Postgres
        const result = await client.query("DELETE FROM agents WHERE id = $1 AND tenantid = $2", [id, tenantId]);
        
        if (result.rowCount === 0) {
            await client.query("ROLLBACK");
            return res.status(404).json({ error: "Agent not found" });
        }

        // 2. Delete related policies
        await client.query("DELETE FROM policies WHERE agentid = $1 AND tenantid = $2", [id, tenantId]);

        const db = getFirestore();
        if (db) {
            await db.collection("agents").doc(id).delete();
        }

        await client.query("COMMIT");
        res.json({ success: true, message: "Agent revoked successfully" });
    } catch (e) {
        await client.query("ROLLBACK");
        logger.error("[Agents] Delete error:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    } finally {
        client.release();
    }
});

// PATCH agent config (Admin Protected)
router.patch("/:id/guardrails", adminAuth, async (req: Request, res: Response) => {
    try {
        const id = req.params.id as string;
        const tenantId = (req as AuthenticatedRequest).tenantId as string;
        const { budget, max_iterations, loop_detection } = req.body;

        const max_cost_usd = budget?.limitUsd;
        const budget_alert_usd = max_cost_usd ? max_cost_usd * 0.8 : undefined;

        const result = await pool.query(
            `UPDATE agents 
             SET max_cost_usd = COALESCE($1, max_cost_usd),
                 budget_alert_usd = COALESCE($2, budget_alert_usd),
                 max_iterations = COALESCE($3, max_iterations),
                 loop_detection = COALESCE($4, loop_detection)
             WHERE id = $5 AND tenantid = $6
             RETURNING *`,
            [max_cost_usd, budget_alert_usd, max_iterations, loop_detection, id, tenantId]
        );

        if (result.rows.length === 0) return res.status(404).json({ error: "Agent not found" });
        res.json(result.rows[0]);
    } catch (e) {
        logger.error("[Agents] Guardrails update error:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST /v1/agents/:id/rotate-key — Regenerate API key (Admin Protected)
router.post("/:id/rotate-key", adminAuth, async (req: Request, res: Response) => {
    const client = await pool.connect();
    try {
        const id = req.params.id as string;
        const tenantId = (req as AuthenticatedRequest).tenantId as string;

        const newApiKey = generateApiKey();
        const newApiKeyHash = crypto.createHash('sha256').update(newApiKey).digest('hex');

        await client.query("BEGIN");

        const result = await client.query(
            "UPDATE agents SET apikeyhash = $1 WHERE id = $2 AND tenantid = $3 RETURNING id, name",
            [newApiKeyHash, id, tenantId]
        );

        if (result.rows.length === 0) {
            await client.query("ROLLBACK");
            return res.status(404).json({ error: "Agent not found" });
        }

        // Sync new key to Firestore so gatekeeper runtime uses the new key hash immediately
        const db = getFirestore();
        if (db) {
            await db.collection("agents").doc(id).update({ apiKeyHash: newApiKeyHash });
        }

        await client.query("COMMIT");

        res.json({
            id,
            apiKey: newApiKey,
            rotatedAt: new Date().toISOString()
        });
    } catch (e) {
        await client.query("ROLLBACK");
        logger.error("[Agents] Key rotation error:", { error: e });
        res.status(500).json({ error: "Internal Server Error" });
    } finally {
        client.release();
    }
});

export default router;

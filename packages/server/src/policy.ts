// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Request, Response } from "express";
import { pool } from "./db";
import { logger } from "./logger";
import { resolveVaultTokens, VaultResolutionResult } from "./vault";
import { logToFirestore, admin } from "./firebase";
import { scrubResponse } from "./scrubber";
import { getAgentById } from "./auth";
import { sendSlackNotification } from "./slack";
import { TIER_LIMITS, currentMonth } from "./tier-config";
import type { Tier } from "./tier-config";
import { checkEvaluationLimit, recordEvaluation } from "./tier-guard";
import { analyzeCall, type SemanticAnalysisResult } from "./semantic";
import { updateBaseline } from "./behavioral";
import { getDataEncryptionKey, encryptPayload } from "./gdpr";

export interface EvaluationRequest {
    agentId: string;
    toolName: string;
    arguments: any;
    tenantId?: string;
    delegationChain?: string[]; 
}

async function insertAuditLog(
    tenantid: string,
    agentid: string | undefined,
    toolname: string,
    args: any,
    decision: string,
    riskscore: number,
    cost_usd: number,
    metadata: any
) {
    if (!tenantid) return;
    try {
        const subjectId = metadata?.subjectId || "entire_tenant";
        const dataKey = await getDataEncryptionKey(tenantid, subjectId);
        
        const encryptedArguments = encryptPayload(args || {}, dataKey);
        
        await pool.query(
            "INSERT INTO audit_logs (tenantid, agentid, toolname, parameters, encrypted_arguments, subject_id, decision, riskscore, cost_usd, metadata) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
            [
                tenantid, 
                agentid || null, 
                toolname, 
                JSON.stringify(args || {}), // Keep legacy until fully migrated
                encryptedArguments, 
                subjectId,
                decision, 
                riskscore, 
                cost_usd, 
                JSON.stringify(metadata || {})
            ]
        );
    } catch (e) {
        logger.error("Failed to insert audit log", { error: e });
    }
}

export const evaluatePolicy = async (req: Request, res: Response) => {
    try {
        const authReq = req as any;
        const agent = authReq.agent;
        
        const { toolName, arguments: args } = req.body as EvaluationRequest;
        const agentId = agent?.id || req.body.agentId;
        const tenantId = agent?.tenantId || req.body.tenantId || "default-tenant";

        if (!agentId || !toolName) {
            return res.status(400).json({ error: "Missing agentId or toolName" });
        }

        // 0. Cost Estimation (Alignment with Dashboard Evaluator)
        const inputTokens = req.body.inputTokens || 0;
        const outputTokens = req.body.outputTokens || 0;
        const model = req.body.model || "gpt-4o-mini";
        
        const estimateActionCost = (inT: number, outT: number, mdl: string) => {
            if (inT > 0 || outT > 0) {
                const rates: any = { "gpt-4o": 0.005, "gpt-4o-mini": 0.00015, "claude": 0.003 };
                const rate = rates[Object.keys(rates).find(k => mdl.includes(k)) || "gpt-4o-mini"];
                return (inT / 1000 * rate) + (outT / 1000 * rate * 3);
            }
            return 0.0001; // minimal fallback for non-token actions
        };
        const estimatedCost = req.body.costUsd ?? estimateActionCost(inputTokens, outputTokens, model);

        // 0a. Resolve tenant tier
        // resolveTier middleware already ran at app.use("/v1", resolveTier) — use it.
        // Fall back to a fresh DB query only if not already on the request (defensive).
        let tenantTier: Tier = (authReq.tier as Tier) || "open_source";
        let tierLimits = authReq.tierLimits || TIER_LIMITS["open_source"];
        if (!authReq.tierLimits) {
            try {
                const tierResult = await pool.query("SELECT tier FROM tenants WHERE id = $1", [tenantId]);
                const rawTier = tierResult.rows[0]?.tier;
                const knownTiers: Tier[] = ['open_source', 'developer', 'team', 'business', 'enterprise'];
                tenantTier = knownTiers.includes(rawTier) ? rawTier : 'open_source';
                tierLimits = TIER_LIMITS[tenantTier];
            } catch { /* keep open_source default */ }
        }

        // 0b. Framework Plugin Enforcement
        const requestedFramework = (req.headers["x-suprawall-framework"] as string) || (req.body as any).framework || "langchain";
        if (tierLimits.frameworkPlugins !== "all") {
            const allowed = Array.isArray(tierLimits.frameworkPlugins) ? tierLimits.frameworkPlugins : [];
            if (!allowed.includes(requestedFramework.toLowerCase())) {
                return res.status(403).json({
                    decision: "DENY",
                    reason: `Framework '${requestedFramework}' is not supported on your current tier. Upgrade to Business for full SDK plugin support.`,
                    code: "FRAMEWORK_NOT_SUPPORTED",
                    upgradeUrl: "https://www.supra-wall.com/pricing",
                });
            }
        }

        // 0c. Monthly Evaluation Limit
        // Uses tenant_usage table via checkEvaluationLimit (same table as recordEvaluation).
        // open_source hard-stops at 5K; paid tiers allow overage.
        if (isFinite(tierLimits.maxEvaluationsPerMonth)) {
            const { allowed, current } = await checkEvaluationLimit(tenantId, tierLimits);
            if (!allowed) {
                return res.status(402).json({
                    decision: "DENY",
                    reason: `Monthly evaluation limit reached (${current.toLocaleString()}/${tierLimits.maxEvaluationsPerMonth.toLocaleString()}). Upgrade your plan to continue.`,
                    upgradeUrl: "https://www.supra-wall.com/pricing",
                    code: "TIER_LIMIT_EXCEEDED",
                });
            }
        }

        // 0. Budget Enforcement (Cloud/Enterprise only)
        if (tierLimits.budgetEnforcement) {
            const maxBudget = agent?.max_cost_usd || 10;
            const spendResult = await pool.query(
                "SELECT SUM(cost_usd) as total FROM audit_logs WHERE agentid = $1 AND decision = 'ALLOW'",
                [agentId]
            );
            const currentSpend = parseFloat(spendResult.rows[0].total || 0);

            if (currentSpend + estimatedCost >= maxBudget) {
                await insertAuditLog(
                    tenantId, agentId, toolName, args, "DENY", 100, 0,
                    { reason: "Budget exceeded", currentSpend, maxBudget }
                );

                return res.status(403).json({
                    decision: "DENY",
                    reason: `Budget exceeded: Current spend $${(currentSpend + estimatedCost).toFixed(2)} exceeds limit $${maxBudget.toFixed(2)}.`
                });
            }
        }

        // 0. Threat Detection (Blocking — returns DENY on match)
        const argsString = JSON.stringify(args || {});

        const THREAT_RULES: { type: string, severity: string, riskScore: number, labelPrefix: string, patterns: { pattern: RegExp, label?: string }[] }[] = [
            { type: "sql_injection", severity: "critical", riskScore: 100, labelPrefix: "SQL injection", patterns: [
                { pattern: /DROP\s+TABLE/i, label: "DROP TABLE" },
                { pattern: /DELETE\s+FROM/i, label: "DELETE FROM" },
                { pattern: /INSERT\s+INTO/i, label: "INSERT INTO" },
                { pattern: /UPDATE\s+\S+\s+SET/i, label: "UPDATE SET" },
                { pattern: /UNION\s+SELECT/i, label: "UNION SELECT" },
                { pattern: /OR\s+['"]?1['"]?\s*=\s*['"]?1/i, label: "OR 1=1" },
                { pattern: /'\s*OR\s+'[^']*'\s*=\s*'/i, label: "OR tautology" },
                { pattern: /;\s*--/i, label: "comment terminator" },
                { pattern: /'\s*;\s*DROP/i, label: "chained DROP" },
                { pattern: /EXEC(\s+|\()sp_/i, label: "EXEC stored procedure" },
                { pattern: /xp_cmdshell/i, label: "xp_cmdshell" },
            ]},
            { type: "prompt_injection", severity: "high", riskScore: 95, labelPrefix: "Prompt injection", patterns: [
                { pattern: /Ignore\s+(all\s+)?previous\s+instructions/i },
                { pattern: /System\s+bypass/i },
                { pattern: /You\s+are\s+now\s+(a|an|the)\s/i },
                { pattern: /Forget\s+(all\s+)?(your|previous)\s+instructions/i },
                { pattern: /IGNORE\s+PREVIOUS/i },
                { pattern: /Do\s+not\s+follow\s+(your|the|any)\s+(previous|original)/i },
                { pattern: /Override\s+(system|safety|security)/i },
                { pattern: /Disregard\s+(all|any|your)\s+(previous|prior|safety)/i },
                { pattern: /Act\s+as\s+if\s+you\s+have\s+no\s+restrictions/i },
                { pattern: /Reveal\s+(your|the)\s+(system\s+)?prompt/i },
            ]},
            { type: "xss_injection", severity: "high", riskScore: 95, labelPrefix: "XSS/script injection", patterns: [
                { pattern: /<script[\s>]/i },
                { pattern: /javascript\s*:/i },
                { pattern: /on(error|load|click|mouseover)\s*=/i },
                { pattern: /<iframe[\s>]/i },
                { pattern: /<img[^>]+onerror/i },
            ]},
            { type: "path_traversal", severity: "high", riskScore: 90, labelPrefix: "Path traversal", patterns: [
                { pattern: /\.\.[\/\\]/ },
            ]},
        ];

        for (const rule of THREAT_RULES) {
            for (const item of rule.patterns) {
                if (item.pattern.test(argsString)) {
                    const labelDesc = item.label ? `${rule.labelPrefix} pattern (${item.label})` : `${rule.labelPrefix} attempt`;
                    const logPattern = item.label || item.pattern.source || "path_traversal";
                    
                    logger.warn(`[ThreatEngine] ${labelDesc} blocked`, { agentId, toolName, pattern: logPattern });
                    
                    await pool.query(
                        "INSERT INTO threat_events (tenantid, agentid, event_type, severity, details) VALUES ($1, $2, $3, $4, $5)",
                        [tenantId, agentId, `${rule.type}_attempt`, rule.severity, JSON.stringify({ toolName, pattern: logPattern })]
                    ).catch(err => logger.error(`Failed to log ${rule.type} threat`, { error: err }));
                    
                    await insertAuditLog(
                        tenantId, agentId, toolName, args, "DENY", rule.riskScore, 0,
                        { reason: `Threat blocked: ${labelDesc}`, matchedRule: "threat_engine" }
                    );
                    
                    return res.status(403).json({
                        decision: "DENY",
                        reason: `Threat detected: ${labelDesc} blocked by SupraWall Threat Engine.`,
                        threatType: rule.type,
                    });
                }
            }
        }

        // 1. Gatekeeper: Scope Verification (Delegation Chain)
        const { delegationChain } = req.body as EvaluationRequest;
        const chain = delegationChain || [];
        const uniqueChain = Array.from(new Set([...chain, agentId]));

        for (const actorId of uniqueChain) {
            const actor = (agent && agent.id === actorId) ? agent : await getAgentById(actorId);
            
            if (!actor) {
                logger.warn(`[Gatekeeper] Actor ${actorId} in chain not found.`);
                continue; 
            }

            const scopes = actor.scopes || [];
            const isAllowedByScope = scopes.includes("*:*") || 
                                     scopes.includes(toolName) || 
                                     (toolName.includes(":") && scopes.includes(`${toolName.split(":")[0]}:*`));
            
            if (!isAllowedByScope) {
                await insertAuditLog(
                    tenantId, agentId, toolName, args, "DENY", 100, 0,
                    { reason: "Chain scope failure", actorId, requiredScope: toolName, agentScopes: scopes }
                );

                return res.status(403).json({ 
                    decision: "DENY", 
                    reason: `Unauthorized: Actor '${actorId}' in delegation chain lacks scope for '${toolName}'.` 
                });
            }
        }

        // 2. Policy Engine: Check complex rules in Postgres
        const result = await pool.query(
            "SELECT * FROM policies WHERE (tenantid = $1 OR tenantid = 'global')",
            [tenantId]
        );
        
        // Advanced matching in JS
        const toolMatches = (ruleTool: string, targetTool: string) => {
            if (!ruleTool || ruleTool === "*" || ruleTool === "" || ruleTool === targetTool) return true;
            if (ruleTool.includes("*")) {
                const regex = new RegExp("^" + ruleTool.replace(/\*/g, ".*") + "$");
                return regex.test(targetTool);
            }
            return false;
        };

        const policies = result.rows.filter(p => 
            toolMatches(p.toolname, toolName) &&
            (!p.agentid || p.agentid === agentId)
        ).sort((a, b) => a.priority - b.priority);

        let decision = "ALLOW";
        let matchedRule = "default";

        // Check DENY policies
        const denyRules = policies.filter((p) => p.ruletype && p.ruletype.toUpperCase() === "DENY");
        for (const rule of denyRules) {
            if (rule.condition) {
                try {
                    if (new RegExp(rule.condition).test(argsString)) {
                        decision = "DENY";
                        matchedRule = rule.name || "Unnamed Rule";
                        break;
                    }
                } catch (e) {
                    logger.error("[PolicyEngine] Invalid regex in policy:", { condition: rule.condition });
                }
            } else {
                decision = "DENY";
                matchedRule = rule.name || "Unnamed Rule";
                break;
            }
        }

        const response: any = {
            decision,
            reason: decision === "ALLOW" ? "No restrictions matched" : `Matched rule ${matchedRule}`,
        };

        // Check REQUIRE_APPROVAL policies
        if (decision !== "DENY") {
            const approvalRules = policies.filter((p) => p.ruletype && p.ruletype.toUpperCase() === "REQUIRE_APPROVAL");
            for (const rule of approvalRules) {
                let match = false;
                if (rule.condition) {
                    try {
                        if (new RegExp(rule.condition).test(argsString)) {
                            match = true;
                        }
                    } catch (e) {
                        logger.error("[PolicyEngine] Invalid regex in policy:", { condition: rule.condition });
                    }
                } else {
                    match = true;
                }

                if (match) {
                    decision = "REQUIRE_APPROVAL";
                    matchedRule = rule.name || "Unnamed Rule";
                    response.decision = decision;
                    response.reason = `Matched rule ${matchedRule}`;
                    break;
                }
            }

            if (decision === "REQUIRE_APPROVAL") {
                // Create approval request in DB
                try {
                    const approvalRes = await pool.query(
                        "INSERT INTO approval_requests (tenantid, agentid, toolname, parameters, metadata) VALUES ($1, $2, $3, $4, $5) RETURNING id",
                        [tenantId, agentId, toolName, JSON.stringify(args || {}), JSON.stringify({ matchedRule })]
                    );
                    const approvalId = approvalRes.rows[0].id;
                    
                    // Send Slack notification (Paid tiers only)
                    const agentDetails = await getAgentById(agentId);
                    if (tierLimits.slackApprovals && agentDetails?.slack_webhook) {
                        await sendSlackNotification(
                            agentDetails.slack_webhook,
                            agentDetails.name || agentId,
                            toolName,
                            args,
                            approvalId
                        );
                    }
                    
                    // Attach ID to response for tracking
                    response.approvalId = approvalId;
                } catch (err) {
                    logger.error("Failed to create approval request", { error: err, agentId, toolName });
                    // Fallback to DENY if we can't create the approval request
                    decision = "DENY";
                    matchedRule = "approval_system_error";
                    response.decision = decision;
                    response.reason = matchedRule;
                }
            }
        }

        // 3. Vault: Secret Resolution
        let resolvedArgs = args;
        let vaultResult: VaultResolutionResult | null = null;
        let hasVaultTokens = false;

        // argsString is already declared above
        hasVaultTokens = /\$SUPRAWALL_VAULT_[A-Z][A-Z0-9_]+/.test(argsString);

        if (hasVaultTokens && decision !== "DENY") {
            vaultResult = await resolveVaultTokens(tenantId, agentId, toolName, args);

            if (!vaultResult.success) {
                decision = "DENY";
                matchedRule = `vault:${vaultResult.errors.map(e => e.reason).join(",")}`;

                await insertAuditLog(
                    tenantId, agentId, toolName, args, decision, 95, 0,
                    { vaultErrors: vaultResult.errors }
                );

                return res.status(403).json({
                    decision: "DENY",
                    reason: `Vault access denied: ${vaultResult.errors.map(e => e.message).join("; ")}`,
                    vaultErrors: vaultResult.errors,
                });
            }

            resolvedArgs = vaultResult.resolvedArgs;
        }

        // 3b. Record evaluation usage (writes to tenant_usage, tracks overage)
        if (decision === "ALLOW") {
            recordEvaluation(tenantId, tierLimits).catch(err =>
                logger.error("[TierGuard] Failed to record evaluation:", { error: err, tenantId })
            );
        }

        // ── Layer 2: AI Semantic Analysis (Growth+ tiers only) ──
        let semanticResult: SemanticAnalysisResult | null = null;

        if (decision === "ALLOW" && tierLimits.semanticLayer !== 'none') {
            try {
                // Check for custom endpoint (enterprise)
                let customEndpoint: string | undefined;
                if (tierLimits.semanticLayer === 'custom') {
                    const epResult = await pool.query(
                        "SELECT endpoint_url FROM custom_model_endpoints WHERE tenant_id = $1 AND enabled = true",
                        [tenantId]
                    );
                    if (epResult.rows.length > 0) {
                        customEndpoint = epResult.rows[0].endpoint_url;
                    }
                }

                semanticResult = await analyzeCall({
                    tenantId,
                    agentId,
                    toolName,
                    args: resolvedArgs,
                    argsString: JSON.stringify(resolvedArgs),
                    delegationChain: chain,
                    semanticLayer: tierLimits.semanticLayer,
                    customEndpoint,
                });

                // Override decision if Layer 2 flags a threat
                if (semanticResult.decision === 'DENY') {
                    decision = "DENY";
                    matchedRule = `semantic:${semanticResult.reasoning}`;
                    response.decision = decision;
                    response.reason = `AI semantic analysis: ${semanticResult.reasoning}`;
                    response.semanticScore = semanticResult.semanticScore;
                } else if (semanticResult.decision === 'REQUIRE_APPROVAL') {
                    decision = "REQUIRE_APPROVAL";
                    matchedRule = `semantic:approval_required`;
                    response.decision = decision;
                    response.reason = `AI flagged for review: ${semanticResult.reasoning}`;
                    response.semanticScore = semanticResult.semanticScore;

                    // Create approval request for semantic flags
                    try {
                        const approvalRes = await pool.query(
                            "INSERT INTO approval_requests (tenantid, agentid, toolname, parameters, metadata) VALUES ($1, $2, $3, $4, $5) RETURNING id",
                            [tenantId, agentId, toolName, JSON.stringify(args || {}),
                             JSON.stringify({ matchedRule, semanticScore: semanticResult.semanticScore })]
                        );
                        response.approvalId = approvalRes.rows[0].id;
                    } catch (err) {
                        logger.error("[Layer2] Failed to create approval request", { error: err });
                        decision = "DENY";
                        response.decision = decision;
                        response.reason = "Semantic analysis flagged for review but approval system unavailable";
                    }
                } else if (semanticResult.decision === 'FLAG') {
                    // Don't change decision, but attach metadata
                    response.semanticFlag = true;
                    response.semanticScore = semanticResult.semanticScore;
                    response.semanticReasoning = semanticResult.reasoning;
                }
            } catch (err) {
                logger.error("[Layer2] Semantic analysis failed", { error: err });
                // NEVER block on Layer 2 failure — continue with Layer 1 decision
            }
        }

        // Update behavioral baseline (async, non-blocking, business+ only)
        if (decision === "ALLOW" &&
            (tierLimits.semanticLayer === 'behavioral' || tierLimits.semanticLayer === 'custom')) {
            updateBaseline(tenantId, agentId, toolName, resolvedArgs).catch(() => {});
        }

        // 4. Audit Logging
        const auditRecord = {
            tenantid: tenantId,
            agentid: agentId,
            toolname: toolName,
            parameters: args,
            decision,
            riskscore: decision === "DENY" ? 90 : (decision === "REQUIRE_APPROVAL" ? 60 : 10),
            cost_usd: decision === "ALLOW" ? estimatedCost : 0,
            metadata: {
                subjectId: req.body.subjectId || "entire_tenant",
                framework: requestedFramework,
                matchedRule,
                agentName: agent?.name,
                vaultInjected: hasVaultTokens,
                vaultSecrets: vaultResult?.injectedSecrets || [],
                ...(semanticResult ? {
                    semanticScore: semanticResult.semanticScore,
                    anomalyScore: semanticResult.anomalyScore,
                    semanticDecision: semanticResult.decision,
                    semanticLatencyMs: semanticResult.latencyMs,
                } : {}),
            }
        };

        await insertAuditLog(
            auditRecord.tenantid,
            auditRecord.agentid,
            auditRecord.toolname,
            auditRecord.parameters,
            auditRecord.decision,
            auditRecord.riskscore,
            auditRecord.cost_usd,
            auditRecord.metadata
        );

        // 5. Mirror to Firestore & Update Agent Stats
        const firestore = (admin as any)?.apps?.length > 0 ? admin.firestore() : null;
        if (firestore) {
            logToFirestore("audit_logs", auditRecord);

            // Update Agent cumulative stats for dashboard
            firestore.collection("agents").doc(agentId).update({
                totalCalls: admin.firestore.FieldValue.increment(1),
                totalSpendUsd: admin.firestore.FieldValue.increment(auditRecord.cost_usd),
                lastUsedAt: admin.firestore.FieldValue.serverTimestamp()
            }).catch((err: any) => logger.error("[Firestore] Agent update failed:", err));

            // Update User monthly usage
            firestore.collection("users").doc(tenantId).update({
                operationsThisMonth: admin.firestore.FieldValue.increment(1),
                lastUsedAt: admin.firestore.FieldValue.serverTimestamp(),
            }).catch(() => {});
        }

        if (hasVaultTokens && vaultResult?.success) {
            response.resolvedArguments = resolvedArgs;
            response.vaultInjected = true;
            response.injectedSecrets = vaultResult.injectedSecrets;
        }

        res.json(response);
    } catch (e) {
        logger.error("Evaluation error:", { error: e });
        res.status(500).json({ decision: "DENY", reason: "Internal Server Error" });
    }
};

export const scrubToolResponse = async (req: Request, res: Response) => {
    let tenantId = "default-tenant";
    try {
        const { tenantId: reqTenantId, secretNames, toolResponse } = req.body;
        tenantId = reqTenantId || "default-tenant";
        
        if (!secretNames || secretNames.length === 0) {
            return res.json({ scrubbedResponse: toolResponse });
        }

        const secretValues: string[] = [];
        for (const name of secretNames) {
            const result = await pool.query(
                `SELECT pgp_sym_decrypt(encrypted_value, $1) as value
                 FROM vault_secrets
                 WHERE tenant_id = $2 AND secret_name = $3`,
                [process.env.VAULT_ENCRYPTION_KEY, tenantId || "default-tenant", name]
            );
            if (result.rows.length > 0) {
                secretValues.push(result.rows[0].value);
            }
        }

        const scrubbed = scrubResponse(toolResponse, secretValues);
        res.json({ scrubbedResponse: scrubbed });
    } catch (e) {
        logger.error("Scrub error:", { error: e, tenantId });
        res.json({ scrubbedResponse: "[SCRUB_ERROR: Response redacted for safety]" });
    }
};

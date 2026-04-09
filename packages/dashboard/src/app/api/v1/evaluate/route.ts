// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export const dynamic = 'force-dynamic';


import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/firebase-admin';
import { admin } from '@/lib/firebase-admin';
import * as crypto from 'crypto';
import { resolveVaultTokens } from '@/lib/vault-server';
import { scrubPii } from '@/lib/guardrail-scrubber';
import { analyzeCall, updateBaseline, type SemanticAnalysisResult, type SemanticLayerMode } from '@/lib/semantic-server';
import { pool as pgPool, ensureSchema } from '@/lib/db_sql';

// ── Types ──

interface PolicyRule {
    toolPattern: string;
    action: "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
    conditions?: Record<string, any>;
}

interface RateLimitConfig {
    requestsPerMinute: number;
    requestsPerDay: number;
}

interface EvaluateResponse {
    decision: "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
    reason?: string;
    estimated_cost_usd?: number;
    is_loop?: boolean;
}

// ── Route Handler ──

export async function POST(req: NextRequest) {
    const startTime = Date.now();
    let body;
    try {
        body = await req.json();
    } catch {
        return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
    }

    let {
        apiKey,
        toolName,
        args,
        arguments: argsAlias, // Alias for SDK-native naming
        sessionId = null,
        agentRole = null,
        model = "gpt-4o-mini",
        inputTokens = 0,
        outputTokens = 0,
        costUsd = null,
        isLoop = false,
        source = "direct-sdk"
    } = body;

    let finalArgs = args ?? argsAlias;

    if (!apiKey || !toolName || finalArgs === undefined) {
        return NextResponse.json({ error: "apiKey and toolName are required." }, { status: 400 });
    }

    try {
        let tenantId: string;
        let agentId: string;
        let userId: string;
        let showBranding: boolean = true;
        let effectiveRules: PolicyRule[] = [];
        let effectiveRateLimit: RateLimitConfig | null = null;
        let platformId: string | null = null;
        let customerId: string | null = null;
        let agentName: string = "Unknown Agent";
        let userPlan: string = 'free';

        // ── Auth & Key Resolution ──

        if (apiKey.startsWith("agc_")) {
            // Platform connect key
            const subKeySnap = await db.collection("connect_keys").doc(apiKey).get();
            if (!subKeySnap.exists || !subKeySnap.data()?.active) {
                return NextResponse.json({ error: "Invalid or inactive Connect sub-key." }, { status: 401 });
            }

            const subKey = subKeySnap.data()!;
            platformId = subKey.platformId;
            customerId = subKey.customerId;
            tenantId = subKey.platformId; // Using platformId as tenant for vault
            agentId = apiKey; // Using apiKey as agentId for vault reference

            const platformSnap = await db.collection("platforms").doc(platformId!).get();
            const platformData = platformSnap.data();
            userId = platformData?.ownerId;
            userPlan = platformData?.plan || 'free';
            // Hide branding for any paid tier
            showBranding = !['starter', 'growth', 'business', 'enterprise'].includes(userPlan);

            const basePolicySnap = await db.collection("platforms").doc(platformId!).collection("base_policies").doc("default").get();
            const baseRules: PolicyRule[] = basePolicySnap.data()?.rules ?? [];
            const baseRateLimit: RateLimitConfig = basePolicySnap.data()?.rateLimit ?? { requestsPerMinute: 60, requestsPerDay: 10000 };

            effectiveRules = [...(subKey.policyOverrides ?? []), ...baseRules];
            effectiveRateLimit = subKey.rateLimitOverride ?? baseRateLimit;
        } else {
            // Regular agent key
            const agentsSnapshot = await db.collection("agents").where("apiKey", "==", apiKey).limit(1).get();
            if (agentsSnapshot.empty) {
                return NextResponse.json({ decision: "DENY", reason: "Invalid API Key" }, { status: 403 });
            }

            const agentDoc = agentsSnapshot.docs[0];
            const agentData = agentDoc.data();
            agentId = agentDoc.id;
            tenantId = agentData.userId;
            userId = agentData.userId;
            agentName = agentData.name || "Unknown Agent";

            const userSnap = await db.collection("users").doc(userId).get();
            const userData = userSnap.data();
            userPlan = userData?.plan || 'free';
            // Hide branding for any paid tier
            showBranding = !['starter', 'growth', 'business', 'enterprise'].includes(userPlan);

            if (agentData.status && agentData.status !== 'active') {
                return NextResponse.json({ decision: "DENY", reason: `Agent is ${agentData.status}.` }, { status: 403 });
            }

            // ── Threat Detection — blocks before any policy evaluation ──
            const threatResult = detectThreats(toolName, finalArgs);
            if (threatResult.blocked) {
                await logAudit(tenantId, agentId, toolName, JSON.stringify(finalArgs), "DENY", 0, threatResult.reason!, sessionId, agentRole, isLoop, source);
                
                // Fire-and-forget threat event log (Postgres + Firestore)
                db.collection("threat_events").add({
                    agentId, tenantId, toolName,
                    event_type: threatResult.threatType,
                    severity: threatResult.severity,
                    details: threatResult.detail,
                    timestamp: admin.firestore.FieldValue.serverTimestamp(),
                }).catch(err => console.error("[ThreatEvent] Firestore write failed:", err));

                // Log threat to Postgres for dashboard visibility
                logThreat(tenantId, agentId, toolName, threatResult.threatType!, threatResult.severity!, threatResult.detail || threatResult.reason!);

                return NextResponse.json({
                    decision: "DENY",
                    reason: threatResult.reason,
                    threatType: threatResult.threatType,
                }, { status: 403 });
            }

            // ── Guardrail Evaluation — hard stops before policy evaluation ──
            const guardrailResult = evaluateGuardrailsSync(agentData, toolName, finalArgs);
            if (guardrailResult.blocked) {
                const gr = guardrailResult.reason || 'Blocked by agent guardrail';
                await logAudit(tenantId, agentId, toolName, JSON.stringify(finalArgs), "DENY", 0, gr, sessionId, agentRole, isLoop, source);
                return NextResponse.json({ decision: "DENY", reason: gr });
            }
            if (guardrailResult.modifiedArgs) {
                finalArgs = guardrailResult.modifiedArgs;
            }

            // Fetch tenant policies
            const policiesSnapshot = await db.collection("policies")
                .where("tenantId", "==", tenantId)
                .get();

            const docs = policiesSnapshot.docs.sort((a, b) => (b.data().priority || 0) - (a.data().priority || 0));

            for (const doc of docs) {
                const policy = doc.data();
                
                // Only apply if it's for this agent or global for the tenant
                if (policy.agentId && policy.agentId !== agentId) continue;
                
                effectiveRules.push({
                    toolPattern: policy.toolName || "*",
                    action: (policy.ruleType || "ALLOW").toUpperCase() as "ALLOW" | "DENY" | "REQUIRE_APPROVAL",
                    conditions: {
                        reason: policy.description,
                        regex: policy.condition
                    }
                });
            }
        }

        const branding = showBranding ? {
            enabled: true,
            text: "🛡️ Secured by SupraWall — AI agent security & EU AI Act compliance",
            url: "https://supra-wall.com?ref=agent-output",
            format: "text"
        } : { enabled: false };

        // ── Vault Evaluation ──
        
        const vaultResult = await resolveVaultTokens(tenantId, agentId, toolName, finalArgs);
        let resolvedArguments = finalArgs;
        let vaultInjected = false;

        if (!vaultResult.success) {
            return NextResponse.json({ 
                decision: "DENY", 
                reason: `Vault Error: ${vaultResult.errors[0].message}`,
                branding 
            });
        }
        
        if (vaultResult.injectedSecrets.length > 0) {
            resolvedArguments = vaultResult.resolvedArgs;
            vaultInjected = true;
        }

        // ── Rate Limit Check ──

        if (effectiveRateLimit) {
            const limitOk = await checkRateLimit(apiKey, effectiveRateLimit);
            if (!limitOk) {
                return NextResponse.json({ decision: "DENY", reason: "Rate limit exceeded.", branding }, { status: 429 });
            }
        }

        // ── Policy Final Decision ──

        const decisionResult = evaluatePolicies(toolName, resolvedArguments, effectiveRules);
        let decision = decisionResult.decision;

        // ── Cost Estimation ──

        const estimatedCost = costUsd ?? estimateActionCost(finalArgs, toolName, model, inputTokens, outputTokens);
        const latencyMs = Date.now() - startTime;

        // ── Layer 2: AI Semantic Analysis (Growth+ tiers only) ──
        const PLAN_TO_SEMANTIC: Record<string, SemanticLayerMode> = {
            free: 'none', starter: 'none',
            team: 'semantic', business: 'behavioral', enterprise: 'custom',
        };
        const semanticLayer = PLAN_TO_SEMANTIC[userPlan] || 'none';
        let semanticResult: SemanticAnalysisResult | null = null;
        let semanticResponseFields: Record<string, unknown> = {};

        if (decision === "ALLOW" && semanticLayer !== 'none') {
            try {
                let customEndpoint: string | undefined;
                if (semanticLayer === 'custom') {
                    // Firestore check for custom endpoint
                    const epSnap = await db.collection("custom_model_endpoints").doc(tenantId).get();
                    const epData = epSnap.data();
                    if (epData?.enabled && epData?.endpoint_url) {
                        customEndpoint = epData.endpoint_url;
                    }
                }

                semanticResult = await analyzeCall({
                    tenantId, agentId, toolName,
                    args: resolvedArguments,
                    argsString: JSON.stringify(resolvedArguments),
                    semanticLayer,
                    customEndpoint,
                });

                if (semanticResult.decision === 'DENY') {
                    decision = "DENY";
                    semanticResponseFields = {
                        semanticScore: semanticResult.semanticScore,
                        semanticReasoning: semanticResult.reasoning,
                    };
                } else if (semanticResult.decision === 'REQUIRE_APPROVAL') {
                    decision = "REQUIRE_APPROVAL";
                    semanticResponseFields = {
                        semanticScore: semanticResult.semanticScore,
                        semanticReasoning: semanticResult.reasoning,
                    };
                } else if (semanticResult.decision === 'FLAG') {
                    semanticResponseFields = {
                        semanticFlag: true,
                        semanticScore: semanticResult.semanticScore,
                        semanticReasoning: semanticResult.reasoning,
                    };
                }
            } catch (err) {
                console.error("[Layer2] Semantic analysis failed:", err);
                // Never block on Layer 2 failure
            }
        }

        // Update behavioral baseline (async, non-blocking)
        if (decision === "ALLOW" && (semanticLayer === 'behavioral' || semanticLayer === 'custom')) {
            updateBaseline(tenantId, agentId, toolName, resolvedArguments).catch(() => {});
        }

        // ── Approval Flow ──

        if (decision === "REQUIRE_APPROVAL") {
            const finalArgsString = JSON.stringify(resolvedArguments);
            const requestId = await createApprovalRequest(userId, agentId, agentName, toolName, finalArgsString, sessionId, agentRole, estimatedCost);
            
            await logAudit(tenantId, agentId, toolName, finalArgsString, "PAUSED", estimatedCost, "Awaiting human approval", sessionId, agentRole, isLoop, source);
            
            return NextResponse.json({ 
                decision: "REQUIRE_APPROVAL", 
                reason: "This action requires human approval.", 
                requestId, 
                branding 
            });
        }

        // ── Post-Evaluation Writes ──

        const updates: Promise<any>[] = [
            logAudit(tenantId, agentId, toolName, JSON.stringify(resolvedArguments), decision, estimatedCost, decisionResult.reason, sessionId, agentRole, isLoop, source)
        ];

        if (apiKey.startsWith("agc_")) {
            updates.push(db.collection("connect_keys").doc(apiKey).update({
                lastUsedAt: admin.firestore.FieldValue.serverTimestamp(),
                totalCalls: admin.firestore.FieldValue.increment(1),
                totalSpendUsd: admin.firestore.FieldValue.increment(estimatedCost),
            }));
            updates.push(db.collection("connect_events").add({
                platformId, customerId, toolName, decision, reason: decisionResult.reason ?? null, latencyMs, costUsd: estimatedCost, isLoop, timestamp: admin.firestore.FieldValue.serverTimestamp(),
            }));
        } else {
            updates.push(db.collection("agents").doc(agentId).update({
                totalCalls: admin.firestore.FieldValue.increment(1),
                totalSpendUsd: admin.firestore.FieldValue.increment(estimatedCost),
                lastUsedAt: admin.firestore.FieldValue.serverTimestamp(),
                verifiedAt: admin.firestore.FieldValue.serverTimestamp() // Update verification heartbeat
            }));
        }

        if (userId) {
            updates.push(db.collection("users").doc(userId).update({
                operationsThisMonth: admin.firestore.FieldValue.increment(1),
                lastUsedAt: admin.firestore.FieldValue.serverTimestamp(),
            }).catch(e => console.error("Failed to update user usage:", e)));
        }

        // Non-blocking writes
        Promise.all(updates).catch(e => console.error("Evaluate background updates failed:", e));

        return NextResponse.json({
            decision,
            reason: semanticResult?.decision === 'DENY'
                ? `AI semantic analysis: ${semanticResult.reasoning}`
                : decisionResult.reason,
            resolvedArguments: vaultInjected ? resolvedArguments : undefined,
            vaultInjected,
            injectedSecrets: vaultInjected ? vaultResult.injectedSecrets : undefined,
            branding,
            estimated_cost_usd: estimatedCost,
            ...semanticResponseFields,
        });

    } catch (e: any) {
        console.error("Evaluate error:", e);
        return NextResponse.json({ error: "Internal error", decision: "DENY" }, { status: 500 });
    }
}

// ── Helpers ──

// ── Threat Detection Engine ──

interface ThreatResult {
    blocked: boolean;
    reason?: string;
    threatType?: string;
    severity?: string;
    detail?: string;
}

function detectThreats(toolName: string, finalArgs: any): ThreatResult {
    const payload = `${toolName} ${JSON.stringify(finalArgs || {})}`.toLowerCase();
    const rawPayload = JSON.stringify(finalArgs || {});

    // SQL Injection Patterns
    const sqlPatterns: Array<{ re: RegExp; label: string }> = [
        { re: /drop\s+table/i,                        label: "DROP TABLE" },
        { re: /delete\s+from/i,                       label: "DELETE FROM" },
        { re: /insert\s+into/i,                       label: "INSERT INTO" },
        { re: /update\s+\S+\s+set/i,                  label: "UPDATE SET" },
        { re: /union\s+select/i,                      label: "UNION SELECT" },
        { re: /or\s+['"]?1['"]?\s*=\s*['"]?1/i,      label: "OR 1=1" },
        { re: /;\s*--/i,                              label: "comment terminator" },
        { re: /exec(\s+|\()sp_/i,                     label: "EXEC stored procedure" },
        { re: /xp_cmdshell/i,                         label: "xp_cmdshell" },
        { re: /\bsleep\s*\(\s*\d+\s*\)/i,             label: "SLEEP() time-based" },
        { re: /benchmark\s*\(/i,                      label: "BENCHMARK() DoS" },
        { re: /load_file\s*\(/i,                      label: "LOAD_FILE() exfil" },
        { re: /into\s+outfile/i,                      label: "INTO OUTFILE exfil" },
    ];

    for (const { re, label } of sqlPatterns) {
        if (re.test(rawPayload)) {
            return {
                blocked: true,
                reason: `Threat detected: SQL injection pattern (${label}) blocked by SupraWall Threat Engine.`,
                threatType: "sql_injection",
                severity: "critical",
                detail: label,
            };
        }
    }

    // Prompt Injection Patterns (now even more flexible)
    const promptPatterns: Array<{ re: RegExp; label: string }> = [
        { re: /(ignore|forget|disregard)\s+(.*)\s+(instructions|prompt|original|directives|rules|safety|security)/i, label: "instruction override" },
        { re: /system\s+bypass/i,                                             label: "system bypass" },
        { re: /you\s+are\s+now\s+(a|an|the)\s/i,                             label: "persona override" },
        { re: /override\s+(system|safety|security)/i,                        label: "override safety" },
        { re: /act\s+as\s+if\s+you\s+have\s+no\s+restrictions/i,             label: "no restrictions" },
        { re: /reveal\s+(your|the)\s+(system\s+)?prompt/i,                   label: "reveal system prompt" },
        { re: /do\s+not\s+follow\s+(.*)\s*(instructions|prompt|directives|rules)/i, label: "do not follow instructions" },
        { re: /DAN\s+mode/i,                                                 label: "DAN mode bypass" },
        { re: /jailbreak/i,                                                  label: "jailbreak attempt" },
    ];

    for (const { re, label } of promptPatterns) {
        if (re.test(rawPayload)) {
            return {
                blocked: true,
                reason: "Threat detected: Prompt injection attempt blocked by SupraWall Threat Engine.",
                threatType: "prompt_injection",
                severity: "high",
                detail: label,
            };
        }
    }

    // OS Command Injection Patterns
    const osPatterns: Array<{ re: RegExp; label: string }> = [
        { re: /;\s*(rm|mv|cp|ls|cat|sh|bash|pwd|id|whoami|curl|wget)\s/i, label: "piped command" },
        { re: /\|\s*(rm|mv|cp|ls|cat|sh|bash|pwd|id|whoami|curl|wget)\s/i, label: "piped command" },
        { re: /&\s*(rm|mv|cp|ls|cat|sh|bash|pwd|id|whoami|curl|wget)\s/i, label: "piped command" },
        { re: /`.*`/i,                                                      label: "backtick execution" },
        { re: /\$\(.*\)/i,                                                   label: "subshell execution" },
        { re: /\/etc\/(passwd|shadow|hostname|hosts)/i,                    label: "sensitive system file" },
        { re: /\/proc\//i,                                                  label: "proc file access" },
        { re: /\/root\//i,                                                  label: "root file access" },
    ];

    for (const { re, label } of osPatterns) {
        if (re.test(rawPayload)) {
            return {
                blocked: true,
                reason: "Threat detected: OS Command injection attempt blocked by SupraWall Threat Engine.",
                threatType: "os_command_injection",
                severity: "critical",
                detail: label,
            };
        }
    }

    // Sensitive Data Access Patterns
    const dataPatterns: Array<{ re: RegExp; label: string }> = [
        { re: /password[s]?\.(txt|json|csv|yaml|yml)/i, label: "password file" },
        { re: /id_rsa|id_ecdsa|id_ed25519/i,          label: "SSH private key" },
        { re: /\.env(\.|$)/i,                        label: "environment file" },
        { re: /credential[s]?\.(txt|json)/i,          label: "credentials file" },
        { re: /access_token|api_key|secret_key/i,     label: "exposed secret" },
    ];

    for (const { re, label } of dataPatterns) {
        if (re.test(rawPayload)) {
            return {
                blocked: true,
                reason: "Threat detected: Unauthorized access to sensitive data blocked by SupraWall.",
                threatType: "sensitive_data_access",
                severity: "critical",
                detail: label,
            };
        }
    }

    // XSS Patterns
    const xssPatterns: Array<{ re: RegExp; label: string }> = [
        { re: /<script[\s>]/i,                    label: "<script> tag" },
        { re: /javascript\s*:/i,                  label: "javascript: URI" },
        { re: /on(error|load|click|mouseover)\s*=/i, label: "inline event handler" },
        { re: /eval\s*\(/i,                       label: "eval()" },
        { re: /<iframe/i,                         label: "<iframe>" },
    ];

    for (const { re, label } of xssPatterns) {
        if (re.test(rawPayload)) {
            return {
                blocked: true,
                reason: `Threat detected: XSS pattern (${label}) blocked by SupraWall Threat Engine.`,
                threatType: "xss_injection",
                severity: "high",
                detail: label,
            };
        }
    }

    return { blocked: false };
}

function matchesWildcard(toolName: string, pattern: string): boolean {
    if (!pattern.includes('*')) return toolName === pattern;
    return new RegExp('^' + pattern.replace(/\*/g, '.*') + '$').test(toolName);
}

function evaluateGuardrailsSync(
    agentData: any, toolName: string, finalArgs: any
): { blocked: boolean; reason?: string; modifiedArgs?: any } {
    const g = agentData.guardrails;
    if (!g) return { blocked: false };

    if (g.budget?.limitUsd) {
        const spend = agentData.totalSpendUsd || 0;
        if (spend >= g.budget.limitUsd) {
            if (g.budget.onExceeded === 'block')
                return { blocked: true, reason: `Spend guardrail: limit $${g.budget.limitUsd} exceeded ($${spend.toFixed(4)} spent)` };
            if (g.budget.onExceeded === 'require_approval')
                return { blocked: true, reason: 'PENDING_APPROVAL:budget_exceeded' };
        }
    }

    if (g.allowedTools?.length > 0) {
        if (!g.allowedTools.some((p: string) => matchesWildcard(toolName, p)))
            return { blocked: true, reason: `Tool guardrail: "${toolName}" not in allowlist` };
    }

    if (g.blockedTools?.length > 0) {
        if (g.blockedTools.some((p: string) => matchesWildcard(toolName, p)))
            return { blocked: true, reason: `Tool guardrail: "${toolName}" is blocked` };
    }

    if (g.piiScrubbing?.enabled && g.piiScrubbing.patterns?.length > 0) {
        const { modifiedArgs, shouldBlock } = scrubPii(finalArgs, g.piiScrubbing);
        if (shouldBlock) return { blocked: true, reason: 'PII guardrail: sensitive data detected in arguments' };
        return { blocked: false, modifiedArgs };
    }

    return { blocked: false };
}

function evaluatePolicies(toolName: string, finalArgs: any, rules: PolicyRule[]): { decision: "ALLOW" | "DENY" | "REQUIRE_APPROVAL"; reason?: string } {
    const finalArgsString = JSON.stringify(finalArgs);
    for (const rule of rules) {
        if (matchesPattern(toolName, rule.toolPattern)) {
            if (rule.conditions?.regex) {
                try {
                    if (new RegExp(rule.conditions.regex).test(finalArgsString)) {
                        return { decision: rule.action, reason: rule.conditions.reason || `Blocked by rule matching ${rule.toolPattern}` };
                    }
                } catch (e) {
                    console.error("Invalid regex in policy rule:", rule.conditions.regex);
                }
            } else {
                return { decision: rule.action, reason: rule.conditions?.reason || `Blocked by rule matching ${rule.toolPattern}` };
            }
        }
    }
    return { decision: "ALLOW" };
}

function matchesPattern(toolName: string, pattern: string): boolean {
    if (pattern === "*") return true;
    if (pattern.endsWith("*")) return toolName.startsWith(pattern.slice(0, -1));
    return toolName === pattern;
}

async function checkRateLimit(key: string, config: RateLimitConfig): Promise<boolean> {
    const now = new Date();
    const minKey = `rl_${key}_${now.toISOString().slice(0, 16)}`; // simplified
    const snap = await db.collection("rate_limit_counters").doc(minKey).get();
    if (snap.exists && (snap.data()?.count || 0) >= config.requestsPerMinute) return false;
    
    await db.collection("rate_limit_counters").doc(minKey).set({
        count: admin.firestore.FieldValue.increment(1),
        expiresAt: new Date(Date.now() + 60000)
    }, { merge: true });
    return true;
}

function estimateActionCost(finalArgs: any, toolName: string, model: string, inT: number, outT: number): number {
    if (inT > 0 || outT > 0) {
        const rates: any = { "gpt-4o": 0.005, "gpt-4o-mini": 0.00015, "claude": 0.003 };
        const rate = rates[Object.keys(rates).find(k => model.includes(k)) || "gpt-4o-mini"];
        return (inT / 1000 * rate) + (outT / 1000 * rate * 3);
    }
    return 0.0001; // minimal fallback
}

async function logThreat(tenantId: string, agentId: string, toolName: string, eventType: string, severity: string, details: string) {
    (async () => {
        try {
            await ensureSchema();
            await pgPool.query(
                `INSERT INTO threat_events (tenantid, agentid, event_type, severity, details)
                 VALUES ($1, $2, $3, $4, $5)`,
                [tenantId, agentId, eventType, severity, JSON.stringify({ toolName, details })]
            );
        } catch (err) {
            console.error("[logThreat] PostgreSQL write failed (non-fatal):", err);
        }
    })();
}

async function createApprovalRequest(userId: string, agentId: string, agentName: string, toolName: string, finalArgs: string, sessionId: any, agentRole: any, cost: number) {
    // Firestore write
    const res = await db.collection("approvalRequests").add({
        userId, agentId, agentName, toolName, arguments: finalArgs, sessionId, agentRole,
        status: "pending", createdAt: admin.firestore.FieldValue.serverTimestamp(),
        expiresAt: new Date(Date.now() + 86400000), estimatedCostUsd: cost
    });
    
    // Postgres write for dashboard visibility
    const requestId = res.id;
    (async () => {
        try {
            await ensureSchema();
            await pgPool.query(
                `INSERT INTO approval_requests (id, tenantid, agentid, agentname, toolname, arguments, status, estimated_cost_usd, metadata)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
                [requestId, userId, agentId, agentName, toolName, finalArgs, "pending", cost, JSON.stringify({ sessionId, agentRole })]
            );
        } catch (err) {
            console.error("[createApprovalRequest] PostgreSQL write failed (non-fatal):", err);
        }
    })();

    return requestId;
}

async function logAudit(tenantId: string, agentId: string, toolName: string, finalArgs: string, decision: string, cost: number, reason: any, sId: any, role: any, isLoop: boolean, source: string = "direct-sdk") {
    // Primary: Firestore (real-time agent spend tracking)
    await db.collection("audit_logs").add({
        userId: tenantId, 
        agentId, toolName, arguments: finalArgs, decision, reason, sessionId: sId, agentRole: role,
        cost_usd: cost, is_loop: isLoop, timestamp: admin.firestore.FieldValue.serverTimestamp()
    });

    // Secondary: PostgreSQL (forensic audit trail — non-blocking, never fails the request)
    const riskScore = (decision === "DENY" || decision === "REQUIRE_APPROVAL") ? 90 : 10;
    
    // Non-blocking schema sync + write
    (async () => {
        try {
            await ensureSchema();
            await pgPool.query(
                `INSERT INTO audit_logs (tenantid, agentid, toolname, parameters, decision, riskscore, cost_usd, metadata)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
                [tenantId, agentId, toolName, finalArgs, decision, riskScore, cost,
                 JSON.stringify({ reason, sessionId: sId, agentRole: role, is_loop: isLoop, source })]
            );
        } catch (err) {
            console.error("[AuditLog] PostgreSQL write failed (non-fatal):", err);
        }
    })();
}

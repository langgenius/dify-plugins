// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Request, Response, NextFunction } from "express";
import { pool } from "./db";
import { TIER_LIMITS, Tier, TierLimits, currentMonth } from "./tier-config";
import { logger } from "./logger";
import { sendDiscordUsageAlert } from "./discord";

export interface TieredRequest extends Request {
    tier?: Tier;
    tierLimits?: TierLimits;
    tenantId?: string;
}

/**
 * Middleware that resolves the tenant's billing tier and injects
 * `req.tier` and `req.tierLimits` for downstream enforcement.
 *
 * Falls back to 'open_source' if the tenant has no subscription or if
 * DB resolution fails. When SUPRAWALL_MODE=local, always uses open_source
 * limits regardless of any DB state (correct behavior for self-hosters).
 */
export async function resolveTier(req: TieredRequest, res: Response, next: NextFunction) {
    // SECURITY: tenantId must come from auth middleware, never from client input
    const tenantId =
        (req as any).tenantId ||
        (req as any).agent?.tenantId;

    if (!tenantId) {
        return res.status(401).json({ error: "Unauthorized: No tenant context. Authenticate first." });
    }

    req.tenantId = tenantId;

    // SUPRAWALL_MODE=local: enforce open_source limits for all self-hosted deployments
    if (process.env.SUPRAWALL_MODE === "local") {
        req.tier = "open_source";
        req.tierLimits = TIER_LIMITS["open_source"];
        return next();
    }

    try {
        const result = await pool.query(
            "SELECT tier FROM tenants WHERE id = $1",
            [tenantId]
        );

        // Validate the DB-stored tier is a known value; fall back to open_source if not
        const rawTier = result.rows[0]?.tier;
        const knownTiers: Tier[] = ['open_source', 'developer', 'team', 'business', 'enterprise'];
        const tier: Tier = knownTiers.includes(rawTier) ? rawTier : 'open_source';

        req.tier = tier;
        req.tierLimits = TIER_LIMITS[tier];

        if (req.tierLimits.semanticLayer !== 'none') {
            logger.info(`[TierGuard] Semantic layer enabled: ${req.tierLimits.semanticLayer}`, { tenantId });
        }
    } catch (err) {
        logger.warn("[TierGuard] Failed to resolve tier, defaulting to open_source", { tenantId, error: err });
        req.tier = "open_source";
        req.tierLimits = TIER_LIMITS["open_source"];
    }

    next();
}

/**
 * Checks if a tenant has exceeded their monthly evaluation limit.
 * If overage is allowed (metered), it returns true but logs a warning.
 * If overage is blocked (OSS), it returns false (triggers 402).
 */
export async function checkEvaluationLimit(tenantId: string, limits: TierLimits): Promise<{ allowed: boolean; current: number }> {
    const month = currentMonth();
    try {
        const result = await pool.query(
            "SELECT evaluation_count FROM tenant_usage WHERE tenant_id = $1 AND month = $2",
            [tenantId, month]
        );
        const current = result.rows[0]?.evaluation_count || 0;

        // Block if over limit AND overage is not allowed (null = hard stop)
        if (current >= limits.maxEvaluationsPerMonth && limits.overageRatePerEval == null) {
            return { allowed: false, current };
        }
        return { allowed: true, current };
    } catch (err) {
        // SECURITY: Fail-closed. A DB error must not allow unlimited free usage.
        // A brief circuit-breaker window is acceptable; silent overage is not.
        logger.error("[TierGuard] Error checking evaluation limit — denying request:", err);
        return { allowed: false, current: -1 };
    }
}

/**
 * Increments the evaluation counter for a tenant.
 * Also calculates overage units if the tenant is beyond their base limit.
 */
export async function recordEvaluation(tenantId: string, limits: TierLimits): Promise<void> {
    const month = currentMonth();
    try {
        const result = await pool.query(
            `INSERT INTO tenant_usage (tenant_id, month, evaluation_count)
             VALUES ($1, $2, 1)
             ON CONFLICT (tenant_id, month)
             DO UPDATE SET
                evaluation_count = tenant_usage.evaluation_count + 1,
                overage_units = CASE
                    WHEN (tenant_usage.evaluation_count + 1) > $3 THEN (tenant_usage.evaluation_count + 1) - $3
                    ELSE 0
                END,
                last_updated = $4
             RETURNING evaluation_count`,
            [tenantId, month, limits.maxEvaluationsPerMonth, new Date().toISOString()]
        );

        // Discord usage alerts at 50%, 75%, 90%, 100% thresholds
        const discordUrl = process.env.DISCORD_WEBHOOK_URL;
        if (discordUrl && result.rows.length > 0) {
            const current = result.rows[0].evaluation_count;
            const max = limits.maxEvaluationsPerMonth;
            const pct = current / max;

            const alertThresholds = [0.5, 0.75, 0.9, 1.0];
            const prevPct = (current - 1) / max;

            const crossed = alertThresholds.find(t => prevPct < t && pct >= t);
            if (crossed) {
                // Fire-and-forget: don't block the request
                setImmediate(async () => {
                    try {
                        // Look up company info for better alert context
                        const companyResult = await pool.query(
                            `SELECT pc.paperclip_company_id, t.tier
                             FROM paperclip_companies pc
                             JOIN tenants t ON t.id = pc.tenant_id
                             WHERE pc.tenant_id = $1
                             LIMIT 1`,
                            [tenantId]
                        );
                        const companyId = companyResult.rows[0]?.paperclip_company_id || tenantId;
                        const tier = companyResult.rows[0]?.tier || "developer";

                        await sendDiscordUsageAlert(discordUrl, {
                            companyId,
                            tenantId,
                            currentUsage: current,
                            maxUsage: max,
                            currentTier: tier,
                            upgradeUrl: `https://supra-wall.com/pricing?source=discord_alert&tenant=${tenantId}`,
                        });
                    } catch (e) {
                        logger.warn("[TierGuard] Discord alert failed:", e);
                    }
                });
            }
        }
    } catch (err) {
        logger.error("[TierGuard] Failed to record evaluation:", { tenantId, error: err });
    }
}

/**
 * Middleware: Enforces SSO enablement for Business+ tiers.
 */
export async function enforceSSO(req: TieredRequest, res: Response, next: NextFunction) {
    if (!req.tierLimits?.ssoEnabled) {
        return res.status(403).json({
            error: "SSO not supported",
            message: "SSO features are only available on Business and Enterprise plans. Upgrade to enable SSO.",
            upgradeUrl: "https://www.supra-wall.com/pricing"
        });
    }
    next();
}

/**
 * Returns a standard tier-limit upgrade error response (402 Payment Required).
 */
export function tierLimitError(
    feature: string,
    current: number | string,
    limit: number | string,
    currentTier?: string
) {
    const upgradeMap: Record<string, { nextTier: string; price: string }> = {
        open_source: { nextTier: "developer", price: "Free" },
        developer:   { nextTier: "team",      price: "$79/mo" },
        team:        { nextTier: "business",   price: "$249/mo" },
        business:    { nextTier: "enterprise", price: "Custom" },
    };
    const upgrade = upgradeMap[currentTier || "developer"] ?? upgradeMap.developer;

    return {
        error: `${feature} limit reached (${current}/${limit}). Upgrade to ${upgrade.nextTier} to continue without interruption.`,
        currentTier: currentTier || "developer",
        message: `Your ${currentTier || "current"} plan allows ${limit} ${feature.toLowerCase()}(s). You currently have ${current}.`,
        upgradeUrl: `https://www.supra-wall.com/pricing?plan=${upgrade.nextTier}&source=${feature.toLowerCase().replace(/\s+/g, "_")}_limit`,
        upgradePrice: upgrade.price,
        code: "TIER_LIMIT_EXCEEDED",
    };
}

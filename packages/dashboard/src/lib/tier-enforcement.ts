import "server-only";
import { db } from './firebase-admin';

export type Tier = 'open_source' | 'developer' | 'team' | 'business' | 'enterprise';

export interface TierLimits {
    maxAgents: number;
    maxVaultSecrets: number;
    maxEvaluationsPerMonth: number;
    maxSeats: number;
    auditRetentionDays: number;
    ssoEnabled: boolean;
    policyEngine: 'regex' | 'ai' | 'advanced';
    dashboard: 'none' | 'cloud' | 'vpc';
    budgetEnforcement: boolean;
    euAiActTemplates: boolean;
    pdfReports: boolean;
}

// Single source of truth for limits (matching backend tier-config.ts)
const LIMITS: Record<Tier, TierLimits> = {
    open_source: {
        maxAgents: 2,
        maxVaultSecrets: 3,
        maxEvaluationsPerMonth: 5_000,
        maxSeats: 1,
        auditRetentionDays: 3,
        ssoEnabled: false,
        policyEngine: 'regex',
        dashboard: 'none',
        budgetEnforcement: false,
        euAiActTemplates: false,
        pdfReports: false,
    },
    developer: {
        maxAgents: 5,
        maxVaultSecrets: 15,
        maxEvaluationsPerMonth: 25_000,
        maxSeats: 1,
        auditRetentionDays: 30,
        ssoEnabled: false,
        policyEngine: 'regex',
        dashboard: 'cloud',
        budgetEnforcement: false,
        euAiActTemplates: false,
        pdfReports: false,
    },
    team: {
        maxAgents: 25,
        maxVaultSecrets: 100,
        maxEvaluationsPerMonth: 250_000,
        maxSeats: 3,
        auditRetentionDays: 90,
        ssoEnabled: false,
        policyEngine: 'ai',
        dashboard: 'cloud',
        budgetEnforcement: true,
        euAiActTemplates: true,
        pdfReports: true,
    },
    business: {
        maxAgents: Infinity,
        maxVaultSecrets: Infinity,
        maxEvaluationsPerMonth: 2_000_000,
        maxSeats: 10,
        auditRetentionDays: 365,
        ssoEnabled: true,
        policyEngine: 'ai',
        dashboard: 'cloud',
        budgetEnforcement: true,
        euAiActTemplates: true,
        pdfReports: true,
    },
    enterprise: {
        maxAgents: Infinity,
        maxVaultSecrets: Infinity,
        maxEvaluationsPerMonth: Infinity,
        maxSeats: Infinity,
        auditRetentionDays: 2555,
        ssoEnabled: true,
        policyEngine: 'advanced',
        dashboard: 'vpc',
        budgetEnforcement: true,
        euAiActTemplates: true,
        pdfReports: true,
    },
};

/**
 * Resolves the tier for a given userId.
 * Primary: SupraWall Backend (PostgreSQL)
 * Secondary: Firestore Fallback
 */
export async function getUserTier(userId: string): Promise<Tier> {
    const VALID_TIERS: Tier[] = ['open_source', 'developer', 'team', 'business', 'enterprise'];

    try {
        // 1. Primary: Check Backend Server (PostgreSQL source of truth)
        const serverUrl = process.env.SUPRAWALL_API_URL || "https://suprawall.vercel.app";
        const res = await fetch(`${serverUrl}/v1/tenants/${userId}`);
        if (res.ok) {
            const data = await res.json();
            if (data.tier && VALID_TIERS.includes(data.tier)) return data.tier as Tier;
        }

        // 2. Fallback: Firestore check
        const orgDoc = await db.collection('organizations').doc(userId).get();
        if (orgDoc.exists) {
            const plan = orgDoc.data()?.plan || orgDoc.data()?.tier;
            if (plan) {
                // Handle legacy tier names
                if (plan === 'free') return 'open_source';
                if (plan === 'starter') return 'developer';
                if (plan === 'growth') return 'team';
                // Validate before casting
                if (VALID_TIERS.includes(plan as Tier)) return plan as Tier;
            }
        }

        return 'open_source';
    } catch (err) {
        console.warn(`[getUserTier Proxy Fallback] for ${userId}:`, err);
        return 'open_source';
    }
}

/**
 * Returns the resource limits for a specific tier.
 */
export function getLimitsForTier(tier: Tier): TierLimits {
    return LIMITS[tier] || LIMITS.open_source;
}

/**
 * Shared check for resource limits.
 * Now queries the Backend to ensure PG-Firestore consistency.
 */
export async function checkResourceLimit(
    userId: string,
    collectionName: 'agents' | 'vault_secrets',
    field: 'userId' | 'tenant_id'
): Promise<{ allowed: boolean; count: number; limit: number; tier: Tier }> {
    const tier = await getUserTier(userId);
    const limits = getLimitsForTier(tier);

    const limit = collectionName === 'agents' ? limits.maxAgents : limits.maxVaultSecrets;

    // For agents, we prefer counting in PostgreSQL via the backend
    if (collectionName === 'agents') {
        try {
            const serverUrl = process.env.SUPRAWALL_API_URL || "https://suprawall.vercel.app";
            const res = await fetch(`${serverUrl}/v1/agents?tenantId=${userId}`);
            if (res.ok) {
                const agents = await res.json();
                const count = Array.isArray(agents) ? agents.length : (agents.rows ? agents.rows.length : 0);
                return { allowed: count < limit, count, limit, tier };
            }
        } catch (e) {
            console.warn("[checkResourceLimit] Failed to count agents via PG, falling back to Firestore");
        }
    }

    // Default/Fallback: Firestore count
    const snapshot = await db.collection(collectionName).where(field, "==", userId).get();
    const count = snapshot.size;

    return {
        allowed: count < limit,
        count,
        limit,
        tier
    };
}

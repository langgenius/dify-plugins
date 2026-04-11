// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Request, Response, NextFunction } from "express";
import { pool } from "./db";
import { getAuth } from "./firebase";
import { AuthProvider, AgentInfo } from "./auth/types";
import { PostgresAuthProvider } from "./auth/postgres";
import { logger } from "./logger";
import { hashApiKey } from "./util/hash";

// Re-export types for backward compatibility
export type { AgentInfo } from "./auth/types";
export type { AuthProvider } from "./auth/types";

export interface AuthenticatedRequest extends Request {
    agent?: AgentInfo;
    tenantId?: string;
    userEmail?: string; // Set when authenticated via Firebase ID token (not master key)
}

/**
 * Initialize the auth provider based on configuration.
 *
 * Priority:
 *   1. AUTH_PROVIDER=firebase → FirebaseAuthProvider (requires firebase-admin)
 *   2. AUTH_PROVIDER=postgres → PostgresAuthProvider (default)
 *   3. No config → PostgresAuthProvider
 */
function createAuthProvider(): AuthProvider {
    const providerType = (process.env.AUTH_PROVIDER || "postgres").toLowerCase();

    if (providerType === "firebase") {
        try {
            const { FirebaseAuthProvider } = require("./auth/firebase");
            logger.info("[Auth] Using FirebaseAuthProvider");
            return new FirebaseAuthProvider();
        } catch (e) {
            logger.warn("[Auth] Firebase provider requested but failed to load. Falling back to PostgreSQL.");
            return new PostgresAuthProvider();
        }
    }

    logger.info("[Auth] Using PostgresAuthProvider");
    return new PostgresAuthProvider();
}

// Singleton auth provider instance
let authProvider: AuthProvider | null = null;

export function getAuthProvider(): AuthProvider {
    if (!authProvider) {
        authProvider = createAuthProvider();
    }
    return authProvider;
}

/**
 * Admin authentication middleware.
 * Validates the master API key (Bearer token) against the tenants table.
 * Uses database index lookups which are not vulnerable to standard string-comparison timing attacks.
 */
export const adminAuth = async (req: Request, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ error: "Unauthorized: Missing or invalid Authorization header. Use Bearer sw_admin_xxxx" });
    }

    const masterKey = authHeader.split(" ")[1];
    const hashedMasterKey = hashApiKey(masterKey);

    try {
        // 1. Try resolving via Master API Key
        const result = await pool.query(
            "SELECT id FROM tenants WHERE master_api_key = $1 LIMIT 1",
            [hashedMasterKey]
        );

        if (result.rows.length > 0) {
            (req as AuthenticatedRequest).tenantId = result.rows[0].id;
            return next();
        }

        // 2. Try resolving via Firebase ID Token
        const firebaseAdmin = require("./firebase").admin;
        if (firebaseAdmin) {
            try {
                const decodedToken = await firebaseAdmin.auth().verifyIdToken(masterKey);
                (req as AuthenticatedRequest).tenantId = decodedToken.uid;
                (req as AuthenticatedRequest).userEmail = decodedToken.email;
                return next();
            } catch (fbErr) {
                // Not a valid Firebase token either
            }
        }

        return res.status(401).json({ error: "Unauthorized: Invalid Master API Key or Session Token." });
    } catch (error) {
        logger.error("[AdminAuth] Error:", { error });
        res.status(500).json({ error: "Internal authentication error" });
    }
};

/**
 * Gatekeeper authentication middleware.
 * Validates agent API keys using the configured AuthProvider.
 */
export async function gatekeeperAuth(req: Request, res: Response, next: NextFunction) {
    let apiKey = req.body.apiKey || req.headers["x-api-key"];
    const authHeader = req.headers.authorization;

    // Support Bearer Token (Master Key or Firebase Token) in gatekeeper as well
    if (!apiKey && authHeader && authHeader.startsWith("Bearer ")) {
        const token = authHeader.substring(7);
        const hashedToken = hashApiKey(token);
        
        // 1. Try resolving as Master API Key
        const masterRes = await pool.query(
            "SELECT id FROM tenants WHERE master_api_key = $1",
            [hashedToken]
        );
        if (masterRes.rows.length === 0) {
            // 2. Try Firebase ID Token
            try {
                const firebaseAuth = getAuth();
                const decoded = await firebaseAuth.verifyIdToken(token);
                (req as AuthenticatedRequest).tenantId = decoded.uid;
                return next();
            } catch (e) {
                // Fall through to error
            }
        } else {
            (req as AuthenticatedRequest).tenantId = masterRes.rows[0].id;
            return next();
        }
    }

    // sw_temp_* keys: issued during Paperclip onboard for frictionless start
    if (apiKey && typeof apiKey === "string" && apiKey.startsWith("sw_temp_")) {
        try {
            const tokenResult = await pool.query(
                `SELECT tenant_id, tier, expires_at, activated
                 FROM paperclip_tokens WHERE token = $1 LIMIT 1`,
                [hashApiKey(apiKey)]
            );
            if (tokenResult.rows.length > 0) {
                const tokenRow = tokenResult.rows[0];
                if (new Date(tokenRow.expires_at) > new Date()) {
                    (req as AuthenticatedRequest).tenantId = tokenRow.tenant_id;
                    return next();
                }
                return res.status(401).json({ decision: "DENY", reason: "Temporary API key has expired. Visit your activation URL to get a new one." });
            }
        } catch (tempKeyErr) {
            logger.error("[Gatekeeper] Temp key lookup error:", { error: tempKeyErr });
        }
        return res.status(401).json({ decision: "DENY", reason: "Unauthorized: Invalid temporary key." });
    }

    if (!apiKey) {
        return res.status(401).json({
            decision: "DENY",
            reason: "Unauthorized: Missing API Key. Get your key at https://supra-wall.com"
        });
    }

    try {
        const provider = getAuthProvider();
        const agent = await provider.validateApiKey(apiKey);

        if (!agent) {
            return res.status(401).json({
                decision: "DENY",
                reason: "Unauthorized: Invalid API Key."
            });
        }

        if (agent.status && agent.status !== "active") {
            return res.status(403).json({
                decision: "DENY",
                reason: `Unauthorized: Agent is ${agent.status}.`
            });
        }

        // 2. Attach agent info to request
        (req as AuthenticatedRequest).agent = agent;
        (req as AuthenticatedRequest).tenantId = agent.tenantId;
        next();
    } catch (error) {
        logger.error("[Gatekeeper] Auth error:", { error });
        res.status(500).json({ decision: "DENY", reason: "Internal authentication error" });
    }
};

/**
 * Role-enforcement middleware for organization member management.
 * If the caller authenticated via Firebase token (userEmail is set), verify they hold
 * the required role in organization_members. Master API key holders are implicitly owners.
 */
export function requireMemberRole(requiredRole: "admin" | "owner") {
    return async (req: Request, res: Response, next: NextFunction) => {
        const authReq = req as AuthenticatedRequest;

        // Master API key holders are implicitly owners — no additional check needed
        if (!authReq.userEmail) return next();

        try {
            const result = await pool.query(
                `SELECT role FROM organization_members
                 WHERE tenant_id = $1 AND user_email = $2 AND status = 'active'`,
                [authReq.tenantId, authReq.userEmail]
            );

            if (result.rows.length === 0) {
                return res.status(403).json({ error: "Forbidden: Not a member of this organization" });
            }

            const role: string = result.rows[0].role;
            const roleHierarchy = ["viewer", "member", "admin", "owner"];
            const callerLevel = roleHierarchy.indexOf(role);
            const requiredLevel = roleHierarchy.indexOf(requiredRole);

            if (callerLevel < requiredLevel) {
                return res.status(403).json({ error: `Forbidden: Requires '${requiredRole}' role or higher` });
            }

            next();
        } catch (error) {
            logger.error("[RoleCheck] Error:", { error });
            res.status(500).json({ error: "Internal authentication error" });
        }
    };
}

/**
 * Look up an agent by its ID using the configured AuthProvider.
 */
export const getAgentById = async (agentId: string): Promise<AgentInfo | null> => {
    const provider = getAuthProvider();
    return provider.getAgentById(agentId);
};

/**
 * Verify that an agent has the required scope for a tool.
 */
export const verifyScope = (req: AuthenticatedRequest, toolName: string): boolean => {
    const scopes = req.agent?.scopes || [];

    // Simple wildcard support: "*:*" or "namespace:*"
    if (scopes.includes("*:*")) return true;

    const [namespace] = toolName.includes(":") ? toolName.split(":") : [null];

    if (namespace && scopes.includes(`${namespace}:*`)) return true;

    return scopes.includes(toolName);
};

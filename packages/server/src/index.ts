// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import express from "express";
import cors from "cors";
import helmet from "helmet";
import dotenv from "dotenv";
import { initDb, pool, purgeOldLogs } from "./db";
import { evaluatePolicy, scrubToolResponse } from "./policy";
import complianceRouter from "./routes/compliance";
import vaultRouter from "./routes/vault";
import threatRouter from "./routes/threat";
import policiesRouter from "./routes/policies";
import approvalsRouter from "./routes/approvals";
import agentsRouter from "./routes/agents";
import { logger } from "./logger";
import scanRouter from "./routes/scan";
import auditLogsRouter from "./routes/audit_logs";
import tenantsRouter from "./routes/tenants";
import statsRouter from "./routes/stats";
import contentRouter from "./routes/content";
import shieldRouter from "./routes/shield";
import membersRouter from "./routes/members";
import { resolveTier } from "./tier-guard";
import { gatekeeperAuth } from "./auth";
import { rateLimit } from "./rate-limit";
import gdprRouter from "./routes/gdpr";
import awsMarketplaceRouter from "./routes/aws-marketplace";
import paperclipRouter from "./routes/paperclip";
import templatesRouter from "./routes/templates";

// NOTE: stripe-app routes are part of SupraWall Cloud (proprietary).
// See: https://github.com/suprawall/suprawall-cloud

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Security headers (HSTS, XSS protection, no-sniff, etc.)
app.use(helmet());

// Global Rate Limit Fallback: 300 req/min
app.use(rateLimit({ 
    max: 300, 
    windowMs: 60_000, 
    message: "Global rate limit exceeded. Please contact support for high-volume access." 
}));

// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// 1. Global Safety & Security Middleware
// ---------------------------------------------------------------------------

// Response body scrubbing middleware for telemetry/logging safety
// MUST be registered before routers so res.json is monkey-patched.
app.use((req, res, next) => {
    const originalJson = res.json;
    const redactSensitive = (obj: any): any => {
        if (!obj || typeof obj !== 'object') return obj;
        if (Array.isArray(obj)) return obj.map(redactSensitive);
        const redacted = { ...obj };
        const keysToRedact = [
            'apiKey', 'agentApiKey', 'secret', 'password', 'token', 
            'authorization', 'credentials', 'vault_key'
        ];
        for (const key of Object.keys(redacted)) {
            if (keysToRedact.some(k => key.toLowerCase().includes(k))) {
                redacted[key] = '[REDACTED]';
            } else if (typeof redacted[key] === 'object') {
                redacted[key] = redactSensitive(redacted[key]);
            }
        }
        return redacted;
    };

    res.json = function (body) {
        if ((res as any)._scrubBody && body && typeof body === 'object') {
            return originalJson.call(this, redactSensitive(body));
        }
        return originalJson.call(this, body);
    };
    next();
});

const allowedOrigins = [
    'https://www.supra-wall.com',
    'https://supra-wall.com',
    ...(process.env.NODE_ENV !== 'production' ? ['http://localhost:3000'] : [])
];
app.use(cors({ origin: allowedOrigins, credentials: true }));

// CSRF defence: reject POST/PUT/DELETE requests that lack a JSON Content-Type.
app.use((req, res, next) => {
    const method = req.method.toUpperCase();
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        const ct = req.headers["content-type"] ?? "";
        // Webhooks use raw-body parsing but still have application/json CT
        if (!ct.includes("application/json") && !ct.includes("multipart/form-data")) {
            return res.status(415).json({ error: "Unsupported Media Type: application/json required" });
        }
    }
    next();
});

// ---------------------------------------------------------------------------
// 2. Specialized Routing
// ---------------------------------------------------------------------------

// Important: Paperclip router handles its own parsing (express.raw for webhooks,
// express.json for others) to ensure HMAC verification is possible.
app.use("/v1/paperclip", paperclipRouter);

// Paperclip: Agent Invoke — top-level alias so Paperclip agents call /v1/agent/invoke.
// Must be mounted before the global express.json() to prevent double-parsing.
app.post(
    "/v1/agent/invoke",
    rateLimit({ max: 120, windowMs: 60_000, message: "Agent invoke rate limit exceeded." }),
    (req, res, next) => {
        req.url = "/invoke";
        paperclipRouter(req, res, next);
    }
);

// Global JSON body parser for all other standard routes
app.use(express.json());

// Healthcheck — returns status only. We deliberately do NOT expose DB-connection
// detail in the public response body to avoid aiding reconnaissance; detailed
// failure reasons are still logged server-side for operators.
app.get("/health", async (req, res) => {
    try {
        await pool.query("SELECT 1");
        res.status(200).json({ status: "ok" });
    } catch (err) {
        logger.error("[Health] DB connectivity check failed:", err);
        res.status(503).json({ status: "degraded" });
    }
});

// Policy Evaluation Webhook (rate limited: 120 req/min per IP)
const evaluateRateLimit = rateLimit({ max: 120, windowMs: 60_000, message: "Evaluate rate limit exceeded. Upgrade your plan or reduce request frequency." });
app.post("/v1/evaluate", evaluateRateLimit, gatekeeperAuth, resolveTier, evaluatePolicy);
app.post("/v1/evaluateAction", evaluateRateLimit, gatekeeperAuth, resolveTier, evaluatePolicy); // Alias for MCP compatibility

// Vault scrub endpoint
app.post("/v1/scrub", gatekeeperAuth, scrubToolResponse);

// Compliance Routes
app.use("/v1/compliance", complianceRouter);

// Templates Routes
app.use("/v1/templates", templatesRouter);

// Scan Routes (CI/CD)
app.use("/v1/scan", scanRouter);

// Vault Routes (rate limited: 60 req/min per IP)
app.use("/v1/vault", rateLimit({ max: 60, windowMs: 60_000, message: "Vault rate limit exceeded." }), vaultRouter);

// Threat Intel Routes
app.use("/v1/threat", threatRouter);

// Policies Routes
app.use("/v1/policies", policiesRouter);

// Approvals Routes
app.use("/v1/approvals", approvalsRouter);

// Agents Routes
app.use("/v1/agents", agentsRouter);

// Audit Logs Routes
app.use("/v1/audit-logs", auditLogsRouter);

// Tenants Routes
app.use("/v1/tenants", tenantsRouter);

// Stats Routes
app.use("/v1/stats", statsRouter);

// Content Migration Routes
app.use("/v1/content", contentRouter);

// Shield Status Route
app.use("/v1/shield", shieldRouter);

// GDPR Routes
app.use("/v1/gdpr", gdprRouter);

// Organization Members Route
app.use("/v1/members", membersRouter);

// AWS Marketplace Integration Routes (Registration URL + SNS webhook + Entitlement check)
app.use("/v1/aws", awsMarketplaceRouter);

// Export the app for Vercel
export default app;

// Only start the server listener if not on Vercel
if (process.env.NODE_ENV !== 'test' && (process.env.NODE_ENV !== "production" || !process.env.VERCEL)) {
    const start = async () => {
        try {
            await initDb();
            logger.info("[Database] Schema initialized.");

            // Start daily log purging
            purgeOldLogs().catch(err => logger.error("[Purge] Startup error:", err));
            if (process.env.NODE_ENV !== 'test') {
                setInterval(purgeOldLogs, 24 * 60 * 60 * 1000); // Once every 24h
            }

            app.listen(port, () => {
                logger.info(`[SupraWall] Gateway listening on port ${port} (Mode: ${process.env.SUPRAWALL_MODE || 'cloud'})`);
            });
        } catch (e) {
            logger.error("[Startup] Critical failure:", e);
            process.exit(1);
        }
    };

    if (require.main === module) {
        start();
    }
} else {
    // On Vercel, we still need to ensure DB is initialized
    initDb().catch(err => logger.error("Database initialization failed", { error: err }));
}

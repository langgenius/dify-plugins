// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Pool } from "pg";
import sqlite3 from "sqlite3";
import { promisify } from "util";
import dotenv from "dotenv";
import { logger } from "./logger";
import { TIER_LIMITS, Tier } from "./tier-config";

if (!process.env.VERCEL) {
    dotenv.config();
}

const rawUrl = process.env.DATABASE_URL || process.env.POSTGRES_URL || "";
// Mask password for safe logging
const maskedUrl = rawUrl.replace(/(postgresql?:\/\/)([^:]+):([^@]+)(@)/, "$1$2:****$4");
if (maskedUrl) {
    logger.info(`[DB] Initializing connection: ${maskedUrl}`);
}

let dbUrl = rawUrl.trim();

// Add SQLite fallback for local development without Docker
const isLocalNoDocker = !process.env.DATABASE_URL && !process.env.VERCEL;
let sqliteDb: sqlite3.Database | null = null;

if (isLocalNoDocker) {
    logger.warn("[DB] No DATABASE_URL found and not on Vercel. Falling back to SQLite for local development.");
    sqliteDb = new sqlite3.Database("suprawall.db");
}

// Neon / Vercel Postgres use Let's Encrypt certificates, which are in Node's default CA bundle.
// If your provider uses a custom CA, set DATABASE_CA_CERT to the PEM-encoded certificate.
const sslConfig = process.env.NODE_ENV === 'production'
    ? { rejectUnauthorized: true, ...(process.env.DATABASE_CA_CERT ? { ca: process.env.DATABASE_CA_CERT } : {}) }
    : false;

const pgPool = new Pool({
    connectionString: dbUrl || (isLocalNoDocker ? "" : (() => { throw new Error("[DB] DATABASE_URL is required in production"); })()),
    ssl: sslConfig,
    max: 20, // Increased for production concurrency
    idleTimeoutMillis: 10000, // Reduced to reclaim idle connections faster
    connectionTimeoutMillis: 5000, // Fail fast on connection stalls
});

interface QueryResult {
    rows: any[];
    rowCount: number | null;
}

export const pool = {
    query: async (text: string, params?: any[]): Promise<QueryResult> => {
        if (sqliteDb) {
            const sql = text.replace(/\$(\d+)/g, "?");
            if (sql.trim().toUpperCase().startsWith("SELECT")) {
                const all = promisify(sqliteDb.all.bind(sqliteDb));
                const rows = await all(sql, params || []) as any[];
                return { rows, rowCount: rows.length };
            } else {
                const run = promisify(sqliteDb.run.bind(sqliteDb));
                const result: any = await run(sql, params || []);
                return { rows: [], rowCount: result ? result.changes : 0 };
            }
        }
        return pgPool.query(text, params);
    },
    connect: async () => {
        if (sqliteDb) {
            // Mock client for SQLite
            return {
                query: pool.query,
                release: () => {},
            };
        }
        return pgPool.connect();
    },
    on: (event: any, listener: (...args: any[]) => void) => {
        if (!sqliteDb) pgPool.on(event, listener);
    }
};

export const initDb = async () => {
    if (sqliteDb) {
        logger.info("[DB] Initializing SQLite schema...");
        const queries = [
            `CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenantid TEXT NOT NULL,
                name TEXT,
                agentid TEXT,
                toolname TEXT NOT NULL,
                condition TEXT,
                ruletype TEXT NOT NULL,
                priority INTEGER DEFAULT 100,
                isdryrun INTEGER DEFAULT 0,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenantid TEXT NOT NULL,
                agentid TEXT,
                toolname TEXT,
                decision TEXT,
                riskscore INTEGER,
                cost_usd FLOAT DEFAULT 0,
                reason TEXT,
                arguments TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                parameters TEXT,
                metadata TEXT
            )`,
            `CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                tenantid TEXT NOT NULL,
                name TEXT NOT NULL,
                apikeyhash TEXT,
                scopes TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                slack_webhook TEXT,
                max_cost_usd FLOAT DEFAULT 10,
                budget_alert_usd FLOAT DEFAULT 8,
                max_iterations INTEGER DEFAULT 50,
                loop_detection INTEGER DEFAULT 0,
                createdat DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT,
                master_api_key TEXT,
                slack_webhook_url TEXT,
                tier TEXT DEFAULT 'open_source',
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                billing_cycle_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                tier_expires_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS tenant_usage (
                tenant_id TEXT NOT NULL,
                month TEXT NOT NULL,
                evaluation_count INTEGER DEFAULT 0,
                overage_units INTEGER DEFAULT 0,
                overage_billed_usd DECIMAL(10,4) DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (tenant_id, month)
            )`,
            `CREATE TABLE IF NOT EXISTS organization_members (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                user_email TEXT NOT NULL,
                user_id TEXT,
                role TEXT NOT NULL DEFAULT 'member',
                status TEXT DEFAULT 'pending',
                invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                accepted_at DATETIME,
                UNIQUE(tenant_id, user_email)
            )`,
            `CREATE TABLE IF NOT EXISTS sso_configs (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL UNIQUE REFERENCES tenants(id),
                provider TEXT NOT NULL,
                client_id TEXT,
                client_secret_encrypted BLOB,
                domain TEXT,
                enabled INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS vault_secrets (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                secret_name TEXT NOT NULL,
                encrypted_value BLOB NOT NULL,
                description TEXT,
                expires_at DATETIME,
                assigned_agents TEXT DEFAULT '[]',
                last_rotated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, secret_name)
            )`,
            `CREATE TABLE IF NOT EXISTS vault_access_rules (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                secret_id TEXT REFERENCES vault_secrets(id) ON DELETE CASCADE,
                allowed_tools TEXT NOT NULL DEFAULT '[]',
                max_uses_per_hour INT DEFAULT 100,
                requires_approval INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, agent_id, secret_id)
            )`,
            `CREATE TABLE IF NOT EXISTS threat_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenantid TEXT NOT NULL,
                agentid TEXT,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS threat_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenantid TEXT NOT NULL,
                entity_id TEXT NOT NULL, 
                entity_type TEXT NOT NULL,
                threat_score FLOAT DEFAULT 0,
                total_events INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenantid, entity_id, entity_type)
            )`,
            `CREATE TABLE IF NOT EXISTS approval_requests (
                id TEXT PRIMARY KEY,
                tenantid TEXT NOT NULL,
                agentid TEXT NOT NULL,
                toolname TEXT NOT NULL,
                parameters TEXT,
                status TEXT DEFAULT 'PENDING',
                decision_by TEXT,
                decision_at DATETIME,
                decision_comment TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS content_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenantid TEXT NOT NULL,
                url TEXT NOT NULL,
                type TEXT,
                primary_keyword TEXT,
                status TEXT DEFAULT 'draft',
                published_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS agent_behavioral_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                avg_args_length FLOAT DEFAULT 0,
                avg_calls_per_hour FLOAT DEFAULT 0,
                common_arg_patterns TEXT DEFAULT '[]',
                total_samples INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, agent_id, tool_name)
            )`,
            `CREATE TABLE IF NOT EXISTS semantic_analysis_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                semantic_score FLOAT NOT NULL,
                anomaly_score FLOAT,
                confidence TEXT NOT NULL,
                decision_override TEXT,
                reasoning TEXT,
                model_used TEXT,
                latency_ms INTEGER,
                parameters TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS custom_model_endpoints (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL UNIQUE,
                endpoint_url TEXT NOT NULL,
                auth_header TEXT,
                model_name TEXT,
                max_latency_ms INTEGER DEFAULT 500,
                enabled INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE TABLE IF NOT EXISTS beta_testers (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                framework TEXT,
                agent_count TEXT,
                main_risk TEXT,
                is_qualified INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            // Paperclip Integration Tables
            `CREATE TABLE IF NOT EXISTS paperclip_companies (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                paperclip_company_id TEXT NOT NULL UNIQUE,
                paperclip_api_key_encrypted BLOB,
                agent_count INTEGER DEFAULT 0,
                paperclip_version TEXT,
                api_url TEXT DEFAULT 'https://api.paperclipai.com',
                status TEXT DEFAULT 'pending',
                onboarded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE INDEX IF NOT EXISTS idx_paperclip_companies_tenant ON paperclip_companies(tenant_id)`,
            `CREATE INDEX IF NOT EXISTS idx_paperclip_companies_company ON paperclip_companies(paperclip_company_id)`,
            `CREATE TABLE IF NOT EXISTS paperclip_tokens (
                id TEXT PRIMARY KEY,
                token TEXT NOT NULL UNIQUE,
                tenant_id TEXT NOT NULL REFERENCES tenants(id),
                paperclip_company_id TEXT NOT NULL,
                tier TEXT DEFAULT 'developer',
                expires_at DATETIME NOT NULL,
                activated INTEGER DEFAULT 0,
                activation_email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            `CREATE INDEX IF NOT EXISTS idx_paperclip_tokens_token ON paperclip_tokens(token)`,
            `CREATE TABLE IF NOT EXISTS paperclip_run_tokens (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                scoped_credentials TEXT NOT NULL DEFAULT '{}',
                ttl_seconds INTEGER DEFAULT 3600,
                issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                revoked INTEGER DEFAULT 0,
                revoked_at DATETIME,
                consumed INTEGER DEFAULT 0,
                consumed_at DATETIME,
                UNIQUE(tenant_id, agent_id, run_id)
            )`,
            `CREATE INDEX IF NOT EXISTS idx_paperclip_run_tokens_run ON paperclip_run_tokens(run_id)`,
            `CREATE INDEX IF NOT EXISTS idx_paperclip_run_tokens_agent ON paperclip_run_tokens(agent_id)`,
            // Rate limiting table — created at startup, not per-request
            `CREATE TABLE IF NOT EXISTS api_rate_limits (
                key TEXT PRIMARY KEY,
                count INTEGER NOT NULL,
                reset_at BIGINT NOT NULL
            )`,
            // Compliance Templates (Snapshot versioning)
            `CREATE TABLE IF NOT EXISTS agent_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1.0.0',
                priority_order INTEGER DEFAULT 0,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                applied_by TEXT,
                custom_overrides TEXT DEFAULT '{}',
                is_active INTEGER DEFAULT 1,
                UNIQUE(agent_id, template_id, version)
            )`,
            `CREATE TABLE IF NOT EXISTS template_compliance_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                control_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                evidence TEXT DEFAULT '{}',
                UNIQUE(agent_id, template_id, control_id)
            )`,
            // Performance indices for SQLite
            `CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenantid, timestamp)`,
            `CREATE INDEX IF NOT EXISTS idx_agents_apikeyhash ON agents(apikeyhash)`,
            `CREATE INDEX IF NOT EXISTS idx_tenants_master_key ON tenants(master_api_key)`,
            `CREATE INDEX IF NOT EXISTS idx_vault_secrets_tenant ON vault_secrets(tenant_id)`,
            `CREATE INDEX IF NOT EXISTS idx_vault_access_rules_lookup ON vault_access_rules(tenant_id, agent_id, secret_id)`,
            // Insert seed data so the dashboard is not empty
            `INSERT OR IGNORE INTO tenants (id, name, tier) VALUES ('default', 'SupraWall Org', 'business')`,
            `INSERT OR IGNORE INTO agents (id, tenantid, name, status) VALUES ('agent_1', 'default', 'LinkedIn Manager', 'active')`,
            `INSERT OR IGNORE INTO agents (id, tenantid, name, status) VALUES ('agent_2', 'default', 'X.com Scout', 'active')`
        ];

        const run = promisify(sqliteDb.run.bind(sqliteDb));
        for (const q of queries) {
            await run(q);
        }
        return;
    }

    const query = `
        CREATE TABLE IF NOT EXISTS policies (
            id SERIAL PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            agentid VARCHAR(255),
            toolname VARCHAR(255) NOT NULL,
            condition TEXT,
            ruletype VARCHAR(50) NOT NULL,
            priority INTEGER DEFAULT 100,
            isdryrun BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            agentid VARCHAR(255),
            toolname VARCHAR(255),
            decision VARCHAR(50),
            riskscore INTEGER,
            cost_usd FLOAT DEFAULT 0,
            reason TEXT,
            arguments TEXT,
            timestamp TIMESTAMP DEFAULT NOW(),
            parameters JSONB,
            metadata JSONB
        );
        CREATE TABLE IF NOT EXISTS agents (
            id VARCHAR(255) PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            apikeyhash VARCHAR(255),
            scopes TEXT[] DEFAULT '{}',
            status VARCHAR(50) DEFAULT 'active',
            slack_webhook VARCHAR(255),
            max_cost_usd FLOAT DEFAULT 10,
            budget_alert_usd FLOAT DEFAULT 8,
            max_iterations INTEGER DEFAULT 50,
            loop_detection BOOLEAN DEFAULT FALSE,
            createdat TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS tenants (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            master_api_key VARCHAR(255),
            slack_webhook_url TEXT,
            tier VARCHAR(20) DEFAULT 'open_source',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            billing_cycle_start TIMESTAMP DEFAULT NOW(),
            tier_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Ensure modern billing columns exist for existing deployments
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tenants' AND column_name='stripe_customer_id') THEN
                ALTER TABLE tenants ADD COLUMN stripe_customer_id TEXT;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tenants' AND column_name='stripe_subscription_id') THEN
                ALTER TABLE tenants ADD COLUMN stripe_subscription_id TEXT;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tenants' AND column_name='billing_cycle_start') THEN
                ALTER TABLE tenants ADD COLUMN billing_cycle_start TIMESTAMP DEFAULT NOW();
            END IF;
            -- Migrate legacy 'free' tier name to 'open_source' if present
            UPDATE tenants SET tier = 'open_source' WHERE tier = 'free';
            ALTER TABLE tenants ALTER COLUMN tier SET DEFAULT 'open_source';
        END $$;

        -- Usage Metering (Usage-based billing)
        CREATE TABLE IF NOT EXISTS tenant_usage (
            tenant_id VARCHAR(255) NOT NULL,
            month VARCHAR(7) NOT NULL, -- YYYY-MM
            evaluation_count INTEGER DEFAULT 0,
            overage_units INTEGER DEFAULT 0,
            overage_billed_usd DECIMAL(10,4) DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (tenant_id, month)
        );

        -- Seats / Organization Members
        CREATE TABLE IF NOT EXISTS organization_members (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL REFERENCES tenants(id),
            user_email VARCHAR(255) NOT NULL,
            user_id VARCHAR(255), -- Firebase UID
            role VARCHAR(50) NOT NULL DEFAULT 'member', -- owner | admin | member | viewer
            status VARCHAR(50) DEFAULT 'pending', -- pending | active | removed
            invited_at TIMESTAMP DEFAULT NOW(),
            accepted_at TIMESTAMP,
            UNIQUE(tenant_id, user_email)
        );

        -- SSO Configuration
        CREATE TABLE IF NOT EXISTS sso_configs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL UNIQUE REFERENCES tenants(id),
            provider VARCHAR(100) NOT NULL, -- okta | azure-ad | google
            client_id TEXT,
            client_secret_encrypted BYTEA,
            domain TEXT,
            enabled BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Enable encryption (pgcrypto)
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        -- PERFORMANCE INDEXES (Critical for high-volume logs and policy lookups)
        CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_timestamp ON audit_logs(tenantid, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_policies_tenant_agent_tool ON policies(tenantid, agentid, toolname);
        CREATE INDEX IF NOT EXISTS idx_agents_apikeyhash ON agents(apikeyhash);
        CREATE INDEX IF NOT EXISTS idx_tenants_master_key ON tenants(master_api_key);
        CREATE INDEX IF NOT EXISTS idx_approval_requests_tenant_status ON approval_requests(tenantid, status);

        -- Unique constraint on policies(tenantid, agentid, toolname) for webhook idempotency.
        -- Prevents duplicate policy rows when agent.hired webhooks are retried.
        CREATE UNIQUE INDEX IF NOT EXISTS idx_policies_unique_credential
            ON policies(tenantid, agentid, toolname)
            WHERE agentid IS NOT NULL;

        -- Vault: encrypted secret storage
        CREATE TABLE IF NOT EXISTS vault_secrets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL,
            secret_name VARCHAR(255) NOT NULL,
            encrypted_value BYTEA NOT NULL,
            description TEXT,
            expires_at TIMESTAMP,
            assigned_agents TEXT[] DEFAULT '{}',
            last_rotated_at TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(tenant_id, secret_name)
        );
        CREATE INDEX IF NOT EXISTS idx_vault_secrets_tenant ON vault_secrets(tenant_id);

        -- Vault: access rules
        CREATE TABLE IF NOT EXISTS vault_access_rules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            secret_id UUID REFERENCES vault_secrets(id) ON DELETE CASCADE,
            allowed_tools TEXT[] NOT NULL DEFAULT '{}',
            max_uses_per_hour INT DEFAULT 100,
            requires_approval BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(tenant_id, agent_id, secret_id)
        );

        -- Vault: access logs
        CREATE TABLE IF NOT EXISTS vault_access_log (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            secret_name VARCHAR(255) NOT NULL,
            tool_name VARCHAR(255),
            action VARCHAR(50) NOT NULL, -- INJECTED | DENIED | EXPIRED | NOT_FOUND
            request_metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_vault_access_log_tenant ON vault_access_log(tenant_id, created_at DESC);

        -- Vault: rate limits
        CREATE TABLE IF NOT EXISTS vault_rate_limits (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            secret_name VARCHAR(255) NOT NULL,
            window_start TIMESTAMP NOT NULL,
            use_count INT DEFAULT 1,
            UNIQUE(tenant_id, agent_id, secret_name, window_start)
        );

        -- Threat Intel
        CREATE TABLE IF NOT EXISTS threat_events (
            id SERIAL PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            agentid VARCHAR(255),
            event_type VARCHAR(100) NOT NULL,
            severity VARCHAR(50) DEFAULT 'medium',
            details JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_threat_events_tenant ON threat_events(tenantid, timestamp DESC);

        CREATE TABLE IF NOT EXISTS threat_summaries (
            id SERIAL PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            entity_id VARCHAR(255) NOT NULL, 
            entity_type VARCHAR(50) NOT NULL,
            threat_score FLOAT DEFAULT 0,
            total_events INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NOW(),
            UNIQUE(tenantid, entity_id, entity_type)
        );

        -- Approval Queue
        CREATE TABLE IF NOT EXISTS approval_requests (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenantid VARCHAR(255) NOT NULL,
            agentid VARCHAR(255) NOT NULL,
            toolname VARCHAR(255) NOT NULL,
            parameters JSONB,
            status VARCHAR(50) DEFAULT 'PENDING',
            decision_by VARCHAR(255),
            decision_at TIMESTAMP,
            decision_comment TEXT,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Content/SEO Tasks (Migrated from Supabase)
        CREATE TABLE IF NOT EXISTS content_tasks (
            id SERIAL PRIMARY KEY,
            tenantid VARCHAR(255) NOT NULL,
            url VARCHAR(555) NOT NULL,
            type VARCHAR(100),
            primary_keyword VARCHAR(255),
            status VARCHAR(50) DEFAULT 'draft',
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Layer 2: AI Semantic Analysis Engine
        CREATE TABLE IF NOT EXISTS agent_behavioral_baselines (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            tool_name VARCHAR(255) NOT NULL,
            avg_args_length FLOAT DEFAULT 0,
            avg_calls_per_hour FLOAT DEFAULT 0,
            common_arg_patterns JSONB DEFAULT '[]',
            total_samples INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NOW(),
            UNIQUE(tenant_id, agent_id, tool_name)
        );

        CREATE INDEX IF NOT EXISTS idx_baselines_tenant_agent
            ON agent_behavioral_baselines(tenant_id, agent_id);

        CREATE TABLE IF NOT EXISTS semantic_analysis_log (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            tool_name VARCHAR(255) NOT NULL,
            semantic_score FLOAT NOT NULL,
            anomaly_score FLOAT,
            confidence VARCHAR(20) NOT NULL,
            decision_override VARCHAR(20),
            reasoning TEXT,
            model_used VARCHAR(100),
            latency_ms INTEGER,
            parameters JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_semantic_log_tenant
            ON semantic_analysis_log(tenant_id, timestamp DESC);

        CREATE TABLE IF NOT EXISTS custom_model_endpoints (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL UNIQUE,
            endpoint_url VARCHAR(500) NOT NULL,
            auth_header VARCHAR(500),
            model_name VARCHAR(100),
            max_latency_ms INTEGER DEFAULT 500,
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS beta_testers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            framework VARCHAR(100),
            agent_count VARCHAR(50),
            main_risk TEXT,
            is_qualified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Paperclip Integration: company registry
        CREATE TABLE IF NOT EXISTS paperclip_companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL REFERENCES tenants(id),
            paperclip_company_id VARCHAR(255) NOT NULL UNIQUE,
            paperclip_api_key_encrypted BYTEA,
            agent_count INTEGER DEFAULT 0,
            paperclip_version VARCHAR(50),
            api_url VARCHAR(500) DEFAULT 'https://api.paperclipai.com',
            status VARCHAR(50) DEFAULT 'pending',
            onboarded_at TIMESTAMP DEFAULT NOW()
        );
        -- Ensure api_url column exists on existing deployments
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='paperclip_companies' AND column_name='api_url') THEN
                ALTER TABLE paperclip_companies ADD COLUMN api_url VARCHAR(500) DEFAULT 'https://api.paperclipai.com';
            END IF;
        END $$;
        CREATE INDEX IF NOT EXISTS idx_paperclip_companies_tenant ON paperclip_companies(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_paperclip_companies_company ON paperclip_companies(paperclip_company_id);

        -- Paperclip Integration: temporary API keys for frictionless install
        CREATE TABLE IF NOT EXISTS paperclip_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            token VARCHAR(255) NOT NULL UNIQUE,
            tenant_id VARCHAR(255) NOT NULL REFERENCES tenants(id),
            paperclip_company_id VARCHAR(255) NOT NULL,
            tier VARCHAR(20) DEFAULT 'developer',
            expires_at TIMESTAMP NOT NULL,
            activated BOOLEAN DEFAULT FALSE,
            activation_email VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_paperclip_tokens_token ON paperclip_tokens(token);

        -- Paperclip Integration: per-invocation scoped run tokens
        CREATE TABLE IF NOT EXISTS paperclip_run_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            run_id VARCHAR(255) NOT NULL,
            scoped_credentials JSONB NOT NULL DEFAULT '{}',
            ttl_seconds INTEGER DEFAULT 3600,
            issued_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP NOT NULL,
            revoked BOOLEAN DEFAULT FALSE,
            revoked_at TIMESTAMP,
            consumed BOOLEAN DEFAULT FALSE,
            consumed_at TIMESTAMP,
            UNIQUE(tenant_id, agent_id, run_id)
        );

        -- Ensure modern consumed columns exist for existing deployments
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='paperclip_run_tokens' AND column_name='consumed') THEN
                ALTER TABLE paperclip_run_tokens ADD COLUMN consumed BOOLEAN DEFAULT FALSE;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='paperclip_run_tokens' AND column_name='consumed_at') THEN
                ALTER TABLE paperclip_run_tokens ADD COLUMN consumed_at TIMESTAMP;
            END IF;
        END $$;
        CREATE INDEX IF NOT EXISTS idx_paperclip_run_tokens_run ON paperclip_run_tokens(run_id);
        CREATE INDEX IF NOT EXISTS idx_paperclip_run_tokens_agent ON paperclip_run_tokens(agent_id);

        CREATE TABLE IF NOT EXISTS api_rate_limits (
            key TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            reset_at BIGINT NOT NULL
        );

        -- Compliance Templates
        CREATE TABLE IF NOT EXISTS agent_templates (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            template_id VARCHAR(50) NOT NULL,
            version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
            priority_order INTEGER DEFAULT 0,
            applied_at TIMESTAMP DEFAULT NOW(),
            applied_by VARCHAR(255),
            custom_overrides JSONB DEFAULT '{}',
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(agent_id, template_id, version)
        );

        CREATE TABLE IF NOT EXISTS template_compliance_status (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            template_id VARCHAR(50) NOT NULL,
            control_id VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            last_checked TIMESTAMP DEFAULT NOW(),
            evidence JSONB DEFAULT '{}',
            UNIQUE(agent_id, template_id, control_id)
        );
    `;
    await pool.query(query);
};

/**
 * Daily Background Task: Purges logs older than tenant-specific retention limits.
 * Also cleans up expired paperclip tokens and run tokens to prevent unbounded growth.
 */
export async function purgeOldLogs(): Promise<void> {
    logger.info("[Purge] Starting daily audit log cleanup...");
    try {
        const tiers = (Object.entries(TIER_LIMITS) as [Tier, typeof TIER_LIMITS[Tier]][]).map(
            ([id, cfg]) => ({ id, days: cfg.auditRetentionDays })
        );

        for (const tier of tiers) {
            const result = await pool.query(
                `DELETE FROM audit_logs WHERE tenantid IN (
                    SELECT id FROM tenants WHERE tier = $1
                 ) AND timestamp < NOW() - ($2 || ' days')::INTERVAL`,
                [tier.id, tier.days]
            );
            if (result.rowCount && result.rowCount > 0) {
                logger.info(`[Purge] Cleared ${result.rowCount} logs for ${tier.id} tier.`);
            }
        }

        // Purge expired paperclip temp tokens (> 7 days past expiry gives activation grace period)
        const expiredTokens = await pool.query(
            `DELETE FROM paperclip_tokens WHERE expires_at < NOW() - INTERVAL '7 days' RETURNING id`
        );
        if (expiredTokens.rowCount && expiredTokens.rowCount > 0) {
            logger.info(`[Purge] Cleared ${expiredTokens.rowCount} expired paperclip_tokens.`);
        }

        // Purge revoked and expired run tokens (> 24h post-expiry)
        const expiredRunTokens = await pool.query(
            `DELETE FROM paperclip_run_tokens
             WHERE (revoked = TRUE OR expires_at < NOW() - INTERVAL '24 hours')
             RETURNING id`
        );
        if (expiredRunTokens.rowCount && expiredRunTokens.rowCount > 0) {
            logger.info(`[Purge] Cleared ${expiredRunTokens.rowCount} expired paperclip_run_tokens.`);
        }

        // Purge expired rate limit entries
        await pool.query(`DELETE FROM api_rate_limits WHERE reset_at < $1`, [Date.now()]);

        logger.info("[Purge] Audit log cleanup complete.");
    } catch (err) {
        logger.error("[Purge] Failed to cleanup logs:", err);
    }
}

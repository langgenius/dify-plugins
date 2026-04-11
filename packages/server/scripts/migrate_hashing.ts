// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { pool } from "../src/db";
import { hashApiKey } from "../src/util/hash";
import { logger } from "../src/logger";

async function migrate() {
    logger.info("[Migration] Starting database credential hashing...");

    try {
        // 1. Migrate Agent API Keys
        const agents = await pool.query("SELECT id, apikeyhash FROM agents");
        let agentCount = 0;

        for (const agent of agents.rows) {
            // Check if it's already hashed (SHA-256 hex is 64 chars)
            if (agent.apikeyhash && agent.apikeyhash.length === 64 && /^[a-f0-9]+$/i.test(agent.apikeyhash)) {
                continue;
            }

            const hashed = hashApiKey(agent.apikeyhash);
            await pool.query(
                "UPDATE agents SET apikeyhash = $1 WHERE id = $2",
                [hashed, agent.id]
            );
            agentCount++;
        }
        logger.info(`[Migration] Hashed ${agentCount} Agent API keys.`);

        // 2. Migrate Master API Keys
        const tenants = await pool.query("SELECT id, master_api_key FROM tenants");
        let tenantCount = 0;

        for (const tenant of tenants.rows) {
            if (!tenant.master_api_key) continue;

            // Check if already hashed
            if (tenant.master_api_key.length === 64 && /^[a-f0-9]+$/i.test(tenant.master_api_key)) {
                continue;
            }

            const hashed = hashApiKey(tenant.master_api_key);
            await pool.query(
                "UPDATE tenants SET master_api_key = $1 WHERE id = $2",
                [hashed, tenant.id]
            );
            tenantCount++;
        }
        logger.info(`[Migration] Hashed ${tenantCount} Tenant Master keys.`);

        logger.info("[Migration] Credential hashing complete.");
    } catch (err) {
        logger.error("[Migration] Critical failure during hashing:", err);
        process.exit(1);
    }
}

if (require.main === module) {
    migrate().then(() => process.exit(0));
}

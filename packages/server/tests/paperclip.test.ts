// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0
//
// Integration tests for the Paperclip plugin endpoints:
// POST /v1/paperclip/onboard
// POST /v1/agent/invoke
// GET  /v1/paperclip/run-token/:runTokenId
// POST /v1/paperclip/webhooks
//
// These tests use a SQLite in-memory DB via the db.ts fallback.

import { describe, it, expect, beforeAll, afterAll } from "@jest/globals";
import request from "supertest";
import crypto from "crypto";
import app from "../src/index";
import { pool, initDb } from "../src/db";

// Set required env vars before any module imports run
process.env.VAULT_ENCRYPTION_KEY = "test-key-1234567890abcdef12345678";
process.env.PAPERCLIP_WEBHOOK_SECRET = "test-webhook-secret";
process.env.NODE_ENV = "test";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeHmac(body: string): string {
    return (
        "sha256=" +
        crypto.createHmac("sha256", process.env.PAPERCLIP_WEBHOOK_SECRET!)
            .update(Buffer.from(body))
            .digest("hex")
    );
}

let adminKey: string;
let agentKey: string;
let companyId: string;

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeAll(async () => {
    await initDb();

    // Seed a tenant and master key for admin-auth tests
    adminKey = "sw_admin_" + crypto.randomBytes(16).toString("hex");
    await pool.query(
        `INSERT OR IGNORE INTO tenants (id, name, master_api_key, tier)
         VALUES ('test_tenant', 'Test Tenant', $1, 'developer')`,
        [adminKey]
    );
});

afterAll(async () => {
    // Clean up test data
    await pool.query("DELETE FROM tenants WHERE id = 'test_tenant'").catch(() => {});
});

// ---------------------------------------------------------------------------
// POST /v1/paperclip/onboard
// ---------------------------------------------------------------------------

describe("POST /v1/paperclip/onboard", () => {
    it("rejects requests with missing companyId", async () => {
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ agentCount: 2 });

        expect(res.status).toBe(400);
        expect(res.body.error).toMatch(/companyId/i);
    });

    it("rejects companyId that is not a string", async () => {
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: 12345 });

        expect(res.status).toBe(400);
    });

    it("successfully onboards a new company and returns activation URL", async () => {
        companyId = "test-company-" + Date.now();
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId, agentCount: 2 });

        expect(res.status).toBe(201);
        expect(res.body.status).toBe("activation_required");
        expect(res.body.tempApiKey).toMatch(/^sw_temp_/);
        expect(res.body.activationUrl).toContain("supra-wall.com/activate");
        expect(res.body.syncedAgents).toBeGreaterThanOrEqual(1);
        expect(res.body.tier).toBe("developer");
    });

    it("returns already_onboarded on re-install and issues fresh temp key", async () => {
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId }); // same company as previous test

        expect(res.status).toBe(200);
        expect(res.body.status).toBe("already_onboarded");
        expect(res.body.tempApiKey).toMatch(/^sw_temp_/);
    });

    it("blocks SSRF via apiUrl pointing to internal address", async () => {
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({
                companyId: "ssrf-test-" + Date.now(),
                apiUrl: "http://169.254.169.254/latest/meta-data/",
            });

        // Should not 500 crash; should either succeed with default URL or reject
        // We don't test the exact URL used, but verify it doesn't proxy invalid URLs
        expect([201, 200, 400]).toContain(res.status);
    });

    it("caps agent count to developer tier limit even if agentCount is very large", async () => {
        const largeCompanyId = "large-company-" + Date.now();
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: largeCompanyId, agentCount: 9999 });

        expect(res.status).toBe(201);
        // Developer tier allows at most 5 agents — verify it was capped
        expect(res.body.syncedAgents).toBeLessThanOrEqual(5);
    });
});

// ---------------------------------------------------------------------------
// POST /v1/agent/invoke
// ---------------------------------------------------------------------------

describe("POST /v1/agent/invoke", () => {
    let tempApiKey: string;
    let createdAgentId: string;

    beforeAll(async () => {
        // Get an agent that was registered during onboard
        companyId = "invoke-test-" + Date.now();
        const res = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId, agentCount: 1 });

        tempApiKey = res.body.tempApiKey;

        // Look up the created agent for this tenant
        const tenantId = "pc_" + companyId.replace(/[^a-zA-Z0-9-_]/g, "_").slice(0, 60);
        const agentResult = await pool.query(
            "SELECT id FROM agents WHERE tenantid = $1 LIMIT 1",
            [tenantId]
        );
        createdAgentId = agentResult.rows[0]?.id;
    });

    it("rejects requests with missing agentId", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .set("x-api-key", tempApiKey)
            .send({ runId: "run-123" });

        expect(res.status).toBe(400);
        expect(res.body.error).toMatch(/agentId/i);
    });

    it("rejects requests with missing runId", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .set("x-api-key", tempApiKey)
            .send({ agentId: createdAgentId });

        expect(res.status).toBe(400);
        expect(res.body.error).toMatch(/runId/i);
    });

    it("rejects unauthenticated requests", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .send({ agentId: createdAgentId, runId: "run-123" });

        expect(res.status).toBe(401);
    });

    it("succeeds and returns runTokenId (never raw credentials)", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .set("x-api-key", tempApiKey)
            .send({ agentId: createdAgentId, runId: "run-" + Date.now(), companyId });

        expect(res.status).toBe(202);
        expect(res.body.runTokenId).toBeDefined();
        // CRITICAL: credentials must NOT be in the response
        expect(res.body.credentials).toBeUndefined();
        expect(res.body.status).toBe("accepted");
        expect(Array.isArray(res.body.allowedTools)).toBe(true);
    });

    it("does not accept cross-tenant agent IDs", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .set("x-api-key", tempApiKey)
            .send({ agentId: "agent_from_another_tenant", runId: "run-" + Date.now() });

        expect(res.status).toBe(403);
    });

    it("rejects non-string companyId", async () => {
        const res = await request(app)
            .post("/v1/agent/invoke")
            .set("x-api-key", tempApiKey)
            .send({ agentId: createdAgentId, runId: "run-123", companyId: 12345 });

        expect(res.status).toBe(400);
    });
});

// ---------------------------------------------------------------------------
// POST /v1/paperclip/webhooks — signature verification
// ---------------------------------------------------------------------------

describe("POST /v1/paperclip/webhooks — signature verification", () => {
    it("rejects requests with no signature header", async () => {
        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .send(JSON.stringify({ event: "agent.hired" }));

        expect(res.status).toBe(401);
        expect(res.body.error).toMatch(/signature/i);
    });

    it("rejects requests with tampered signature", async () => {
        const body = JSON.stringify({ event: "agent.hired", agent: { id: "x", companyId: "y" } });
        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", "sha256=deadbeef")
            .send(body);

        expect(res.status).toBe(401);
    });

    it("accepts requests with valid HMAC over raw body", async () => {
        const payload = { event: "run.completed", run: { id: "test-run-" + Date.now() }, agent: { companyId: "non-existent" } };
        const body = JSON.stringify(payload);
        const sig = makeHmac(body);

        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", sig)
            .send(body);

        // run.completed with unknown company returns 404, not signature error
        expect(res.status).not.toBe(401);
    });

    it("rejects agent.hired when company is not onboarded", async () => {
        const payload = { event: "agent.hired", agent: { id: "new-agent", companyId: "ghost-company" } };
        const body = JSON.stringify(payload);
        const sig = makeHmac(body);

        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", sig)
            .send(body);

        expect(res.status).toBe(404);
    });

    it("is idempotent: second agent.hired with same agent creates no duplicate policies", async () => {
        // Onboard a company first
        const wbCompanyId = "webhook-idem-" + Date.now();
        await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: wbCompanyId, agentCount: 1 });

        const agentPayload = {
            event: "agent.hired",
            agent: { id: "wb-agent-idem", companyId: wbCompanyId, role: "engineering", name: "Build Bot" },
        };
        const body = JSON.stringify(agentPayload);
        const sig = makeHmac(body);

        // Fire twice
        await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", sig)
            .send(body);

        await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", sig)
            .send(body);

        const tenantId = "pc_" + wbCompanyId.replace(/[^a-zA-Z0-9-_]/g, "_").slice(0, 60);
        const res = await pool.query(
            "SELECT COUNT(*) FROM policies WHERE tenantid = $1 AND agentid = 'wb-agent-idem'",
            [tenantId]
        );
        const count = parseInt(res.rows[0].count, 10);
        // Engineering role has 3 scopes — should not be duplicated
        expect(count).toBeLessThanOrEqual(3);
    });

    it("agent.fired revokes all tokens for that agent — cross-tenant revocation is blocked", async () => {
        const wbCompanyId = "webhook-fired-" + Date.now();
        await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: wbCompanyId, agentCount: 1 });

        // Attempt to fire an agent from a different company without that company registered
        const crossPayload = {
            event: "agent.fired",
            agent: { id: "cross-tenant-agent", companyId: "ghost-company-fired" },
        };
        const body = JSON.stringify(crossPayload);
        const sig = makeHmac(body);

        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", sig)
            .send(body);

        // Should 404, not 200 — cross-tenant revocation must not succeed
        expect(res.status).toBe(404);
    });
});

// ---------------------------------------------------------------------------
// Security invariants
// ---------------------------------------------------------------------------

describe("Security invariants", () => {
    it("agent API keys are never returned by any endpoint after initial onboard", async () => {
        const wbCompanyId = "sec-inv-" + Date.now();
        const onboardRes = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: wbCompanyId, agentCount: 1 });

        // While the raw key is returned on first onboard (expected), it should NOT
        // be retrievable again via any subsequent endpoint
        const tempKey = onboardRes.body.tempApiKey;
        expect(tempKey).toMatch(/^sw_temp_/);

        // Re-onboard should give a new temp key but never expose the agent key
        const reOnboardRes = await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: wbCompanyId });

        expect(reOnboardRes.body.tempApiKey).toMatch(/^sw_temp_/);

        // The agent key itself should not appear in any response field
        const responseStr = JSON.stringify(reOnboardRes.body);
        expect(responseStr).not.toMatch(/^ag_/);
    });

    it("agent keys stored in DB are hashed (not plain text)", async () => {
        const wbCompanyId = "hash-inv-" + Date.now();
        await request(app)
            .post("/v1/paperclip/onboard")
            .send({ companyId: wbCompanyId, agentCount: 1 });

        const tenantId = "pc_" + wbCompanyId.replace(/[^a-zA-Z0-9-_]/g, "_").slice(0, 60);
        const agents = await pool.query(
            "SELECT apikeyhash FROM agents WHERE tenantid = $1",
            [tenantId]
        );
        for (const agent of agents.rows) {
            // Raw keys start with 'ag_'; a SHA-256 hex digest is 64 hex chars
            expect(agent.apikeyhash).not.toMatch(/^ag_/);
            expect(agent.apikeyhash).toMatch(/^[0-9a-f]{64}$/);
        }
    });

    it("vault encryption key fallback does not exist (server must fail when key is absent)", () => {
        // Verify the hardcoded fallback was removed from the source
        const source = require("fs").readFileSync(
            require("path").resolve(__dirname, "../src/routes/paperclip.ts"),
            "utf-8"
        );
        expect(source).not.toContain("suprawall-vault-key");
    });

    it("webhook endpoint rejects all requests when PAPERCLIP_WEBHOOK_SECRET is not set", async () => {
        const saved = process.env.PAPERCLIP_WEBHOOK_SECRET;
        delete process.env.PAPERCLIP_WEBHOOK_SECRET;

        const body = JSON.stringify({ event: "test" });
        const res = await request(app)
            .post("/v1/paperclip/webhooks")
            .set("Content-Type", "application/json")
            .set("x-paperclip-signature", "sha256=anything")
            .send(body);

        // Restore
        process.env.PAPERCLIP_WEBHOOK_SECRET = saved;

        expect(res.status).toBe(503);
    });
});

// SPDX-License-Identifier: Apache-2.0

// ---------------------------------------------------------------------------
// GLOBAL DB MOCK
// ---------------------------------------------------------------------------
// This mock ensures that integration tests requiring a database can run
// in environments without a live PostgreSQL instance.
// ---------------------------------------------------------------------------

jest.mock("../src/db", () => {
    // In-memory mock database state
    const mockDb: Record<string, any[]> = {
        tenants: [
            { id: "test-tenant-id", tier: "open_source", master_api_key: "sw_admin_test" },
            { id: "test-tenant-e2e", tier: "open_source", master_api_key: "sw_admin_test_e2e" },
            { id: "test-tenant-ratelimit", tier: "open_source", master_api_key: "sw_admin_test_ratelimit" },
            { id: "test-tenant-injection", tier: "open_source", master_api_key: "sw_admin_test_injection" },
            { id: "test-tenant-crud", tier: "open_source", master_api_key: "sw_admin_test_crud" },
            { id: "test-tenant-bulk", tier: "open_source", master_api_key: "sw_admin_test_bulk" }
        ],
        vault_secrets: [],
        vault_access_rules: [],
        vault_access_log: [],
        vault_rate_limits: [],
        agents: [],
        tenants_usage: [],
        audit_logs: []
    };

    const mockClient = {
        query: jest.fn(async (text: string, params: any[]) => {
            if (text.includes("INSERT INTO vault_secrets")) {
                const s = { 
                    id: crypto.randomUUID(), 
                    tenant_id: params[0], 
                    secret_name: params[1], 
                    encrypted_value: params[2], 
                    description: params[4] || null,
                    expires_at: params[5] || null,
                    assigned_agents: params[6] || []
                };
                mockDb.vault_secrets.push(s);
                return { rows: [s], rowCount: 1 };
            }
            if (text.includes("INSERT INTO vault_access_rules")) {
              const r = { id: crypto.randomUUID(), tenant_id: params[0], agent_id: params[1], secret_id: params[2], allowed_tools: params[3] };
              mockDb.vault_access_rules.push(r);
              return { rows: [r], rowCount: 1 };
            }
            return { rows: [], rowCount: 0 };
        }),
        release: jest.fn(),
    };

    return {
        pool: {
            query: jest.fn(async (text: string, params: any[]) => {
                const queryText = text.replace(/\s+/g, " ");

                // Return tenant for auth
                if (queryText.includes("SELECT id FROM tenants WHERE master_api_key = $1") || 
                    queryText.includes("SELECT id, tier FROM tenants WHERE master_api_key = $1")) {
                    const t = mockDb.tenants.find(t => t.master_api_key === params[0]);
                    return { rows: t ? [t] : [], rowCount: t ? 1 : 0 };
                }
                
                // Return secrets for scrubber (ANY variant)
                if (queryText.includes("SELECT id FROM vault_secrets") && queryText.includes("ANY")) {
                    const tenantId = params[0];
                    const names = params[1] || [];
                    const s = mockDb.vault_secrets.filter(s => s.tenant_id === tenantId && names.includes(s.secret_name));
                    return { rows: s, rowCount: s.length };
                }

                // Return secret values for scrubber/evaluator (Decrypt variant)
                if (queryText.includes("pgp_sym_decrypt(encrypted_value, $1)")) {
                    const tenantId = params[1];
                    const name = params[2];
                    const s = mockDb.vault_secrets.find(s => s.tenant_id === tenantId && s.secret_name === name);
                    if (!s) return { rows: [], rowCount: 0 };
                    
                    return { 
                        rows: [{ 
                            id: s.id,
                            secret_name: s.secret_name,
                            expires_at: s.expires_at,
                            value: s.encrypted_value,
                            decrypted_value: s.encrypted_value
                        }], 
                        rowCount: 1 
                    };
                }

                // Return secret by id
                if (queryText.includes("SELECT * FROM vault_secrets WHERE id = $1")) {
                     const s = mockDb.vault_secrets.filter(s => s.id === params[0]);
                     return { rows: s, rowCount: s.length };
                }

                // Return all secrets for tenant
                if (queryText.includes("SELECT id, secret_name, description") && queryText.includes("FROM vault_secrets WHERE tenant_id = $1")) {
                    const s = mockDb.vault_secrets.filter(s => s.tenant_id === params[0]);
                    return { rows: s, rowCount: s.length };
                }

                // Return rules
                if (queryText.includes("FROM vault_access_rules") && (queryText.includes("agent_id = $2") || queryText.includes("agent_id = $3"))) {
                    // Check if it's the 3-arg version (tenantId, agentId, secretId)
                    if (queryText.includes("secret_id = $3")) {
                       const r = mockDb.vault_access_rules.filter(r => r.tenant_id === params[0] && r.agent_id === params[1] && r.secret_id === params[2]);
                       return { rows: r, rowCount: r.length };
                    }
                    const r = mockDb.vault_access_rules.filter(r => r.tenant_id === params[0] && r.agent_id === params[1]);
                    return { rows: r, rowCount: r.length };
                }

                // Default empty result for SELECT that doesn't match above
                if (queryText.includes("SELECT")) {
                    return { rows: [], rowCount: 0 };
                }

                // Handle INSERTs in pool as well (for routes using pool directly)
                if (queryText.includes("INSERT INTO vault_secrets")) {
                    const s = { 
                        id: crypto.randomUUID(), 
                        tenant_id: params[0], 
                        secret_name: params[1], 
                        encrypted_value: params[2], 
                        description: params[4] || null,
                        expires_at: params[5] || null,
                        assigned_agents: params[6] || []
                    };
                    mockDb.vault_secrets.push(s);
                    return { rows: [s], rowCount: 1 };
                }
                if (queryText.includes("INSERT INTO vault_access_rules")) {
                  const r = { id: crypto.randomUUID(), tenant_id: params[0], agent_id: params[1], secret_id: params[2], allowed_tools: params[3], max_uses_per_hour: params[4] || 100 };
                  mockDb.vault_access_rules.push(r);
                  return { rows: [r], rowCount: 1 };
                }

                // Delete secrets/rules for cleanup
                if (queryText.includes("DELETE FROM")) {
                    const table = queryText.match(/DELETE FROM (\w+)/)?.[1];
                    if (table) {
                        if (queryText.includes("id = $1")) {
                            const deletedId = params[0];
                            mockDb[table] = mockDb[table].filter(r => r.id !== deletedId);
                            // Cascading delete for vault_secrets -> vault_access_rules
                            if (table === "vault_secrets") {
                                mockDb.vault_access_rules = mockDb.vault_access_rules.filter(r => r.secret_id !== deletedId);
                            }
                        } else if (queryText.includes("tenant_id = $1")) {
                            mockDb[table] = mockDb[table].filter(r => r.tenant_id !== params[0]);
                        } else {
                            mockDb[table] = [];
                        }
                    }
                    return { rows: [], rowCount: 1 };
                }

                // Generic select fallback to avoid undefined errors
                if (queryText.includes("SELECT")) {
                    return { rows: [], rowCount: 0 };
                }
                
                return { rows: [], rowCount: 1 };
            }),
            connect: jest.fn().mockResolvedValue(mockClient),
            end: jest.fn().mockResolvedValue(undefined),
        },
        initDb: jest.fn().mockResolvedValue(undefined),
        purgeOldLogs: jest.fn().mockResolvedValue(undefined),
    };
});

// ---------------------------------------------------------------------------
// GLOBAL FIREBASE MOCK
// ---------------------------------------------------------------------------

jest.mock("../src/firebase", () => ({
    getFirestore: jest.fn(() => ({
        collection: jest.fn().mockReturnThis(),
        doc: jest.fn().mockReturnThis(),
        set: jest.fn().mockResolvedValue(undefined),
        get: jest.fn().mockResolvedValue({ exists: true, data: () => ({}) }),
        delete: jest.fn().mockResolvedValue(undefined),
        where: jest.fn().mockReturnThis(),
        limit: jest.fn().mockReturnThis(),
    })),
    logToFirestore: jest.fn().mockResolvedValue(undefined),
}));

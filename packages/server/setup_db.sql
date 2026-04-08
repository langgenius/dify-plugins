-- Agents
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenantid TEXT NOT NULL,
    name TEXT NOT NULL,
    apikey TEXT UNIQUE NOT NULL,
    scopes TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'active',
    max_cost_usd DECIMAL(10,4) DEFAULT 10.0,
    budget_alert_usd DECIMAL(10,4) DEFAULT 8.0,
    max_iterations INTEGER DEFAULT 50,
    loop_detection BOOLEAN DEFAULT true,
    slack_webhook TEXT,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tenants / Workspaces
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY, -- Firebase UID
    name TEXT,
    master_api_key TEXT,
    slack_webhook_url TEXT,
    notification_email TEXT,
    webhook_url TEXT,
    webhook_secret TEXT,
    db_type TEXT DEFAULT 'postgres',
    db_string TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Policies
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenantid TEXT NOT NULL,
    agentid TEXT, -- optional, if null apply to all agents in tenant
    toolname TEXT NOT NULL,
    condition TEXT,
    ruletype TEXT NOT NULL, -- ALLOW, DENY, REQUIRE_APPROVAL
    priority INTEGER DEFAULT 100,
    isdryrun BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Approval Requests
CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenantid TEXT NOT NULL,
    agentid TEXT NOT NULL,
    toolname TEXT NOT NULL,
    parameters TEXT,
    status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
    decision_by TEXT,
    decision_at TIMESTAMP WITH TIME ZONE,
    decision_comment TEXT,
    metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenantid TEXT NOT NULL,
    agentid TEXT NOT NULL,
    toolname TEXT NOT NULL,
    arguments TEXT,              -- Legacy/Plaintext fields
    parameters JSONB,            -- Legacy/Plaintext fields
    encrypted_arguments TEXT,    -- Shredded fields
    encrypted_context TEXT,      -- Shredded fields
    encrypted_response TEXT,     -- Shredded fields
    subject_id TEXT DEFAULT 'entire_tenant', -- Used to lookup data key
    riskscore INTEGER,
    metadata JSONB,
    decision TEXT NOT NULL,
    reason TEXT,
    sessionid TEXT,
    agentrole TEXT,
    cost_usd DECIMAL(10,6),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Threat Events
CREATE TABLE IF NOT EXISTS threat_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenantid TEXT NOT NULL,
    agentid TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vault Secrets
CREATE TABLE IF NOT EXISTS vault_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    secret_name TEXT NOT NULL,
    encrypted_value BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, secret_name)
);

-- ══════════════════════════════════════════════════════════════
-- Layer 2: AI Semantic Analysis Engine
-- ══════════════════════════════════════════════════════════════

-- Behavioral Baselines — per-agent/per-tool running averages
CREATE TABLE IF NOT EXISTS agent_behavioral_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    avg_args_length FLOAT DEFAULT 0,
    avg_calls_per_hour FLOAT DEFAULT 0,
    common_arg_patterns JSONB DEFAULT '[]',
    total_samples INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, agent_id, tool_name)
);

CREATE INDEX IF NOT EXISTS idx_baselines_tenant_agent
    ON agent_behavioral_baselines(tenant_id, agent_id);

-- Semantic Analysis Log — audit trail for every Layer 2 decision
CREATE TABLE IF NOT EXISTS semantic_analysis_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    parameters JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_semantic_log_tenant
    ON semantic_analysis_log(tenant_id, timestamp DESC);

-- Custom Model Endpoints — enterprise customers' fine-tuned models
CREATE TABLE IF NOT EXISTS custom_model_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL UNIQUE,
    endpoint_url TEXT NOT NULL,
    auth_header TEXT,
    model_name TEXT,
    max_latency_ms INTEGER DEFAULT 500,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GDPR Erasure Logs — records cryptographic shredding events
CREATE TABLE IF NOT EXISTS gdpr_erasure_log (
    erasure_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,       -- specific user or 'entire_tenant'
    requested_by TEXT NOT NULL,       -- who made the request
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    method TEXT NOT NULL DEFAULT 'cryptographic_shredding',
    receipt_json JSONB NOT NULL,      -- signed receipt for the enterprise's records
    receipt_hash TEXT NOT NULL        -- SHA-256 of receipt for tamper detection
);

-- Tenant Data Keys — stores the shreddable encryption keys per tenant/subject
CREATE TABLE IF NOT EXISTS tenant_data_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    encrypted_key BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, subject_id)
);

-- ══════════════════════════════════════════════════════════════
-- Compliance Templates
-- ══════════════════════════════════════════════════════════════

-- Track which template(s) are applied to each agent (Point-in-Time Snapshots)
CREATE TABLE IF NOT EXISTS agent_templates (
  id SERIAL PRIMARY KEY,
  agent_id TEXT NOT NULL,
  template_id VARCHAR(50) NOT NULL,
  version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
  priority_order INT DEFAULT 0,
  applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  applied_by VARCHAR(255),
  custom_overrides JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT TRUE,
  UNIQUE(agent_id, template_id, version)
);

-- Template compliance status per agent
CREATE TABLE IF NOT EXISTS template_compliance_status (
  id SERIAL PRIMARY KEY,
  agent_id TEXT NOT NULL,
  template_id VARCHAR(50) NOT NULL,
  control_id VARCHAR(50) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending', -- pending, compliant, non_compliant, partial
  last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  evidence JSONB DEFAULT '{}',
  UNIQUE(agent_id, template_id, control_id)
);


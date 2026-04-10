

export interface SemanticAnalysisRequest {
    tenantId: string;
    agentId: string;
    toolName: string;
    args: unknown;
    argsString: string;
    delegationChain?: string[];
    semanticLayer: string;
    customEndpoint?: string;
}

export interface SemanticAnalysisResult {
    semanticScore: number;
    anomalyScore: number | null;
    confidence: 'high' | 'medium' | 'low';
    decision: 'DENY' | 'REQUIRE_APPROVAL' | 'FLAG' | null;
    reasoning: string;
    latencyMs: number;
    modelUsed: string;
}

interface QueryResult<T = Record<string, unknown>> {
    rows: T[];
}

interface IDatabasePool {
    query<T = Record<string, unknown>>(text: string, params?: unknown[]): Promise<QueryResult<T>>;
}

interface EnvInfo {
    SUPRAWALL_DENY_THRESHOLD?: string;
    SUPRAWALL_APPROVAL_THRESHOLD?: string;
    SUPRAWALL_FLAG_THRESHOLD?: string;
    SUPRAWALL_SEMANTIC_LLM_KEY?: string;
    SUPRAWALL_SEMANTIC_MODEL?: string;
    SUPRAWALL_SEMANTIC_TIMEOUT_MS?: string;
}

interface Logger {
    warn(message: string, meta?: Record<string, unknown>): void;
    error(message: string, meta?: Record<string, unknown>): void;
}

export async function analyzeCall(
    pool: IDatabasePool,
    envInfo: EnvInfo,
    logger: Logger,
    req: SemanticAnalysisRequest
): Promise<SemanticAnalysisResult> {
    const start = Date.now();
    const thresholds = {
        denyAbove: parseFloat(envInfo.SUPRAWALL_DENY_THRESHOLD || '0.85'),
        approvalAbove: parseFloat(envInfo.SUPRAWALL_APPROVAL_THRESHOLD || '0.60'),
        flagAbove: parseFloat(envInfo.SUPRAWALL_FLAG_THRESHOLD || '0.35'),
    };

    const prompt = buildAnalysisPrompt(req);

    let llmResult: { score: number; reasoning: string; model: string };
    if (req.customEndpoint) {
        llmResult = await callCustomEndpoint(pool, envInfo, logger, req.tenantId, req.customEndpoint, prompt);
    } else {
        llmResult = await callStandardLLM(envInfo, logger, prompt);
    }

    let anomalyScore: number | null = null;
    if (req.semanticLayer === 'behavioral' || req.semanticLayer === 'custom') {
        anomalyScore = await computeAnomalyScore(pool, req);
    }

    const combinedScore = anomalyScore !== null
        ? clamp(llmResult.score * 0.7 + anomalyScore * 0.3)
        : clamp(llmResult.score);

    let decision: SemanticAnalysisResult['decision'] = null;
    let confidence: SemanticAnalysisResult['confidence'] = 'low';

    if (combinedScore >= thresholds.denyAbove) {
        decision = 'DENY'; confidence = 'high';
    } else if (combinedScore >= thresholds.approvalAbove) {
        decision = 'REQUIRE_APPROVAL'; confidence = 'medium';
    } else if (combinedScore >= thresholds.flagAbove) {
        decision = 'FLAG'; confidence = 'low';
    }

    const latencyMs = Date.now() - start;

    pool.query(
        `INSERT INTO semantic_analysis_log
         (tenant_id, agent_id, tool_name, semantic_score, anomaly_score,
          confidence, decision_override, reasoning, model_used, latency_ms, parameters)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
        [req.tenantId, req.agentId, req.toolName, combinedScore, anomalyScore,
         confidence, decision, llmResult.reasoning, llmResult.model, latencyMs,
         JSON.stringify(req.args)]
    ).catch((err: unknown) => logger.error('[Semantic] Failed to log analysis', { error: err }));

    return { semanticScore: combinedScore, anomalyScore, confidence, decision, reasoning: llmResult.reasoning, latencyMs, modelUsed: llmResult.model };
}

async function computeAnomalyScore(pool: IDatabasePool, req: SemanticAnalysisRequest): Promise<number> {
    try {
        const result = await pool.query(
            `SELECT avg_args_length, common_arg_patterns, total_samples
             FROM agent_behavioral_baselines
             WHERE tenant_id = $1 AND agent_id = $2 AND tool_name = $3`,
            [req.tenantId, req.agentId, req.toolName]
        );
        if (result.rows.length === 0 || (result.rows[0] as any).total_samples < 10) return 0;

        const b = result.rows[0] as any;
        let anomaly = 0;

        const argsLen = req.argsString.length;
        const avgLen = Number(b.avg_args_length) || 1;
        const dev = Math.abs(argsLen - avgLen) / avgLen;
        if (dev > 3) anomaly += 0.4;
        else if (dev > 2) anomaly += 0.2;

        const known: string[] = Array.isArray(b.common_arg_patterns) ? b.common_arg_patterns : [];
        const argKeys = (req.args && typeof req.args === 'object' && !Array.isArray(req.args))
            ? Object.keys(req.args) : [];
        if (argKeys.length > 0) {
            const unknownKeys = argKeys.filter(k => !known.includes(k));
            if (unknownKeys.length > 0) anomaly += 0.3 * (unknownKeys.length / argKeys.length);
        }

        return Math.min(1, anomaly);
    } catch { return 0; }
}

export async function updateBaseline(
    pool: IDatabasePool, tenantId: string, agentId: string, toolName: string, args: unknown
): Promise<void> {
    const argsLen = JSON.stringify(args).length;
    const argKeys = (args && typeof args === 'object' && !Array.isArray(args))
        ? Object.keys(args) : [];

    await pool.query(
        `INSERT INTO agent_behavioral_baselines
             (tenant_id, agent_id, tool_name, avg_args_length, total_samples, common_arg_patterns)
         VALUES ($1, $2, $3, $4, 1, $5)
         ON CONFLICT (tenant_id, agent_id, tool_name) DO UPDATE SET
             avg_args_length = (
                 agent_behavioral_baselines.avg_args_length * agent_behavioral_baselines.total_samples + $4
             ) / (agent_behavioral_baselines.total_samples + 1),
             total_samples = agent_behavioral_baselines.total_samples + 1,
             common_arg_patterns = (
                 SELECT COALESCE(jsonb_agg(DISTINCT val), '[]'::jsonb)
                 FROM jsonb_array_elements_text(
                     agent_behavioral_baselines.common_arg_patterns || $5::jsonb
                 ) AS val
             ),
             last_updated = NOW()`,
        [tenantId, agentId, toolName, argsLen, JSON.stringify(argKeys)]
    );
}

function buildAnalysisPrompt(req: SemanticAnalysisRequest): string {
    const truncated = req.argsString.length > 2000
        ? req.argsString.slice(0, 2000) + '...[truncated]' : req.argsString;

    return `You are a security analyst evaluating an AI agent tool call for potential threats.
Assess the threat level on a scale of 0.0 (completely safe) to 1.0 (definitely malicious).

Consider:
- Is the combination of tool + arguments suspicious?
- Could this be part of a multi-step attack (exfiltration, privilege escalation)?
- Are the arguments unusually formatted, encoded, or obfuscated?
- Does the delegation chain suggest unauthorized escalation?

Tool: ${req.toolName}
Arguments: ${truncated}
Delegation Chain: ${JSON.stringify(req.delegationChain || [])}

Respond ONLY with JSON: { "score": <float 0-1>, "reasoning": "<one sentence>" }`;
}

async function callStandardLLM(envInfo: EnvInfo, logger: Logger, prompt: string): Promise<{ score: number; reasoning: string; model: string }> {
    const apiKey = envInfo.SUPRAWALL_SEMANTIC_LLM_KEY;
    const model = envInfo.SUPRAWALL_SEMANTIC_MODEL || 'gpt-4o-mini';
    const timeoutMs = parseInt(envInfo.SUPRAWALL_SEMANTIC_TIMEOUT_MS || '300', 10);

    if (!apiKey) return { score: 0, reasoning: 'Layer 2 not configured (no key)', model: 'none' };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0, max_tokens: 100,
                response_format: { type: 'json_object' },
            }),
            signal: controller.signal,
        });
        clearTimeout(timeout);
        if (!res.ok) return { score: 0, reasoning: 'LLM error — defaulting safe', model };

        const data = await res.json() as { choices: Array<{ message: { content: string } }> };
        let content: { score?: number; reasoning?: string };
        try {
            content = JSON.parse(data.choices[0].message.content);
        } catch (e) {
            logger.error('[Semantic] Failed to parse LLM JSON response', { error: e, raw: data.choices[0].message.content });
            return { score: 0, reasoning: 'LLM returned malformed response — defaulting safe', model };
        }
        return { score: clamp(content.score ?? 0), reasoning: content.reasoning || '', model };
    } catch (err) {
        clearTimeout(timeout);
        logger.warn('[Semantic] LLM timeout / failure', { error: err });
        return { score: 0, reasoning: 'Layer 2 timeout — defaulting safe', model };
    }
}

async function callCustomEndpoint(pool: IDatabasePool, envInfo: EnvInfo, logger: Logger, tenantId: string, endpoint: string, prompt: string): Promise<{ score: number; reasoning: string; model: string }> {
    let authHeader: string | null = null;
    let maxLatencyMs = 500;
    let modelName = 'custom';

    try {
        const ep = await pool.query(
            'SELECT auth_header, max_latency_ms, model_name FROM custom_model_endpoints WHERE tenant_id = $1 AND enabled = true',
            [tenantId]
        );
        if (ep.rows.length > 0) {
            const row = ep.rows[0] as any;
            authHeader = row.auth_header;
            maxLatencyMs = row.max_latency_ms || 500;
            modelName = row.model_name || 'custom';
        }
    } catch { /* fall through */ }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), maxLatencyMs);

    try {
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        if (authHeader) headers['Authorization'] = authHeader;

        const res = await fetch(endpoint, {
            method: 'POST', headers,
            body: JSON.stringify({ prompt, model: modelName }),
            signal: controller.signal,
        });
        clearTimeout(timeout);
        if (!res.ok) return { score: 0, reasoning: 'Custom endpoint error — defaulting safe', model: modelName };

        const data = await res.json() as { score?: number; reasoning?: string };
        return { score: clamp(data.score ?? 0), reasoning: data.reasoning ?? '', model: modelName };
    } catch (err) {
        clearTimeout(timeout);
        logger.warn('[Semantic] Custom endpoint failed/timed out', { error: err, endpoint });
        return { score: 0, reasoning: 'Custom endpoint timeout — defaulting safe', model: modelName };
    }
}

function clamp(n: number): number { return Math.min(1, Math.max(0, n)); }

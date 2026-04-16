// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

// ---------------------------------------------------------------------------
// Behavioral Baseline Service
// ---------------------------------------------------------------------------
// Maintains running baselines of per-agent/per-tool behavior and computes
// anomaly scores for Layer 2 semantic analysis.
// ---------------------------------------------------------------------------

import { pool } from "./db";
import { logger } from "./logger";

interface BehavioralRequest {
    tenantId: string;
    agentId: string;
    toolName: string;
    args: unknown;
    argsString: string;
}

const MIN_SAMPLES_FOR_ANOMALY = 10;

/**
 * Computes an anomaly score (0.0–1.0) by comparing the current call
 * against the agent's historical behavioral baseline for this tool.
 *
 * Returns 0 when insufficient data exists (cold-start safe).
 */
export async function computeAnomalyScore(req: BehavioralRequest): Promise<number> {
    try {
        const result = await pool.query(
            `SELECT avg_args_length, avg_calls_per_hour, common_arg_patterns, total_samples
             FROM agent_behavioral_baselines
             WHERE tenant_id = $1 AND agent_id = $2 AND tool_name = $3`,
            [req.tenantId, req.agentId, req.toolName]
        );

        if (result.rows.length === 0 || result.rows[0].total_samples < MIN_SAMPLES_FOR_ANOMALY) {
            return 0;
        }

        const baseline = result.rows[0];
        let anomaly = 0;

        // 1. Argument length deviation
        const argsLen = req.argsString.length;
        const avgLen = baseline.avg_args_length || 1;
        const lengthDeviation = Math.abs(argsLen - avgLen) / avgLen;

        if (lengthDeviation > 3) {
            anomaly += 0.4;    // >3x deviation from average
        } else if (lengthDeviation > 2) {
            anomaly += 0.2;    // >2x deviation
        }

        // 2. Unknown argument keys (never seen before)
        const knownPatterns: string[] = Array.isArray(baseline.common_arg_patterns)
            ? baseline.common_arg_patterns
            : [];

        const argKeys = extractArgKeys(req.args);
        if (argKeys.length > 0) {
            const unknownKeys = argKeys.filter(k => !knownPatterns.includes(k));
            if (unknownKeys.length > 0) {
                anomaly += 0.3 * (unknownKeys.length / argKeys.length);
            }
        }

        // 3. Call-frequency spike detection.
        // A sudden burst (vs the baseline average) is a common sign of a compromised
        // agent or a runaway loop. We compare the last hour's call count against
        // the historical avg_calls_per_hour from the baseline.
        const avgCallsPerHour = Number(baseline.avg_calls_per_hour) || 0;
        if (avgCallsPerHour > 0) {
            const freqRes = await pool.query(
                `SELECT COUNT(*)::int AS n
                 FROM audit_logs
                 WHERE tenantid = $1 AND agentid = $2 AND toolname = $3
                   AND created_at >= NOW() - INTERVAL '1 hour'`,
                [req.tenantId, req.agentId, req.toolName]
            );
            const recentCallsPerHour = freqRes.rows[0]?.n || 0;
            const freqRatio = recentCallsPerHour / avgCallsPerHour;
            if (freqRatio > 5) {
                anomaly += 0.4;
            } else if (freqRatio > 3) {
                anomaly += 0.2;
            }
        }

        return Math.min(1, anomaly);
    } catch (err) {
        logger.warn('[Behavioral] Failed to compute anomaly score', { error: err });
        return 0; // Never block on behavioral failure
    }
}

/**
 * Updates the running behavioral baseline for an agent/tool pair.
 * Called asynchronously after ALLOW decisions (non-blocking).
 * Uses UPSERT to handle both first-time and subsequent updates.
 */
export async function updateBaseline(
    tenantId: string,
    agentId: string,
    toolName: string,
    args: unknown
): Promise<void> {
    const argsLen = JSON.stringify(args).length;
    const argKeys = extractArgKeys(args);

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

/**
 * Extracts top-level keys from an args object.
 * Returns empty array for non-object args.
 */
function extractArgKeys(args: unknown): string[] {
    if (args !== null && typeof args === 'object' && !Array.isArray(args)) {
        return Object.keys(args);
    }
    return [];
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { db, admin } from '@/lib/firebase-admin';
import { pool as pgPool, ensureSchema } from '@/lib/db_sql';
import { z } from 'zod';
import { apiError } from '@/lib/api-errors';

// ── Schema ──

const LogBodySchema = z.object({
    apiKey: z.string().min(1),
    event: z.string().min(1).max(200),
    agentId: z.string().min(1).max(200),
    severity: z.enum(['low', 'medium', 'high', 'critical']),
    metadata: z.record(z.unknown()).optional().default({}),
});

// ── In-memory rate limiter: 60 req / min per apiKey ──
const rateLimitMap = new Map<string, { count: number; reset: number }>();

function checkRateLimit(key: string): boolean {
    const now = Date.now();
    const window = 60_000; // 1 minute
    const limit = 60;

    const entry = rateLimitMap.get(key);
    if (!entry || entry.reset < now) {
        rateLimitMap.set(key, { count: 1, reset: now + window });
        return true;
    }
    if (entry.count >= limit) return false;
    entry.count += 1;
    return true;
}

/**
 * POST /api/v1/threat/log
 *
 * Accepts threat event submissions from agents.
 * Requires a valid agent API key.
 * Rate-limited to 60 requests per minute per key.
 */
export async function POST(req: NextRequest) {
    let body: unknown;
    try {
        body = await req.json();
    } catch {
        return apiError.badRequest("Invalid JSON body");
    }

    const parsed = LogBodySchema.safeParse(body);
    if (!parsed.success) {
        const missing = parsed.error.errors.map(e => ({ field: e.path.join('.'), message: e.message }));
        if (missing.some(e => e.field === 'apiKey')) {
            return NextResponse.json(
                { error: "API key required" },
                { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
            );
        }
        return apiError.badRequest("Invalid request body", { errors: missing });
    }

    const { apiKey, event, agentId, severity, metadata } = parsed.data;

    // ── Validate API key format ──
    const AGENT_KEY_FORMAT = /^sw_(agent|admin|agc)_[a-zA-Z0-9]{16,}$/;
    if (!AGENT_KEY_FORMAT.test(apiKey)) {
        return NextResponse.json(
            { error: "Invalid API key format" },
            { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
        );
    }

    // ── Rate limit check ──
    if (!checkRateLimit(apiKey)) {
        return apiError.tooManyRequests("Rate limit exceeded: maximum 60 threat log requests per minute per key");
    }

    // ── Verify API key exists in Firestore ──
    try {
        const agentsSnapshot = await db.collection("agents").where("apiKey", "==", apiKey).limit(1).get();
        if (agentsSnapshot.empty) {
            return NextResponse.json(
                { error: "Invalid API key" },
                { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
            );
        }

        const agentDoc = agentsSnapshot.docs[0];
        const agentData = agentDoc.data();
        const tenantId: string = agentData.userId;

        // ── Write to Firestore (real-time) ──
        db.collection("threat_events").add({
            agentId,
            tenantId,
            event_type: event,
            severity,
            details: metadata,
            source: "threat_log_api",
            timestamp: admin.firestore.FieldValue.serverTimestamp(),
        }).catch(err => console.error("[ThreatLog] Firestore write failed:", err));

        // ── Write to Postgres (audit trail, non-blocking) ──
        (async () => {
            try {
                await ensureSchema();
                await pgPool.query(
                    `INSERT INTO threat_events (tenantid, agentid, event_type, severity, details)
                     VALUES ($1, $2, $3, $4, $5)`,
                    [tenantId, agentId, event, severity, JSON.stringify(metadata)]
                );
            } catch (err) {
                console.error("[ThreatLog] Postgres write failed (non-fatal):", err);
            }
        })();

        return NextResponse.json({ success: true });

    } catch (err: any) {
        console.error("[ThreatLog] Error:", err);
        return apiError.internal();
    }
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db_sql';
import { requireDashboardAuth } from '@/lib/api-guard';
import { apiError } from '@/lib/api-errors';

export const dynamic = "force-dynamic";

/**
 * GET /api/v1/approvals/status/[id]
 *
 * Checked by SDKs to see if a REQUIRE_APPROVAL action has been decided.
 * Polls Postgres for the decision.
 * Requires a valid Firebase ID token.
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    const guard = await requireDashboardAuth(request);
    if (guard instanceof NextResponse) return guard;

    try {
        const { id } = await params;

        // Validate id is non-empty before hitting the DB
        if (!id || typeof id !== 'string' || id.trim().length === 0) {
            return apiError.badRequest("Invalid approval request ID");
        }

        // Check Postgres first (Primary source for dashboard actions)
        const result = await query(
            `SELECT status, decision_comment FROM approval_requests
             WHERE id = $1 OR metadata->>'id' = $1`,
            [id]
        );

        if (result.rows.length > 0) {
            return NextResponse.json({
                status: result.rows[0].status,
                decision_comment: result.rows[0].decision_comment
            });
        }

        // Fallback: Check Firestore (Legacy or direct-to-firebase actions)
        const { db } = require('@/lib/firebase-admin');
        const doc = await db.collection('approvalRequests').doc(id).get();
        if (doc.exists) {
            const data = doc.data();
            return NextResponse.json({
                status: (data?.status || 'PENDING').toUpperCase(),
                decision_comment: data?.reviewNote || ''
            });
        }

        return apiError.notFound("Approval request");
    } catch (err: any) {
        console.error("[API Approval Status GET] Error:", err);
        return apiError.internal();
    }
}

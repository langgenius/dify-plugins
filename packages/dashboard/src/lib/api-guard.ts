// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import "server-only";
import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from './api-auth';

/**
 * Guards dashboard UI API routes with Firebase ID token auth.
 * Returns { userId } on success or a NextResponse (401/403) on failure.
 *
 * Usage:
 *   const guard = await requireDashboardAuth(req);
 *   if (guard instanceof NextResponse) return guard;
 *   const { userId } = guard;
 */
export async function requireDashboardAuth(
    req: NextRequest
): Promise<{ userId: string } | NextResponse> {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader?.startsWith('Bearer ')) {
        return NextResponse.json(
            { error: 'Authentication required', code: 'MISSING_AUTH' },
            { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
        );
    }

    const userId = await verifyAuth(req);
    if (!userId) {
        return NextResponse.json(
            { error: 'Invalid or expired token', code: 'INVALID_TOKEN' },
            { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
        );
    }

    return { userId };
}

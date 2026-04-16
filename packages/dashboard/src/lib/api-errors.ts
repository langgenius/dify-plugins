// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextResponse } from 'next/server';
import * as crypto from 'crypto';

function requestId(): string {
    return crypto.randomUUID();
}

/**
 * Canonical error response helpers.
 * All 5xx bodies include a request_id so ops can correlate logs.
 * Never leak raw error messages to the client.
 */
export const apiError = {
    /** 400 — malformed input */
    badRequest(message: string, details?: Record<string, unknown>): NextResponse {
        return NextResponse.json(
            { error: { code: 'BAD_REQUEST', message, ...(details ? { details } : {}) } },
            { status: 400 }
        );
    },

    /** 401 — missing or invalid credential */
    unauthorized(message = 'Authentication required'): NextResponse {
        return NextResponse.json(
            { error: { code: 'UNAUTHORIZED', message } },
            { status: 401, headers: { 'WWW-Authenticate': 'Bearer' } }
        );
    },

    /** 403 — authenticated but not permitted */
    forbidden(message = 'Access denied'): NextResponse {
        return NextResponse.json(
            { error: { code: 'FORBIDDEN', message } },
            { status: 403 }
        );
    },

    /** 404 — resource does not exist */
    notFound(resource = 'Resource'): NextResponse {
        return NextResponse.json(
            { error: { code: 'NOT_FOUND', message: `${resource} not found` } },
            { status: 404 }
        );
    },

    /** 429 — rate limit hit */
    tooManyRequests(message = 'Rate limit exceeded'): NextResponse {
        return NextResponse.json(
            { error: { code: 'RATE_LIMITED', message } },
            { status: 429 }
        );
    },

    /** 500 — unexpected server error (never leaks the real error) */
    internal(): NextResponse {
        return NextResponse.json(
            { error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred', request_id: requestId() } },
            { status: 500 }
        );
    },
};

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

/**
 * CSRF Protection utilities for Next.js API routes.
 *
 * SECURITY: Prevents cross-site request forgery attacks on state-changing operations.
 * Uses double-submit cookie pattern with SameSite=Strict.
 */

const CSRF_TOKEN_HEADER = 'x-csrf-token';
const CSRF_COOKIE_NAME = '__suprawall_csrf_token';
const CSRF_TOKEN_LENGTH = 32;

/**
 * Generates a cryptographically secure CSRF token.
 */
export function generateCsrfToken(): string {
    return crypto.randomBytes(CSRF_TOKEN_LENGTH).toString('hex');
}

/**
 * Validates CSRF token from request header against cookie.
 *
 * SECURITY: Rejects requests where the token in the header doesn't match the cookie,
 * or if either is missing. This prevents CSRF attacks because the attacker cannot
 * read cookies from other domains (SOP).
 */
export async function validateCsrfToken(req: NextRequest): Promise<boolean> {
    // Only validate on state-changing methods
    const method = req.method.toUpperCase();
    if (!['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
        return true;
    }

    // Get token from header
    const headerToken = req.headers.get(CSRF_TOKEN_HEADER);
    if (!headerToken) {
        console.warn('[CSRF] Missing CSRF token in header');
        return false;
    }

    // Get token from cookie
    const cookieToken = req.cookies.get(CSRF_COOKIE_NAME)?.value;
    if (!cookieToken) {
        console.warn('[CSRF] Missing CSRF token in cookie');
        return false;
    }

    // Tokens must match exactly
    const tokensMatch = crypto.timingSafeEqual(
        Buffer.from(headerToken),
        Buffer.from(cookieToken)
    );

    if (!tokensMatch) {
        console.warn('[CSRF] CSRF token mismatch - potential attack detected');
        return false;
    }

    // Optional: Validate Origin/Referer header
    const origin = req.headers.get('origin');
    const referer = req.headers.get('referer');
    const expectedHost = req.headers.get('host');

    if (origin && expectedHost && !origin.includes(expectedHost)) {
        console.warn('[CSRF] Origin mismatch:', { origin, expectedHost });
        return false;
    }

    return true;
}

/**
 * Middleware to check CSRF token on state-changing endpoints.
 * Returns 403 if validation fails, otherwise calls next().
 */
export async function checkCsrfToken(req: NextRequest): Promise<NextResponse | null> {
    const isValid = await validateCsrfToken(req);

    if (!isValid) {
        return NextResponse.json(
            { error: 'CSRF token validation failed' },
            { status: 403 }
        );
    }

    return null; // Valid — caller should proceed
}

/**
 * Sets CSRF token cookie in response.
 * Must be called when issuing an authenticated session to the user.
 */
export function setCsrfTokenCookie(response: NextResponse, token: string): void {
    response.cookies.set(CSRF_COOKIE_NAME, token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 24 * 60 * 60, // 24 hours
        path: '/'
    });
}

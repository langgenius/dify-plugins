// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Request, Response, NextFunction } from "express";
import { pool } from "./db";
import { logger } from "./logger";

// ---------------------------------------------------------------------------
// In-memory fallback used when the DB is unavailable.
// Keyed by: `${windowMs}:${max}:${key}` → { count, resetAt }
// ---------------------------------------------------------------------------
const memoryFallback = new Map<string, { count: number; resetAt: number }>();

function memoryRateLimit(key: string, max: number, windowMs: number): { allowed: boolean; count: number; resetAt: number } {
    const now = Date.now();
    const cacheKey = `${windowMs}:${max}:${key}`;
    let entry = memoryFallback.get(cacheKey);
    if (!entry || entry.resetAt < now) {
        entry = { count: 1, resetAt: now + windowMs };
    } else {
        entry.count += 1;
    }
    memoryFallback.set(cacheKey, entry);
    return { allowed: entry.count <= max, count: entry.count, resetAt: entry.resetAt };
}

// ---------------------------------------------------------------------------
// DB-Backed Distributed Rate Limiter
// ---------------------------------------------------------------------------

interface RateLimitOptions {
    /** Maximum requests per window */
    max: number;
    /** Window duration in milliseconds */
    windowMs: number;
    /** Key extractor — defaults to IP address */
    keyGenerator?: (req: Request) => string;
    /** Custom message */
    message?: string;
}

/**
 * Creates an Express rate limiter middleware backed by PostgreSQL.
 */
export function rateLimit(opts: RateLimitOptions) {
    const {
        max,
        windowMs,
        keyGenerator = (req) => req.ip || req.socket.remoteAddress || "unknown",
        message = "Too many requests. Please try again later.",
    } = opts;

    return async (req: Request, res: Response, next: NextFunction) => {
        if (process.env.NODE_ENV === "test") return next();
        const key = keyGenerator(req);
        
        try {
            const now = Date.now();
            const resetAt = now + windowMs;

            // Delete expired entries to keep the table compact
            await pool.query(`DELETE FROM api_rate_limits WHERE reset_at < $1`, [now]);

            // Upsert the limit key — on conflict, ONLY increment count.
            // The reset_at is NEVER updated so the window is fixed and cannot
            // be extended indefinitely by timing requests before expiry.
            const upsertResult = await pool.query(`
                INSERT INTO api_rate_limits (key, count, reset_at)
                VALUES ($1, 1, $2)
                ON CONFLICT (key) DO UPDATE SET
                    count = api_rate_limits.count + 1
                RETURNING count, reset_at;
            `, [key, resetAt]);

            const row = upsertResult.rows[0];
            const currentCount = row.count;
            const currentResetAt = Number(row.reset_at);

            // Set standard rate-limit headers
            res.setHeader("X-RateLimit-Limit", max);
            res.setHeader("X-RateLimit-Remaining", Math.max(0, max - currentCount));
            res.setHeader("X-RateLimit-Reset", Math.ceil(currentResetAt / 1000));

            if (currentCount > max) {
                res.setHeader("Retry-After", Math.ceil((currentResetAt - now) / 1000));
                return res.status(429).json({
                    error: message,
                    code: "RATE_LIMIT_EXCEEDED",
                    retryAfter: Math.ceil((currentResetAt - now) / 1000),
                });
            }

            next();
        } catch (error) {
            logger.error("[Rate Limit] DB unavailable, using in-memory fallback", { error });
            const fallback = memoryRateLimit(key, max, windowMs);
            if (!fallback.allowed) {
                const retryAfter = Math.ceil((fallback.resetAt - Date.now()) / 1000);
                res.setHeader("Retry-After", retryAfter);
                return res.status(429).json({
                    error: message,
                    code: "RATE_LIMIT_EXCEEDED",
                    retryAfter,
                });
            }
            next();
        }
    };
}

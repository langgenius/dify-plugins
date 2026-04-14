// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Request, Response, NextFunction } from "express";
import { logger } from "./logger";
import { AuthenticatedRequest } from "./auth";

// Log Masking
const MASKED_KEYS = ["apikey", "token", "secret", "authorization", "password"];

export function maskSensitiveData(obj: any): any {
    if (typeof obj !== 'object' || obj === null) return obj;
    if (Array.isArray(obj)) return obj.map(maskSensitiveData);
    
    const clone = { ...obj };
    for (const key of Object.keys(clone)) {
        if (MASKED_KEYS.some(m => key.toLowerCase().includes(m))) {
            clone[key] = "[REDACTED]";
        } else if (typeof clone[key] === 'object') {
            clone[key] = maskSensitiveData(clone[key]);
        }
    }
    return clone;
}

export function observabilityMiddleware(req: Request, res: Response, next: NextFunction) {
    const start = Date.now();
    
    // Attempt to mask incoming request body and headers for debug logs if needed elsewhere
    // However, we just grab metrics here for Axiom Golden Signals
    
    res.on("finish", () => {
        const duration = Date.now() - start;
        const authReq = req as AuthenticatedRequest;
        
        // Output clean structured log for Axiom
        logger.info("Request Summary", {
            route: req.baseUrl + req.path,
            method: req.method,
            status_code: res.statusCode,
            response_time_ms: duration,
            tenant_id: authReq.tenantId || null,
            tier: (authReq as any).tier || null,
            paperclip_event: req.baseUrl.includes('paperclip'),
            error: res.statusCode >= 400
        });
    });
    
    next();
}

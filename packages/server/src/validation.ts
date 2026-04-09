// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { z } from "zod";
import { Request, Response, NextFunction } from "express";

// ---------------------------------------------------------------------------
// Reusable field schemas
// ---------------------------------------------------------------------------

const nonEmptyStr = (max = 255) => z.string().min(1).max(max).trim();
const optionalStr = (max = 255) => z.string().max(max).trim().optional();
const ruleType = z.enum(["ALLOW", "DENY", "REQUIRE_APPROVAL"]);

// ---------------------------------------------------------------------------
// Route-specific schemas
// ---------------------------------------------------------------------------

export const CreatePolicySchema = z.object({
    name:        nonEmptyStr(100),
    ruleType,
    toolName:    optionalStr(200),
    description: optionalStr(500),
    condition:   optionalStr(1000).refine(
        (val) => {
            if (!val) return true;
            try {
                new RegExp(val);
                return true;
            } catch {
                return false;
            }
        },
        "Condition must be a valid regex pattern"
    ),
    tenantId:    optionalStr(100),
});

export const CreateAgentSchema = z.object({
    name:      nonEmptyStr(100),
    scopes:    z.array(z.string().max(100)).max(50).optional(),
    guardrails: z.record(z.string(), z.unknown()).optional(),
});

export const UpdateTenantSchema = z.object({
    name:              optionalStr(100),
    slack_webhook_url: z.string().url().max(500).optional(),
    tier:              z.enum(["open_source", "developer", "team", "business", "enterprise"]).optional(),
}).refine(obj => Object.keys(obj).length > 0, { message: "At least one field required" });

export const CreateVaultSecretSchema = z.object({
    secretName:  nonEmptyStr(100).regex(/^[A-Za-z][A-Za-z0-9_]{2,63}$/, "Secret name must start with a letter and contain only alphanumeric characters and underscores"),
    secretValue: nonEmptyStr(10_000),
    tenantId:    optionalStr(100),
    expiresAt:   z.string().datetime({ offset: true }).optional(),
    allowedTools: z.array(z.string().max(200)).max(100).optional(),
    maxUsesPerHour: z.number().int().min(1).max(10_000).optional(),
});

// ---------------------------------------------------------------------------
// Generic validation middleware factory
// ---------------------------------------------------------------------------

export function validate<T>(schema: z.ZodType<T>) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.body);
        if (!result.success) {
            return res.status(400).json({
                error: "Validation failed",
                details: result.error.issues.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                })),
            });
        }
        req.body = result.data;
        next();
    };
}

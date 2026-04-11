// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import crypto from "crypto";

/**
 * Hash an API key using SHA-256.
 * Must match the implementation in packages/server/src/util/hash.ts exactly —
 * tokens are stored hashed on the server and must be hashed identically here
 * for the activate lookup to succeed.
 */
export function hashApiKey(apiKey: string): string {
    if (!apiKey) return "";
    return crypto.createHash("sha256").update(apiKey).digest("hex");
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import crypto from "crypto";

/**
 * Hash an API key using SHA-256.
 * This is used for both Agent API keys and Master API keys.
 */
export function hashApiKey(apiKey: string): string {
    if (!apiKey) return "";
    return crypto.createHash("sha256").update(apiKey).digest("hex");
}

/**
 * Compare an incoming plain API key with a stored hash.
 * Uses timing-safe constant-time comparison to prevent side-channel attacks.
 */
export function compareApiKey(plainKey: string, hashedKey: string): boolean {
    if (!plainKey || !hashedKey) return false;
    const incomingHash = hashApiKey(plainKey);
    
    // Use timingSafeEqual to prevent timing attacks
    // We must ensure both buffers have the same length
    const buff1 = Buffer.from(incomingHash, "hex");
    const buff2 = Buffer.from(hashedKey, "hex");
    
    if (buff1.length !== buff2.length) return false;
    return crypto.timingSafeEqual(buff1, buff2);
}

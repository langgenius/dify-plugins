// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { hashApiKey, compareApiKey } from "./src/util/hash";

async function verifyHashing() {
    console.log("--- SupraWall Hashing Verification ---");

    const rawKey = "sw_agent_test_key_12345";
    const hashedKey = hashApiKey(rawKey);

    console.log(`Raw Key: ${rawKey}`);
    console.log(`Hashed Key: ${hashedKey}`);

    // Verify length (SHA-256 is 64 hex chars)
    if (hashedKey.length !== 64) {
        throw new Error(`Invalid hash length: ${hashedKey.length}`);
    }

    // Verify comparison
    const match = compareApiKey(rawKey, hashedKey);
    console.log(`Comparison Match: ${match}`);
    if (!match) {
        throw new Error("Comparison failed: Raw key should match its hash");
    }

    // Verify negative comparison
    const mismatch = compareApiKey("wrong_key", hashedKey);
    console.log(`Negative Comparison (Correctly mismatches): ${!mismatch}`);
    if (mismatch) {
        throw new Error("Comparison failed: Wrong key should not match hash");
    }

    console.log("✅ Hashing verification PASSED");
}

verifyHashing().catch(err => {
    console.error("❌ Hashing verification FAILED:", err);
    process.exit(1);
});

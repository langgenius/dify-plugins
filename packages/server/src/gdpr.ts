// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import crypto from "crypto";
import { pool } from "./db";
import { v4 as uuid } from "uuid";
import { logger } from "./logger";

// Standard AES-256-GCM encryption for GDPR cryptographic shredding
export function encryptString(text: string, keyBuffer: Buffer): string {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv("aes-256-gcm", keyBuffer, iv);
    const encrypted = Buffer.concat([cipher.update(text, "utf8"), cipher.final()]);
    const authTag = cipher.getAuthTag();
    // Return iv:encrypted:authTag
    return `${iv.toString("hex")}:${encrypted.toString("hex")}:${authTag.toString("hex")}`;
}

export function decryptString(encryptedData: string, keyBuffer: Buffer): string | null {
    try {
        const parts = encryptedData.split(":");
        if (parts.length !== 3) return null;
        const [ivHex, cipherHex, authTagHex] = parts;
        
        const decipher = crypto.createDecipheriv(
            "aes-256-gcm",
            keyBuffer,
            Buffer.from(ivHex, "hex")
        );
        decipher.setAuthTag(Buffer.from(authTagHex, "hex"));
        
        const dec = Buffer.concat([
            decipher.update(Buffer.from(cipherHex, "hex")),
            decipher.final()
        ]);
        return dec.toString("utf8");
    } catch (e) {
        return null;
    }
}

// Retrieves or creates a 32-byte encryption key for a specific tenant/subject.
// The key itself is returned as a Buffer. The DB stores an encrypted version of it 
// using the master VAULT_ENCRYPTION_KEY (using Postgres PGP).
export async function getDataEncryptionKey(tenantId: string, subjectId: string): Promise<Buffer> {
    const masterKey = process.env.VAULT_ENCRYPTION_KEY;
    if (!masterKey) {
        throw new Error(
            "[GDPR] VAULT_ENCRYPTION_KEY environment variable is not set. " +
            "This is required for GDPR compliance. " +
            "Set it in your environment before starting the server."
        );
    }
    
    // Check if key already exists
    const res = await pool.query(
        `SELECT pgp_sym_decrypt(encrypted_key, $1) as key_hex FROM tenant_data_keys WHERE tenant_id = $2 AND subject_id = $3`,
        [masterKey, tenantId, subjectId]
    );

    if (res.rows && res.rows.length > 0) {
        return Buffer.from(res.rows[0].key_hex, "hex");
    }

    // Generate new key
    const newKeyBuffer = crypto.randomBytes(32);
    const newKeyHex = newKeyBuffer.toString("hex");

    // Use DO UPDATE with RETURNING to guarantee we always get back the key that is
    // actually stored, even if a concurrent insert won the race. Setting encrypted_key
    // to its existing value is a no-op that keeps the original key intact while still
    // triggering the RETURNING clause — eliminating the prior orphaned-key risk.
    const insertRes = await pool.query(
        `INSERT INTO tenant_data_keys (tenant_id, subject_id, encrypted_key)
         VALUES ($1, $2, pgp_sym_encrypt($3, $4))
         ON CONFLICT (tenant_id, subject_id)
         DO UPDATE SET encrypted_key = tenant_data_keys.encrypted_key
         RETURNING pgp_sym_decrypt(encrypted_key, $4) AS key_hex`,
        [tenantId, subjectId, newKeyHex, masterKey]
    );

    if (!insertRes.rows || insertRes.rows.length === 0) {
        logger.error("[GDPR] INSERT/UPSERT returned no rows — cannot guarantee key integrity", { tenantId, subjectId });
        throw new Error("[GDPR] Failed to persist data encryption key");
    }

    return Buffer.from(insertRes.rows[0].key_hex, "hex");
}

// Process GDPR Erasure Request
export async function processGDPRErasure(
    tenantId: string,
    subjectId: string,
    requestedBy: string
) {
    // 1. Delete the encryption key — this is the erasure (Cryptographic Shredding)
    const delRes = await pool.query(
        `DELETE FROM tenant_data_keys WHERE tenant_id = $1 AND subject_id = $2 RETURNING id`,
        [tenantId, subjectId]
    );

    const wasKeyPresent = (delRes.rowCount || 0) > 0;

    // 2. Null out plaintext parameters in audit_logs for this subject (GDPR Article 17).
    // Column is named 'tenantid' (no underscore) — matches insertAuditLog in policy.ts.
    await pool.query(
        `UPDATE audit_logs SET parameters = NULL WHERE tenantid = $1 AND subject_id = $2`,
        [tenantId, subjectId]
    );

    // 3. Log the erasure receipt
    const receipt = {
        erasureId: uuid(),
        tenantId,
        subjectId,
        requestedBy,
        executedAt: new Date().toISOString(),
        method: "cryptographic_shredding",
        affectedTables: ["audit_logs"],
        structuralRecordsPreserved: true,
        piiRecoverable: false,
        keyShredded: wasKeyPresent
    };

    // Calculate receipt hash for tamper detection
    const receiptStr = JSON.stringify(receipt);
    const receiptHash = crypto.createHash("sha256").update(receiptStr).digest("hex");

    await pool.query(
        `INSERT INTO gdpr_erasure_log (erasure_id, tenant_id, subject_id, requested_by, method, receipt_json, receipt_hash)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [receipt.erasureId, tenantId, subjectId, requestedBy, receipt.method, receiptStr, receiptHash]
    );

    return receipt;
}

export function encryptPayload(payload: any, keyBuffer: Buffer): string {
    return encryptString(JSON.stringify(payload), keyBuffer);
}

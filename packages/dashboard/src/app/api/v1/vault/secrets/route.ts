// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export const dynamic = 'force-dynamic';


import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/firebase-admin';
import { admin } from '@/lib/firebase-admin';
import { encrypt } from '@/lib/vault-server';
import { checkResourceLimit } from '@/lib/tier-enforcement';
import { apiError } from '@/lib/api-errors';

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const tenantId = searchParams.get('tenantId');

        if (!tenantId) return apiError.badRequest("Missing required parameter: tenantId");

        const snap = await db.collection("vault_secrets")
            .where("tenant_id", "==", tenantId)
            .get();

        const secrets = snap.docs.map(doc => ({
            id: doc.id,
            ...doc.data(),
            assigned_agents: doc.data().assigned_agents || [],
            encrypted_value: undefined // Never return the encrypted value
        }));

        return NextResponse.json(secrets);
    } catch (e: any) {
        console.error("[Vault API GET Error]:", e);
        return apiError.internal();
    }
}

export async function POST(req: NextRequest) {
    try {
        const body = await req.json().catch(() => null);
        if (!body || typeof body !== 'object') {
            return apiError.badRequest("Invalid or missing JSON body");
        }

        const { tenantId, secretName, secretValue, description, expiresAt, assignedAgents } = body;

        // Explicit field-level validation so callers know exactly what is missing (SEC-009)
        const missing: string[] = [];
        if (!tenantId) missing.push('tenantId');
        if (!secretName) missing.push('secretName');
        if (!secretValue) missing.push('secretValue');

        if (missing.length > 0) {
            return apiError.badRequest(
                `Missing required field${missing.length > 1 ? 's' : ''}: ${missing.join(', ')}`,
                { missing, note: "Expected shape: { tenantId, secretName, secretValue, description?, expiresAt?, assignedAgents? }" }
            );
        }

        // --- Tier Enforcement: Secret Count ---
        const { allowed, count, limit } = await checkResourceLimit(tenantId, 'vault_secrets', 'tenant_id');
        if (!allowed) {
            return NextResponse.json({
                error: `Vault secret limit reached (${count}/${limit}). Upgrade your plan to store more secrets.`,
                code: "TIER_LIMIT_EXCEEDED"
            }, { status: 403 });
        }

        // Check if secret already exists
        const existing = await db.collection("vault_secrets")
            .where("tenant_id", "==", tenantId)
            .where("secret_name", "==", secretName)
            .limit(1)
            .get();

        if (!existing.empty) {
            return NextResponse.json({ error: "Secret name already exists in vault" }, { status: 409 });
        }

        const encrypted = encrypt(secretValue);

        const res = await db.collection("vault_secrets").add({
            tenant_id: tenantId,
            secret_name: secretName,
            encrypted_value: encrypted,
            description: description || null,
            assigned_agents: assignedAgents || [],
            expires_at: expiresAt ? new Date(expiresAt) : null,
            last_rotated_at: new Date(),
            created_at: new Date()
        });

        return NextResponse.json({ id: res.id, secret_name: secretName });
    } catch (e: any) {
        console.error("[Vault API POST Error]:", e);
        return apiError.internal();
    }
}

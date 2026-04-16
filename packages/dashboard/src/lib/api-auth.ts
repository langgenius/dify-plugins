import "server-only";
import { NextRequest, NextResponse } from 'next/server';
import { getAdminAuth, getAdminDb } from './firebase-admin';
import * as crypto from 'crypto';

export interface AuthResult {
    uid: string;
    email?: string;
    tenantId?: string;
    /** 'firebase' = ID token; 'admin_key' = sw_admin_* API key */
    authMethod?: 'firebase' | 'admin_key';
}

const ADMIN_KEY_PREFIX = /^sw_admin_/;

/**
 * Verifies the Firebase ID token from the Authorization header.
 * Returns the authenticated userId (uid) or null if invalid.
 *
 * Usage in API routes:
 *   const userId = await verifyAuth(req);
 *   if (!userId) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
 */
export async function verifyAuth(req: NextRequest): Promise<string | null> {
    const result = await verifyAuthFull(req);
    return result?.uid ?? null;
}

/**
 * Verifies auth and returns full context.
 * Accepts two credential forms:
 *   1. Firebase ID token  (Bearer <firebase-jwt>)
 *   2. Admin API key      (Bearer sw_admin_<hex>)
 *
 * Admin keys are stored in Firestore collection `admin_api_keys` with the SHA-256
 * hash of the raw key in field `key_hash`. The document also carries `tenant_id`
 * and `scopes` so callers can apply fine-grained checks.
 *
 * SEC-008: this extends the original Firebase-only auth to support programmatic
 * access from CLI / CI pipelines that cannot obtain a browser-based JWT.
 */
export async function verifyAuthFull(req: NextRequest): Promise<AuthResult | null> {
    try {
        const authHeader = req.headers.get('Authorization');
        if (!authHeader?.startsWith('Bearer ')) return null;

        const token = authHeader.split(' ')[1];
        if (!token) return null;

        // ── Branch 1: Admin API key (sw_admin_*) ──
        if (ADMIN_KEY_PREFIX.test(token)) {
            return verifyAdminKey(token);
        }

        // ── Branch 2: Firebase ID token ──
        const auth = getAdminAuth();
        const decodedToken = await auth.verifyIdToken(token);
        return {
            uid: decodedToken.uid,
            email: decodedToken.email,
            authMethod: 'firebase',
        };
    } catch (err) {
        console.warn('[API Auth] Token verification failed:', err);
        return null;
    }
}

/**
 * Looks up a sw_admin_* key in Firestore by its SHA-256 hash.
 * Returns AuthResult on success, null if not found or inactive.
 */
async function verifyAdminKey(rawKey: string): Promise<AuthResult | null> {
    try {
        const keyHash = crypto.createHash('sha256').update(rawKey).digest('hex');
        const db = getAdminDb();

        const snap = await db.collection('admin_api_keys')
            .where('key_hash', '==', keyHash)
            .where('active', '==', true)
            .limit(1)
            .get();

        if (snap.empty) return null;

        const data = snap.docs[0].data();

        // Honour expiry if set
        if (data.expires_at) {
            const expiresAt: Date = data.expires_at.toDate ? data.expires_at.toDate() : new Date(data.expires_at);
            if (expiresAt < new Date()) return null;
        }

        return {
            uid: data.tenant_id,
            tenantId: data.tenant_id,
            authMethod: 'admin_key',
        };
    } catch (err) {
        console.warn('[API Auth] Admin key lookup failed:', err);
        return null;
    }
}

/**
 * Returns a standard 401 Unauthorized response.
 */
export function unauthorizedResponse() {
    return NextResponse.json(
        { error: 'Unauthorized: Missing or invalid authentication token.' },
        { status: 401 }
    );
}

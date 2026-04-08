import "server-only";
import { NextRequest, NextResponse } from 'next/server';
import { getAdminAuth } from './firebase-admin';

export interface AuthResult {
    uid: string;
    email?: string;
}

/**
 * Verifies the Firebase ID token from the Authorization header.
 * Returns the authenticated userId (uid) or null if invalid.
 *
 * Usage in API routes:
 *   const userId = await verifyAuth(req);
 *   if (!userId) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
 */
export async function verifyAuth(req: NextRequest): Promise<string | null> {
    try {
        const authHeader = req.headers.get('Authorization');
        if (!authHeader?.startsWith('Bearer ')) return null;

        const idToken = authHeader.split(' ')[1];
        if (!idToken) return null;

        const auth = getAdminAuth();
        const decodedToken = await auth.verifyIdToken(idToken);
        return decodedToken.uid;
    } catch (err) {
        console.warn('[API Auth] Token verification failed:', err);
        return null;
    }
}

/**
 * Same as verifyAuth but also returns the email from the token.
 */
export async function verifyAuthFull(req: NextRequest): Promise<AuthResult | null> {
    try {
        const authHeader = req.headers.get('Authorization');
        if (!authHeader?.startsWith('Bearer ')) return null;

        const idToken = authHeader.split(' ')[1];
        if (!idToken) return null;

        const auth = getAdminAuth();
        const decodedToken = await auth.verifyIdToken(idToken);
        return { uid: decodedToken.uid, email: decodedToken.email };
    } catch (err) {
        console.warn('[API Auth] Token verification failed:', err);
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

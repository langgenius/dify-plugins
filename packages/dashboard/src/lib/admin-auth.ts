// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import "server-only";
import { NextRequest, NextResponse } from "next/server";
import { getAdminAuth } from "./firebase-admin";
import { getAdminEmails } from "./auth-config";

/**
 * Verifies that an incoming request is authenticated AND made by an admin user.
 *
 * Returns null if the request is authorized (caller should proceed).
 * Returns a NextResponse with 401 or 403 if unauthorized (caller should return it immediately).
 *
 * Usage in admin API route handlers:
 *   const authError = await verifyAdminRequest(req);
 *   if (authError) return authError;
 */
export async function verifyAdminRequest(req: NextRequest): Promise<NextResponse | null> {
    const authHeader = req.headers.get("authorization");
    if (!authHeader?.startsWith("Bearer ")) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const token = authHeader.slice(7);
    let decodedToken: { email?: string };

    try {
        decodedToken = await getAdminAuth().verifyIdToken(token);
    } catch {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const adminEmails = getAdminEmails();
    if (!decodedToken.email || !adminEmails.includes(decodedToken.email)) {
        return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // Authorized — caller may proceed
    return null;
}

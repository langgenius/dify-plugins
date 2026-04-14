// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { getAdminAuth } from "./firebase-admin";

export async function getUserEmail(userId: string): Promise<string | null> {
    try {
        const user = await getAdminAuth().getUser(userId);
        return user.email || null;
    } catch (error) {
        console.error(`Error fetching user email for ${userId}:`, error);
        return null;
    }
}

export async function getTenantAdminEmails(tenantId: string): Promise<string[]> {
    // In a real multi-tenant app, you'd query the DB for users associated with this tenant
    // For now, we'll return the system admins as a fallback if no tenant-specific admins are found.
    // This is a placeholder for real tenant isolation logic.
    return [process.env.DEFAULT_ADMIN_EMAIL || 'admin@supra-wall.com'];
}

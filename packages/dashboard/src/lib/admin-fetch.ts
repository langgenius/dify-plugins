// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { auth } from "./firebase";

/**
 * Perform an authenticated fetch to an admin API route.
 * Automatically retrieves the current user's Firebase ID token.
 */
export async function adminFetch(url: string, options: RequestInit = {}) {
    const token = await auth.currentUser?.getIdToken();
    
    const headers = {
        ...options.headers,
        "Authorization": token ? `Bearer ${token}` : "",
        "Content-Type": "application/json",
    };

    return fetch(url, {
        ...options,
        headers,
    });
}

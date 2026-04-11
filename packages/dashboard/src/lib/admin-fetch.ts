import { auth } from "./firebase";

/**
 * Perform an authenticated fetch to an admin API route.
 * Automatically retrieves the current user's Firebase ID token.
 * 
 * @param url The API endpoint to fetch
 * @param options Standard RequestInit options
 */
export async function adminFetch(url: string, options: RequestInit = {}) {
    const user = auth.currentUser;
    if (!user) {
        console.error("[AdminFetch] No authenticated user found.");
        return new Response(JSON.stringify({ error: "No authenticated user" }), { status: 401 });
    }

    const token = await user.getIdToken();
    
    const headers = {
        ...options.headers,
        "Authorization": token ? `Bearer ${token}` : "",
        "Content-Type": "application/json",
        "x-suprawall-admin": "true" // Extra header for easier server-side identification
    };

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (response.status === 401 || response.status === 403) {
        console.warn(`[AdminFetch] Unauthorized request to ${url} (Status: ${response.status})`);
        // If we are in the browser, we might want to redirect, but for now we just log
        // and let the caller handle the UI state.
    }

    return response;
}

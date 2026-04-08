// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export interface SupraWallConfig {
    /** Your SupraWall API key. Set via SUPRAWALL_API_KEY env var or pass directly. */
    apiKey?: string;
    /** SupraWall API base URL. Defaults to https://api.supra-wall.com */
    apiUrl?: string;
    /** Timeout in ms for API calls. Default: 5000 */
    timeout?: number;
}

export interface InvokeRequest {
    agentId: string;
    companyId: string;
    role: string;
    runId: string;
}

export interface InvokeResponse {
    status: "accepted" | "denied";
    /** Run token ID — exchange this for actual credentials via resolveRunToken() */
    runTokenId: string;
    /** ISO timestamp when the run token expires */
    expiresAt: string;
    allowedTools: string[];
    /** Secret names (not values) this agent is authorized to access */
    authorizedSecrets: string[];
    /** Convenience URL for manual run token resolution */
    resolveUrl: string;
}

export interface RunTokenResponse {
    /** Decrypted credential values, keyed by lowercase secret name */
    credentials: Record<string, string>;
    runId: string;
    expiresAt: string;
}

export interface OnboardRequest {
    companyId: string;
    paperclipApiKey?: string;
    paperclipVersion?: string;
    agentCount?: number;
    /** The Paperclip instance API URL (for self-hosted deployments). Default: https://api.paperclipai.com */
    apiUrl?: string;
}

export interface OnboardResponse {
    status: "activation_required" | "already_onboarded";
    activationUrl: string;
    tempApiKey: string;
    docsUrl: string;
    syncedAgents?: number;
    tier?: string;
}

export interface UpgradeError {
    error: string;
    currentTier: string;
    message: string;
    upgradeUrl: string;
    upgradePrice: string;
    /** Always "TIER_LIMIT_EXCEEDED" — use this field for reliable upgrade detection */
    code: "TIER_LIMIT_EXCEEDED";
    /** Synthetic field added by the client for backward compatibility */
    httpStatus: 402;
}

export interface BeforeToolCallContext {
    agentId: string;
    companyId: string;
    role: string;
    runId: string;
    toolName: string;
}

export interface BeforeToolCallResult {
    /** Resolved credential values for this run, keyed by lowercase secret name */
    credentials?: Record<string, string>;
    /** Authorized secret names (populated from invoke before credential resolution) */
    authorizedSecrets?: string[];
    /** The run token ID, available for manual resolution */
    runTokenId?: string;
    error?: string;
    upgradeUrl?: string;
}

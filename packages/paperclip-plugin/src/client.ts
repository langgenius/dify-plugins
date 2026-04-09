// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import axios, { AxiosInstance, AxiosError } from "axios";
import {
    SupraWallConfig,
    InvokeRequest,
    InvokeResponse,
    OnboardRequest,
    OnboardResponse,
    UpgradeError,
    RunTokenResponse,
} from "./types";

export class SupraWallClient {
    private http: AxiosInstance;

    constructor(config: SupraWallConfig = {}) {
        const apiKey = config.apiKey || process.env.SUPRAWALL_API_KEY || "";
        const baseURL = config.apiUrl || process.env.SUPRAWALL_API_URL || "https://api.supra-wall.com";

        this.http = axios.create({
            baseURL,
            timeout: config.timeout || 5000,
            headers: {
                "Content-Type": "application/json",
                ...(apiKey ? { "x-api-key": apiKey } : {}),
            },
        });
    }

    /**
     * Invoke: get a scoped run token for an agent run.
     * Called before each agent tool execution.
     * Returns a runTokenId — call resolveRunToken() to get actual credential values.
     */
    async invoke(request: InvokeRequest): Promise<InvokeResponse | UpgradeError> {
        try {
            const response = await this.http.post<InvokeResponse>("/v1/paperclip/invoke", request);
            return response.data;
        } catch (err) {
            const axiosErr = err as AxiosError<any>;
            if (axiosErr.response) {
                const { status, data } = axiosErr.response;
                if (status === 402) {
                    // Use the code field for reliable upgrade detection
                    return {
                        ...data,
                        code: data?.code ?? "TIER_LIMIT_EXCEEDED",
                        httpStatus: 402,
                    } as UpgradeError;
                }
                throw new Error(data?.error || `SupraWall invoke failed: HTTP ${status}`);
            }
            throw err;
        }
    }

    /**
     * Resolve run token: exchange a runTokenId for actual decrypted credential values.
     * This is the second half of the invoke flow — credentials are never returned in
     * the /invoke response to prevent secret leakage in logs.
     */
    async resolveRunToken(runTokenId: string): Promise<RunTokenResponse> {
        try {
            const response = await this.http.get<RunTokenResponse>(`/v1/paperclip/run-token/${runTokenId}`);
            return response.data;
        } catch (err) {
            const axiosErr = err as AxiosError<any>;
            if (axiosErr.response) {
                const { status, data } = axiosErr.response;
                throw new Error(data?.error || `SupraWall run token resolve failed: HTTP ${status}`);
            }
            throw err;
        }
    }

    /**
     * Onboard: register a Paperclip company with SupraWall.
     * Called once during plugin install.
     */
    async onboard(request: OnboardRequest): Promise<OnboardResponse> {
        try {
            const response = await this.http.post<OnboardResponse>("/v1/paperclip/onboard", request);
            return response.data;
        } catch (err) {
            const axiosErr = err as AxiosError<any>;
            if (axiosErr.response) {
                const { status, data } = axiosErr.response;
                throw new Error(data?.error || `SupraWall onboard failed: HTTP ${status}`);
            }
            throw err;
        }
    }

    /**
     * Check integration status for the current tenant.
     */
    async getStatus(): Promise<{ company: any; agentCount: number; activeRunTokens: number }> {
        try {
            const response = await this.http.get<{ company: any; agentCount: number; activeRunTokens: number }>(
                "/v1/paperclip/status"
            );
            return response.data;
        } catch (err) {
            const axiosErr = err as AxiosError<any>;
            if (axiosErr.response) {
                const { status, data } = axiosErr.response;
                throw new Error(data?.error || `SupraWall status check failed: HTTP ${status}`);
            }
            throw err;
        }
    }
}

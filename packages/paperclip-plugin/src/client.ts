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
    RequestOptions,
} from "./types";

export class SupraWallClient {
    private http: AxiosInstance;
    private config: SupraWallConfig;

    constructor(config: SupraWallConfig = {}) {
        this.config = {
            maxRetries: 3,
            retryDelay: 500,
            timeout: 5000,
            ...config
        };

        const apiKey = this.config.apiKey || process.env.SUPRAWALL_API_KEY || "";
        const baseURL = this.config.apiUrl || process.env.SUPRAWALL_API_URL || "https://api.supra-wall.com";

        this.http = axios.create({
            baseURL,
            timeout: this.config.timeout,
            headers: {
                "Content-Type": "application/json",
                ...(apiKey ? { "x-api-key": apiKey } : {}),
            },
        });
    }

    /**
     * Internal helper to execute a request with exponential backoff retries
     * only on transient errors (5xx, network timeouts).
     */
    private async requestWithRetry<T>(
        fn: (options?: RequestOptions) => Promise<T>,
        options: RequestOptions = {}
    ): Promise<T> {
        const maxRetries = options.maxRetries ?? this.config.maxRetries ?? 3;
        let attempt = 0;

        while (true) {
            try {
                return await fn(options);
            } catch (err) {
                const axiosErr = err as AxiosError;
                const isRetryable = !axiosErr.response || (
                    axiosErr.response.status >= 500 && 
                    axiosErr.response.status <= 599 && 
                    axiosErr.response.status !== 503 // 503 usually means config error in SupraWall
                );
                
                if (!isRetryable || attempt >= maxRetries) {
                    throw err;
                }

                attempt++;
                const delay = (this.config.retryDelay || 500) * Math.pow(2, attempt - 1);
                console.warn(`[SupraWall] Request failed (attempt ${attempt}/${maxRetries+1}). Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    /**
     * Invoke: get a scoped run token for an agent run.
     * Called before each agent tool execution.
     * Returns a runTokenId — call resolveRunToken() to get actual credential values.
     */
    async invoke(request: InvokeRequest, options: RequestOptions = {}): Promise<InvokeResponse | UpgradeError> {
        return this.requestWithRetry(async (opts) => {
            try {
                const response = await this.http.post<InvokeResponse>("/v1/paperclip/invoke", request, {
                    timeout: opts?.timeout
                });
                return response.data;
            } catch (err) {
                const axiosErr = err as AxiosError<any>;
                if (axiosErr.response) {
                    const { status, data } = axiosErr.response;
                    if (status === 402) {
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
        }, options);
    }

    /**
     * Resolve run token: exchange a runTokenId for actual decrypted credential values.
     * This is the second half of the invoke flow — credentials are never returned in
     * the /invoke response to prevent secret leakage in logs.
     */
    async resolveRunToken(runTokenId: string, options: RequestOptions = {}): Promise<RunTokenResponse> {
        return this.requestWithRetry(async (opts) => {
            try {
                const response = await this.http.get<RunTokenResponse>(`/v1/paperclip/run-token/${runTokenId}`, {
                    timeout: opts?.timeout
                });
                return response.data;
            } catch (err) {
                const axiosErr = err as AxiosError<any>;
                if (axiosErr.response) {
                    const { status, data } = axiosErr.response;
                    throw new Error(data?.error || `SupraWall run token resolve failed: HTTP ${status}`);
                }
                throw err;
            }
        }, options);
    }

    /**
     * Onboard: register a Paperclip company with SupraWall.
     * Called once during plugin install.
     */
    async onboard(request: OnboardRequest, options: RequestOptions = {}): Promise<OnboardResponse> {
        return this.requestWithRetry(async (opts) => {
            try {
                const response = await this.http.post<OnboardResponse>("/v1/paperclip/onboard", request, {
                    timeout: opts?.timeout
                });
                return response.data;
            } catch (err) {
                const axiosErr = err as AxiosError<any>;
                if (axiosErr.response) {
                    const { status, data } = axiosErr.response;
                    throw new Error(data?.error || `SupraWall onboard failed: HTTP ${status}`);
                }
                throw err;
            }
        }, options);
    }

    /**
     * Check integration status for the current tenant.
     */
    async getStatus(options: RequestOptions = {}): Promise<{ company: any; agentCount: number; activeRunTokens: number }> {
        return this.requestWithRetry(async (opts) => {
            try {
                const response = await this.http.get<{ company: any; agentCount: number; activeRunTokens: number }>(
                    "/v1/paperclip/status", {
                        timeout: opts?.timeout
                    }
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
        }, options);
    }
}

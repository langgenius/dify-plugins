// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { SupraWallClient } from "./client";
import {
    SupraWallConfig,
    InvokeResponse,
    UpgradeError,
    BeforeToolCallContext,
    BeforeToolCallResult,
    OnboardRequest,
    OnboardResponse,
} from "./types";

export { SupraWallClient } from "./client";
export * from "./types";

// ---------------------------------------------------------------------------
// Plugin factory — the main export consumed by Paperclip's plugin runtime
// ---------------------------------------------------------------------------

export function createPlugin(config: SupraWallConfig = {}) {
    const client = new SupraWallClient(config);

    return {
        name: "suprawall-vault",
        version: "1.0.0",

        /**
         * Called before each agent tool invocation.
         *
         * Step 1: POST /v1/agent/invoke → returns runTokenId (no credentials in response)
         * Step 2: GET /v1/paperclip/run-token/:runTokenId → returns decrypted credentials
         *
         * This two-step flow ensures credentials never appear in HTTP response logs.
         */
        async beforeToolCall(context: BeforeToolCallContext): Promise<BeforeToolCallResult> {
            const invokeResult = await client.invoke({
                agentId: context.agentId,
                companyId: context.companyId,
                role: context.role,
                runId: context.runId,
            });

            // Upgrade wall: surface the upgrade URL to the Paperclip dashboard.
            // Detect upgrades via the code field — not duck-typing on httpStatus.
            if ("code" in invokeResult && invokeResult.code === "TIER_LIMIT_EXCEEDED") {
                const upgradeResult = invokeResult as UpgradeError;
                console.warn(
                    `[SupraWall] Tier limit reached: ${upgradeResult.error}\n` +
                    `  Upgrade at: ${upgradeResult.upgradeUrl}`
                );
                return {
                    error: upgradeResult.error,
                    upgradeUrl: upgradeResult.upgradeUrl,
                };
            }

            const response = invokeResult as InvokeResponse;

            // If there are no authorized secrets, return early (no resolution needed)
            if (!response.authorizedSecrets || response.authorizedSecrets.length === 0) {
                return {
                    runTokenId: response.runTokenId,
                    authorizedSecrets: [],
                    credentials: {},
                };
            }

            // Step 2: resolve credentials using the run token
            // This keeps secret values out of the invoke response and its logs.
            try {
                const tokenData = await client.resolveRunToken(response.runTokenId);
                return {
                    runTokenId: response.runTokenId,
                    authorizedSecrets: response.authorizedSecrets,
                    credentials: tokenData.credentials,
                };
            } catch (resolveErr) {
                console.error("[SupraWall] Failed to resolve run token credentials:", resolveErr);
                // Return the runTokenId so the agent can retry resolution if needed
                return {
                    runTokenId: response.runTokenId,
                    authorizedSecrets: response.authorizedSecrets,
                    credentials: {},
                    error: resolveErr instanceof Error ? resolveErr.message : "Credential resolution failed",
                };
            }
        },

        /**
         * Called once when the plugin is installed.
         * Registers the Paperclip company with SupraWall and returns the temp key.
         */
        async onInstall(context: {
            companyId: string;
            agentCount?: number;
            apiUrl?: string;
            paperclipVersion?: string;
        }): Promise<OnboardResponse> {
            const result = await client.onboard({
                companyId: context.companyId,
                agentCount: context.agentCount,
                // Use the version from the Paperclip runtime context when available,
                // or fall back to the PAPERCLIP_VERSION env var. Never hardcode.
                paperclipVersion: context.paperclipVersion || process.env.PAPERCLIP_VERSION || undefined,
                apiUrl: context.apiUrl,
            });

            // Print to terminal (Paperclip surfaces plugin output)
            console.log(`
✅  SupraWall Vault installed successfully!
🔑  Temp API key (Developer tier): ${result.tempApiKey}
🚀  Activate your account: ${result.activationUrl}
📖  Docs: ${result.docsUrl}
            `.trim());

            return result;
        },

        /**
         * Expose the underlying client for advanced usage.
         */
        client,
    };
}

// Default export for convenience
export default createPlugin;

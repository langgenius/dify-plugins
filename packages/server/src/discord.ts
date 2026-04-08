// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { logger } from "./logger";

export interface DiscordUsageAlert {
    companyId: string;
    tenantId: string;
    currentUsage: number;
    maxUsage: number;
    currentTier: string;
    upgradeUrl: string;
}

/**
 * Send a usage alert embed to a Discord webhook.
 * Called when a tenant crosses 50%, 75%, 90%, or 100% of their monthly ops limit.
 */
export async function sendDiscordUsageAlert(webhookUrl: string, payload: DiscordUsageAlert): Promise<void> {
    try {
        const percentage = Math.round((payload.currentUsage / payload.maxUsage) * 100);

        // Color: green → orange → red
        const color = percentage >= 100 ? 0xff2222 : percentage >= 90 ? 0xff6600 : percentage >= 75 ? 0xffa500 : 0x22cc88;

        const embed = {
            title: "⚠️ SupraWall Usage Alert",
            description: `Company \`${payload.companyId}\` is at **${percentage}%** of monthly operations`,
            color,
            fields: [
                {
                    name: "Usage",
                    value: `${payload.currentUsage.toLocaleString()} / ${payload.maxUsage.toLocaleString()} ops`,
                    inline: true,
                },
                {
                    name: "Current Plan",
                    value: payload.currentTier,
                    inline: true,
                },
                {
                    name: "Action",
                    value: `[Upgrade Now](${payload.upgradeUrl})`,
                    inline: true,
                },
            ],
            footer: {
                text: `SupraWall • Tenant: ${payload.tenantId}`,
            },
            timestamp: new Date().toISOString(),
        };

        const response = await fetch(webhookUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ embeds: [embed] }),
            signal: AbortSignal.timeout(5000),
        });

        if (!response.ok) {
            logger.warn(`[Discord] Alert failed with status ${response.status}`);
        }
    } catch (err) {
        logger.error("[Discord] Failed to send usage alert:", { error: err });
    }
}

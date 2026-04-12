// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { PostHog } from 'posthog-node';

export const posthogClient = process.env.NEXT_PUBLIC_POSTHOG_KEY 
    ? new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY, { host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com' })
    : null;

export const trackEvent = (event: string, properties: any, distinctId?: string) => {
    if (!posthogClient) return;
    try {
        posthogClient.capture({
            distinctId: distinctId || properties.companyId || properties.tenantId || 'anonymous',
            event,
            properties
        });
    } catch (e) {
        console.error("[PostHog] Failed to track event", { error: e });
    }
}

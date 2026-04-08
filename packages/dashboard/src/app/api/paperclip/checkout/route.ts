// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { pool } from "@/lib/db_sql";

// Plan → Stripe price IDs (base flat fee + metered overage component)
const PLANS: Record<string, { basePriceId: string; meteredPriceId: string; tier: string; label: string }> = {
    developer: {
        basePriceId:    process.env.STRIPE_DEVELOPER_PRICE_ID!,
        meteredPriceId: process.env.STRIPE_DEVELOPER_METERED_PRICE_ID!,
        tier: "developer",
        label: "Developer — Free",
    },
    team: {
        basePriceId:    process.env.STRIPE_TEAM_PRICE_ID!,
        meteredPriceId: process.env.STRIPE_TEAM_METERED_PRICE_ID!,
        tier: "team",
        label: "Team — $149/mo",
    },
    business: {
        basePriceId:    process.env.STRIPE_BUSINESS_PRICE_ID!,
        meteredPriceId: process.env.STRIPE_BUSINESS_METERED_PRICE_ID!,
        tier: "business",
        label: "Business — $499/mo",
    },
};

/**
 * POST /api/paperclip/checkout
 * Creates a Stripe Checkout session for a Paperclip company.
 * No Firebase auth required — user arrives from the /activate page with their email.
 *
 * Body: { plan: "team"|"business", companyId: string, email: string }
 */
export async function POST(req: NextRequest) {
    let body: { plan?: string; companyId?: string; email?: string };
    try {
        body = await req.json();
    } catch {
        return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
    }

    const { plan, companyId, email } = body;

    // Validate inputs
    if (!plan || !PLANS[plan]) {
        return NextResponse.json(
            { error: `Invalid plan. Choose one of: ${Object.keys(PLANS).join(", ")}` },
            { status: 400 }
        );
    }
    if (!companyId || typeof companyId !== "string") {
        return NextResponse.json({ error: "Missing companyId" }, { status: 400 });
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
    }

    const planConfig = PLANS[plan];

    if (!planConfig.basePriceId || !planConfig.meteredPriceId) {
        console.error(`[Paperclip Checkout] Missing Stripe Price IDs for plan: ${plan}`);
        return NextResponse.json(
            { error: "Stripe price IDs not configured for this plan. Contact support@supra-wall.com" },
            { status: 500 }
        );
    }

    try {
        // Look up the tenant for this Paperclip company
        const companyResult = await pool.query(
            "SELECT tenant_id FROM paperclip_companies WHERE paperclip_company_id = $1",
            [companyId]
        );
        if (companyResult.rows.length === 0) {
            return NextResponse.json(
                { error: "Company not found. Install the SupraWall plugin first." },
                { status: 404 }
            );
        }
        const tenantId = companyResult.rows[0].tenant_id;

        // Create or retrieve Stripe customer by email
        const existingCustomers = await stripe.customers.list({ email, limit: 1 });
        let customerId = existingCustomers.data[0]?.id;

        if (!customerId) {
            const customer = await stripe.customers.create({
                email,
                metadata: {
                    companyId,
                    tenantId,
                    source: "paperclip_activate",
                },
            });
            customerId = customer.id;
        } else {
            // Update metadata on existing customer to capture Paperclip linkage
            await stripe.customers.update(customerId, {
                metadata: { companyId, tenantId, source: "paperclip_activate" },
            });
        }

        const origin = req.headers.get("origin") || "https://supra-wall.com";

        // Create Checkout Session
        const session = await stripe.checkout.sessions.create({
            customer: customerId,
            billing_address_collection: "auto",
            line_items: [
                { price: planConfig.basePriceId, quantity: 1 },
                { price: planConfig.meteredPriceId }, // Metered component — no quantity
            ],
            mode: "subscription",
            success_url: `${origin}/activate/success?session_id={CHECKOUT_SESSION_ID}&company=${encodeURIComponent(companyId)}`,
            cancel_url: `${origin}/activate?company=${encodeURIComponent(companyId)}&canceled=true`,
            customer_email: customerId ? undefined : email, // Only set if no customer object
            client_reference_id: tenantId,
            metadata: {
                companyId,
                tenantId,
                plan,
                source: "paperclip_activate",
            },
            subscription_data: {
                metadata: { companyId, tenantId, plan, source: "paperclip" },
            },
        });

        return NextResponse.json({
            checkoutUrl: session.url,
            sessionId: session.id,
        });
    } catch (err: any) {
        console.error("[Paperclip Checkout] Stripe error:", err);
        return NextResponse.json({ error: err.message || "Stripe error" }, { status: 500 });
    }
}

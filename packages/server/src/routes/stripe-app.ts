// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import express, { Request, Response } from "express";
import Stripe from "stripe";
import { pool } from "../db";
import { gatekeeperAuth } from "../auth";
import { TIER_LIMITS, currentMonth } from "../tier-config";
import { logger } from "../logger";

const router = express.Router();
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "", {
    apiVersion: "2025-01-27-preview.beta.2" as any,
});

// ONBOARD: Links Stripe account -> SupraWall tenant
router.post("/onboard", gatekeeperAuth, async (req: Request, res: Response) => {
    try {
        const { stripeAccountId, tenantId } = req.body;
        if (!stripeAccountId || !tenantId) {
            return res.status(400).json({ error: "Missing stripeAccountId or tenantId" });
        }
        await pool.query(`UPDATE tenants SET stripe_customer_id = $1 WHERE id = $2`, [stripeAccountId, tenantId]);
        res.json({ success: true, message: "Onboarding complete" });
    } catch (e) {
        logger.error("[Stripe] Onboarding error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

/**
 * GET /v1/billing/usage — Returns current month usage and projected overages
 */
router.get("/usage", gatekeeperAuth, async (req: Request, res: Response) => {
    try {
        const { tenantId } = req.query;
        if (!tenantId) return res.status(400).json({ error: "Missing tenantId" });

        const month = currentMonth();
        const usageResult = await pool.query(
            "SELECT evaluation_count, overage_units FROM tenant_usage WHERE tenant_id = $1 AND month = $2",
            [tenantId, month]
        );
        const tenantResult = await pool.query("SELECT tier FROM tenants WHERE id = $1", [tenantId]);

        const tier = tenantResult.rows[0]?.tier || "open_source";
        const limits = TIER_LIMITS[tier as keyof typeof TIER_LIMITS];
        const usage = usageResult.rows[0] || { evaluation_count: 0, overage_units: 0 };

        res.json({
            tenantId,
            month,
            tier,
            limits: {
                maxEvaluations: limits.maxEvaluationsPerMonth,
                overageRate: limits.overageRatePerEval,
            },
            current: {
                evaluations: usage.evaluation_count,
                overages: usage.overage_units,
                projectedOverageCost: usage.overage_units * (limits.overageRatePerEval || 0)
            }
        });
    } catch (e) {
        logger.error("[Stripe] Usage fetch error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

/**
 * POST /v1/billing/report-usage — Syncs overages to Stripe metered components
 */
router.post("/report-usage", gatekeeperAuth, async (req: Request, res: Response) => {
    try {
        const { tenantId } = req.body;
        if (!tenantId) return res.status(400).json({ error: "Missing tenantId" });

        const month = currentMonth();
        const usageResult = await pool.query(
            "SELECT overage_units FROM tenant_usage WHERE tenant_id = $1 AND month = $2",
            [tenantId, month]
        );
        const overageUnits = usageResult.rows[0]?.overage_units || 0;

        if (overageUnits === 0) return res.json({ skipped: true, reason: "No overages to report" });

        const tenantResult = await pool.query(
            "SELECT stripe_subscription_id FROM tenants WHERE id = $1",
            [tenantId]
        );
        const subId = tenantResult.rows[0]?.stripe_subscription_id;

        if (!subId) return res.status(400).json({ error: "Tenant has no active Stripe subscription" });

        // Retrieve subscription items to find the metered one
        const subscription = await stripe.subscriptions.retrieve(subId);
        const meteredItem = subscription.items.data.find(item => item.price.recurring?.usage_type === "metered");

        if (!meteredItem) return res.status(400).json({ error: "No metered item found on subscription" });

        await (stripe as any).subscriptionItems.createUsageRecord(meteredItem.id, {
            quantity: overageUnits,
            timestamp: Math.floor(Date.now() / 1000),
            action: "set",
        });

        res.json({ success: true, reportedUnits: overageUnits });
    } catch (e) {
        logger.error("[Stripe] Usage reporting error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

/**
 * POST /v1/billing/webhook — Handle Stripe events
 */
router.post("/webhook", express.raw({ type: "application/json" }), async (req: Request, res: Response) => {
    const sig = req.headers["stripe-signature"] as string;
    let event;

    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
    if (!webhookSecret) {
        logger.error("[Stripe Webhook] STRIPE_WEBHOOK_SECRET is not configured. Rejecting request.");
        return res.status(500).send("Webhook secret not configured");
    }

    try {
        event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
    } catch (err: any) {
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    try {
        switch (event.type) {
            // Payment completed — upgrade tenant to the purchased tier
            case "checkout.sessions.completed": {
                const session = event.data.object as Stripe.Checkout.Session;
                const tenantId = session.client_reference_id || session.metadata?.tenantId;
                const plan = session.metadata?.plan;
                const subscriptionId = typeof session.subscription === "string" ? session.subscription : null;
                const customerId = typeof session.customer === "string" ? session.customer : null;
                const companyId = session.metadata?.companyId;

                if (!tenantId || !plan) {
                    logger.warn("[Stripe Webhook] checkout.sessions.completed missing tenantId or plan in metadata", { sessionId: session.id });
                    break;
                }

                await pool.query(
                    `UPDATE tenants
                     SET tier = $1,
                         stripe_subscription_id = COALESCE($2, stripe_subscription_id),
                         stripe_customer_id = COALESCE($3, stripe_customer_id)
                     WHERE id = $4`,
                    [plan, subscriptionId, customerId, tenantId]
                );
                logger.info(`[Stripe Webhook] Upgraded tenant ${tenantId} to ${plan} (sub: ${subscriptionId})`);
                if (companyId) {
                    logger.info("[Metric] Paperclip Funnel", {
                        event_type: "funnel_paid",
                        company_id: companyId,
                        tenant_id: tenantId,
                        tier: plan
                    });
                }
                break;
            }

            // Subscription renewal — confirm tier stays active
            case "invoice.paid": {
                const invoice = event.data.object as Stripe.Invoice;
                const subId = typeof (invoice as any).subscription === "string" ? (invoice as any).subscription : null;
                if (!subId) break;

                // Retrieve the plan from subscription metadata and re-affirm the tier
                const sub = await stripe.subscriptions.retrieve(subId);
                const plan = sub.metadata?.plan;
                if (plan) {
                    await pool.query(
                        "UPDATE tenants SET tier = $1 WHERE stripe_subscription_id = $2",
                        [plan, subId]
                    );
                    logger.info(`[Stripe Webhook] Renewed: tier ${plan} confirmed for sub ${subId}`);
                }
                break;
            }

            // Plan upgrade/downgrade via Stripe portal
            case "customer.subscription.updated": {
                const subscription = event.data.object as Stripe.Subscription;
                const plan = subscription.metadata?.plan;
                if (plan) {
                    await pool.query(
                        "UPDATE tenants SET tier = $1 WHERE stripe_subscription_id = $2",
                        [plan, subscription.id]
                    );
                    logger.info(`[Stripe Webhook] Plan updated to ${plan} for sub ${subscription.id}`);
                }
                break;
            }

            // Cancellation or payment failure — downgrade to open_source
            case "customer.subscription.deleted":
            case "invoice.payment_failed": {
                const subscription = event.data.object as Stripe.Subscription;
                await pool.query(
                    "UPDATE tenants SET tier = 'open_source' WHERE stripe_subscription_id = $1",
                    [subscription.id]
                );
                logger.info(`[Stripe Webhook] Downgraded tenant for sub ${subscription.id} due to payment failure or cancellation.`);
                break;
            }
        }
    } catch (err) {
        logger.error("[Stripe Webhook] Processing error:", err);
    }

    res.json({ received: true });
});

// BUDGET-CTRL: Revoke/Restore based on billing state
router.post("/budget-ctrl", async (req: Request, res: Response) => {
    try {
        const { action, subscriptionId } = req.body;
        if (!action || !subscriptionId) return res.status(400).json({ error: "Missing action or subscriptionId" });

        if (action === "revoke") {
            // Drop to open_source
            await pool.query(
                "UPDATE tenants SET tier = 'open_source' WHERE stripe_subscription_id = $1",
                [subscriptionId]
            );
            logger.warn(`[Stripe Budget] REVOKE: Downgraded tenant for sub ${subscriptionId}`);
        } else if (action === "restore") {
            const sub = await stripe.subscriptions.retrieve(subscriptionId);
            const tier = (sub.metadata as any).plan || "developer";
            await pool.query(
                "UPDATE tenants SET tier = $1 WHERE stripe_subscription_id = $2",
                [tier, subscriptionId]
            );
            logger.info(`[Stripe Budget] RESTORE: Tier ${tier} restored for sub ${subscriptionId}`);
        }

        res.json({ success: true });
    } catch (e) {
        logger.error("[Stripe Budget] Control error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

// VAULT-PROXY: Wraps a Stripe Restricted API Key
router.post("/vault-proxy", gatekeeperAuth, async (req: Request, res: Response) => {
    try {
        const { tenantId, apiKey, label } = req.body;
        if (!apiKey || !tenantId) return res.status(400).json({ error: "Missing apiKey or tenantId" });

        const secretName = `STRIPE_RAK_${Date.now()}`;
        await pool.query(
            `INSERT INTO vault_secrets (tenant_id, secret_name, encrypted_value, description)
             VALUES ($1, $2, pgp_sym_encrypt($3, $4), $5)`,
            [tenantId, secretName, apiKey, process.env.VAULT_ENCRYPTION_KEY, label || "Stripe Proxy Key"]
        );

        res.json({ success: true, vaultToken: `$SUPRAWALL_VAULT_${secretName}` });
    } catch (e) {
        logger.error("[Stripe Proxy] Error:", e);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

export default router;

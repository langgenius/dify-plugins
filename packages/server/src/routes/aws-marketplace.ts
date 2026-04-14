// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

/**
 * AWS Marketplace Integration Routes
 *
 * Implements the three required endpoints for AWS Marketplace SaaS listings:
 *
 *   POST /v1/aws/register  — Registration URL: AWS redirects buyers here post-subscribe.
 *                            Resolves the customerIdentifier → tenant, upgrades tier.
 *
 *   POST /v1/aws/sns       — SNS webhook: AWS sends subscription lifecycle events here.
 *                            Handles: subscribe, unsubscribe, entitlement-updated.
 *
 *   GET  /v1/aws/entitlement — Internal: verifies an active AWS entitlement for a tenant.
 *
 * Architecture notes:
 *   - Reuses `tenants` table (adds `aws_customer_id`, `aws_product_code` columns via migration).
 *   - Reuses `tier-config.ts` tier names — AWS subscriptions map to existing Tier values.
 *   - SNS topic must be whitelisted to the AWS Marketplace SNS ARN only (validated below).
 *   - Registration URL is unauthenticated (buyer has no key yet); all other routes are signed.
 *
 * Required env vars (add to .env.example):
 *   AWS_MARKETPLACE_PRODUCT_CODE=        # from AMMP product page
 *   AWS_MARKETPLACE_SNS_TOPIC_ARN=       # from AMMP → SNS configuration
 *   AWS_MARKETPLACE_REDIRECT_URL=        # where to send buyer after registration (dashboard)
 *   AWS_REGION=us-east-1
 *   AWS_ACCESS_KEY_ID=                   # IAM role with marketplace:ResolveCustomer permission
 *   AWS_SECRET_ACCESS_KEY=
 */

import express, { Request, Response } from "express";
import { pool } from "../db";
import { logger } from "../logger";
import type { Tier } from "../tier-config";
import crypto from "crypto";

const router = express.Router();

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Maps AWS Marketplace dimension names (set in AMMP pricing wizard) to
 * internal SupraWall tier names. Update these to match your AMMP dimension IDs.
 */
const AWS_DIMENSION_TO_TIER: Record<string, Tier> = {
    developer:  "developer",
    team:       "team",
    business:   "business",
    enterprise: "enterprise",
} as const;

const FALLBACK_TIER: Tier = "developer";

// AWS Marketplace SNS topic ARNs are always in us-east-1 under this account.
// This prefix is constant across all AWS Marketplace listings.
const AWS_SNS_TOPIC_ARN_PREFIX = "arn:aws:sns:us-east-1:287250355862:aws-mp-subscription-notification";

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Calls the AWS Marketplace resolveCustomer API to exchange a registration token
 * for a stable customerIdentifier. Requires IAM permission marketplace:ResolveCustomer.
 *
 * Returns null if the token is invalid or the API call fails.
 */
async function resolveAwsCustomerIdentifier(registrationToken: string): Promise<{
    customerId: string;
    productCode: string;
    customerAWSAccountId: string;
} | null> {
    const productCode = process.env.AWS_MARKETPLACE_PRODUCT_CODE;
    if (!productCode) {
        logger.error("[AWS Marketplace] AWS_MARKETPLACE_PRODUCT_CODE is not configured.");
        return null;
    }

    const region = process.env.AWS_REGION || "us-east-1";
    const endpoint = `https://metering.marketplace.${region}.amazonaws.com/`;

    // Build AWS Signature v4 signed request
    const host = `metering.marketplace.${region}.amazonaws.com`;
    const service = "aws-marketplace";
    const now = new Date();
    const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "").slice(0, 15) + "Z";
    const dateStamp = amzDate.slice(0, 8);

    const payload = JSON.stringify({ RegistrationToken: registrationToken });
    const payloadHash = crypto.createHash("sha256").update(payload).digest("hex");

    const canonicalUri = "/";
    const canonicalQueryString = "";
    const canonicalHeaders =
        `content-type:application/x-amz-json-1.1\n` +
        `host:${host}\n` +
        `x-amz-date:${amzDate}\n` +
        `x-amz-target:AWSMPMeteringService.ResolveCustomer\n`;
    const signedHeaders = "content-type;host;x-amz-date;x-amz-target";

    const canonicalRequest = [
        "POST",
        canonicalUri,
        canonicalQueryString,
        canonicalHeaders,
        signedHeaders,
        payloadHash,
    ].join("\n");

    const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
    const stringToSign = [
        "AWS4-HMAC-SHA256",
        amzDate,
        credentialScope,
        crypto.createHash("sha256").update(canonicalRequest).digest("hex"),
    ].join("\n");

    const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
    const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

    if (!accessKeyId || !secretAccessKey) {
        logger.error("[AWS Marketplace] AWS credentials not configured (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY).");
        return null;
    }

    const hmac = (key: Buffer | string, data: string) =>
        crypto.createHmac("sha256", key).update(data).digest();

    const signingKey = hmac(
        hmac(
            hmac(hmac(`AWS4${secretAccessKey}`, dateStamp), region),
            service
        ),
        "aws4_request"
    );

    const signature = crypto
        .createHmac("sha256", signingKey)
        .update(stringToSign)
        .digest("hex");

    const authorizationHeader =
        `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, ` +
        `SignedHeaders=${signedHeaders}, Signature=${signature}`;

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Date": amzDate,
                "X-Amz-Target": "AWSMPMeteringService.ResolveCustomer",
                Authorization: authorizationHeader,
            },
            body: payload,
        });

        if (!response.ok) {
            const errBody = await response.text();
            logger.error("[AWS Marketplace] resolveCustomer failed:", { status: response.status, body: errBody });
            return null;
        }

        const data = await response.json() as {
            CustomerIdentifier: string;
            ProductCode: string;
            CustomerAWSAccountId: string;
        };

        return {
            customerId: data.CustomerIdentifier,
            productCode: data.ProductCode,
            customerAWSAccountId: data.CustomerAWSAccountId,
        };
    } catch (err) {
        logger.error("[AWS Marketplace] resolveCustomer network error:", err);
        return null;
    }
}

/**
 * Validates that the certificate URL belongs to a trusted AWS SNS domain.
 * Prevents SSRF and certificate spoofing.
 */
function isValidSnsCertUrl(url: string): boolean {
    const parsed = new URL(url);
    return (
        parsed.protocol === "https:" &&
        parsed.hostname.endsWith(".amazonaws.com") &&
        /^sns\.[a-z0-9\-]+\.amazonaws\.com$/.test(parsed.hostname)
    );
}

/**
 * Verifies the cryptographic signature of an AWS SNS message.
 * See: https://docs.aws.amazon.com/sns/latest/dg/sns-verify-signature-endpoint.html
 */
async function verifySnsSignature(body: any): Promise<boolean> {
    const { Signature, SignatureVersion, SigningCertURL, Type } = body;

    if (SignatureVersion !== "1") {
        logger.warn("[AWS SNS] Unsupported SignatureVersion:", { version: SignatureVersion });
        return false;
    }

    if (!isValidSnsCertUrl(SigningCertURL)) {
        logger.warn("[AWS SNS] Invalid SigningCertURL domain:", { url: SigningCertURL });
        return false;
    }

    try {
        // Fetch the public certificate from AWS
        const certResponse = await fetch(SigningCertURL);
        if (!certResponse.ok) throw new Error(`HTTP ${certResponse.status}`);
        const certText = await certResponse.text();

        // Construct the "String to Sign"
        let stringToSign = "";
        const keys = Type === "Notification"
            ? ["Message", "MessageId", "Subject", "Timestamp", "TopicArn", "Type"]
            : ["Message", "MessageId", "SubscribeURL", "Timestamp", "Token", "TopicArn", "Type"];

        for (const key of keys) {
            if (key in body && body[key] !== undefined) {
                stringToSign += `${key}\n${body[key]}\n`;
            }
        }

        // Verify the signature using the certificate's public key
        const verifier = crypto.createVerify("sha1WithRSAEncryption");
        verifier.update(stringToSign, "utf8");
        return verifier.verify(certText, Signature, "base64");
    } catch (err) {
        logger.error("[AWS SNS] Signature verification failed:", err);
        return false;
    }
}

/**
 * Validates that an SNS notification came from the genuine AWS Marketplace topic.
 */
async function validateSnsNotification(body: any): Promise<boolean> {
    const topicArn = body.TopicArn;
    if (!topicArn || !topicArn.startsWith(AWS_SNS_TOPIC_ARN_PREFIX)) {
        return false;
    }
    return await verifySnsSignature(body);
}

// ─────────────────────────────────────────────────────────────────────────────
// Route 1 — Registration URL (POST /v1/aws/register)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Called by AWS after a buyer completes the subscribe flow in AWS Marketplace.
 * AWS appends ?x-amzn-marketplace-token=<JWT> to the URL configured in AMMP.
 *
 * Flow:
 *   1. Extract the registration token from query params.
 *   2. Call ResolveCustomer API to get the stable customerIdentifier.
 *   3. Upsert tenant row with aws_customer_id (sets tier = developer by default).
 *   4. Redirect buyer to the dashboard onboarding page with their tenant ID.
 *
 * This endpoint must be publicly reachable (no auth — the buyer has no key yet).
 * AWS will retry up to 3 times if it receives a non-2xx response.
 */
router.post("/register", async (req: Request, res: Response) => {
    // AWS sends the token as a query param OR in the body depending on listing type
    const registrationToken =
        (req.query["x-amzn-marketplace-token"] as string | undefined) ||
        req.body?.["x-amzn-marketplace-token"] ||
        req.body?.registrationToken;

    if (!registrationToken || typeof registrationToken !== "string" || registrationToken.trim() === "") {
        logger.warn("[AWS Register] Missing or invalid registration token.");
        return res.status(400).json({ error: "Missing AWS Marketplace registration token" });
    }

    logger.info("[AWS Register] Received registration token — resolving customer...");

    const customer = await resolveAwsCustomerIdentifier(registrationToken);

    if (!customer) {
        // Do not leak internal detail to caller
        return res.status(400).json({ error: "Invalid or expired registration token" });
    }

    const { customerId, productCode, customerAWSAccountId } = customer;

    if (productCode !== process.env.AWS_MARKETPLACE_PRODUCT_CODE) {
        logger.warn("[AWS Register] Product code mismatch:", { received: productCode });
        return res.status(400).json({ error: "Product code mismatch" });
    }

    try {
        // Upsert tenant — use customerId as the tenant primary key for AWS-sourced tenants.
        // If another tenant with this aws_customer_id already exists (e.g., resubscribe),
        // we update their tier rather than creating a duplicate row.
        const tenantId = `aws_${customerId}`;

        await pool.query(
            `INSERT INTO tenants (id, name, aws_customer_id, aws_product_code, aws_account_id, tier)
             VALUES ($1, $2, $3, $4, $5, $6)
             ON CONFLICT (id) DO UPDATE
               SET aws_customer_id  = EXCLUDED.aws_customer_id,
                   aws_product_code = EXCLUDED.aws_product_code,
                   aws_account_id   = EXCLUDED.aws_account_id,
                   updated_at       = NOW()`,
            [tenantId, `AWS Customer ${customerId.slice(0, 8)}`, customerId, productCode, customerAWSAccountId, FALLBACK_TIER]
        );

        logger.info("[AWS Register] Tenant provisioned:", { tenantId, customerId });

        // Redirect buyer to the dashboard onboarding page
        const redirectBase = process.env.AWS_MARKETPLACE_REDIRECT_URL || "https://www.supra-wall.com/onboarding";
        const redirectUrl = `${redirectBase}?tenantId=${encodeURIComponent(tenantId)}&source=aws`;

        return res.redirect(302, redirectUrl);
    } catch (err) {
        logger.error("[AWS Register] Database error during tenant provisioning:", err);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Route 2 — SNS Webhook (POST /v1/aws/sns)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Receives AWS Marketplace SNS subscription lifecycle notifications.
 *
 * AWS sends SNS notifications for these event types:
 *   - subscribe-success     → activate tenant's subscription
 *   - subscribe-fail        → mark subscription as failed
 *   - unsubscribe-pending   → start grace period (do not cut access immediately)
 *   - unsubscribe-success   → revoke access, downgrade to open_source
 *   - entitlement-updated   → buyer upgraded/downgraded plan, update tier
 *
 * SNS first sends a SubscriptionConfirmation message. We auto-confirm by
 * fetching the SubscribeURL (safe — it's an AWS-signed HTTPS endpoint).
 *
 * Security: validate TopicArn prefix before processing any message.
 */
router.post("/sns", express.raw({ type: "application/json" }), async (req: Request, res: Response) => {
    let body: Record<string, any>;

    try {
        const rawBody = req.body instanceof Buffer ? req.body.toString("utf8") : JSON.stringify(req.body);
        body = JSON.parse(rawBody);
    } catch (err) {
        logger.warn("[AWS SNS] Failed to parse SNS notification body:", err);
        return res.status(400).json({ error: "Invalid JSON body" });
    }

    // Validate SNS notification signatures before trusting any content
    if (!(await validateSnsNotification(body))) {
        logger.warn("[AWS SNS] Rejected notification: Signature or TopicArn validation failed.", { topicArn: body.TopicArn });
        return res.status(403).json({ error: "Forbidden: Invalid SNS notification" });
    }

    // Handle SNS subscription confirmation (one-time handshake)
    if (body.Type === "SubscriptionConfirmation") {
        const subscribeUrl = body.SubscribeURL;
        if (typeof subscribeUrl === "string" && subscribeUrl.startsWith("https://sns.")) {
            try {
                await fetch(subscribeUrl); // Confirms the SNS subscription
                logger.info("[AWS SNS] SNS subscription confirmed.");
            } catch (err) {
                logger.error("[AWS SNS] Failed to confirm SNS subscription:", err);
            }
        }
        return res.status(200).json({ confirmed: true });
    }

    // Parse the nested Notification Message
    if (body.Type !== "Notification") {
        return res.status(200).json({ skipped: true }); // Unexpected type — ack and ignore
    }

    let notification: Record<string, any>;
    try {
        notification = JSON.parse(body.Message ?? "{}");
    } catch (err) {
        logger.warn("[AWS SNS] Failed to parse SNS notification Message payload:", err);
        return res.status(400).json({ error: "Invalid Notification Message JSON" });
    }

    const { "action": action, "customer-identifier": customerId, "product-code": productCode, "offer-identifier": offerId } = notification;

    if (!customerId || typeof customerId !== "string") {
        logger.warn("[AWS SNS] Missing customer-identifier in notification.");
        return res.status(400).json({ error: "Missing customer-identifier" });
    }

    const tenantId = `aws_${customerId}`;

    logger.info("[AWS SNS] Processing notification:", { action, customerId, tenantId });

    try {
        switch (action) {
            case "subscribe-success": {
                // Determine tier from offer-identifier (maps to dimension/plan name in AMMP)
                const tier = resolveAwsTierFromOffer(offerId);
                await pool.query(
                    `UPDATE tenants
                     SET tier = $1, aws_subscription_status = 'active', updated_at = NOW()
                     WHERE aws_customer_id = $2`,
                    [tier, customerId]
                );
                logger.info("[AWS SNS] Subscription activated:", { customerId, tier });
                break;
            }

            case "subscribe-fail": {
                await pool.query(
                    `UPDATE tenants
                     SET aws_subscription_status = 'failed', updated_at = NOW()
                     WHERE aws_customer_id = $1`,
                    [customerId]
                );
                logger.warn("[AWS SNS] Subscription failed for customer:", { customerId });
                break;
            }

            case "unsubscribe-pending": {
                // AWS gives a grace period before access is revoked.
                // Mark as pending; do NOT revoke access yet.
                await pool.query(
                    `UPDATE tenants
                     SET aws_subscription_status = 'unsubscribe-pending', updated_at = NOW()
                     WHERE aws_customer_id = $1`,
                    [customerId]
                );
                logger.info("[AWS SNS] Unsubscribe pending for customer:", { customerId });
                break;
            }

            case "unsubscribe-success": {
                // Access must be revoked immediately. Downgrade to open_source hard limits.
                await pool.query(
                    `UPDATE tenants
                     SET tier = 'open_source',
                         aws_subscription_status = 'unsubscribed',
                         updated_at = NOW()
                     WHERE aws_customer_id = $1`,
                    [customerId]
                );
                logger.info("[AWS SNS] Tenant downgraded to open_source:", { tenantId });
                break;
            }

            case "entitlement-updated": {
                // Buyer changed their plan. Re-resolve tier from offerId.
                const newTier = resolveAwsTierFromOffer(offerId);
                await pool.query(
                    `UPDATE tenants
                     SET tier = $1, aws_subscription_status = 'active', updated_at = NOW()
                     WHERE aws_customer_id = $2`,
                    [newTier, customerId]
                );
                logger.info("[AWS SNS] Entitlement updated:", { customerId, newTier });
                break;
            }

            default:
                logger.warn("[AWS SNS] Unhandled notification action:", { action, customerId });
        }

        return res.status(200).json({ received: true });
    } catch (err) {
        logger.error("[AWS SNS] Database error processing notification:", { err, action, customerId });
        // Always return 200 to AWS to prevent infinite retries on DB errors.
        // Errors are captured in logs; use CloudWatch alerts to monitor.
        return res.status(200).json({ received: true, error: "Internal processing error — logged" });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Route 3 — Entitlement Check (GET /v1/aws/entitlement)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Internal entitlement verification endpoint.
 * Used by the dashboard and API gateway to confirm an AWS-sourced tenant
 * has an active subscription before serving paid features.
 *
 * Protected by admin auth (master API key).
 * Query: ?tenantId=aws_<customerId>
 */
import { adminAuth } from "../auth";

router.get("/entitlement", adminAuth, async (req: Request, res: Response) => {
    const tenantId = req.query.tenantId as string | undefined;

    if (!tenantId || typeof tenantId !== "string" || !tenantId.startsWith("aws_")) {
        return res.status(400).json({ error: "Missing or invalid tenantId (must start with aws_)" });
    }

    try {
        const result = await pool.query(
            `SELECT tier, aws_subscription_status, aws_customer_id
             FROM tenants
             WHERE id = $1 LIMIT 1`,
            [tenantId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ entitled: false, reason: "Tenant not found" });
        }

        const { tier, aws_subscription_status, aws_customer_id } = result.rows[0];
        const isActive = aws_subscription_status === "active";

        return res.json({
            entitled: isActive,
            tier,
            awsCustomerId: aws_customer_id,
            subscriptionStatus: aws_subscription_status,
        });
    } catch (err) {
        logger.error("[AWS Entitlement] Database error:", err);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Private helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Maps an AWS offer/dimension identifier to a SupraWall tier.
 * The offer-identifier comes from the SNS entitlement-updated notification
 * and matches the dimension name configured in the AMMP pricing wizard.
 */
function resolveAwsTierFromOffer(offerId: string | undefined): Tier {
    if (!offerId) return FALLBACK_TIER;

    // Normalize: lowercase, strip any suffix (e.g. "team_annual" → "team")
    const normalized = offerId.toLowerCase().split("_")[0];
    return AWS_DIMENSION_TO_TIER[normalized] ?? FALLBACK_TIER;
}

export default router;

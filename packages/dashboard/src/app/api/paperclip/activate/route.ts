// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from "next/server";
import { pool } from "@/lib/db_sql";

export const dynamic = "force-dynamic";

/**
 * GET /api/paperclip/activate?token=<sw_temp_xxx>
 * Returns pending activation info for the given temp token.
 */
export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const token = searchParams.get("token");

    if (!token || !token.startsWith("sw_temp_")) {
        return NextResponse.json({ error: "Invalid or missing activation token" }, { status: 400 });
    }

    try {
        const result = await pool.query(
            `SELECT pt.id, pt.paperclip_company_id, pt.tier, pt.expires_at, pt.activated, pt.activation_email,
                    pc.agent_count, pc.paperclip_version, pc.status as company_status
             FROM paperclip_tokens pt
             LEFT JOIN paperclip_companies pc ON pc.paperclip_company_id = pt.paperclip_company_id
             WHERE pt.token = $1
             LIMIT 1`,
            [token]
        );

        if (result.rows.length === 0) {
            return NextResponse.json({ error: "Token not found or expired" }, { status: 404 });
        }

        const row = result.rows[0];

        if (new Date(row.expires_at) < new Date()) {
            return NextResponse.json({ error: "Activation token has expired. Reinstall the plugin to get a new one." }, { status: 410 });
        }

        return NextResponse.json({
            companyId: row.paperclip_company_id,
            agentCount: row.agent_count || 0,
            tier: row.tier,
            alreadyActivated: row.activated,
            expiresAt: row.expires_at,
        });
    } catch (err) {
        console.error("[Paperclip Activate GET] Error:", err);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}

/**
 * POST /api/paperclip/activate
 * Activates an account: captures email, marks token activated.
 * Body: { token: string, email: string }
 */
export async function POST(request: NextRequest) {
    let body: { token?: string; email?: string };
    try {
        body = await request.json();
    } catch {
        return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
    }

    const { token, email } = body;

    if (!token || !token.startsWith("sw_temp_")) {
        return NextResponse.json({ error: "Invalid activation token" }, { status: 400 });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
    }

    try {
        const tokenResult = await pool.query(
            `SELECT pt.id, pt.tenant_id, pt.paperclip_company_id, pt.tier, pt.expires_at, pt.activated
             FROM paperclip_tokens pt
             WHERE pt.token = $1
             LIMIT 1`,
            [token]
        );

        if (tokenResult.rows.length === 0) {
            return NextResponse.json({ error: "Token not found" }, { status: 404 });
        }

        const row = tokenResult.rows[0];

        if (new Date(row.expires_at) < new Date()) {
            return NextResponse.json({ error: "Token expired" }, { status: 410 });
        }

        // Prevent re-activation (idempotency)
        if (row.activated) {
            return NextResponse.json(
                { error: "This account has already been activated." },
                { status: 409 }
            );
        }

        // Mark token as activated and capture email
        await pool.query(
            `UPDATE paperclip_tokens
             SET activated = TRUE, activation_email = $1
             WHERE token = $2`,
            [email.toLowerCase().trim(), token]
        );

        // Update company status to active
        await pool.query(
            `UPDATE paperclip_companies SET status = 'active'
             WHERE paperclip_company_id = $1`,
            [row.paperclip_company_id]
        );

        return NextResponse.json({
            success: true,
            message: "Account activated successfully",
            tenantId: row.tenant_id,
            tier: row.tier,
            redirectUrl: `/dashboard?source=paperclip_activate&company=${row.paperclip_company_id}`,
        });
    } catch (err) {
        console.error("[Paperclip Activate POST] Error:", err);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}

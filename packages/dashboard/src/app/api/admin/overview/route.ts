// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import { db, getAdminAuth } from '@/lib/firebase-admin';
import { query } from '@/lib/db_sql';
import { stripe } from '@/lib/stripe';
import { subDays, startOfDay } from 'date-fns';

export const dynamic = 'force-dynamic';

const ADMIN_EMAILS = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean);

export async function GET(req: NextRequest) {
    try {
        // --- 1. Admin Auth Check ---
        const authHeader = req.headers.get('authorization');
        if (!authHeader?.startsWith('Bearer ')) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }
        const token = authHeader.slice(7);
        let decodedToken: { email?: string };
        try {
            decodedToken = await getAdminAuth().verifyIdToken(token);
        } catch {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }
        if (!decodedToken.email || !ADMIN_EMAILS.includes(decodedToken.email)) {
            return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
        }

        // --- 2. Aggregate Data from Firebase ---
        const [usersSnap, agentsSnap, orgsSnap] = await Promise.all([
            db.collection('users').get(),
            db.collection('agents').get(),
            db.collection('organizations').get()
        ]);

        const totalUsers = usersSnap.size;
        const totalAgents = agentsSnap.size;
        const totalPaidUsers = orgsSnap.docs.filter(d => d.data().status === 'active').length;

        // --- 3. Aggregate Data from PostgreSQL ---
        // Operations today
        const todayStr = startOfDay(new Date()).toISOString();
        const opsTodayRes = await query(
            "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp >= $1",
            [todayStr]
        );
        const opsToday = parseInt(opsTodayRes.rows[0].count);

        // Success rate today
        const successTodayRes = await query(
            "SELECT decision, COUNT(*) as count FROM audit_logs WHERE timestamp >= $1 GROUP BY decision",
            [todayStr]
        );
        let allowed = 0, denied = 0;
        successTodayRes.rows.forEach(row => {
            if (row.decision === 'ALLOW') allowed = parseInt(row.count);
            else if (row.decision === 'DENY') denied = parseInt(row.count);
        });
        const successRate = allowed + denied > 0 ? (allowed / (allowed + denied) * 100).toFixed(1) + "%" : "100%";

        // --- 4. Aggregate Data from Stripe ---
        let mrr = 0;
        let totalRevenue = 0;
        let churnRate = 0;

        try {
            const subscriptions = await stripe.subscriptions.list({ status: 'active', limit: 100 });
            subscriptions.data.forEach(sub => {
                // Approximate MRR from active subscriptions
                const amount = sub.items.data[0]?.plan?.amount || 0;
                mrr += (amount / 100);
            });

            // Total revenue (last 30 days of paid invoices)
            const invoices = await stripe.invoices.list({ status: 'paid', limit: 100 });
            invoices.data.forEach(inv => {
                totalRevenue += (inv.amount_paid / 100);
            });

            // Churn rate (simplified: canceled in last 30 days / total active)
            const thirtyDaysAgo = Math.floor(subDays(new Date(), 30).getTime() / 1000);
            const canceledSubs = await stripe.subscriptions.list({ 
                status: 'canceled', 
                limit: 100,
                created: { gte: thirtyDaysAgo } 
            });
            const totalActiveCount = subscriptions.data.length || 1;
            churnRate = (canceledSubs.data.length / totalActiveCount) * 100;
        } catch {
            // Stripe metrics unavailable — continue with zero values
        }

        // --- 5. Signup Trends (Last 7 days) ---
        const signupTrends = [];
        for (let i = 6; i >= 0; i--) {
            const date = subDays(new Date(), i);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            // In a better system, this would be a pre-aggregated map
            const count = usersSnap.docs.filter(d => {
                const createdAt = d.data().createdAt;
                if (!createdAt) return false;
                const createdDate = new Date(createdAt);
                return createdDate.toDateString() === date.toDateString();
            }).length;
            signupTrends.push({ date: dateStr, count });
        }

        return NextResponse.json({
            stats: {
                totalUsers,
                totalAgents,
                totalPaidUsers,
                opsToday,
                successRate,
                mrr: Math.round(mrr),
                totalRevenue: Math.round(totalRevenue),
                churnRate: churnRate.toFixed(1) + "%"
            },
            signupTrends
        });

    } catch {
        return NextResponse.json({ error: 'Failed to aggregate admin data' }, { status: 500 });
    }
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import { db, getAdminAuth } from '@/lib/firebase-admin';
import { query } from '@/lib/db_sql';
import { subMonths, startOfMonth, format } from 'date-fns';

export const dynamic = 'force-dynamic';

const ADMIN_EMAILS_RAW = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean);
const ADMIN_EMAILS = ADMIN_EMAILS_RAW.length > 0 ? ADMIN_EMAILS_RAW : ['peghin@gmail.com'];

export async function GET(req: NextRequest) {
    try {
        // --- 0. Admin Auth Check ---
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
        const [usersSnap, agentsSnap, orgsSnap] = await Promise.all([
            db.collection('users').get(),
            db.collection('agents').get(),
            db.collection('organizations').where('status', '==', 'active').get()
        ]);

        const allUserIds = usersSnap.docs.map(d => d.id);
        const usersWithAgents = new Set(agentsSnap.docs.map(d => d.data().userId));
        const paidUserIds = new Set(orgsSnap.docs.map(d => d.id));

        // Let's get "users with evaluations" from PostgreSQL
        const evalUsersRes = await query("SELECT DISTINCT tenantid FROM audit_logs");
        const usersWithEvals = new Set(evalUsersRes.rows.map(r => r.tenantid));

        // --- 1. Compute Funnel Counts ---
        const stage1_Signups = allUserIds.length;
        const stage2_AgentsCreated = allUserIds.filter(id => usersWithAgents.has(id)).length;
        const stage3_FirstEval = allUserIds.filter(id => usersWithEvals.has(id)).length;
        const stage4_Paid = allUserIds.filter(id => paidUserIds.has(id)).length;

        const funnel = [
            { name: "Signups", count: stage1_Signups, ratio: 100 },
            { name: "Agent Created", count: stage2_AgentsCreated, ratio: stage1_Signups > 0 ? Math.round((stage2_AgentsCreated / stage1_Signups) * 100) : 0 },
            { name: "First Eval", count: stage3_FirstEval, ratio: stage2_AgentsCreated > 0 ? Math.round((stage3_FirstEval / stage2_AgentsCreated) * 100) : 0 },
            { name: "Paid Coverage", count: stage4_Paid, ratio: stage3_FirstEval > 0 ? Math.round((stage4_Paid / stage3_FirstEval) * 100) : 0 }
        ];

        // --- 2. Aggregate Funnel Trends (Simplified over last 4 months) ---
        const trends = [];
        for (let i = 3; i >= 0; i--) {
            const start = startOfMonth(subMonths(new Date(), i)).getTime();
            const monthLabel = format(start, 'MMM');
            
            // Simplified count based on createdAt for signups
            const monthlySignups = usersSnap.docs.filter(d => {
                const c = d.data().createdAt;
                return c && new Date(c).getTime() >= start; 
            }).length;
            
            // In a better data system, we'd have timestamps for every conversion.
            // For now, let's provide snapshots.
            trends.push({ month: monthLabel, Signups: monthlySignups, Paid: stage4_Paid });
        }

        return NextResponse.json({
            funnel,
            trends,
            leakyPoint: stage2_AgentsCreated > 0 && (stage3_FirstEval / stage2_AgentsCreated) < 0.5 
                        ? 'Activation Gap (Agent to Eval)' 
                        : stage1_Signups > 0 && (stage2_AgentsCreated / stage1_Signups) < 0.5 
                        ? 'Setup Drop-off (Signup to Agent)' 
                        : 'Retention Gap (Eval to Paid)',
            conversionRate: stage1_Signups > 0 ? (stage4_Paid / stage1_Signups * 100).toFixed(1) + "%" : "0%"
        });

    } catch (error: any) {
        console.error('[Admin Funnel API] Error:', error);
        return NextResponse.json({ error: 'Failed' }, { status: 500 });
    }
}

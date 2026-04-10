// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import { db, getAdminAuth } from '@/lib/firebase-admin';
import { query } from '@/lib/db_sql';
import { subDays, startOfDay, subMonths, format } from 'date-fns';

export const dynamic = 'force-dynamic';

const ADMIN_EMAILS_RAW = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean);
const ADMIN_EMAILS = ADMIN_EMAILS_RAW.length > 0 ? ADMIN_EMAILS_RAW : ['peghin@gmail.com'];

export async function GET(req: NextRequest) {
    try {
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

        const [usersSnap, orgsSnap] = await Promise.all([
            db.collection('users').get(),
            db.collection('organizations').get()
        ]);

        const totalUsers = usersSnap.size;
        const paidUserIds = new Set(orgsSnap.docs.filter(d => d.data().status === 'active').map(d => d.id));

        // --- 1. DAU / WAU / MAU (Based on firestore lastLogin) ---
        const now = new Date();
        const dauCount = usersSnap.docs.filter(d => {
            const last = d.data().lastLogin;
            return last && new Date(last) >= subDays(now, 1);
        }).length;

        const wauCount = usersSnap.docs.filter(d => {
            const last = d.data().lastLogin;
            return last && new Date(last) >= subDays(now, 7);
        }).length;

        const mauCount = usersSnap.docs.filter(d => {
            const last = d.data().lastLogin;
            return last && new Date(last) >= subDays(now, 30);
        }).length;

        // --- 2. Power Users (Top 10 by Eval Volume globally in PG) ---
        const powerUsersRes = await query(
            `SELECT tenantid as userId, COUNT(*) as count 
             FROM audit_logs 
             GROUP BY tenantid 
             ORDER BY count DESC 
             LIMIT 10`
        );

        const powerUsers = powerUsersRes.rows.map(row => {
            const userDoc = usersSnap.docs.find(d => d.id === row.userId);
            return {
                email: userDoc?.data().email || row.userId,
                evaluations: parseInt(row.count),
                isPaid: paidUserIds.has(row.userId)
            };
        });

        // --- 3. User Segments ---
        const segments = [
            { name: 'Free', value: totalUsers - paidUserIds.size },
            { name: 'Paid', value: paidUserIds.size },
            { name: 'Churned', value: orgsSnap.docs.filter(d => d.data().status === 'canceled').length }
        ];

        // --- 4. Retention (Cohort-based) ---
        // Calculate retention by checking if users were active at day 1, 7, 14, 30
        const cohortDays = [1, 7, 14, 30];
        const retention = cohortDays.map(day => {
            const cohortStart = subDays(new Date(), day);
            const usersInCohort = usersSnap.docs.filter(d => {
                const created = d.data().createdAt;
                return created && new Date(created) >= subDays(cohortStart, 1) && new Date(created) < cohortStart;
            }).length;

            if (usersInCohort === 0) return { day: `Day ${day}`, value: 0 };

            const activeInCohort = usersSnap.docs.filter(d => {
                const created = d.data().createdAt;
                const lastLogin = d.data().lastLogin;
                return created && new Date(created) >= subDays(cohortStart, 1) && new Date(created) < cohortStart &&
                       lastLogin && new Date(lastLogin) >= subDays(new Date(), day);
            }).length;

            return { day: `Day ${day}`, value: Math.round((activeInCohort / usersInCohort) * 100 * 10) / 10 };
        });

        // --- 5. Growth (Period-over-period) ---
        const currentPeriodStart = subMonths(new Date(), 1);
        const previousPeriodStart = subMonths(new Date(), 2);

        const currentPeriodUsers = usersSnap.docs.filter(d => {
            const created = d.data().createdAt;
            return created && new Date(created) >= currentPeriodStart;
        }).length;

        const previousPeriodUsers = usersSnap.docs.filter(d => {
            const created = d.data().createdAt;
            return created && new Date(created) >= previousPeriodStart && new Date(created) < currentPeriodStart;
        }).length;

        const totalGrowth = previousPeriodUsers > 0
            ? (((currentPeriodUsers - previousPeriodUsers) / previousPeriodUsers) * 100).toFixed(1)
            : "0";

        const currentPeriodActive = usersSnap.docs.filter(d => {
            const created = d.data().createdAt;
            const lastLogin = d.data().lastLogin;
            return created && new Date(created) >= currentPeriodStart &&
                   lastLogin && new Date(lastLogin) >= subDays(new Date(), 30);
        }).length;

        const previousPeriodActive = usersSnap.docs.filter(d => {
            const created = d.data().createdAt;
            const lastLogin = d.data().lastLogin;
            return created && new Date(created) >= previousPeriodStart && new Date(created) < currentPeriodStart &&
                   lastLogin && new Date(lastLogin) >= subDays(new Date(), 30);
        }).length;

        const activeGrowth = previousPeriodActive > 0
            ? (((currentPeriodActive - previousPeriodActive) / previousPeriodActive) * 100).toFixed(1)
            : "0";

        return NextResponse.json({
            stats: { dauCount, wauCount, mauCount, totalUsers },
            growth: {
                totalGrowth: `${totalGrowth}%`,
                activeGrowth: `${activeGrowth}%`
            },
            segments,
            powerUsers,
            retention
        });

    } catch (error: any) {
        console.error('[Admin User Stats API] Error:', error);
        return NextResponse.json({ error: 'Failed to fetch user analytics' }, { status: 500 });
    }
}

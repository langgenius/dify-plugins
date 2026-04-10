// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from 'next/server';
import { db, getAdminAuth } from '@/lib/firebase-admin';

export const dynamic = 'force-dynamic';

const ADMIN_EMAILS_RAW = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean);
const ADMIN_EMAILS = ADMIN_EMAILS_RAW.length > 0 ? ADMIN_EMAILS_RAW : ['peghin@gmail.com'];
const CRON_SECRET = process.env.CRON_SECRET;

export async function POST(req: NextRequest) {
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

        // Call the cron endpoint with the server-side secret
        if (!CRON_SECRET) {
            return NextResponse.json({ error: 'Cron secret not configured' }, { status: 500 });
        }

        const cronRes = await fetch(process.env.CRON_ENDPOINT || 'http://localhost:3000/api/cron/generate-content', {
            headers: {
                'Authorization': `Bearer ${CRON_SECRET}`
            }
        });

        const data = await cronRes.json();

        if (!cronRes.ok) {
            return NextResponse.json(data, { status: cronRes.status });
        }

        return NextResponse.json(data);

    } catch (error: any) {
        console.error('[Admin Queue API] Error:', error);
        return NextResponse.json({ error: 'Failed to trigger content generation' }, { status: 500 });
    }
}

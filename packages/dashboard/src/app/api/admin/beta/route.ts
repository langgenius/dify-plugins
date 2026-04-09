// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from "next/server";
import { db, getAdminAuth } from "@/lib/firebase-admin";

export const dynamic = "force-dynamic";

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

        const snapshot = await db.collection("waitlist").get();
        const leads = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data(),
            appliedAt: doc.data().appliedAt?.toDate() || new Date()
        })).sort((a, b) => b.appliedAt.getTime() - a.appliedAt.getTime());

        return NextResponse.json({ leads });
    } catch (err: any) {
        console.error("[Admin Beta API] Error:", err);
        return NextResponse.json({ error: "Internal Server Error", message: err.message }, { status: 500 });
    }
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export const dynamic = 'force-dynamic';

import { NextResponse, NextRequest } from 'next/server';
import { getAdminDb, getAdminAuth } from '@/lib/firebase-admin';
import { admin } from '@/lib/firebase-admin';

const ADMIN_EMAILS_RAW = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean);
const ADMIN_EMAILS = ADMIN_EMAILS_RAW.length > 0 ? ADMIN_EMAILS_RAW : ['peghin@gmail.com'];

async function checkAuth(req: Request) {
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) return false;
    const token = authHeader.slice(7);
    try {
        const decodedToken = await getAdminAuth().verifyIdToken(token);
        return decodedToken.email && ADMIN_EMAILS.includes(decodedToken.email);
    } catch {
        return false;
    }
}

// PATCH /api/tasks/[id] - Update task status and review notes
export async function PATCH(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    if (!await checkAuth(request)) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    try {
        const body = await request.json();
        const { id } = await params;
        const db = getAdminDb();

        const updateData: any = {
            status: body.status,
            updatedAt: admin.firestore.FieldValue.serverTimestamp(),
        };

        if (body.humanAction) updateData.humanAction = body.humanAction;
        if (body.humanNote) updateData.humanNote = body.humanNote;
        if (body.reviewedAt) {
            updateData.reviewedAt = admin.firestore.FieldValue.serverTimestamp();
        }

        await db.collection('tasks').doc(id).update(updateData);

        const updatedDoc = await db.collection('tasks').doc(id).get();

        return NextResponse.json({ id, ...updatedDoc.data() });
    } catch (error: any) {
        console.error('Error updating task:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

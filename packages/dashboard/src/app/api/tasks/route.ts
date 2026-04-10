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

// POST /api/tasks - Create a new task
export async function POST(request: Request) {
    if (!await checkAuth(request)) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    try {
        const body = await request.json();
        const db = getAdminDb();

        const taskData = {
            ...body,
            status: body.status || 'pending_review',
            createdAt: admin.firestore.FieldValue.serverTimestamp(),
            updatedAt: admin.firestore.FieldValue.serverTimestamp(),
            reviewedAt: null,
            publishedAt: null,
            humanAction: null,
            humanNote: null
        };

        const docRef = await db.collection('tasks').add(taskData);

        return NextResponse.json({
            id: docRef.id,
            taskNumber: body.taskNumber
        }, { status: 201 });
    } catch (error: any) {
        console.error('Error creating task:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

// GET /api/tasks - Fetch tasks (can be filtered by status)
export async function GET(request: Request) {
    if (!await checkAuth(request)) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    try {
        const { searchParams } = new URL(request.url);
        const status = searchParams.get('status');
        const db = getAdminDb();

        let queryBuilder = db.collection('tasks').orderBy('createdAt', 'desc');

        if (status) {
            const snapshot = await db.collection('tasks')
                .where('status', '==', status)
                .orderBy('createdAt', 'desc')
                .get();

            const tasks = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));

            return NextResponse.json(tasks);
        }

        const snapshot = await queryBuilder.get();
        const tasks = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));

        return NextResponse.json(tasks);
    } catch (error: any) {
        console.error('Error fetching tasks:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

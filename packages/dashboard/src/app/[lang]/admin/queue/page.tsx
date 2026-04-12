// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

'use client';

import React, { useState, useEffect } from 'react';
import { db, auth } from '@/lib/firebase';
import { collection, onSnapshot, query, orderBy, Timestamp } from 'firebase/firestore';
import { Clock, CheckCircle, Loader2, AlertTriangle, Plus, Zap } from 'lucide-react';
import { adminFetch } from '@/lib/admin-fetch';

interface QueueItem {
    id: string;
    status: 'queued' | 'generating' | 'generated' | 'published' | 'failed';
    type: string;
    urlPath: string;
    primaryKeyword: string;
    secondaryKeywords: string[];
    targetSearchVolume?: number;
    priority: number;
    taskNumber?: string;
    createdAt?: Timestamp;
    generatedAt?: Timestamp;
}

export default function QueuePage() {
    const [items, setItems] = useState<QueueItem[]>([]);
    const [triggerLoading, setTriggerLoading] = useState(false);
    const [triggerResult, setTriggerResult] = useState<string | null>(null);

    useEffect(() => {
        const q = query(collection(db, 'content_queue'), orderBy('priority', 'asc'));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            const data = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            })) as QueueItem[];
            setItems(data);
        });
        return () => unsubscribe();
    }, []);

    const triggerGeneration = async () => {
        setTriggerLoading(true);
        setTriggerResult(null);
        try {
            const res = await adminFetch('/api/admin/queue', {
                method: 'POST'
            });
            const data = await res.json();
            if (res.ok) {
                setTriggerResult(`✅ Generated: ${data.page} (${data.keyword}) — Task ${data.taskNumber}`);
            } else {
                setTriggerResult(`❌ Error: ${data.error || data.message}`);
            }
        } catch (err: any) {
            setTriggerResult(`❌ Failed: ${err.message}`);
        } finally {
            setTriggerLoading(false);
        }
    };

    const statusConfig = {
        queued: { icon: Clock, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Queued' },
        generating: { icon: Loader2, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Generating...' },
        generated: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10', label: 'Generated' },
        published: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10', label: 'Published' },
        failed: { icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Failed' },
    };

    const queuedCount = items.filter(i => i.status === 'queued').length;
    const generatedCount = items.filter(i => i.status === 'generated' || i.status === 'published').length;

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Content Queue</h1>
                    <p className="text-neutral-500 text-sm">
                        Automated daily content pipeline — generates one page per day at 8 AM CET.
                    </p>
                </div>
                <button
                    onClick={triggerGeneration}
                    disabled={triggerLoading || queuedCount === 0}
                    className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-neutral-800 disabled:text-neutral-600 text-white font-bold py-2.5 px-5 rounded-xl text-sm transition-all shadow-lg shadow-emerald-900/20"
                >
                    {triggerLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Zap className="w-4 h-4" />
                    )}
                    Generate Now
                </button>
            </header>

            {triggerResult && (
                <div className={`p-4 rounded-xl border text-sm font-medium ${triggerResult.startsWith('✅')
                    ? 'bg-green-500/5 border-green-500/20 text-green-400'
                    : 'bg-red-500/5 border-red-500/20 text-red-400'
                    }`}>
                    {triggerResult}
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <StatCard label="Total Items" value={items.length} />
                <StatCard label="Queued" value={queuedCount} color="blue" />
                <StatCard label="Generated" value={generatedCount} color="green" />
                <StatCard label="Days Left" value={queuedCount} color="purple" />
            </div>

            {/* Queue Table */}
            <div className="bg-neutral-900/50 border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-neutral-500 bg-black/20">
                            <th className="px-6 py-4">#</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Page</th>
                            <th className="px-6 py-4">Keyword</th>
                            <th className="px-6 py-4">Type</th>
                            <th className="px-6 py-4">Vol</th>
                            <th className="px-6 py-4">Task</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {items.map((item, i) => {
                            const config = statusConfig[item.status] || statusConfig.queued;
                            const Icon = config.icon;
                            return (
                                <tr key={item.id} className="hover:bg-white/[0.05] transition-colors">
                                    <td className="px-6 py-4 text-sm text-neutral-600 tabular-nums font-mono">{item.priority}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${config.bg} ${config.color}`}>
                                            <Icon className={`w-3 h-3 ${item.status === 'generating' ? 'animate-spin' : ''}`} />
                                            {config.label}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-white font-medium">{item.urlPath}</td>
                                    <td className="px-6 py-4 text-sm text-neutral-400">{item.primaryKeyword}</td>
                                    <td className="px-6 py-4">
                                        <span className="bg-neutral-800 text-neutral-400 px-2 py-0.5 rounded text-[10px] uppercase font-bold">{item.type}</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-neutral-500 tabular-nums">{item.targetSearchVolume || '—'}</td>
                                    <td className="px-6 py-4 text-xs text-neutral-600 font-mono">{item.taskNumber || '—'}</td>
                                </tr>
                            );
                        })}
                        {items.length === 0 && (
                            <tr>
                                <td colSpan={7} className="px-6 py-12 text-center text-neutral-500">
                                    Content queue is empty. Items will be seeded on next cron run.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="bg-neutral-900/30 border border-white/5 rounded-xl p-4 text-xs text-neutral-600">
                <strong className="text-neutral-400">How it works:</strong> Every day at 8 AM CET, Vercel triggers the <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-neutral-400">/api/cron/generate-content</code> endpoint.
                It picks the next queued item, generates content via Gemini AI, and creates a pending task in the <strong className="text-neutral-400">Task Review</strong> panel for your approval. No laptop needed.
            </div>
        </div>
    );
}

function StatCard({ label, value, color }: { label: string; value: number; color?: string }) {
    const colorMap: Record<string, string> = {
        blue: 'text-blue-400',
        green: 'text-green-400',
        purple: 'text-purple-400',
    };
    return (
        <div className="bg-neutral-900/50 border border-white/5 rounded-xl p-5">
            <div className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold mb-2">{label}</div>
            <div className={`text-3xl font-bold tabular-nums ${colorMap[color || ''] || 'text-white'}`}>{value}</div>
        </div>
    );
}

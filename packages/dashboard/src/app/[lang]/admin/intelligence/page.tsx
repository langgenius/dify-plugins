// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

'use client';

import React, { useState, useEffect } from 'react';
import { db } from '@/lib/firebase';
import { collection, query, orderBy, limit, onSnapshot } from 'firebase/firestore';

interface IntelligenceBrief {
    id: string;
    weekStart: string;
    metrics: Record<string, any>;
    wins: string[];
    problems: string[];
    opportunities: string[];
    actions: {
        p0: string[];
        p1: string[];
        p2: string[];
    };
    createdAt: any;
}

export default function IntelligencePage() {
    const [brief, setBrief] = useState<IntelligenceBrief | null>(null);
    const [activeSection, setActiveSection] = useState<'wins' | 'problems' | 'opportunities' | 'actions'>('wins');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const q = query(collection(db, 'intelligence_briefs'), orderBy('createdAt', 'desc'), limit(1));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            if (!snapshot.empty) {
                setBrief({
                    id: snapshot.docs[0].id,
                    ...snapshot.docs[0].data()
                } as IntelligenceBrief);
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    const addToQueue = async (action: string) => {
        try {
            const timestamp = Date.now();
            const randomSuffix = Math.random().toString(36).substring(2, 8).toUpperCase();
            const taskNumber = `AUTO-${timestamp.toString().slice(-6)}-${randomSuffix}`;

            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    taskNumber,
                    type: 'queue_addition',
                    status: 'pending_review',
                    url: 'TBD',
                    primaryKeyword: action,
                    contentDraft: `Auto-generated task from Intelligence Brief: ${action}`,
                    checklist: ["Verify requirement", "Scope implementation"],
                    batch: "B_INTEL"
                })
            });
            alert('Added to task queue!');
        } catch (error) {
            console.error('Failed to add to queue:', error);
        }
    };

    if (loading) return <div className="p-8 text-zinc-500">Loading intelligence...</div>;
    if (!brief) return <div className="p-8 text-zinc-500">No intelligence briefs found.</div>;

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <header className="mb-10 text-center">
                <h1 className="text-3xl font-bold text-white mb-2">Weekly Intelligence Brief</h1>
                <p className="text-zinc-500 font-mono tracking-widest uppercase text-xs">Week of {brief.weekStart} · Data-driven Insights</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <MetricCard title="Total Impressions" value={brief.metrics?.impressions?.total || 'N/A'} delta={brief.metrics?.impressions?.delta} />
                <MetricCard title="Click-Through Rate" value={`${brief.metrics?.ctr?.value || 'N/A'}%`} delta={brief.metrics?.ctr?.delta} />
                <MetricCard title="Avg Position" value={brief.metrics?.position?.value || 'N/A'} delta={brief.metrics?.position?.delta} inverseDelta />
            </div>

            <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden min-h-[500px] flex flex-col shadow-2xl">
                <nav className="flex border-b border-zinc-800 bg-zinc-950/50">
                    <SectionTab active={activeSection === 'wins'} onClick={() => setActiveSection('wins')}>Wins</SectionTab>
                    <SectionTab active={activeSection === 'problems'} onClick={() => setActiveSection('problems')}>Problems</SectionTab>
                    <SectionTab active={activeSection === 'opportunities'} onClick={() => setActiveSection('opportunities')}>Opportunities</SectionTab>
                    <SectionTab active={activeSection === 'actions'} onClick={() => setActiveSection('actions')}>Recommended Actions</SectionTab>
                </nav>

                <div className="p-8 flex-grow">
                    {activeSection === 'wins' && <ListSection items={brief.wins} color="green" />}
                    {activeSection === 'problems' && <ListSection items={brief.problems} color="red" />}
                    {activeSection === 'opportunities' && <ListSection items={brief.opportunities} color="blue" />}
                    {activeSection === 'actions' && (
                        <div className="space-y-8">
                            <ActionGroup title="P0 · Immediate" actions={brief.actions?.p0} onAdd={addToQueue} priority="high" />
                            <ActionGroup title="P1 · High" actions={brief.actions?.p1} onAdd={addToQueue} priority="medium" />
                            <ActionGroup title="P2 · Backlog" actions={brief.actions?.p2} onAdd={addToQueue} priority="low" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value, delta, inverseDelta }: { title: string, value: string | number, delta?: number, inverseDelta?: boolean }) {
    const isPositive = delta && delta > 0;
    const isGood = inverseDelta ? !isPositive : isPositive;
    return (
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800 shadow-xl">
            <div className="text-zinc-500 text-xs font-bold uppercase tracking-wider mb-2">{title}</div>
            <div className="flex justify-between items-end">
                <div className="text-3xl font-bold text-white">{value}</div>
                {delta !== undefined && (
                    <div className={`text-xs font-bold mb-1 ${isGood ? 'text-green-500' : 'text-red-500'}`}>
                        {isPositive ? '↑' : '↓'} {Math.abs(delta)}%
                    </div>
                )}
            </div>
        </div>
    );
}

function SectionTab({ children, active, onClick }: { children: React.ReactNode, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`px-8 py-4 text-sm font-bold transition-all border-b-2 ${active ? 'text-white border-white bg-zinc-900/50' : 'text-zinc-500 border-transparent hover:text-zinc-300'
                }`}
        >
            {children}
        </button>
    );
}

function ListSection({ items, color }: { items: string[], color: 'green' | 'red' | 'blue' }) {
    const colors = {
        green: 'text-green-500 border-green-500/20',
        red: 'text-red-500 border-red-500/20',
        blue: 'text-blue-400 border-blue-400/20'
    };
    return (
        <ul className="space-y-4">
            {items?.map((item, i) => (
                <li key={i} className={`p-4 rounded-xl border bg-zinc-950/50 text-zinc-300 flex items-start gap-4 ${colors[color]}`}>
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-current shrink-0" />
                    {item}
                </li>
            ))}
        </ul>
    );
}

function ActionGroup({ title, actions, onAdd, priority }: { title: string, actions: string[], onAdd: (s: string) => void, priority: 'high' | 'medium' | 'low' }) {
    const priorityColors = {
        high: 'text-red-500',
        medium: 'text-yellow-500',
        low: 'text-blue-400'
    };
    return (
        <div>
            <h4 className={`text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2 ${priorityColors[priority]}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
                {title}
            </h4>
            <div className="space-y-3">
                {actions?.map((action, i) => (
                    <div key={i} className="flex justify-between items-center p-4 bg-zinc-950/30 rounded-xl border border-zinc-800 group hover:border-zinc-700 transition-colors">
                        <span className="text-zinc-300 text-sm">{action}</span>
                        <button
                            onClick={() => onAdd(action)}
                            className="opacity-0 group-hover:opacity-100 bg-white text-black text-[10px] font-bold py-1 px-3 rounded uppercase tracking-tighter transition-all hover:bg-zinc-200"
                        >
                            Add to Queue
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

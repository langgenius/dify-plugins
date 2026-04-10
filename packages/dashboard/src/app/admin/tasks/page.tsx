// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

'use client';

import React, { useState, useEffect } from 'react';
import { db } from '@/lib/firebase';
import { collection, onSnapshot, query, orderBy, Timestamp } from 'firebase/firestore';
import ReactMarkdown from 'react-markdown';

interface Task {
    id: string;
    taskNumber: string;
    type: string;
    status: string;
    url: string;
    primaryKeyword: string;
    secondaryKeywords: string[];
    sourceFile: string;
    previewUrl: string;
    contentDraft: string;
    checklist: string[];
    humanAction: string | null;
    humanNote: string | null;
    batch: string;
    createdAt: Timestamp;
}

export default function TaskReviewPage() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [activeTab, setActiveTab] = useState('pending_review');
    const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);
    const [revisionNote, setRevisionNote] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const q = query(collection(db, 'tasks'), orderBy('createdAt', 'desc'));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            const taskData = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            })) as Task[];
            setTasks(taskData);
        });

        return () => unsubscribe();
    }, []);

    const filteredTasks = tasks.filter(t => {
        if (activeTab === 'all') return true;
        return t.status === activeTab;
    });

    const counts = {
        pending_review: tasks.filter(t => t.status === 'pending_review').length,
        revision: tasks.filter(t => t.status === 'revision').length,
        approved: tasks.filter(t => t.status === 'approved').length,
        published: tasks.filter(t => t.status === 'published').length,
        rejected: tasks.filter(t => t.status === 'rejected').length,
    };

    const handleAction = async (taskId: string, status: string, humanAction: string, note?: string) => {
        setLoading(true);
        try {
            await fetch(`/api/tasks/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status,
                    humanAction,
                    humanNote: note || null,
                    reviewedAt: new Date().toISOString()
                })
            });
            if (status !== 'revision') {
                setExpandedTaskId(null);
                setRevisionNote('');
            }
        } catch (error) {
            console.error('Action failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <header className="mb-8 flex justify-between items-center bg-zinc-900 p-6 rounded-xl border border-zinc-800 shadow-2xl">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-1">SupraWall Admin · Task Review</h1>
                    <p className="text-zinc-400 text-sm">Human-in-the-loop content governance</p>
                </div>
                <div className="flex gap-4">
                    <StatusPill color="red" count={counts.pending_review} label="Pending" />
                    <StatusPill color="yellow" count={counts.revision} label="Revision" />
                    <StatusPill color="green" count={counts.approved} label="Approved" />
                </div>
            </header>

            <div className="flex bg-zinc-900 p-1 rounded-lg border border-zinc-800 mb-6 gap-1 overflow-x-auto">
                <Tab active={activeTab === 'pending_review'} onClick={() => setActiveTab('pending_review')}>Pending Review</Tab>
                <Tab active={activeTab === 'revision'} onClick={() => setActiveTab('revision')}>Revision</Tab>
                <Tab active={activeTab === 'approved'} onClick={() => setActiveTab('approved')}>Approved</Tab>
                <Tab active={activeTab === 'published'} onClick={() => setActiveTab('published')}>Published</Tab>
                <Tab active={activeTab === 'rejected'} onClick={() => setActiveTab('rejected')}>Rejected</Tab>
                <Tab active={activeTab === 'all'} onClick={() => setActiveTab('all')}>All</Tab>
            </div>

            <div className="space-y-4">
                {filteredTasks.length === 0 ? (
                    <div className="text-center py-20 bg-zinc-900 rounded-xl border border-zinc-800 text-zinc-500">
                        No tasks in this category
                    </div>
                ) : (
                    filteredTasks.map(task => (
                        <div key={task.id} className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden transition-all duration-200 hover:border-zinc-700">
                            <div className="p-5 flex justify-between items-center cursor-pointer" onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}>
                                <div className="flex items-center gap-4">
                                    <span className={`px-2 py-1 rounded text-xs font-mono font-bold ${task.status === 'pending_review' ? 'bg-red-500/10 text-red-500' :
                                            task.status === 'revision' ? 'bg-yellow-500/10 text-yellow-500' :
                                                task.status === 'approved' ? 'bg-green-500/10 text-green-500' :
                                                    'bg-zinc-500/10 text-zinc-500'
                                        }`}>
                                        {task.taskNumber}
                                    </span>
                                    <div>
                                        <div className="text-white font-medium">{task.url}</div>
                                        <div className="text-zinc-500 text-sm">{task.primaryKeyword} · Batch {task.batch}</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-zinc-600 text-xs font-mono">{task.createdAt?.toDate().toLocaleTimeString()}</span>
                                    <button className="text-zinc-400 hover:text-white transition-colors">
                                        {expandedTaskId === task.id ? '▲' : '▼'}
                                    </button>
                                </div>
                            </div>

                            {expandedTaskId === task.id && (
                                <div className="border-t border-zinc-800 p-6 space-y-8 bg-zinc-950/50">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                        <section>
                                            <h3 className="text-zinc-400 text-xs font-bold uppercase tracking-widest mb-4">Checklist</h3>
                                            <ul className="space-y-3">
                                                {task.checklist?.map((item, i) => (
                                                    <li key={i} className="flex items-start gap-3 group">
                                                        <div className="mt-1 w-4 h-4 rounded border border-zinc-700 flex items-center justify-center text-[10px] text-green-500 group-hover:border-green-500/50">
                                                            ✓
                                                        </div>
                                                        <span className="text-zinc-300 text-sm">{item}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </section>

                                        <section>
                                            <h3 className="text-zinc-400 text-xs font-bold uppercase tracking-widest mb-4">Metadata</h3>
                                            <div className="space-y-4">
                                                <MetaItem label="Source File" value={task.sourceFile} />
                                                <MetaItem label="Preview URL" value={task.previewUrl} isLink />
                                                <div className="pt-2">
                                                    <h4 className="text-zinc-500 text-xs font-medium mb-2">Secondary Keywords</h4>
                                                    <div className="flex flex-wrap gap-2">
                                                        {task.secondaryKeywords?.map(kw => (
                                                            <span key={kw} className="bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded text-[10px]">{kw}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </section>
                                    </div>

                                    <section>
                                        <h3 className="text-zinc-400 text-xs font-bold uppercase tracking-widest mb-4">Content Preview</h3>
                                        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800 max-h-[500px] overflow-y-auto prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800">
                                            <ReactMarkdown>{task.contentDraft}</ReactMarkdown>
                                        </div>
                                    </section>

                                    <section className="bg-zinc-900/50 p-6 rounded-xl border border-zinc-800/50">
                                        <h3 className="text-zinc-400 text-xs font-bold uppercase tracking-widest mb-6">Your Decision</h3>

                                        <div className="space-y-6">
                                            <div className="p-4 bg-green-500/5 border border-green-500/10 rounded-lg flex justify-between items-center group hover:bg-green-500/10 transition-all cursor-pointer"
                                                onClick={() => handleAction(task.id, 'approved', 'approved')}>
                                                <div>
                                                    <div className="text-green-500 font-bold mb-0.5">Approve for Publication</div>
                                                    <div className="text-green-500/60 text-xs">Ready to go live. Antigravity will handle the rest.</div>
                                                </div>
                                                <span className="text-xl group-hover:translate-x-1 transition-transform">→</span>
                                            </div>

                                            <div className="space-y-3">
                                                <div className="text-yellow-500 font-bold text-sm">Request Revision</div>
                                                <textarea
                                                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-300 focus:outline-none focus:border-yellow-500/50 transition-colors h-24"
                                                    placeholder="Specify what needs to be changed..."
                                                    value={revisionNote}
                                                    onChange={(e) => setRevisionNote(e.target.value)}
                                                />
                                                <button
                                                    className="bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-2 px-6 rounded-lg text-sm transition-colors disabled:opacity-50"
                                                    disabled={!revisionNote || loading}
                                                    onClick={() => handleAction(task.id, 'revision', 'revision', revisionNote)}
                                                >
                                                    Send for Revision
                                                </button>
                                            </div>

                                            <div className="pt-4 border-t border-zinc-800">
                                                <button
                                                    className="text-red-500/50 hover:text-red-500 text-xs font-medium transition-colors"
                                                    onClick={() => {
                                                        if (confirm('Are you sure you want to reject this task?')) {
                                                            handleAction(task.id, 'rejected', 'rejected');
                                                        }
                                                    }}
                                                >
                                                    ❌ Permanent Reject
                                                </button>
                                            </div>
                                        </div>
                                    </section>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

function StatusPill({ color, count, label }: { color: string, count: number, label: string }) {
    const colors = {
        red: 'bg-red-500 shadow-red-500/20',
        yellow: 'bg-yellow-500 shadow-yellow-500/20',
        green: 'bg-green-500 shadow-green-500/20',
    };
    return (
        <div className="flex items-center gap-2 bg-zinc-800/50 px-3 py-1.5 rounded-full border border-zinc-700">
            <span className={`w-2 h-2 rounded-full ${colors[color as keyof typeof colors]} shadow-lg animate-pulse`}></span>
            <span className="text-zinc-200 text-sm font-bold">{count}</span>
            <span className="text-zinc-500 text-xs">{label}</span>
        </div>
    );
}

function Tab({ children, active, onClick }: { children: React.ReactNode, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all whitespace-nowrap ${active ? 'bg-zinc-800 text-white shadow-xl' : 'text-zinc-500 hover:text-zinc-300'
                }`}
        >
            {children}
        </button>
    );
}

function MetaItem({ label, value, isLink }: { label: string, value: string, isLink?: boolean }) {
    return (
        <div>
            <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider mb-1">{label}</div>
            {isLink ? (
                <a href={value} target="_blank" rel="noopener noreferrer" className="text-blue-400 text-xs hover:underline break-all">
                    {value} ↗
                </a>
            ) : (
                <div className="text-zinc-300 text-xs font-mono break-all">{value}</div>
            )}
        </div>
    );
}

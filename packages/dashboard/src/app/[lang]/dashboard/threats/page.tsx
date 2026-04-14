// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Shield, AlertTriangle, Activity, Skull, Filter, RefreshCw, ChevronRight, Brain, BarChart3, Lock } from "lucide-react";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";

interface ThreatEvent {
    id: number;
    agentid: string;
    event_type: string;
    severity: string;
    details: any;
    createdat: string;
}

interface ThreatSummary {
    id: number;
    entity_id: string;
    entity_type: string;
    threat_score: number;
    total_events: number;
    last_updated: string;
}

interface SemanticEntry {
    id: number;
    agent_id: string;
    tool_name: string;
    semantic_score: number;
    anomaly_score: number | null;
    confidence: string;
    decision_override: string | null;
    reasoning: string;
    model_used: string;
    latency_ms: number;
    timestamp: string;
}

interface BaselineEntry {
    agent_id: string;
    tool_name: string;
    avg_args_length: number;
    avg_calls_per_hour: number;
    common_arg_patterns: string[];
    total_samples: number;
    last_updated: string;
}

export default function ThreatIntelligencePage() {
    const [user] = useAuthState(auth);
    const [events, setEvents] = useState<ThreatEvent[]>([]);
    const [summaries, setSummaries] = useState<ThreatSummary[]>([]);
    const [semanticEntries, setSemanticEntries] = useState<SemanticEntry[]>([]);
    const [baselines, setBaselines] = useState<BaselineEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [aggregating, setAggregating] = useState(false);
    const [activeTab, setActiveTab] = useState<'events' | 'semantic' | 'baselines'>('events');

    const API_BASE = "/api";

    const fetchData = async () => {
        if (!user) return;
        setLoading(true);
        try {
            const tenantId = user.uid;

            const [eventsRes, summaryRes, semanticRes, baselinesRes] = await Promise.all([
                fetch(`${API_BASE}/v1/threat/events?tenantId=${tenantId}`),
                fetch(`${API_BASE}/v1/threat/summary?tenantId=${tenantId}`),
                fetch(`${API_BASE}/v1/threat/semantic?tenantId=${tenantId}`),
                fetch(`${API_BASE}/v1/threat/baselines?tenantId=${tenantId}`),
            ]);

            if (eventsRes.ok) setEvents(await eventsRes.json());
            if (summaryRes.ok) setSummaries(await summaryRes.json());
            if (semanticRes.ok) setSemanticEntries(await semanticRes.json());
            if (baselinesRes.ok) setBaselines(await baselinesRes.json());
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const runAggregation = async () => {
        if (!user) return;
        setAggregating(true);
        try {
            const tenantId = user.uid;
            await fetch(`${API_BASE}/v1/threat/aggregate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tenantId: tenantId })
            });
            await fetchData();
        } catch (e) {
            console.error(e);
        } finally {
            setAggregating(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [user]);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                            <Shield className="w-4 h-4 text-emerald-400" />
                        </div>
                        <h1 className="text-2xl font-black uppercase tracking-tighter text-white italic">Threat Intelligence</h1>
                    </div>
                    <p className="text-neutral-400 text-xs font-medium uppercase tracking-[0.2em]">Network-wide anomaly detection & risk scoring</p>
                </div>

                <div className="flex items-center gap-3">
                    <button 
                        onClick={runAggregation}
                        disabled={aggregating}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded-lg text-[10px] font-black uppercase tracking-widest text-emerald-400 transition-all disabled:opacity-50"
                    >
                        <RefreshCw className={`w-3 h-3 ${aggregating ? 'animate-spin' : ''}`} />
                        {aggregating ? 'Aggregating...' : 'Sync Scores'}
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/[0.05] hover:bg-white/[0.06] border border-white/[0.06] rounded-lg text-[10px] font-black uppercase tracking-widest text-neutral-400 transition-all">
                        <Filter className="w-3 h-3" />
                        Filter
                    </button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2 border-b border-white/[0.06] pb-0">
                {([
                    { key: 'events', label: 'Layer 1 Events', icon: Activity },
                    { key: 'semantic', label: 'AI Semantic (Layer 2)', icon: Brain },
                    { key: 'baselines', label: 'Behavioral Baselines', icon: BarChart3 },
                ] as const).map(({ key, label, icon: Icon }) => (
                    <button
                        key={key}
                        onClick={() => setActiveTab(key)}
                        className={`flex items-center gap-2 px-4 py-3 text-[10px] font-black uppercase tracking-widest transition-all border-b-2 -mb-px ${
                            activeTab === key
                                ? 'border-emerald-500 text-emerald-400'
                                : 'border-transparent text-neutral-500 hover:text-neutral-300'
                        }`}
                    >
                        <Icon className="w-3 h-3" />
                        {label}
                    </button>
                ))}
            </div>

            {/* ── Tab: Layer 1 Events ── */}
            {activeTab === 'events' && <>

            {/* Aggregated Scores */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {summaries.slice(0, 3).map((summary) => (
                    <div key={summary.id} className="relative group overflow-hidden rounded-2xl border border-white/[0.06] bg-neutral-900/50 backdrop-blur-xl p-6 transition-all hover:border-emerald-500/30">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Skull className="w-12 h-12 text-rose-500" />
                        </div>
                        <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest mb-1">Entity: {summary.entity_id}</p>
                        <h3 className="text-3xl font-black text-white mb-4 italic tracking-tighter">{summary.threat_score}</h3>
                        <div className="flex items-center justify-between text-[10px] uppercase font-black tracking-widest">
                            <span className="text-rose-500/80">Threat Level</span>
                            <span className={summary.threat_score > 50 ? "text-rose-500" : "text-amber-500"}>
                                {summary.threat_score > 100 ? "CRITICAL" : (summary.threat_score > 50 ? "HIGH" : "ELEVATED")}
                            </span>
                        </div>
                        <div className="mt-4 w-full h-1 bg-white/[0.05] rounded-full overflow-hidden">
                            <div 
                                className={`h-full transition-all duration-1000 ${summary.threat_score > 50 ? "bg-rose-500" : "bg-amber-500"}`}
                                style={{ width: `${Math.min(summary.threat_score, 100)}%` }}
                            />
                        </div>
                    </div>
                ))}
                {summaries.length === 0 && !loading && (
                    <div className="md:col-span-3 py-12 rounded-2xl border border-dashed border-white/[0.06] flex flex-col items-center justify-center text-neutral-400">
                        <Shield className="w-8 h-8 mb-3 opacity-20" />
                        <p className="text-[10px] font-black uppercase tracking-widest">No critical threats detected</p>
                    </div>
                )}
            </div>

            {/* Live Event Stream */}
            <div className="rounded-2xl border border-white/[0.06] bg-neutral-900/40 overflow-hidden">
                <div className="px-6 py-4 border-b border-white/[0.06] bg-white/[0.05] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Activity className="w-3.5 h-3.5 text-emerald-400" />
                        <h2 className="text-[11px] font-black uppercase tracking-widest text-white">Live Threat Stream</h2>
                    </div>
                    <span className="text-[9px] font-black text-emerald-500/50 uppercase tracking-widest animate-pulse">Scanning Network...</span>
                </div>

                <div className="divide-y divide-white/[0.04]">
                    {events.map((event) => (
                        <div key={event.id} className="p-4 hover:bg-white/[0.05] transition-colors group">
                            <div className="flex items-start gap-4">
                                <div className={`mt-1 p-1.5 rounded-lg border flex-shrink-0 ${
                                    event.severity === 'high' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' :
                                    event.severity === 'medium' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' :
                                    'bg-blue-500/10 border-blue-500/20 text-blue-400'
                                }`}>
                                    <AlertTriangle className="w-3 h-3" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <h4 className="text-[11px] font-black text-white uppercase tracking-wider">{event.event_type.replace(/_/g, ' ')}</h4>
                                        <span className="text-[9px] font-medium text-neutral-600 italic">{new Date(event.createdat).toLocaleString()}</span>
                                    </div>
                                    <p className="text-[10px] text-neutral-400 font-medium mb-2">Agent <code className="text-emerald-400 px-1 bg-emerald-500/5 rounded">{event.agentid}</code> triggered a security flag.</p>
                                    <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
                                        {Object.entries(event.details || {}).map(([k, v]) => (
                                            <span key={k} className="text-[8px] font-black text-neutral-400 border border-white/[0.06] px-2 py-0.5 rounded uppercase tracking-tighter whitespace-nowrap">
                                                {k}: {String(v)}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-neutral-600 hover:text-white">
                                    <ChevronRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                    {events.length === 0 && !loading && (
                        <div className="p-12 text-center text-neutral-600">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em]">Silence is golden. No incidents recorded.</p>
                        </div>
                    )}
                </div>
            </div>

            </>}

            {/* ── Tab: AI Semantic Analysis (Layer 2) ── */}
            {activeTab === 'semantic' && (
                <div className="rounded-2xl border border-white/[0.06] bg-neutral-900/40 overflow-hidden">
                    <div className="px-6 py-4 border-b border-white/[0.06] bg-white/[0.05] flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Brain className="w-3.5 h-3.5 text-emerald-400" />
                            <h2 className="text-[11px] font-black uppercase tracking-widest text-white">Semantic Analysis Feed</h2>
                        </div>
                        <span className="text-[9px] font-black text-neutral-500 uppercase tracking-widest">
                            {semanticEntries.length} entries
                        </span>
                    </div>

                    {semanticEntries.length === 0 && !loading ? (
                        <div className="p-12 text-center">
                            <Lock className="w-8 h-8 mx-auto mb-3 text-neutral-700" />
                            <p className="text-[10px] font-black uppercase tracking-widest text-neutral-500 mb-2">AI Semantic Layer</p>
                            <p className="text-[10px] text-neutral-600">
                                Upgrade to Team tier for AI-powered contextual threat detection.
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-[10px]">
                                <thead>
                                    <tr className="border-b border-white/[0.06] text-neutral-500 font-black uppercase tracking-widest">
                                        <th className="px-4 py-3 text-left">Timestamp</th>
                                        <th className="px-4 py-3 text-left">Agent</th>
                                        <th className="px-4 py-3 text-left">Tool</th>
                                        <th className="px-4 py-3 text-center">Score</th>
                                        <th className="px-4 py-3 text-center">Anomaly</th>
                                        <th className="px-4 py-3 text-center">Confidence</th>
                                        <th className="px-4 py-3 text-center">Decision</th>
                                        <th className="px-4 py-3 text-left">Reasoning</th>
                                        <th className="px-4 py-3 text-right">Latency</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.04]">
                                    {semanticEntries.map((entry) => (
                                        <tr key={entry.id} className="hover:bg-white/[0.03] transition-colors">
                                            <td className="px-4 py-3 text-neutral-400 whitespace-nowrap">
                                                {new Date(entry.timestamp).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-3">
                                                <code className="text-emerald-400 bg-emerald-500/5 px-1 rounded">{entry.agent_id.slice(0, 12)}</code>
                                            </td>
                                            <td className="px-4 py-3 text-white font-bold">{entry.tool_name}</td>
                                            <td className="px-4 py-3 text-center">
                                                <span className={`font-black ${
                                                    entry.semantic_score >= 0.85 ? 'text-rose-400' :
                                                    entry.semantic_score >= 0.6 ? 'text-amber-400' :
                                                    entry.semantic_score >= 0.35 ? 'text-yellow-400' :
                                                    'text-emerald-400'
                                                }`}>
                                                    {entry.semantic_score.toFixed(2)}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-center text-neutral-400">
                                                {entry.anomaly_score !== null ? entry.anomaly_score.toFixed(2) : '—'}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase ${
                                                    entry.confidence === 'high' ? 'bg-rose-500/10 text-rose-400' :
                                                    entry.confidence === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                                                    'bg-emerald-500/10 text-emerald-400'
                                                }`}>
                                                    {entry.confidence}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                {entry.decision_override ? (
                                                    <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase ${
                                                        entry.decision_override === 'DENY' ? 'bg-rose-500/10 text-rose-400' :
                                                        entry.decision_override === 'REQUIRE_APPROVAL' ? 'bg-amber-500/10 text-amber-400' :
                                                        'bg-blue-500/10 text-blue-400'
                                                    }`}>
                                                        {entry.decision_override}
                                                    </span>
                                                ) : (
                                                    <span className="text-neutral-600">—</span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-neutral-400 max-w-[200px] truncate" title={entry.reasoning}>
                                                {entry.reasoning}
                                            </td>
                                            <td className="px-4 py-3 text-right text-neutral-500">{entry.latency_ms}ms</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* ── Tab: Behavioral Baselines ── */}
            {activeTab === 'baselines' && (
                <div className="rounded-2xl border border-white/[0.06] bg-neutral-900/40 overflow-hidden">
                    <div className="px-6 py-4 border-b border-white/[0.06] bg-white/[0.05] flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
                            <h2 className="text-[11px] font-black uppercase tracking-widest text-white">Agent Behavioral Baselines</h2>
                        </div>
                        <span className="text-[9px] font-black text-neutral-500 uppercase tracking-widest">
                            {baselines.length} baselines
                        </span>
                    </div>

                    {baselines.length === 0 && !loading ? (
                        <div className="p-12 text-center">
                            <BarChart3 className="w-8 h-8 mx-auto mb-3 text-neutral-700" />
                            <p className="text-[10px] font-black uppercase tracking-widest text-neutral-500 mb-2">No Baselines Yet</p>
                            <p className="text-[10px] text-neutral-600">
                                Behavioral baselines are built automatically as agents make calls. Available on Business tier and above.
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-[10px]">
                                <thead>
                                    <tr className="border-b border-white/[0.06] text-neutral-500 font-black uppercase tracking-widest">
                                        <th className="px-4 py-3 text-left">Agent</th>
                                        <th className="px-4 py-3 text-left">Tool</th>
                                        <th className="px-4 py-3 text-right">Avg Args Length</th>
                                        <th className="px-4 py-3 text-right">Calls/Hour</th>
                                        <th className="px-4 py-3 text-left">Known Patterns</th>
                                        <th className="px-4 py-3 text-right">Samples</th>
                                        <th className="px-4 py-3 text-right">Last Updated</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.04]">
                                    {baselines.map((b, i) => (
                                        <tr key={i} className="hover:bg-white/[0.03] transition-colors">
                                            <td className="px-4 py-3">
                                                <code className="text-emerald-400 bg-emerald-500/5 px-1 rounded">{b.agent_id.slice(0, 12)}</code>
                                            </td>
                                            <td className="px-4 py-3 text-white font-bold">{b.tool_name}</td>
                                            <td className="px-4 py-3 text-right text-neutral-400">{Math.round(b.avg_args_length)}</td>
                                            <td className="px-4 py-3 text-right text-neutral-400">{b.avg_calls_per_hour.toFixed(1)}</td>
                                            <td className="px-4 py-3">
                                                <div className="flex gap-1 flex-wrap max-w-[200px]">
                                                    {(b.common_arg_patterns || []).slice(0, 5).map((p: string, j: number) => (
                                                        <span key={j} className="px-1.5 py-0.5 bg-white/[0.05] border border-white/[0.06] rounded text-[8px] text-neutral-400">{p}</span>
                                                    ))}
                                                    {(b.common_arg_patterns || []).length > 5 && (
                                                        <span className="text-[8px] text-neutral-600">+{b.common_arg_patterns.length - 5}</span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-right text-neutral-400">{b.total_samples}</td>
                                            <td className="px-4 py-3 text-right text-neutral-500 whitespace-nowrap">
                                                {new Date(b.last_updated).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

        </div>
    );
}

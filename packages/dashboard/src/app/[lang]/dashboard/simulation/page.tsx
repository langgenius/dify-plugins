// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect } from "react";
import { 
    Activity, 
    Play, 
    Square, 
    Zap, 
    ShieldAlert, 
    ShieldCheck, 
    PauseCircle,
    UserCircle,
    Terminal,
    Settings2,
    RefreshCw,
    Database,
    Cloud,
    AlertTriangle,
    CheckCircle2
} from "lucide-react";
import { db, auth } from "@/lib/firebase";
import { collection, query, where, getDocs, addDoc, serverTimestamp, updateDoc, doc, increment } from "firebase/firestore";
import { useAuthState } from "react-firebase-hooks/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";

interface Agent {
    id: string;
    name: string;
    status: string;
}

const SIMULATED_TOOLS = [
    "gmail_send_email",
    "stripe_create_payment",
    "aws_s3_upload",
    "github_create_repo",
    "slack_post_message",
    "openai_generate_completion",
    "zoom_create_meeting",
    "notion_add_page",
    "database_query_sensitive",
    "filesystem_delete_recursive"
];

const DECISIONS = ["ALLOW", "ALLOW", "ALLOW", "DENY", "PAUSED"];

export default function SimulationPage() {
    const [user] = useAuthState(auth);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [selectedAgentId, setSelectedAgentId] = useState<string>("");
    const [isSimulating, setIsSimulating] = useState(false);
    const [simLogs, setSimLogs] = useState<any[]>([]);
    const [speed, setSpeed] = useState(3000); // ms
    const [totalEvents, setTotalEvents] = useState(0);

    useEffect(() => {
        if (!user) return;
        const fetchAgents = async () => {
            const q = query(collection(db, "agents"), where("userId", "==", user.uid));
            const snap = await getDocs(q);
            const list = snap.docs.map(d => ({ id: d.id, name: d.data().name, status: d.data().status }));
            setAgents(list);
            if (list.length > 0) setSelectedAgentId(list[0].id);
        };
        fetchAgents();
    }, [user]);

    useEffect(() => {
        let timer: any;
        if (isSimulating && selectedAgentId && user) {
            timer = setInterval(async () => {
                const tool = SIMULATED_TOOLS[Math.floor(Math.random() * SIMULATED_TOOLS.length)];
                const decision = DECISIONS[Math.floor(Math.random() * DECISIONS.length)];
                const cost = decision === 'ALLOW' ? (Math.random() * 0.5).toFixed(4) : 0;
                const isLoop = Math.random() < 0.1;

                const logData = {
                    userId: user.uid,
                    agentId: selectedAgentId,
                    timestamp: serverTimestamp(),
                    toolName: tool,
                    decision: decision,
                    arguments: JSON.stringify({
                        resource: "production-alpha-" + Math.floor(Math.random() * 1000),
                        volume: Math.floor(Math.random() * 100) + "GB",
                        urgency: "high"
                    }),
                    estimated_cost_usd: parseFloat(cost as string),
                    reason: decision === 'DENY' ? "Policy Violation: Unauthorized resource range" : 
                            decision === 'PAUSED' ? "Human-in-the-loop: External approval required" : "Gatekeeper validated",
                    isLoop: isLoop
                };

                // Add log
                const logRef = await addDoc(collection(db, "audit_logs"), logData);
                
                // Update agent stats
                const agentRef = doc(db, "agents", selectedAgentId);
                await updateDoc(agentRef, {
                    totalCalls: increment(1),
                    totalSpendUsd: increment(parseFloat(cost as string)),
                    lastUsedAt: serverTimestamp()
                });

                setSimLogs(prev => [{ id: logRef.id, ...logData, localTime: new Date().toLocaleTimeString() }, ...prev].slice(0, 10));
                setTotalEvents(prev => prev + 1);

                // If PAUSED, also create an approval request
                if (decision === 'PAUSED') {
                    await addDoc(collection(db, "approvalRequests"), {
                        userId: user.uid,
                        agentId: selectedAgentId,
                        logId: logRef.id,
                        toolName: tool,
                        status: 'pending',
                        requestedAt: serverTimestamp(),
                        parameters: logData.arguments
                    });
                }

            }, speed);
        }
        return () => clearInterval(timer);
    }, [isSimulating, selectedAgentId, user, speed]);

    return (
        <div className="min-h-screen bg-black text-white p-8 font-sans selection:bg-indigo-500/30">
            <div className="max-w-6xl mx-auto space-y-12">
                
                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-8">
                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.1)]">
                                <Zap className="w-6 h-6 text-indigo-400" />
                            </div>
                            <h1 className="text-4xl font-black tracking-tighter uppercase italic">Adversarial Simulator</h1>
                        </div>
                        <p className="text-neutral-400 max-w-lg text-sm font-medium leading-relaxed tracking-wide uppercase">
                            Stress-test your security perimeter by injecting synthetic agent activity and policy-triggering events.
                        </p>
                    </div>

                    <div className="flex items-center gap-4 bg-white/5 p-2 rounded-2xl border border-white/10">
                        <Button 
                            onClick={() => setIsSimulating(!isSimulating)}
                            className={`h-12 px-8 rounded-xl font-black uppercase tracking-widest text-xs transition-all ${
                                isSimulating 
                                    ? "bg-rose-500 text-white hover:bg-rose-600 shadow-[0_0_20px_rgba(244,63,94,0.3)]" 
                                    : "bg-emerald-500 text-black hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                            }`}
                        >
                            {isSimulating ? <><Square className="w-4 h-4 mr-2" /> Halt Simulation</> : <><Play className="w-4 h-4 mr-2" /> Initiate Drift</>}
                        </Button>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Controls Sidebar */}
                    <div className="space-y-8">
                        <section className="bg-neutral-900/60 border border-white/10 rounded-3xl p-8 space-y-8 backdrop-blur-3xl relative overflow-hidden group">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-indigo-500/10 transition-colors" />
                            
                            <div className="space-y-6 relative z-10">
                                <div className="space-y-3">
                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400 ml-1">Assigned Agent Identity</label>
                                    <select 
                                        value={selectedAgentId}
                                        onChange={(e) => setSelectedAgentId(e.target.value)}
                                        className="w-full h-14 bg-black/60 border border-white/10 rounded-2xl px-4 text-sm font-bold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none cursor-pointer"
                                    >
                                        {agents.map(a => (
                                            <option key={a.id} value={a.id}>{a.name} ({a.status})</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="space-y-3">
                                    <div className="flex justify-between items-center px-1">
                                        <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">Emission Frequency</label>
                                        <Badge variant="outline" className="text-indigo-400 border-indigo-500/20">{speed}ms</Badge>
                                    </div>
                                    <input 
                                        type="range" 
                                        min="500" 
                                        max="10000" 
                                        step="500"
                                        value={speed}
                                        onChange={(e) => setSpeed(parseInt(e.target.value))}
                                        className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                                    />
                                    <div className="flex justify-between text-[8px] font-black text-neutral-600 uppercase tracking-widest px-1">
                                        <span>High Frequency</span>
                                        <span>Low Bandwidth</span>
                                    </div>
                                </div>

                                <div className="space-y-4 pt-4 border-t border-white/5">
                                    <div className="flex items-center justify-between bg-black/40 p-4 rounded-2xl border border-white/5">
                                        <div className="flex items-center gap-3">
                                            <Cloud className="w-5 h-5 text-indigo-400" />
                                            <span className="text-xs font-bold uppercase tracking-widest text-neutral-400">Total Injected</span>
                                        </div>
                                        <span className="text-xl font-black text-white">{totalEvents}</span>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <div className="bg-amber-500/5 border border-amber-500/20 rounded-3xl p-6 flex items-start gap-4">
                            <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-relaxed text-amber-500/80">
                                Caution: Simulation generates actual Firebase documents and will impact your real dashboard metrics and cloud usage.
                            </p>
                        </div>
                    </div>

                    {/* Live Stream Page */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-neutral-900/60 border border-white/10 rounded-3xl overflow-hidden min-h-[500px] flex flex-col">
                            <div className="p-6 border-b border-white/5 bg-white/[0.05] flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${isSimulating ? 'bg-emerald-500 animate-pulse' : 'bg-neutral-600'}`} />
                                    <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Live Synthetic Telemetry</h3>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="bg-white/5 text-[9px] font-mono border-white/10 uppercase tracking-widest">Buffer: 10 Events</Badge>
                                </div>
                            </div>

                            <div className="flex-1 p-6 font-mono text-xs space-y-4 overflow-y-auto max-h-[600px] scrollbar-hide">
                                <AnimatePresence initial={false}>
                                    {simLogs.map((log, i) => (
                                        <motion.div 
                                            key={log.id}
                                            initial={{ opacity: 0, x: -20, scale: 0.95 }}
                                            animate={{ opacity: 1, x: 0, scale: 1 }}
                                            className="p-4 bg-black/40 border border-white/5 rounded-2xl space-y-3 relative overflow-hidden"
                                        >
                                            <div className="flex items-center justify-between relative z-10">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-neutral-400 font-bold">[{log.localTime}]</span>
                                                    <span className="text-indigo-400 font-black tracking-tight">{log.toolName}</span>
                                                </div>
                                                <Badge className={`px-2 py-0.5 h-6 text-[9px] font-black border ${
                                                    log.decision === 'ALLOW' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                                                    log.decision === 'PAUSED' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_15px_rgba(245,158,11,0.2)]' :
                                                    'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_15px_rgba(244,63,94,0.1)]'
                                                }`}>
                                                    {log.decision}
                                                </Badge>
                                            </div>
                                            <div className="text-[10px] text-neutral-400 bg-white/5 p-2 rounded-lg border border-white/5 overflow-hidden whitespace-nowrap overflow-ellipsis">
                                                ARGS: {log.arguments}
                                            </div>
                                            {log.decision !== 'ALLOW' && (
                                                <div className="flex items-center gap-2 text-neutral-400">
                                                    <div className={`w-1 h-3 rounded-full ${log.decision === 'PAUSED' ? 'bg-amber-500' : 'bg-rose-500'}`} />
                                                    <span className="italic opacity-60">{log.reason}</span>
                                                </div>
                                            )}
                                            {log.isLoop && (
                                                <div className="absolute top-0 right-0 p-1 bg-indigo-500/20 rounded-bl-xl border-l border-b border-indigo-500/30">
                                                    <RefreshCw className="w-3 h-3 text-indigo-400 animate-spin-slow" />
                                                </div>
                                            )}
                                        </motion.div>
                                    ))}
                                </AnimatePresence>

                                {simLogs.length === 0 && (
                                    <div className="flex flex-col items-center justify-center h-full space-y-4 opacity-20 py-24">
                                        <Database className="w-12 h-12" />
                                        <p className="font-black uppercase tracking-widest text-sm">Awaiting First Signal...</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Visual Breakdown */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-6 flex items-center justify-between">
                                <div className="space-y-1">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Decision Flux</div>
                                    <div className="text-2xl font-black text-white">Adversarial</div>
                                </div>
                                <ShieldAlert className="w-10 h-10 text-rose-500/20" />
                            </div>
                            <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-6 flex items-center justify-between">
                                <div className="space-y-1">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Latency Simulation</div>
                                    <div className="text-2xl font-black text-white">Elastic</div>
                                </div>
                                <Activity className="w-10 h-10 text-emerald-500/20" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

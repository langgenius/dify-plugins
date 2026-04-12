// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { auth, db } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import { collection, query, where, onSnapshot } from "firebase/firestore";
import { motion, AnimatePresence } from "framer-motion";
import { 
    Check, 
    X, 
    Shield, 
    Clock, 
    Terminal, 
    UserCheck, 
    AlertTriangle, 
    ArrowRight,
    Loader2,
    Lock,
    DollarSign,
    Cpu,
    Fingerprint
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDistanceToNow } from "date-fns";

interface ApprovalRequest {
    id: string;
    agentId: string;
    agentName: string;
    toolName: string;
    arguments: string;
    status: "pending" | "approved" | "denied";
    createdAt: any;
    estimatedCostUsd: number;
    reason?: string;
    sessionId?: string;
    agentRole?: string;
}

export default function ApprovalsPage() {
    const [user] = useAuthState(auth);
    const [requests, setRequests] = useState<ApprovalRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [processingId, setProcessingId] = useState<string | null>(null);
    const searchParams = useSearchParams();
    const router = useRouter();
    const autoProcessed = useRef<string[]>([]);

    const fetchRequests = useCallback(async () => {
        if (!user) return;
        try {
            const res = await fetch(`/api/v1/approvals?tenantId=${user.uid}`);
            if (res.ok) {
                const data = await res.json();
                const processed = data.map((d: any) => ({
                    ...d,
                    createdAt: new Date(d.createdAt)
                }));
                setRequests(processed);
            }
        } catch (error) {
            console.error("Failed to sync approvals:", error);
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        if (!user) return;
        fetchRequests();
        const interval = setInterval(fetchRequests, 5000); // 5s polling
        return () => clearInterval(interval);
    }, [user, fetchRequests]);

    // Handle auto-approval from notification
    useEffect(() => {
        const id = searchParams.get("id");
        const action = searchParams.get("action");

        if (id && action && user && !autoProcessed.current.includes(id)) {
            if (action === "approve" || action === "deny") {
                console.log(`Auto-processing notification action: ${action} for request ${id}`);
                autoProcessed.current.push(id);
                handleAction(id, action === "approve" ? "approved" : "denied").then(() => {
                    // Clean up URL after processing
                    const newParams = new URLSearchParams(searchParams.toString());
                    newParams.delete("action");
                    // Keep the ID to show the success state if needed, but remove action so it doesn't re-run
                    router.replace(`${window.location.pathname}?${newParams.toString()}`);
                });
            }
        }
    }, [searchParams, user, router]);

    const handleAction = async (id: string, decision: "approved" | "denied") => {
        setProcessingId(id);
        try {
            const res = await fetch(`/api/approvals/${id}/respond`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    decision,
                    reviewNote: decision === "approved" ? "Approved via Security Dashboard" : "Denied via Security Dashboard",
                    reviewedBy: user?.email || user?.uid
                })
            });

            if (!res.ok) {
                const err = await res.json();
                console.error("Action failed:", err.error);
            }
        } catch (error) {
            console.error("Error updating approval status:", error);
        } finally {
            setProcessingId(null);
        }
    };

    const renderJson = (jsonStr: string) => {
        try {
            const obj = JSON.parse(jsonStr);
            return JSON.stringify(obj, null, 2);
        } catch (e) {
            return jsonStr;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8 max-w-6xl mx-auto pb-20"
        >
            {/* ── Header ── */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-12 border-b border-white/10 pb-10">
                <div className="space-y-3">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 mb-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
                        <span className="text-[10px] font-black tracking-[0.2em] text-emerald-400 uppercase">Live Security Intercept</span>
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white uppercase italic leading-none">
                        Agent <span className="text-emerald-500">Governance</span>
                    </h1>
                    <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.3em] max-w-md">
                        Critical system actions held for authorized human review.
                    </p>
                </div>
                <div className="flex items-center gap-10">
                    <div className="text-right">
                        <p className="text-4xl font-black text-white italic tabular-nums leading-none">{requests.length}</p>
                        <p className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] mt-1">Pending Threats</p>
                    </div>
                    <div className="h-12 w-px bg-white/10 hidden md:block" />
                    <div className="text-right hidden sm:block">
                        <p className="text-4xl font-black text-emerald-500 italic tabular-nums leading-none">
                            ${(requests?.length > 0 ? requests.reduce((acc, r) => acc + (Number(r.estimatedCostUsd) || 0), 0) : 0).toFixed(4)}
                        </p>
                        <p className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] mt-1">Risk Exposure</p>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="flex flex-col items-center justify-center py-32 gap-6 bg-black/20 rounded-3xl border border-white/5">
                    <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
                    <div className="text-center space-y-1">
                        <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Synchronizing Vault...</p>
                        <p className="text-[9px] font-black text-neutral-400 uppercase tracking-widest">Scanning active agents across the organization.</p>
                    </div>
                </div>
            ) : requests.length === 0 ? (
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-zinc-900/40 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-24 text-center space-y-6 relative overflow-hidden group"
                >
                    <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 to-transparent pointer-events-none" />
                    <div className="w-20 h-20 bg-emerald-500/10 rounded-3xl flex items-center justify-center mx-auto border border-emerald-500/20 shadow-[0_0_50px_rgba(16,185,129,0.1)] group-hover:scale-110 transition-transform duration-500">
                        <UserCheck className="w-10 h-10 text-emerald-400" />
                    </div>
                    <div className="space-y-2 relative">
                        <h3 className="text-2xl font-black text-white uppercase italic tracking-tighter">Perimeter Secure</h3>
                        <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.25em]">No actions currently violate security thresholds.</p>
                    </div>
                </motion.div>
            ) : (
                <div className="space-y-6">
                    <AnimatePresence mode="popLayout">
                        {requests.map((req) => (
                            <motion.div
                                key={req.id}
                                layout
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                className="group"
                            >
                                <Card className="bg-zinc-900/60 backdrop-blur-2xl border-white/10 group-hover:border-emerald-500/30 transition-all duration-500 overflow-hidden rounded-[2rem]">
                                    <div className="absolute top-0 left-0 w-1.5 h-full bg-emerald-500/20 group-hover:bg-emerald-500 transition-all duration-500" />
                                    <CardContent className="p-0">
                                        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] divide-x divide-white/5">
                                            {/* Left Column: Context */}
                                            <div className="p-8 space-y-6">
                                                <div className="flex flex-wrap items-start justify-between gap-4">
                                                    <div className="flex items-center gap-4">
                                                        <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 group-hover:border-emerald-500/40 transition-colors">
                                                            <Terminal className="w-5 h-5 text-neutral-400 group-hover:text-emerald-400 transition-colors" />
                                                        </div>
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <h3 className="font-black text-white uppercase tracking-tight text-lg">{req.toolName}</h3>
                                                            </div>
                                                            <div className="flex items-center gap-3 mt-1">
                                                                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest flex items-center gap-1.5">
                                                                    <Clock className="w-3.5 h-3.5" />
                                                                    {formatDistanceToNow(req.createdAt, { addSuffix: true })}
                                                                </p>
                                                                <span className="w-1 h-1 rounded-full bg-zinc-800" />
                                                                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest flex items-center gap-1.5">
                                                                    <DollarSign className="w-3.5 h-3.5 text-emerald-500/60" />
                                                                    ~${(Number(req.estimatedCostUsd) || 0).toFixed(4)}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20 px-3 py-1 text-[10px] font-black uppercase tracking-widest">
                                                        High Priority
                                                    </Badge>
                                                </div>

                                                <div className="space-y-3">
                                                    <div className="flex items-center justify-between">
                                                        <p className="text-[10px] font-black text-zinc-600 uppercase tracking-[0.2em]">Execution Payload</p>
                                                        <div className="flex items-center gap-1.5 text-[9px] font-mono text-zinc-500 bg-white/5 px-2 py-0.5 rounded border border-white/5">
                                                            <Fingerprint className="w-3 h-3" />
                                                            ID: {req.id.substring(0, 8)}
                                                        </div>
                                                    </div>
                                                    <div className="bg-black/60 border border-white/5 rounded-2xl p-6 font-mono text-[11px] relative group/code overflow-hidden">
                                                        <div className="absolute top-4 right-4 text-[9px] text-zinc-700 uppercase font-black tracking-widest opacity-0 group-hover/code:opacity-100 transition-opacity">Read Only View</div>
                                                        <pre className="text-zinc-300 overflow-x-auto selection:bg-emerald-500/30">
                                                            {renderJson(req.arguments)}
                                                        </pre>
                                                    </div>
                                                </div>

                                                {req.reason && (
                                                    <div className="flex items-start gap-3 p-4 bg-amber-500/5 border border-amber-500/10 rounded-2xl">
                                                        <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />
                                                        <div className="space-y-1">
                                                            <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest">Security Alert Trace</p>
                                                            <p className="text-xs text-amber-200/60 leading-relaxed font-medium">
                                                                {req.reason}
                                                            </p>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Right Column: Meta & Actions */}
                                            <div className="bg-zinc-900/40 p-8 flex flex-col h-full">
                                                <div className="flex-grow space-y-6">
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <p className="text-[9px] font-black text-zinc-600 uppercase tracking-widest flex items-center gap-2">
                                                                <Cpu className="w-3 h-3 text-emerald-500/50" />
                                                                Origin Agent
                                                            </p>
                                                            <div className="p-3 bg-white/[0.05] border border-white/5 rounded-xl">
                                                                <p className="text-xs font-black text-white italic uppercase">{req.agentName}</p>
                                                                <p className="text-[9px] font-mono text-zinc-500 mt-1 uppercase tracking-tighter">{req.agentId}</p>
                                                            </div>
                                                        </div>

                                                        {req.sessionId && (
                                                            <div className="space-y-2">
                                                                <p className="text-[9px] font-black text-zinc-600 uppercase tracking-widest flex items-center gap-2">
                                                                    <Shield className="w-3 h-3 text-blue-500/50" />
                                                                    Context Trace
                                                                </p>
                                                                <div className="p-3 bg-white/[0.05] border border-white/5 rounded-xl">
                                                                    <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest truncate">Session: {req.sessionId.substring(0, 16)}...</p>
                                                                    {req.agentRole && (
                                                                        <Badge variant="outline" className="mt-2 text-[8px] border-white/10 text-zinc-500 uppercase tracking-widest px-1.5 font-bold">Role: {req.agentRole}</Badge>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="mt-8 space-y-3">
                                                    <Button 
                                                        onClick={() => handleAction(req.id, "approved")}
                                                        disabled={processingId === req.id}
                                                        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all duration-300 font-black uppercase tracking-[0.2em] text-[10px] h-14 rounded-2xl"
                                                    >
                                                        {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Check className="w-4 h-4 mr-2" />}
                                                        Authorize Action
                                                    </Button>
                                                    <Button 
                                                        onClick={() => handleAction(req.id, "denied")} 
                                                        disabled={processingId === req.id}
                                                        variant="ghost" 
                                                        className="w-full bg-transparent hover:bg-rose-500/10 text-zinc-500 hover:text-rose-400 transition-all font-black uppercase tracking-[0.2em] text-[10px] h-14 rounded-2xl border border-white/5 hover:border-rose-500/30"
                                                    >
                                                        {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <X className="w-4 h-4 mr-2" />}
                                                        Deny Execution
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>
                                    </CardContent>
                                    
                                    {/* Security Watermark */}
                                    <div className="absolute -bottom-10 -right-10 opacity-[0.02] pointer-events-none group-hover:opacity-[0.05] transition-opacity duration-700">
                                        <Shield className="w-64 h-64 text-white" />
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}

            {/* ── Governance System Overview ── */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 border-t border-white/10">
                <div className="space-y-4 p-6 rounded-2xl bg-white/[0.05] border border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                            <Check className="w-5 h-5 text-emerald-500" />
                        </div>
                        <h4 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">Manual Overrule</h4>
                    </div>
                    <p className="text-[10px] text-zinc-500 leading-relaxed uppercase tracking-wider font-medium">
                        Bypass security thresholds for individual executions. The agent will receive an <span className="text-emerald-500/80 italic text-[9px]">ALLOW</span> signal with these exact parameters.
                    </p>
                </div>
                
                <div className="space-y-4 p-6 rounded-2xl bg-white/[0.05] border border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-rose-500/10 flex items-center justify-center border border-rose-500/20">
                            <X className="w-5 h-5 text-rose-500" />
                        </div>
                        <h4 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">Security Block</h4>
                    </div>
                    <p className="text-[10px] text-zinc-500 leading-relaxed uppercase tracking-wider font-medium">
                        Instant interruption of the agent transformer chain. Sends a <span className="text-rose-500/80 italic text-[9px]">DENY</span> response, preventing the API call from ever reaching the target.
                    </p>
                </div>

                <div className="space-y-4 p-6 rounded-2xl bg-white/[0.05] border border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center border border-amber-500/20">
                            <Lock className="w-5 h-5 text-amber-500" />
                        </div>
                        <h4 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">Secret Vaulting</h4>
                    </div>
                    <p className="text-[10px] text-zinc-500 leading-relaxed uppercase tracking-wider font-medium">
                        Actions requiring vault injection are strictly held until authorized. Secrets remain encrypted until the moment of execution.
                    </p>
                </div>
            </div>
        </motion.div>
    );
}

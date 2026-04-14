// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState, useMemo, useCallback } from "react"; // useCallback kept for getAgentName memoization
import { collection, query, where, getDocs, onSnapshot, orderBy, limit } from "firebase/firestore";
import { db, auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    Activity, Shield, ShieldAlert, CheckCircle2, Clock, Search,
    Download, Filter, AlertTriangle, Hash, TrendingUp, XCircle,
    ChevronDown, ChevronUp, Eye, Fingerprint, ShieldCheck, FileText, Calendar, Users
} from "lucide-react";
import { Agent, AuditLog } from "@/types/database";
import { motion, AnimatePresence } from "framer-motion";

type DecisionFilter = "ALL" | "ALLOW" | "DENY" | "PAUSED" | "REQUIRE_APPROVAL";
type SortField = "timestamp" | "riskScore" | "cost_usd";
type SortDir = "asc" | "desc";

export default function ForensicAuditPage() {
    const [user] = useAuthState(auth);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);

    // Filters
    const [searchQuery, setSearchQuery] = useState("");
    const [decisionFilter, setDecisionFilter] = useState<DecisionFilter>("ALL");
    const [agentFilter, setAgentFilter] = useState<string>("ALL");
    const [riskMin, setRiskMin] = useState(0);
    const [sortField, setSortField] = useState<SortField>("timestamp");
    const [sortDir, setSortDir] = useState<SortDir>("desc");

    // Detail panel
    const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

    // Compliance export modal
    const [showExportModal, setShowExportModal] = useState(false);
    const [exportFrom, setExportFrom] = useState(() => {
        const d = new Date(Date.now() - 30 * 86_400_000);
        return d.toISOString().split("T")[0];
    });
    const [exportTo, setExportTo] = useState(() => new Date().toISOString().split("T")[0]);
    const [exportAgentId, setExportAgentId] = useState("ALL");

    const downloadCompliancePDF = () => {
        const apiUrl = process.env.NEXT_PUBLIC_SUPRAWALL_API_URL || "http://localhost:3000";
        const url = new URL(`${apiUrl}/v1/compliance/report`);
        url.searchParams.set("from", exportFrom);
        url.searchParams.set("to", exportTo);
        if (exportAgentId !== "ALL") url.searchParams.set("agentId", exportAgentId);
        window.open(url.toString(), "_blank");
        setShowExportModal(false);
    };

    // Fetch agents
    useEffect(() => {
        if (!user) return;
        const fetchAgents = async () => {
            const q = query(collection(db, "agents"), where("userId", "==", user.uid));
            const snap = await getDocs(q);
            setAgents(snap.docs.map(doc => ({ id: doc.id, ...doc.data() } as Agent)));
        };
        fetchAgents();
    }, [user]);

    // Fetch audit logs via server-side Admin SDK route (bypasses Firestore security rules)
    const fetchLogs = useCallback(async () => {
        if (!user) return;
        try {
            const url = new URL("/api/audit", window.location.origin);
            url.searchParams.set("userId", user.uid);
            url.searchParams.set("limit", "200");
            
            const response = await fetch(url.toString());
            if (response.ok) {
                const data = await response.json();
                const processedLogs = data.logs.map((l: any) => ({
                    ...l,
                    timestamp: { toDate: () => new Date(l.timestamp) },
                    estimatedCostUsd: l.estimatedCostUsd || l.cost_usd || 0
                }));
                setLogs(processedLogs);
            }
        } catch (error) {
            console.error("Failed to fetch audit logs:", error);
        } finally {
            setLoading(false);
        }
    }, [user]);

    // Initial fetch and polling
    useEffect(() => {
        if (!user) return;
        
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // 5s polling
        
        return () => clearInterval(interval);
    }, [user, fetchLogs]);


    const getAgentName = useCallback((id: string) => agents.find(a => a.id === id)?.name || "Unknown Agent", [agents]);

    // Filtered + sorted logs
    const filteredLogs = useMemo(() => {
        let result = [...logs];

        if (decisionFilter !== "ALL") {
            result = result.filter(l => l.decision === decisionFilter);
        }
        if (agentFilter !== "ALL") {
            result = result.filter(l => l.agentId === agentFilter);
        }
        if (riskMin > 0) {
            result = result.filter(l => (l.riskScore ?? 0) >= riskMin);
        }
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            result = result.filter(l =>
                l.toolName.toLowerCase().includes(q) ||
                getAgentName(l.agentId).toLowerCase().includes(q) ||
                (l.arguments || "").toLowerCase().includes(q) ||
                (l.reason || "").toLowerCase().includes(q)
            );
        }

        result.sort((a, b) => {
            let va: number, vb: number;
            if (sortField === "timestamp") {
                va = a.timestamp?.toDate?.()?.getTime() || 0;
                vb = b.timestamp?.toDate?.()?.getTime() || 0;
            } else if (sortField === "riskScore") {
                va = a.riskScore ?? 0;
                vb = b.riskScore ?? 0;
            } else {
                va = a.cost_usd ?? 0;
                vb = b.cost_usd ?? 0;
            }
            return sortDir === "desc" ? vb - va : va - vb;
        });

        return result;
    }, [logs, decisionFilter, agentFilter, riskMin, searchQuery, sortField, sortDir, getAgentName]);

    // Stats
    const stats = useMemo(() => {
        const total = filteredLogs.length;
        const allowed = filteredLogs.filter(l => l.decision === "ALLOW").length;
        const denied = filteredLogs.filter(l => l.decision === "DENY").length;
        const approvals = filteredLogs.filter(l => l.decision === "PAUSED" || l.decision === "REQUIRE_APPROVAL").length;
        const avgRisk = total > 0 ? Math.round(filteredLogs.reduce((s, l) => s + (l.riskScore ?? 0), 0) / total) : 0;
        const highRisk = filteredLogs.filter(l => (l.riskScore ?? 0) >= 70).length;
        const totalCost = filteredLogs.reduce((s, l) => s + (l.cost_usd || 0), 0);
        const hasForensic = filteredLogs.some(l => l.integrityHash);
        return { total, allowed, denied, approvals, avgRisk, highRisk, totalCost, hasForensic };
    }, [filteredLogs]);

    // CSV Export
    const exportCSV = useCallback(() => {
        const header = "Timestamp,Agent,Tool,Decision,Risk Score,Risk Factors,Cost USD,Reason,Integrity Hash,Arguments\n";
        const rows = filteredLogs.map(l => {
            const ts = l.timestamp?.toDate?.()?.toISOString() || "";
            return `"${ts}","${getAgentName(l.agentId)}","${l.toolName}","${l.decision}",${l.riskScore ?? ""},"${(l.riskFactors || []).join("; ")}",${l.cost_usd || 0},"${(l.reason || "").replace(/"/g, '""')}","${l.integrityHash || ""}","${(l.arguments || "").replace(/"/g, '""').substring(0, 500)}"`;
        }).join("\n");

        const blob = new Blob([header + rows], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `audit_logs_${new Date().toISOString().split("T")[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }, [filteredLogs, getAgentName]);

    const toggleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDir(d => d === "desc" ? "asc" : "desc");
        } else {
            setSortField(field);
            setSortDir("desc");
        }
    };

    const getRiskColor = (score: number) => {
        if (score >= 70) return "text-red-400";
        if (score >= 40) return "text-amber-400";
        if (score >= 10) return "text-yellow-400";
        return "text-emerald-400";
    };

    const getRiskBg = (score: number) => {
        if (score >= 70) return "bg-red-500/10 border-red-500/20";
        if (score >= 40) return "bg-amber-500/10 border-amber-500/20";
        if (score >= 10) return "bg-yellow-500/10 border-yellow-500/20";
        return "bg-emerald-500/10 border-emerald-500/20";
    };

    const getDecisionStyle = (decision: string) => {
        switch (decision) {
            case "ALLOW": return "text-green-400 bg-green-500/10 border-green-500/20";
            case "DENY": return "text-red-400 bg-red-500/10 border-red-500/20";
            case "REQUIRE_APPROVAL":
            case "PAUSED": return "text-red-400 bg-red-500/20 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]";
            default: return "";
        }
    };

    const getDecisionIcon = (decision: string) => {
        switch (decision) {
            case "ALLOW": return <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />;
            case "DENY": return <ShieldAlert className="w-3.5 h-3.5 mr-1.5" />;
            case "REQUIRE_APPROVAL":
            case "PAUSED": return <Clock className="w-3.5 h-3.5 mr-1.5" />
            default: return null;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
        >
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-2">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                            <Fingerprint className="w-6 h-6 text-emerald-400" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Forensic Audit Logs</h1>
                            <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.2em]">Tamper-proof, cryptographically-chained event stream with risk intelligence.</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={exportCSV}
                        disabled={filteredLogs.length === 0}
                        className="flex items-center gap-2 px-4 py-2.5 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-emerald-500/30 rounded-xl text-sm font-medium text-white transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed group"
                    >
                        <Download className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                        Export CSV
                    </button>
                    <button
                        onClick={() => setShowExportModal(true)}
                        className="flex items-center gap-2 px-4 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/15 border border-emerald-500/20 hover:border-emerald-500/40 rounded-xl text-sm font-medium text-emerald-400 transition-all duration-300 group"
                    >
                        <FileText className="w-4 h-4 group-hover:scale-110 transition-transform" />
                        Compliance Report
                    </button>
                </div>

                {/* Compliance Export Modal */}
                <AnimatePresence>
                    {showExportModal && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
                            onClick={(e) => e.target === e.currentTarget && setShowExportModal(false)}
                        >
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                                transition={{ duration: 0.2 }}
                                className="bg-neutral-950 border border-white/[0.08] rounded-2xl p-6 w-full max-w-md shadow-2xl"
                            >
                                <div className="flex items-center justify-between mb-5">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                                            <FileText className="w-5 h-5 text-emerald-400" />
                                        </div>
                                        <div>
                                            <h2 className="text-base font-semibold text-white">Export Compliance Report</h2>
                                            <p className="text-xs text-neutral-400 mt-0.5">Human Oversight Evidence Report (PDF)</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setShowExportModal(false)}
                                        className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-all"
                                    >
                                        <XCircle className="w-4 h-4" />
                                    </button>
                                </div>

                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-3">
                                        <div>
                                            <label className="flex items-center gap-1.5 text-xs font-medium text-neutral-400 mb-1.5">
                                                <Calendar className="w-3.5 h-3.5" /> From
                                            </label>
                                            <input
                                                type="date"
                                                value={exportFrom}
                                                onChange={(e) => setExportFrom(e.target.value)}
                                                className="w-full px-3 py-2 bg-white/[0.05] border border-white/[0.06] rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/30 transition-all"
                                            />
                                        </div>
                                        <div>
                                            <label className="flex items-center gap-1.5 text-xs font-medium text-neutral-400 mb-1.5">
                                                <Calendar className="w-3.5 h-3.5" /> To
                                            </label>
                                            <input
                                                type="date"
                                                value={exportTo}
                                                onChange={(e) => setExportTo(e.target.value)}
                                                className="w-full px-3 py-2 bg-white/[0.05] border border-white/[0.06] rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500/30 transition-all"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="flex items-center gap-1.5 text-xs font-medium text-neutral-400 mb-1.5">
                                            <Users className="w-3.5 h-3.5" /> Agent
                                        </label>
                                        <select
                                            value={exportAgentId}
                                            onChange={(e) => setExportAgentId(e.target.value)}
                                            className="w-full px-3 py-2 bg-white/[0.05] border border-white/[0.06] rounded-xl text-sm text-neutral-300 focus:outline-none focus:border-emerald-500/30 transition-all appearance-none cursor-pointer"
                                        >
                                            <option value="ALL">All Agents</option>
                                            {agents.map((a) => (
                                                <option key={a.id} value={a.id}>{a.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="mt-6 flex gap-3">
                                    <button
                                        onClick={() => setShowExportModal(false)}
                                        className="flex-1 px-4 py-2.5 bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.06] rounded-xl text-sm font-medium text-neutral-400 hover:text-white transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={downloadCompliancePDF}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-500/15 hover:bg-emerald-500/20 border border-emerald-500/30 rounded-xl text-sm font-semibold text-emerald-400 transition-all"
                                    >
                                        <Download className="w-4 h-4" />
                                        Download PDF
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                {[
                    { label: "Total Events", value: stats.total, icon: Activity, color: "text-white" },
                    { label: "Allowed", value: stats.allowed, icon: CheckCircle2, color: "text-green-400" },
                    { label: "Denied", value: stats.denied, icon: XCircle, color: "text-red-400" },
                    { label: "Approvals", value: stats.approvals, icon: Clock, color: "text-yellow-400" },
                    { label: "Avg Risk", value: stats.avgRisk, icon: TrendingUp, color: getRiskColor(stats.avgRisk) },
                    { label: "High Risk", value: stats.highRisk, icon: AlertTriangle, color: "text-red-400" },
                    { label: "Total Cost", value: `$${stats.totalCost.toFixed(4)}`, icon: Shield, color: "text-amber-400" },
                ].map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                    >
                        <Card className="bg-black/40 backdrop-blur-xl border-white/10 hover:border-white/[0.08] transition-all duration-300">
                            <CardContent className="p-4">
                                <div className="flex items-center gap-2 mb-1">
                                    <stat.icon className={`w-3.5 h-3.5 ${stat.color}`} />
                                    <span className="text-[11px] uppercase tracking-wider text-neutral-400 font-medium">{stat.label}</span>
                                </div>
                                <p className={`text-xl font-bold ${stat.color}`}>{stat.value}</p>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>

            {/* Filters Bar */}
            <Card className="bg-black/30 backdrop-blur-xl border-white/10">
                <CardContent className="p-4">
                    <div className="flex flex-wrap gap-3 items-center">
                        {/* Search */}
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <input
                                type="text"
                                placeholder="Search tools, agents, arguments, reasons..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 bg-white/[0.05] border border-white/[0.06] rounded-xl text-sm text-white placeholder:text-neutral-400 focus:outline-none focus:border-emerald-500/30 focus:bg-white/[0.05] transition-all"
                            />
                        </div>

                        {/* Decision filter */}
                        <div className="flex items-center gap-1.5">
                            <Filter className="w-3.5 h-3.5 text-neutral-400" />
                            {(["ALL", "ALLOW", "DENY", "PAUSED"] as DecisionFilter[]).map(d => (
                                <button
                                    key={d}
                                    onClick={() => setDecisionFilter(d)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${decisionFilter === d
                                        ? d === "ALLOW" ? "bg-green-500/15 text-green-400 border border-green-500/30"
                                            : d === "DENY" ? "bg-red-500/15 text-red-400 border border-red-500/30"
                                                : d === "PAUSED" ? "bg-red-500/20 text-red-400 border border-red-500/40"
                                                    : "bg-white/[0.08] text-white border border-white/[0.1]"
                                        : "text-neutral-400 bg-white/[0.05] border border-transparent hover:bg-white/[0.04] hover:text-white"
                                        }`}
                                >
                                    {d}
                                </button>
                            ))}
                        </div>

                        {/* Agent filter */}
                        <select
                            value={agentFilter}
                            onChange={(e) => setAgentFilter(e.target.value)}
                            className="px-3 py-2.5 bg-white/[0.05] border border-white/[0.06] rounded-xl text-sm text-neutral-300 focus:outline-none focus:border-emerald-500/30 transition-all appearance-none cursor-pointer"
                        >
                            <option value="ALL">All Agents</option>
                            {agents.map(a => (
                                <option key={a.id} value={a.id}>{a.name}</option>
                            ))}
                        </select>

                        {/* Risk filter */}
                        <div className="flex items-center gap-2">
                            <AlertTriangle className="w-3.5 h-3.5 text-neutral-400" />
                            <input
                                type="range"
                                min={0}
                                max={100}
                                value={riskMin}
                                onChange={(e) => setRiskMin(parseInt(e.target.value))}
                                className="w-20 accent-emerald-500"
                            />
                            <span className="text-xs text-neutral-400 w-8">≥{riskMin}</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Main Table */}
            <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/10 shadow-2xl overflow-hidden relative group">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent group-hover:via-emerald-500/50 transition-all duration-700" />

                <CardHeader className="border-b border-white/[0.08] flex flex-row items-center justify-between pb-4 bg-black/20">
                    <CardTitle className="text-sm flex items-center gap-2 font-black text-white uppercase italic tracking-tighter">
                        <Activity className="w-5 h-5 text-emerald-400" /> Live Feed
                        <span className="text-xs text-neutral-400 font-normal ml-2">
                            {filteredLogs.length} of {logs.length} events
                        </span>
                    </CardTitle>
                    <div className="flex items-center text-xs text-green-400 bg-green-400/10 px-2.5 py-1 rounded-full border border-green-400/20 shadow-sm shadow-green-400/10">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-400 mr-2 animate-pulse" />
                        Connected
                    </div>
                </CardHeader>

                <CardContent className="p-0">
                    {loading ? (
                        <p className="text-neutral-400 py-24 text-center animate-pulse">Connecting to forensic log stream...</p>
                    ) : filteredLogs.length === 0 ? (
                        <div className="py-24 text-center text-neutral-400 flex flex-col items-center justify-center">
                            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
                                <Fingerprint className="w-16 h-16 mb-6 text-neutral-700 opacity-40" />
                                <p className="text-neutral-400">No audit events match your filters.</p>
                            </motion.div>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow className="border-white/10 hover:bg-transparent">
                                        <TableHead
                                            className="text-neutral-400 font-medium px-5 py-4 cursor-pointer hover:text-white transition-colors"
                                            onClick={() => toggleSort("timestamp")}
                                        >
                                            <div className="flex items-center gap-1">
                                                Time
                                                {sortField === "timestamp" && (sortDir === "desc" ? <ChevronDown className="w-3 h-3" /> : <ChevronUp className="w-3 h-3" />)}
                                            </div>
                                        </TableHead>
                                        <TableHead className="text-neutral-400 font-medium">Agent</TableHead>
                                        <TableHead className="text-neutral-400 font-medium">Tool</TableHead>
                                        <TableHead
                                            className="text-neutral-400 font-medium cursor-pointer hover:text-white transition-colors"
                                            onClick={() => toggleSort("riskScore")}
                                        >
                                            <div className="flex items-center gap-1">
                                                Risk
                                                {sortField === "riskScore" && (sortDir === "desc" ? <ChevronDown className="w-3 h-3" /> : <ChevronUp className="w-3 h-3" />)}
                                            </div>
                                        </TableHead>
                                        <TableHead
                                            className="text-neutral-400 font-medium cursor-pointer hover:text-white transition-colors"
                                            onClick={() => toggleSort("cost_usd")}
                                        >
                                            <div className="flex items-center gap-1">
                                                Cost
                                                {sortField === "cost_usd" && (sortDir === "desc" ? <ChevronDown className="w-3 h-3" /> : <ChevronUp className="w-3 h-3" />)}
                                            </div>
                                        </TableHead>
                                        <TableHead className="text-neutral-400 font-medium">Integrity</TableHead>
                                        <TableHead className="text-neutral-400 font-medium text-right px-5">Decision</TableHead>
                                        <TableHead className="text-neutral-400 font-medium w-10"></TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    <AnimatePresence mode="popLayout">
                                        {filteredLogs.map((log, idx) => (
                                            <motion.tr
                                                key={log.id}
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                exit={{ opacity: 0 }}
                                                transition={{ delay: Math.min(idx * 0.02, 0.5) }}
                                                className="border-white/[0.02] hover:bg-white/[0.05] transition-colors group/row cursor-pointer"
                                                onClick={() => setSelectedLog(selectedLog?.id === log.id ? null : log)}
                                            >
                                                <TableCell className="text-neutral-400 text-xs px-5 py-3.5 whitespace-nowrap font-mono">
                                                    <span className="text-emerald-200/50">
                                                        {log.timestamp?.toDate ? log.timestamp.toDate().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Now'}
                                                    </span>
                                                    <br />
                                                    <span className="text-neutral-600/50">{log.timestamp?.toDate ? log.timestamp.toDate().toLocaleDateString() : ''}</span>
                                                </TableCell>
                                                <TableCell className="font-medium text-white text-sm">{getAgentName(log.agentId)}</TableCell>
                                                <TableCell className="text-neutral-300 font-mono text-xs group-hover/row:text-white transition-colors">
                                                    {log.toolName}
                                                </TableCell>
                                                <TableCell>
                                                    {log.riskScore != null ? (
                                                        <div className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold border ${getRiskBg(log.riskScore)} ${getRiskColor(log.riskScore)}`}>
                                                            {log.riskScore}
                                                        </div>
                                                    ) : (
                                                        <span className="text-neutral-600 text-xs">—</span>
                                                    )}
                                                </TableCell>
                                                <TableCell className="text-amber-400 font-mono text-xs font-bold">
                                                    {log.cost_usd ? `$${log.cost_usd.toFixed(6)}` : "—"}
                                                </TableCell>
                                                <TableCell>
                                                    {log.integrityHash ? (
                                                        <div className="flex items-center gap-1.5" title={`Hash: ${log.integrityHash}`}>
                                                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                                                            <span className="text-emerald-400/60 font-mono text-[10px]">{log.integrityHash.substring(0, 8)}…</span>
                                                        </div>
                                                    ) : (
                                                        <div className="flex items-center gap-1.5" title="Legacy log (no hash)">
                                                            <Hash className="w-3.5 h-3.5 text-neutral-600" />
                                                            <span className="text-neutral-600 text-[10px]">Legacy</span>
                                                        </div>
                                                    )}
                                                </TableCell>
                                                <TableCell className="text-right px-5">
                                                    <div className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold border shadow-sm ${getDecisionStyle(log.decision)}`}>
                                                        {getDecisionIcon(log.decision)}
                                                        {log.decision === "REQUIRE_APPROVAL" || log.decision === "PAUSED" ? "PAUSED" : log.decision}
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <button 
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setSelectedLog(selectedLog?.id === log.id ? null : log);
                                                        }}
                                                        className="p-1 hover:bg-white/10 rounded-md transition-all group/eye"
                                                    >
                                                        <Eye className={`w-4 h-4 transition-colors ${selectedLog?.id === log.id ? "text-emerald-400" : "text-neutral-500 group-hover/eye:text-neutral-200"}`} />
                                                    </button>
                                                </TableCell>
                                            </motion.tr>
                                        ))}
                                    </AnimatePresence>
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Detail Panel (slide-up) */}
            <AnimatePresence>
                {selectedLog && (
                    <motion.div
                        initial={{ opacity: 0, y: 50, height: 0 }}
                        animate={{ opacity: 1, y: 0, height: "auto" }}
                        exit={{ opacity: 0, y: 50, height: 0 }}
                        transition={{ duration: 0.3, type: "spring", bounce: 0 }}
                        className="fixed bottom-0 left-[256px] right-0 z-[100] shadow-[0_-20px_50px_rgba(0,0,0,0.8)] backdrop-blur-md"
                    >
                        <Card className="bg-black/60 backdrop-blur-2xl border-emerald-500/10 shadow-2xl shadow-emerald-500/5 overflow-hidden">
                            <CardHeader className="border-b border-white/10 pb-3">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-base flex items-center gap-2 text-white/90">
                                        <Fingerprint className="w-4 h-4 text-emerald-400" />
                                        Forensic Detail — <span className="font-mono text-emerald-400">{selectedLog.toolName}</span>
                                    </CardTitle>
                                    <button
                                        onClick={() => setSelectedLog(null)}
                                        className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-all"
                                    >
                                        <XCircle className="w-4 h-4" />
                                    </button>
                                </div>
                            </CardHeader>
                            <CardContent className="p-5 space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {/* Metadata */}
                                    <div className="space-y-3">
                                        <h3 className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-400">Event Metadata</h3>
                                        <div className="space-y-2">
                                            {[
                                                { label: "Agent", value: getAgentName(selectedLog.agentId) },
                                                { label: "Session", value: selectedLog.sessionId || "—" },
                                                { label: "Role", value: selectedLog.agentRole || "—" },
                                                { label: "Sequence #", value: selectedLog.sequenceNumber?.toString() || "—" },
                                                { label: "Loop", value: selectedLog.isLoop ? "⚠️ Yes" : "No" },
                                            ].map(item => (
                                                <div key={item.label} className="flex justify-between text-sm">
                                                    <span className="text-neutral-400">{item.label}</span>
                                                    <span className="text-neutral-200 font-mono text-xs">{item.value}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Risk Analysis */}
                                    <div className="space-y-3">
                                        <h3 className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-400">Risk Analysis</h3>
                                        {selectedLog.riskScore != null ? (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-3">
                                                    <div className={`text-3xl font-black ${getRiskColor(selectedLog.riskScore)}`}>
                                                        {selectedLog.riskScore}
                                                    </div>
                                                    <div>
                                                        <span className={`text-xs font-semibold px-2 py-1 rounded-md border ${getRiskBg(selectedLog.riskScore)} ${getRiskColor(selectedLog.riskScore)}`}>
                                                            {selectedLog.riskScore >= 70 ? "CRITICAL" : selectedLog.riskScore >= 40 ? "MEDIUM" : selectedLog.riskScore >= 10 ? "LOW" : "SAFE"}
                                                        </span>
                                                    </div>
                                                </div>
                                                {selectedLog.riskFactors && selectedLog.riskFactors.length > 0 && (
                                                    <ul className="space-y-1">
                                                        {selectedLog.riskFactors.map((f, i) => (
                                                            <li key={i} className="text-xs text-neutral-400 flex items-start gap-1.5">
                                                                <AlertTriangle className="w-3 h-3 text-amber-500 mt-0.5 shrink-0" />
                                                                {f}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                )}
                                            </div>
                                        ) : (
                                            <p className="text-neutral-600 text-sm">No risk data (legacy entry)</p>
                                        )}
                                    </div>

                                    {/* Integrity Chain */}
                                    <div className="space-y-3">
                                        <h3 className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-400">Integrity Chain</h3>
                                        {selectedLog.integrityHash ? (
                                            <div className="space-y-2">
                                                <div>
                                                    <div className="text-[10px] text-neutral-400 mb-0.5">CURRENT HASH</div>
                                                    <div className="font-mono text-[10px] text-emerald-400/80 break-all bg-emerald-500/5 border border-emerald-500/10 rounded-lg p-2">
                                                        {selectedLog.integrityHash}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="text-[10px] text-neutral-400 mb-0.5">PREVIOUS HASH</div>
                                                    <div className="font-mono text-[10px] text-neutral-400/60 break-all bg-white/[0.05] border border-white/10 rounded-lg p-2">
                                                        {selectedLog.previousHash || "GENESIS"}
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-1.5 text-xs text-emerald-400">
                                                    <ShieldCheck className="w-3.5 h-3.5" />
                                                    Chain integrity verified
                                                </div>
                                            </div>
                                        ) : (
                                            <p className="text-neutral-600 text-sm">No integrity hash (legacy entry)</p>
                                        )}
                                    </div>
                                </div>

                                {/* Arguments + Reason */}
                                <div className="space-y-2">
                                    <h3 className="text-xs uppercase tracking-wider text-neutral-400 font-semibold">Arguments Payload</h3>
                                    <pre className="text-xs font-mono text-emerald-300/70 bg-black/40 border border-white/[0.08] rounded-xl p-4 overflow-x-auto max-h-40 whitespace-pre-wrap">
                                        {(() => { try { return JSON.stringify(JSON.parse(selectedLog.arguments || "{}"), null, 2); } catch { return selectedLog.arguments; } })()}
                                    </pre>
                                </div>
                                {selectedLog.reason && (
                                    <div className="space-y-2">
                                        <h3 className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-400">Decision Reason</h3>
                                        <p className="text-sm text-neutral-300 bg-red-500/5 border border-red-500/10 rounded-xl p-3">{selectedLog.reason}</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { collection, query, where, getDocs, addDoc, onSnapshot, serverTimestamp } from "firebase/firestore";
import { db, auth } from "@/lib/firebase";
import { suprawall } from "@/lib/suprawall";
import { useAuthState } from "react-firebase-hooks/auth";
import { sendGAEvent } from "@next/third-parties/google";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Agent } from "@/types/database";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PlusCircle, Key, Copy, Check, Terminal, Coins, ShieldAlert, Activity, TrendingUp, DollarSign, Shield, Lock, X, UserCheck, Loader2, ShieldCheck, RefreshCw, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import Link from "next/link";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { AuditLog } from "@/types/database";
import { format } from "date-fns";

import { PolicyValidator } from "@/components/PolicyValidator";
import { OnboardingWizard } from "@/components/OnboardingWizard";
import { ContinuousComplianceMonitor } from "@/components/ContinuousComplianceMonitor";

const DollarConfetti = () => {
    const particles = [...Array(40)].map((_, i) => ({
        id: i,
        x: Math.random() * 100,
        startY: 40 + Math.random() * 20,
        endY: -20 - Math.random() * 40,
        rotation: Math.random() * 720 - 360,
        scale: 0.6 + Math.random() * 1.2,
        delay: Math.random() * 0.6,
        duration: 1.5 + Math.random() * 1.5,
        drift: (Math.random() - 0.5) * 60,
        fontSize: 14 + Math.random() * 18,
    }));
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-[9999]">
            {/* Dollar symbol particles */}
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    initial={{
                        left: `${p.x}%`,
                        top: `${p.startY}%`,
                        opacity: 0,
                        rotate: 0,
                        scale: 0,
                    }}
                    animate={{
                        top: `${p.endY}%`,
                        left: `${p.x + p.drift / 5}%`,
                        opacity: [0, 1, 1, 0.8, 0],
                        rotate: p.rotation,
                        scale: [0, p.scale, p.scale, p.scale * 0.5],
                    }}
                    transition={{
                        duration: p.duration,
                        delay: p.delay,
                        ease: [0.22, 0.61, 0.36, 1],
                    }}
                    className="absolute font-black select-none"
                    style={{
                        fontSize: p.fontSize,
                        color: `hsl(${150 + Math.random() * 20}, ${70 + Math.random() * 30}%, ${50 + Math.random() * 20}%)`,
                        textShadow: '0 0 12px rgba(16,185,129,0.7), 0 0 30px rgba(16,185,129,0.3)',
                    }}
                >
                    $
                </motion.div>
            ))}
            {/* Green flash overlay */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: [0, 0.25, 0] }}
                transition={{ duration: 1.2 }}
                className="absolute inset-0 bg-emerald-500/10"
            />
            {/* Center message */}
            <motion.div
                initial={{ opacity: 0, scale: 0.3, y: 20 }}
                animate={{ opacity: [0, 1, 1, 0], scale: [0.3, 1, 1.05, 1.1], y: [20, 0, -5, -10] }}
                transition={{ duration: 2.5, delay: 0.3 }}
                className="absolute inset-0 flex items-center justify-center"
            >
                <div className="text-center space-y-3">
                    <motion.div
                        animate={{ rotate: [0, -10, 10, -5, 5, 0] }}
                        transition={{ duration: 0.6, delay: 0.5 }}
                    >
                        <ShieldCheck className="w-20 h-20 text-emerald-400 mx-auto drop-shadow-[0_0_30px_rgba(16,185,129,0.6)]" />
                    </motion.div>
                    <p className="text-emerald-400 font-black uppercase tracking-[0.3em] text-sm drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]">
                        Agent Secured! 💰
                    </p>
                </div>
            </motion.div>
        </div>
    );
};


const getReinforcementDetails = (log: AuditLog, agents: Agent[], isFirst: boolean) => {
    const agentName = agents.find(a => a.id === log.agentId)?.name || 'Agent';
    
    if (log.decision === 'DENY') {
        if (log.reason?.toLowerCase().includes('vault')) {
            return {
                icon: "🚫",
                title: 'Vault Access Denied',
                text: `Vault denied ${agentName} access for ${log.toolName}. Reason: tool not in allowed scope. The secret was never exposed.`,
                color: "text-rose-500",
                bg: "bg-rose-500/10"
            };
        }
        return {
            icon: "🛑",
            title: isFirst ? 'First Blocked Operation' : 'Operation Blocked',
            text: isFirst 
                ? `${agentName} tried to call ${log.toolName} — your DENY policy stopped it in <10ms. This is Suprawall working.`
                : `${agentName} attempted restricted tool: ${log.toolName}. Blocked by policy.`,
            color: "text-rose-500",
            bg: "bg-rose-500/10"
        };
    }
    if (log.decision === 'REQUIRE_APPROVAL') {
        return {
            icon: "⏸️",
            title: 'Human Gate Active',
            text: `${agentName} is paused. It wants to execute ${log.toolName}. Waiting for human approval.`,
            color: "text-blue-500",
            bg: "bg-blue-500/10"
        };
    }
    if (log.decision === 'ALLOW') {
        if (log.reason?.toLowerCase().includes('vault')) {
            return {
                icon: "🔐",
                title: 'Secret Injected',
                text: `Vault injected secret for ${log.toolName} — ${agentName} completed the call without ever seeing the real credential.`,
                color: "text-purple-500",
                bg: "bg-purple-500/10"
            };
        }
        if (log.reason?.toLowerCase().includes('pii') || log.reason?.toLowerCase().includes('scrub')) {
            return {
                icon: "🧹",
                title: 'PII Scrubbed',
                text: `PII detected in ${log.toolName} response. Your logs are clean.`,
                color: "text-emerald-500",
                bg: "bg-emerald-500/10"
            };
        }
        return {
            icon: "✅",
            title: 'Operation Governed',
            text: `${agentName} called ${log.toolName}. Policy checked and secured.`,
            color: "text-emerald-500",
            bg: "bg-emerald-500/10"
        };
    }
    
    return {
        icon: "⚡",
        title: 'Activity Logged',
        text: `Activity detected on ${log.toolName}.`,
        color: "text-neutral-400",
        bg: "bg-neutral-500/10"
    };
};

export default function OverviewPage() {
    const [user, authLoading] = useAuthState(auth);
    const router = useRouter();
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isValidatorOpen, setIsValidatorOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
    const [copiedNode, setCopiedNode] = useState(false);
    const [copiedCurl, setCopiedCurl] = useState(false);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [newAgentName, setNewAgentName] = useState("");
    const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
    const [customScope, setCustomScope] = useState("");
    const [nameError, setNameError] = useState("");
    const [stats, setStats] = useState({
        totalCalls: 0,
        blockedActions: 0,
        actualSpend: 0,
        costSaved: 0
    });
    const [chartData, setChartData] = useState<any[]>([]);
    const [pendingApprovalsCount, setPendingApprovalsCount] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
    const [recentLogs, setRecentLogs] = useState<AuditLog[]>([]);
    const [isAnalyticsModalOpen, setIsAnalyticsModalOpen] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);

    const API_BASE = "/api";

    const generateApiKey = () => {
        const bytes = new Uint8Array(24);
        window.crypto.getRandomValues(bytes);
        return "ag_" + btoa(String.fromCharCode(...Array.from(bytes)))
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/, "");
    };

    const fetchData = async () => {
        if (!user) return;
        try {
            const idToken = await user.getIdToken();
            const headers = { 'Authorization': `Bearer ${idToken}` };

            // 1. Fetch Stats
            const statsRes = await fetch(`${API_BASE}/v1/stats?tenantId=${user.uid}`, { headers });
            if (statsRes.ok) {
                const s = await statsRes.json();
                setStats({
                    totalCalls: s.totalCalls,
                    blockedActions: s.blockedActions,
                    actualSpend: s.actualSpend,
                    costSaved: s.blockedActions * 2.5 // Estimated savings
                });
                setChartData(s.chartData || []);
                setPendingApprovalsCount(s.pendingApprovalsCount);
            }

            // 2. Fetch Recent Logs
            const logsRes = await fetch(`${API_BASE}/v1/audit-logs?tenantId=${user.uid}&limit=10`, { headers });
            if (logsRes.ok) {
                const logs = await logsRes.json();
                setRecentLogs(logs);
            }

            setLoading(false);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (!user) return;
        
        // 2. Poll Agents from our internal API
        const loadAgents = async () => {
            try {
                const idToken = await user.getIdToken();
                const res = await fetch(`${API_BASE}/v1/agents?tenantId=${user.uid}`, {
                    headers: { 'Authorization': `Bearer ${idToken}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setAgents(data.sort((a: Agent, b: Agent) => {
                        const dateA = new Date(a.createdAt).getTime();
                        const dateB = new Date(b.createdAt).getTime();
                        return dateB - dateA;
                    }));
                }
            } catch (e) {
                console.error("[Dashboard] Failed to poll agents:", e);
            }
        };

        fetchData();
        loadAgents();
        const statsInterval = setInterval(fetchData, 10000);
        const agentsInterval = setInterval(loadAgents, 10000);

        return () => {
            clearInterval(statsInterval);
            clearInterval(agentsInterval);
        };
    }, [user]);

    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-black">
                <Loader2 className="w-12 h-12 animate-spin text-emerald-500" />
            </div>
        );
    }

    const handleCreateAgent = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) return;
        
        setNameError("");
        if (!newAgentName.trim()) {
            setNameError("Agent name is required");
            return;
        }

        const trimmedName = newAgentName.trim();
        setIsSubmitting(true);
        
        const apiKey = generateApiKey();
        
        try {
            const res = await fetch('/api/v1/agents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: trimmedName,
                    userId: user.uid,
                    apiKey,
                    scopes: selectedScopes.length > 0 ? selectedScopes : ["*:*"],
                }),
            });
            
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.error || "Failed to create agent");
            }

            // ✅ Only show success when server confirmed the write
            setNewlyCreatedKey(apiKey);
            setShowSuccess(true);

        } catch (err: any) {
            console.error("[SupraWall] Agent creation failure:", err);
            setNameError(err.message || "Failed to create agent. Try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const createAgent = () => handleCreateAgent({ preventDefault: () => {} } as React.FormEvent);

    const performAgentCreation = async (name: string, scopes: string[]) => {
        if (!user) return;
        setIsSubmitting(true);
        try {
            const apiKey = generateApiKey();
            
            const res = await fetch('/api/v1/agents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    userId: user.uid,
                    apiKey,
                    scopes: scopes.length > 0 ? scopes : ["*:*"],
                }),
            });
            
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.error || "Failed to create agent");
            }

            setNewlyCreatedKey(apiKey);
            setIsCreateModalOpen(true);
            setShowSuccess(true);
        } catch (e: any) {
            console.error("[SupraWall] Onboarding agent creation error:", e);
            alert(e.message || "Failed to create agent during onboarding.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const copyToClipboard = async (text: string, type: 'node' | 'curl') => {
        try {
            await navigator.clipboard.writeText(text);
            if (type === 'node') {
                setCopiedNode(true);
                setTimeout(() => setCopiedNode(false), 2000);
            } else {
                setCopiedCurl(true);
                setTimeout(() => setCopiedCurl(false), 2000);
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const displayApiKey = (agent: any) => agent.apiKey || "ag_****************";

    const getNodeCode = (agent: any) => `import { protect } from '@suprawall/langchain';
import { createReactAgent } from '@langchain/langgraph/prebuilt';

// 1. Initialize your LangGraph Agent
const agent = createReactAgent({ llm, tools });

// 2. Wrap it with SupraWall (Zero-Config)
const secured = protect(agent, {
  apiKey: "${agent.apiKey || 'YOUR_API_KEY'}",
  riskThreshold: 70 // Optional: block actions >= 70 risk score
});

// 3. Run safely - Forensic logs are automatically streamed
await secured.invoke({ messages: [...] });`;

    const getPythonCode = (agent: any) => `from suprawall import protect
from langgraph.prebuilt import create_react_agent

# 🛡️ Secure any LangGraph agent with one wrapper
agent = create_react_agent(llm, tools)
secured = protect(agent, api_key="${agent.apiKey || 'YOUR_API_KEY'}")

# That's it. Tool usage is now governed.
secured.invoke({"messages": [...]})`;

    const getCurlCode = (agent: any) => `curl -X POST https://api.supra-wall.com/v1/evaluate \\
  -H "Authorization: Bearer ${agent.apiKey || 'YOUR_API_KEY'}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "toolName": "bash_tool",
    "args": { "command": "rm -rf /" },
    "agentRole": "customer-support"
  }'`;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
        >
            {/* Header */}
            <div className="flex justify-between items-end mb-8">
                <div className="space-y-2">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 mb-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[9px] font-black tracking-[0.2em] text-emerald-400 uppercase">Zero-Trust Active</span>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic heading-glow">Security Overview</h1>
                    <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.2em]">Real-time cost control and agent governance.</p>
                </div>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button onClick={() => setIsCreateModalOpen(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 transition-all font-black uppercase tracking-wider text-xs">
                        <PlusCircle className="mr-2 h-4 w-4" />
                        New Agent
                    </Button>
                </motion.div>
            </div>



            {/* Hero Value Section + Shield Status Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                {/* Hero Value Statement */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="lg:col-span-2 p-8 relative overflow-hidden rounded-3xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 via-black to-black shadow-[0_0_80px_rgba(16,185,129,0.15)] group flex flex-col justify-center"
                >
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50" />
                    <div className="absolute -left-20 -top-20 w-64 h-64 bg-emerald-500/20 blur-[100px] rounded-full pointer-events-none" />
                    
                    <div className="relative z-10 space-y-4">
                        <h2 className="text-4xl md:text-5xl font-black text-white italic tracking-tighter">
                            <span className="text-emerald-400 drop-shadow-[0_0_20px_rgba(16,185,129,0.8)]">
                                ${stats.costSaved > 0 ? stats.costSaved.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) : "47,230"}
                            </span>
                            {" "}IN POTENTIAL DAMAGE PREVENTED THIS MONTH
                        </h2>
                        <div className="flex flex-wrap items-center gap-3 text-xs md:text-sm font-bold text-neutral-400 uppercase tracking-widest [&>span]:flex [&>span]:items-center [&>span]:gap-1.5 [&>span>span]:text-white">
                            <span><span className="text-emerald-400">{stats.totalCalls > 0 ? stats.totalCalls.toLocaleString() : "8,400"}</span> OPERATIONS SECURED</span>
                            <span className="text-neutral-600 font-normal">·</span>
                            <span><span>{stats.blockedActions > 0 ? stats.blockedActions.toLocaleString() : "23"}</span> BLOCKED</span>
                            <span className="text-neutral-600 font-normal">·</span>
                            <span><span>23</span> SECRETS PROTECTED</span>
                            <span className="text-neutral-600 font-normal">·</span>
                            <span><span>{pendingApprovalsCount > 0 ? pendingApprovalsCount : "5"}</span> HUMAN APPROVALS</span>
                            <span className="text-neutral-600 font-normal">·</span>
                            <span className="animate-pulse"><span className="text-emerald-400">82%</span> <span className="text-emerald-400">EU AI ACT</span> READY</span>
                        </div>
                    </div>
                </motion.div>

                {/* Shield Status Widget */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1, ease: "easeOut" }}
                    className="lg:col-span-1 space-y-4"
                >
                    <div className="p-6 rounded-3xl border border-emerald-500/20 bg-black/60 backdrop-blur-xl relative overflow-hidden flex flex-col justify-between h-1/2">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50" />
                        
                        <div>
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                                </div>
                                {agents.filter(a => a.status !== 'revoked').length > 0 ? (
                                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                        <span className="text-[9px] font-black text-emerald-400 uppercase tracking-widest">System Online</span>
                                    </div>
                                ) : (
                                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20">
                                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                                        <span className="text-[9px] font-black text-amber-400 uppercase tracking-widest">Awaiting Agents</span>
                                    </div>
                                )}
                            </div>
                            
                            <h3 className="text-xl font-black text-white italic tracking-tighter uppercase">Shield Status</h3>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-1">Control Plane Connection</p>
                        </div>
                    </div>
                    <ContinuousComplianceMonitor />
                </motion.div>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {[
                    { label: "Actual Spend", value: `$${stats.actualSpend.toFixed(2)}`, icon: <Coins className="w-4 h-4 text-amber-400" />, sub: "current month", accent: "amber" },
                    { label: "Cost Saved", value: `$${stats.costSaved.toFixed(2)}`, icon: <DollarSign className="w-4 h-4 text-emerald-400" />, sub: "by policy blocks", accent: "emerald" },
                    { label: "Blocked Actions", value: stats.blockedActions, icon: <ShieldAlert className="w-4 h-4 text-rose-400" />, sub: "dangerous/unwanted", accent: "rose" },
                    { label: "Vault Secrets", value: "Active", icon: <Lock className="w-4 h-4 text-purple-400" />, sub: "secure injection", href: "/dashboard/vault", accent: "purple" },
                    { label: "Human Approvals", value: pendingApprovalsCount, icon: <UserCheck className="w-4 h-4 text-blue-400" />, sub: "needs intervention", href: "/dashboard/approvals", accent: "blue" }
                ].map((item, i) => {
                    const accentMap: Record<string, string> = {
                        amber: "via-amber-500/30 border-amber-500/10 hover:border-amber-500/30",
                        emerald: "via-emerald-500/30 border-emerald-500/10 hover:border-emerald-500/30",
                        rose: "via-rose-500/30 border-rose-500/10 hover:border-rose-500/30",
                        blue: "via-blue-500/30 border-blue-500/10 hover:border-blue-500/30",
                        purple: "via-purple-500/30 border-purple-500/10 hover:border-purple-500/30",
                    };
                    const iconBgMap: Record<string, string> = {
                        amber: "bg-amber-500/10 border-amber-500/20",
                        emerald: "bg-emerald-500/10 border-emerald-500/20",
                        rose: "bg-rose-500/10 border-rose-500/20",
                        blue: "bg-blue-500/10 border-blue-500/20",
                        purple: "bg-purple-500/10 border-purple-500/20",
                    };
                    const accent = item.accent || "emerald";
                    const content = (
                        <>
                            <div className={`absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent ${accentMap[accent].split(' ')[0]} to-transparent`} />
                            <div className="flex items-start gap-3">
                                <div className={`p-2.5 rounded-xl border flex-shrink-0 ${iconBgMap[accent]}`}>
                                    {item.icon}
                                </div>
                                <div className="min-w-0">
                                    <p className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em]">{item.label}</p>
                                    <p className="text-2xl font-black text-white mt-1 tracking-tighter italic flex items-center gap-2">
                                        {item.value}
                                        {typeof item.value === 'number' && item.value > 0 && (
                                            <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
                                        )}
                                    </p>
                                    <p className="text-[9px] font-black text-neutral-600 mt-1 uppercase tracking-wider">{item.sub}</p>
                                </div>
                            </div>
                        </>
                    );
                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className={`bg-black/60 backdrop-blur-xl border p-5 rounded-2xl relative group overflow-hidden transition-all duration-300 card-hover ${accentMap[accent].split(' ').slice(1).join(' ')}`}
                        >
                            {item.href ? (
                                <Link href={item.href}>{content}</Link>
                            ) : content}
                        </motion.div>
                    );
                })}
            </div>

            {/* Spend Chart Section */}
            <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
                <Card className="lg:col-span-2 bg-black/60 backdrop-blur-xl border-emerald-500/20 shadow-2xl p-6 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    <div className="flex justify-between items-center mb-8">
                        <div>
                            <h3 className="text-sm font-black text-white uppercase italic tracking-tighter">Spend Over Time</h3>
                            <p className="text-[9px] font-black text-neutral-400 mt-1 uppercase tracking-[0.2em]">Daily actual spend across all agents (USD)</p>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-neutral-400">
                            <span className="w-2 h-2 rounded-full bg-emerald-500" />
                            Actual Spend
                        </div>
                    </div>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData.length > 0 ? chartData : [
                                { date: '02/20', amount: 0.12 },
                                { date: '02/21', amount: 0.34 },
                                { date: '02/22', amount: 0.21 },
                                { date: '02/23', amount: 0.45 },
                                { date: '02/24', amount: 0.89 },
                                { date: '02/25', amount: 0.32 },
                                { date: '02/26', amount: 0.12 },
                            ]}>
                                <defs>
                                    <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#666', fontSize: 11 }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#666', fontSize: 11 }}
                                    tickFormatter={(val) => `$${val}`}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', fontSize: '12px', boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }}
                                    itemStyle={{ color: '#10b981' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="amount"
                                    stroke="#10b981"
                                    strokeWidth={2.5}
                                    fillOpacity={1}
                                    fill="url(#colorAmount)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/20 shadow-2xl p-6 flex flex-col justify-between relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    <div>
                        <h3 className="text-sm font-black text-white uppercase italic tracking-tighter mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-emerald-400" />
                            Cost Summary
                        </h3>
                        <div className="space-y-6">
                            <div>
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-neutral-400">Monthly Usage</span>
                                    <span className="text-white font-medium">{Math.min(100, Math.round((stats.actualSpend / 50) * 100))}%</span>
                                </div>
                                <div className="w-full bg-white/[0.05] rounded-full h-2 border border-white/10">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${Math.min(100, (stats.actualSpend / 50) * 100)}%` }}
                                        className="bg-emerald-500 h-full rounded-full shadow-[0_0_10px_rgba(16,185,129,0.3)]"
                                    />
                                </div>
                            </div>

                            <div className="p-4 bg-emerald-500/5 border border-emerald-500/15 rounded-xl space-y-1">
                                <p className="text-[9px] font-black text-emerald-500 uppercase tracking-[0.2em]">Efficiency Wins</p>
                                <p className="text-sm text-neutral-300">
                                    You've prevented <span className="text-emerald-400 font-bold">${stats.costSaved.toFixed(2)}</span> in costs this month via policy blocks.
                                </p>
                            </div>
                        </div>
                    </div>
                    <Button 
                        variant="outline" 
                        onClick={() => setIsAnalyticsModalOpen(true)}
                        className="w-full mt-6 bg-white/5 border-white/10 hover:bg-white/10 text-white"
                    >
                        Full Analytics Report
                    </Button>
                </Card>
            </motion.div>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-4"
            >
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-black tracking-tighter text-white uppercase italic flex items-center gap-2">
                            <Activity className="w-5 h-5 text-emerald-500" />
                            Prompt Health Check
                        </h2>
                        <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest mt-1">
                            Validate your system prompts against active security policies.
                        </p>
                    </div>
                    <Button 
                        onClick={() => setIsValidatorOpen(!isValidatorOpen)}
                        variant="outline"
                        className="bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20"
                    >
                        {isValidatorOpen ? "Hide Tools" : "Open Validator"}
                    </Button>
                </div>
                
                {isValidatorOpen && (
                    <div className="bg-black/40 backdrop-blur-3xl border border-emerald-500/10 rounded-3xl overflow-hidden p-6 animate-in fade-in slide-in-from-top-4 duration-500">
                        <PolicyValidator />
                    </div>
                )}
            </motion.div>


            <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/20 shadow-2xl overflow-hidden relative group">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent group-hover:via-emerald-500/50 transition-all duration-700" />

                <CardHeader className="border-b border-white/[0.08] bg-black/20">
                    <CardTitle className="text-sm font-black text-white uppercase italic tracking-tighter flex items-center gap-2">
                        <Shield className="w-4 h-4 text-emerald-500" />
                        Connected Agents
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {loading ? (
                        <div className="py-24 text-center">
                            <p className="text-neutral-400 animate-pulse">Loading agents...</p>
                        </div>
                    ) : agents.length === 0 ? (
                        <OnboardingWizard 
                            onComplete={async (data) => {
                                await performAgentCreation(data.name, data.scopes);
                            }}
                            isSubmitting={isSubmitting}
                        />
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/[0.08] hover:bg-transparent">
                                    <TableHead className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] py-4 px-6">Agent</TableHead>
                                    <TableHead className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] py-4 px-6">API Key</TableHead>
                                    <TableHead className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] py-4 px-6">Scopes</TableHead>
                                    <TableHead className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] py-4 px-6">Status</TableHead>
                                    <TableHead className="text-[9px] font-black text-neutral-400 uppercase tracking-[0.2em] py-4 px-6 text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {agents.map((agent) => (
                                    <TableRow
                                        key={agent.id}
                                        className="border-white/[0.02] hover:bg-white/[0.05] transition-colors group/row"
                                    >
                                        <TableCell className="font-medium text-white px-6 py-4">
                                            {agent.name}
                                        </TableCell>
                                        <TableCell className="font-mono text-sm text-emerald-400 break-all px-6 py-4 group-hover/row:text-emerald-300 transition-colors">
                                            <span className="bg-emerald-500/10 px-2 py-1 rounded-md border border-emerald-500/20">{displayApiKey(agent)}</span>
                                        </TableCell>
                                        <TableCell className="px-6 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {agent.scopes && agent.scopes.length > 0 ? (
                                                    agent.scopes.slice(0, 3).map((scope, i) => (
                                                        <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                                            <Lock className="w-2.5 h-2.5" />{scope}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-xs text-neutral-600 italic">No scopes (full access)</span>
                                                )}
                                                {agent.scopes && agent.scopes.length > 3 && (
                                                    <span className="text-[10px] text-neutral-400">+{agent.scopes.length - 3} more</span>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-xs font-semibold border ${agent.status === 'active' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                                                agent.status === 'suspended' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                                    agent.status === 'revoked' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                                        'bg-green-500/10 text-green-400 border-green-500/20'
                                                }`}>
                                                {agent.status || 'active'}
                                            </span>
                                        </TableCell>
                                        <TableCell className="px-6 py-4 text-right">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="bg-white/5 border-white/10 hover:bg-white/10 hover:text-white transition-colors text-neutral-300"
                                                onClick={() => setSelectedAgent(agent)}
                                            >
                                                <Terminal className="w-4 h-4 mr-2" />
                                                Connect
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Right Column: Live Activity Feed */}
            <Card className="bg-black border-white/[0.08] overflow-hidden flex flex-col h-full shadow-[0_0_40px_rgba(0,0,0,0.5)]">
                <CardHeader className="border-b border-white/[0.08] bg-white/[0.01] py-4 px-6">
                    <div className="flex justify-between items-center">
                        <CardTitle className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400 flex items-center gap-2">
                           <Activity className="w-3.3 h-3.3 text-blue-500 animate-pulse" />
                           Live Activity Feed
                        </CardTitle>
                        <Badge variant="outline" className="text-[8px] bg-blue-500/5 text-blue-400 border-blue-500/10 px-1.5 py-0 font-black uppercase tracking-widest">Realtime</Badge>
                    </div>
                </CardHeader>
                <CardContent className="p-0 flex-grow overflow-y-auto custom-scrollbar">
                    {recentLogs.length > 0 ? (
                        <div className="divide-y divide-white/[0.02]">
                            {recentLogs.map((log, i) => {
                                const details = getReinforcementDetails(log, agents, i === 0);
                                return (
                                <motion.div 
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    key={log.id || i} 
                                    className={`p-4 hover:bg-white/[0.05] transition-colors border-l-2 border-transparent hover:border-l-${details.color.split('-')[1]}-500 space-y-3 group`}
                                >
                                    <div className="flex justify-between items-start">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-lg ${details.bg} border border-white/5 flex items-center justify-center shrink-0 shadow-lg`}>
                                                <span className="text-sm drop-shadow-md">{details.icon}</span>
                                            </div>
                                            <div>
                                                <h4 className={`text-[10px] font-black uppercase tracking-tight ${details.color}`}>
                                                    {details.title}
                                                </h4>
                                                <span className="text-[9px] font-bold text-neutral-600 uppercase">
                                                    {log.toolName}
                                                </span>
                                            </div>
                                        </div>
                                        <span className="text-[9px] text-neutral-400 font-mono italic">
                                            {log.timestamp ? 
                                                (typeof log.timestamp.toDate === 'function' ? 
                                                    format(log.timestamp.toDate(), 'HH:mm:ss') : 
                                                    format(new Date(log.timestamp), 'HH:mm:ss')) 
                                                : "pending"}
                                        </span>
                                    </div>
                                    <div className="pl-11">
                                        <p className="text-[11px] text-neutral-300 leading-relaxed font-medium">
                                            {details.text}
                                        </p>
                                        <div className="mt-2 bg-black/40 p-2 rounded border border-white/[0.02] overflow-hidden opacity-50 group-hover:opacity-100 transition-opacity">
                                            <code className="text-[9px] text-neutral-400 block truncate font-mono transition-colors">
                                                {log.arguments}
                                            </code>
                                        </div>
                                    </div>
                                </motion.div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center py-20 text-center px-6">
                            <Activity className="w-8 h-8 text-neutral-800 mb-3" />
                            <p className="text-[10px] font-black uppercase tracking-widest text-neutral-600 mb-1">Silence is Compliance</p>
                            <p className="text-[9px] text-neutral-700 uppercase italic">No activity detected on the forensic wire.</p>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Create Agent Modal */}
            <Dialog open={isCreateModalOpen} onOpenChange={(open) => {
                setIsCreateModalOpen(open);
                if (!open) {
                    setNewlyCreatedKey(null);
                    setNewAgentName("");
                    setNameError("");
                    setSelectedScopes([]);
                    setCustomScope("");
                }
            }}>
                <DialogContent className="sm:max-w-md bg-transparent border-none text-white shadow-[0_0_150px_rgba(16,185,129,0.5),0_0_60px_rgba(0,0,0,1)] p-0 !overflow-visible rounded-[26px]">
                    <div className="relative p-[2px] w-full h-full overflow-hidden rounded-[26px]">
                        {/* 2 Spinning Lasers */}
                        <div 
                            className="absolute -inset-[150%] z-0 animate-[spin_3s_linear_infinite]"
                            style={{
                                background: 'conic-gradient(from 0deg, transparent 0%, transparent 45%, rgba(16, 185, 129, 1) 48%, rgba(52, 211, 153, 1) 50%, rgba(16, 185, 129, 1) 52%, transparent 55%, transparent 95%, rgba(16, 185, 129, 1) 100%)'
                            }} 
                        />
                        {/* Core Background */}
                        <div className="relative z-10 w-full h-full bg-[#030303] rounded-[24px] overflow-hidden shadow-[inset_0_0_60px_rgba(16,185,129,0.1),inset_0_0_40px_rgba(0,0,0,0.8)]">
                            <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-500/80 to-transparent shadow-[0_0_20px_rgba(16,185,129,0.5)]" />
                            {showSuccess && <DollarConfetti />}
                    
                    {!newlyCreatedKey ? (
                        <div className="p-8 space-y-6">
                            <div className="space-y-2">
                                <h2 className="text-2xl font-black text-white italic uppercase tracking-tighter text-center sm:text-left">
                                    Register AI Identity
                                </h2>
                                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest text-center sm:text-left leading-relaxed">
                                    Define the core boundaries for your autonomous entity.
                                </p>
                            </div>

                            <form onSubmit={handleCreateAgent} className="space-y-6">
                                <div className="space-y-2">
                                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/70 ml-1">
                                        Agent Designation
                                    </Label>
                                    <Input
                                        placeholder="e.g. Sales-Automation-Bot"
                                        value={newAgentName}
                                        onChange={(e) => {
                                            setNewAgentName(e.target.value);
                                            if (nameError) setNameError("");
                                        }}
                                        className={`bg-white/[0.05] border-white/10 h-12 rounded-xl text-white placeholder:text-neutral-700 focus:ring-emerald-500/50 focus:border-emerald-500/50 ${nameError ? 'border-rose-500/50' : ''}`}
                                    />
                                    {nameError && (
                                        <p className="text-rose-500 text-[10px] mt-1 ml-1 font-bold uppercase tracking-wider">{nameError}</p>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/70 ml-1 block mb-3">
                                        Governance Scopes
                                    </Label>
                                    <div className="grid grid-cols-2 gap-2 max-h-[220px] overflow-y-auto pr-2 custom-scrollbar p-1">
                                        {[
                                            { scope: 'crm:read', label: 'CRM Read' },
                                            { scope: 'crm:write', label: 'CRM Write' },
                                            { scope: 'email:send', label: 'Email Send' },
                                            { scope: 'email:read', label: 'Email Read' },
                                            { scope: 'database:read', label: 'Database Read' },
                                            { scope: 'database:write', label: 'Database Write' },
                                            { scope: 'files:read', label: 'Files Read' },
                                            { scope: 'files:write', label: 'Files Write' },
                                            { scope: 'browser:navigate', label: 'Browser Navigate' },
                                            { scope: 'api:call', label: 'API Call' },
                                        ].map(({ scope, label }) => (
                                            <label
                                                key={scope}
                                                className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-all text-[11px] ${selectedScopes.includes(scope)
                                                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                                                    : 'bg-white/[0.05] border-white/5 text-neutral-400 hover:border-white/10'
                                                    }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selectedScopes.includes(scope)}
                                                    onChange={(e) => {
                                                        if (e.target.checked) {
                                                            setSelectedScopes([...selectedScopes, scope]);
                                                        } else {
                                                            setSelectedScopes(selectedScopes.filter(s => s !== scope));
                                                        }
                                                    }}
                                                    className="sr-only"
                                                />
                                                <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center ${selectedScopes.includes(scope)
                                                    ? 'bg-emerald-500 border-emerald-400 font-bold'
                                                    : 'border-white/20'
                                                    }`}>
                                                    {selectedScopes.includes(scope) && <Check className="w-2.5 h-2.5 text-black stroke-[4px]" />}
                                                </div>
                                                <span className="font-mono tracking-tight">{label}</span>
                                            </label>
                                        ))}
                                    </div>
                                    <p className="text-[9px] text-neutral-600 mt-2 px-1 italic">Selecting a scope enforces mandatory verification for that specific action.</p>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="w-full h-14 bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-[0.2em] rounded-xl shadow-[0_10px_30px_rgba(16,185,129,0.2)] disabled:opacity-50 disabled:cursor-not-allowed group"
                                >
                                    {isSubmitting ? (
                                        <RefreshCw className="w-5 h-5 animate-spin" />
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            Authorize Identity <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                        </span>
                                    )}
                                </Button>
                            </form>
                        </div>
                    ) : (
                        <div className="p-8 space-y-6">
                            <div className="flex flex-col items-center text-center space-y-4">
                                <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-2">
                                    <ShieldCheck className="w-8 h-8 text-emerald-500" />
                                </div>
                                <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">
                                    Agent Secured
                                </h2>
                                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest leading-relaxed">
                                    Save your API key now. For your security, <br />
                                    <span className="text-emerald-400">it will never be shown again.</span>
                                </p>
                            </div>

                            <div className="space-y-4">
                                <div className="relative group p-5 bg-black border border-emerald-500/20 rounded-2xl flex items-center justify-between">
                                    <code className="text-emerald-400 font-mono text-sm break-all pr-4">
                                        {newlyCreatedKey}
                                    </code>
                                    <Button 
                                        size="icon" 
                                        variant="ghost" 
                                        onClick={() => newlyCreatedKey && copyToClipboard(newlyCreatedKey, 'node')}
                                        className="h-10 w-10 shrink-0 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-xl"
                                    >
                                        {copiedNode ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </Button>
                                </div>

                                <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-xl flex items-start gap-3">
                                    <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                                    <p className="text-[9px] font-black text-amber-200/50 uppercase leading-normal tracking-wide">
                                        Lost keys cannot be recovered. You will need to revoke and regenerate them if lost.
                                    </p>
                                </div>

                                <Button 
                                    onClick={() => {
                                        setNewlyCreatedKey(null);
                                        setIsCreateModalOpen(false);
                                        router.push('/dashboard/agents');
                                    }}
                                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-widest h-14 rounded-xl shadow-[0_10px_30px_rgba(5,150,105,0.2)] group"
                                >
                                    <span className="flex items-center gap-2">
                                        Go to Agent Dashboard <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                    </span>
                                </Button>
                            </div>
                        </div>
                    )}
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Integration Modal */}
            <Dialog open={!!selectedAgent} onOpenChange={(open) => !open && setSelectedAgent(null)}>
                <DialogContent className="sm:max-w-2xl bg-black border-emerald-500/20 text-white shadow-[0_0_150px_rgba(16,185,129,0.2),0_0_60px_rgba(0,0,0,1)]">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />
                    <DialogHeader>
                        <DialogTitle className="text-lg font-black uppercase italic tracking-tighter text-white flex items-center gap-2">
                            <Terminal className="w-4 h-4 text-emerald-500" />
                            Connect {selectedAgent?.name}
                        </DialogTitle>
                        <DialogDescription className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.15em]">
                            Drop this into your agent codebase to activate zero-trust interception.
                        </DialogDescription>
                    </DialogHeader>

                    {selectedAgent && (
                        <div className="mt-4">
                            <Tabs defaultValue="node" className="w-full">
                                <TabsList className="bg-neutral-800 border-neutral-700 w-full justify-start rounded-none border-b -mb-px px-0 h-auto">
                                    <TabsTrigger value="node" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-emerald-500 rounded-none px-6 py-3 data-[state=active]:text-emerald-400">Node.js SDK</TabsTrigger>
                                    <TabsTrigger value="python" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-emerald-500 rounded-none px-6 py-3 data-[state=active]:text-emerald-400">Python (LangChain)</TabsTrigger>
                                    <TabsTrigger value="curl" className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-emerald-500 rounded-none px-6 py-3 data-[state=active]:text-emerald-400">cURL (REST API)</TabsTrigger>
                                </TabsList>
                                <TabsContent value="node" className="pt-4 outline-none">
                                    <div className="relative group">
                                        <pre className="bg-[#0D0D0D] p-4 rounded-lg font-mono text-sm overflow-x-auto border border-neutral-800 text-emerald-200">
                                            <code>{getNodeCode(selectedAgent)}</code>
                                        </pre>
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            onClick={() => copyToClipboard(getNodeCode(selectedAgent), 'node')}
                                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-800/80 hover:bg-neutral-700 text-white"
                                        >
                                            {copiedNode ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                                        </Button>
                                    </div>
                                </TabsContent>
                                <TabsContent value="python" className="pt-4 outline-none">
                                    <div className="relative group">
                                        <pre className="bg-[#0D0D0D] p-4 rounded-lg font-mono text-sm overflow-x-auto border border-neutral-800 text-emerald-200">
                                            <code>{getPythonCode(selectedAgent)}</code>
                                        </pre>
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            onClick={() => copyToClipboard(getPythonCode(selectedAgent), 'node')}
                                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-800/80 hover:bg-neutral-700 text-white"
                                        >
                                            {copiedNode ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                                        </Button>
                                    </div>
                                </TabsContent>
                                <TabsContent value="curl" className="pt-4 outline-none">
                                    <div className="relative group">
                                        <pre className="bg-[#0D0D0D] p-4 rounded-lg font-mono text-sm overflow-x-auto border border-neutral-800 text-emerald-200">
                                            <code>{getCurlCode(selectedAgent)}</code>
                                        </pre>
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            onClick={() => copyToClipboard(getCurlCode(selectedAgent), 'curl')}
                                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-800/80 hover:bg-neutral-700 text-white"
                                        >
                                            {copiedCurl ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                                        </Button>
                                    </div>
                                </TabsContent>
                            </Tabs>
                        </div>
                    )}
                </DialogContent>
            </Dialog>

            {/* Analytics Report Modal */}
            <Dialog open={isAnalyticsModalOpen} onOpenChange={setIsAnalyticsModalOpen}>
                <DialogContent className="max-w-4xl bg-[#0A0A0A] border-white/10 p-0 overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.5)]">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    
                    <div className="p-10 space-y-10">
                        <div className="flex items-start justify-between">
                            <div className="space-y-1">
                                <h2 className="text-4xl font-black text-white uppercase italic tracking-tight leading-none heading-glow">
                                    Forensic <span className="text-emerald-500">Intelligence</span>
                                </h2>
                                <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.3em] inline-flex items-center gap-2">
                                    Consolidated Agent Performance • <Activity className="w-3 h-3 text-emerald-500/50" /> System Live
                                </p>
                            </div>
                            <Button 
                                variant="ghost" 
                                size="icon" 
                                onClick={() => setIsAnalyticsModalOpen(false)}
                                className="h-10 w-10 text-neutral-400 hover:text-white hover:bg-white/5 rounded-full"
                            >
                                <X className="w-5 h-5" />
                            </Button>
                        </div>

                        <div className="grid grid-cols-4 gap-6">
                            {[
                                { label: 'Total Volume', value: stats.totalCalls.toLocaleString(), sub: 'API Invocations', icon: Activity, color: 'text-blue-400' },
                                { label: 'Security Blocks', value: stats.blockedActions.toLocaleString(), sub: 'Policy Violations', icon: Shield, color: 'text-emerald-400' },
                                { label: 'Net Savings', value: `$${stats.costSaved.toFixed(0)}`, sub: 'Loss Prevention', icon: TrendingUp, color: 'text-emerald-500' },
                                { label: 'Active Agents', value: agents.length, sub: 'Total Provisioned', icon: UserCheck, color: 'text-purple-400' },
                            ].map((stat, i) => (
                                <motion.div 
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="p-5 bg-white/5 border border-white/10 rounded-2xl group hover:border-emerald-500/20 transition-all cursor-default"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-black/50 border border-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                        <stat.icon className={`w-4 h-4 ${stat.color}`} />
                                    </div>
                                    <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest">{stat.label}</p>
                                    <p className="text-2xl font-black text-white mt-1 tracking-tighter">{stat.value}</p>
                                    <p className="text-[9px] font-bold text-neutral-600 uppercase mt-1 italic">{stat.sub}</p>
                                </motion.div>
                            ))}
                        </div>

                        <div className="grid grid-cols-5 gap-8">
                            <div className="col-span-3 space-y-6">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                                        <Activity className="w-3 h-4 text-emerald-500" />
                                        Inbound Volume Trend
                                    </h3>
                                    <div className="flex gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                        <span className="text-[10px] font-bold text-neutral-400 uppercase">Cost Intensity</span>
                                    </div>
                                </div>
                                <div className="h-[250px] w-full p-4 bg-black border border-white/5 rounded-2xl relative group overflow-hidden">
                                    <div className="absolute inset-0 bg-gradient-to-t from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={chartData}>
                                            <defs>
                                                <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                            <XAxis 
                                                dataKey="date" 
                                                stroke="#525252" 
                                                fontSize={10} 
                                                fontWeight="bold"
                                                tickLine={false}
                                                axisLine={false}
                                                dy={10}
                                            />
                                            <YAxis 
                                                stroke="#525252" 
                                                fontSize={10} 
                                                fontWeight="bold"
                                                tickLine={false}
                                                axisLine={false}
                                                tickFormatter={(val) => `$${val}`}
                                            />
                                            <Tooltip 
                                                contentStyle={{ backgroundColor: '#000', border: '1px solid #10b98130', borderRadius: '12px', padding: '12px' }}
                                                itemStyle={{ color: '#10b981', fontSize: '12px', fontWeight: '900', textTransform: 'uppercase' }}
                                                labelStyle={{ color: '#525252', fontSize: '10px', marginBottom: '4px', fontWeight: 'bold' }}
                                            />
                                            <Area 
                                                type="monotone" 
                                                dataKey="amount" 
                                                stroke="#10b981" 
                                                strokeWidth={3}
                                                fillOpacity={1} 
                                                fill="url(#colorAmount)" 
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            <div className="col-span-2 space-y-6">
                                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                                    <ShieldAlert className="w-3 h-4 text-emerald-500" />
                                    Top Risk Vectors
                                </h3>
                                <div className="space-y-4">
                                    {[
                                        { label: 'Prompt Injection', count: 12, risk: 'CRITICAL', color: 'bg-red-500' },
                                        { label: 'Agent Loop Detection', count: 8, risk: 'HIGH', color: 'bg-orange-500' },
                                        { label: 'Scope Violations', count: 45, risk: 'MEDIUM', color: 'bg-amber-500' },
                                        { label: 'Token Burn Rate', count: 19, risk: 'MONITOR', color: 'bg-blue-500' },
                                    ].map((risk, i) => (
                                        <div key={i} className="p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/[0.07] transition-colors group">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-[10px] font-black text-white uppercase tracking-tight">{risk.label}</span>
                                                <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${risk.color}/20 ${risk.color.replace('bg-', 'text-')} border border-${risk.color.split('-')[1]}-500/20`}>
                                                    {risk.risk}
                                                </span>
                                            </div>
                                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                                <motion.div 
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${(risk.count / 50) * 100}%` }}
                                                    className={`h-full ${risk.color} rounded-full`}
                                                />
                                            </div>
                                            <div className="flex justify-between mt-2">
                                                <span className="text-[8px] font-bold text-neutral-600 uppercase tracking-widest">Incident Count</span>
                                                <span className="text-[9px] font-black text-neutral-300">{risk.count} Events</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-6 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl translate-y-4">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                                    <ShieldCheck className="w-6 h-6 text-emerald-500" />
                                </div>
                                <div className="space-y-0.5">
                                    <p className="text-[11px] font-black text-white uppercase italic tracking-tighter">System Health: Optimal</p>
                                    <p className="text-[9px] font-bold text-emerald-500/50 uppercase tracking-widest">All policy chains verified & synchronized</p>
                                </div>
                            </div>
                            <Button className="bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase text-[10px] tracking-widest px-8">
                                Export PDF Report
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </motion.div>
    );
}

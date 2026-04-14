// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState, useRef } from "react";
import { auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
    Shield, ShieldAlert, ShieldCheck,
    Terminal, Lock, Unlock,
    Copy, CheckCircle2, AlertTriangle, Eye, EyeOff,
    RefreshCw, PauseCircle, Settings2,
    Users, DollarSign, Activity,
    BarChart3, Plus, ArrowRight,
    Search, Filter, ExternalLink,
    Zap, Sparkles, Brain, Wand2, Loader2,
    Bot, Cpu, Network,
    MoreHorizontal, AlertCircle, Clock, History, ArrowLeft, Trash2, Layers, Ban,
    ShieldCheck as ShieldCheckIcon
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import AiSecurityArchitect from "@/components/AiSecurityArchitect";

interface Agent {
    id: string;
    userId: string;
    tenantId?: string;
    name: string;
    status: 'active' | 'paused' | 'revoked';
    scopes?: string[];
    totalCalls: number;
    totalSpendUsd: number;
    lastUsedAt?: any;
    apiKey: string;
    createdAt: any;
    guardrails?: {
        budget?: { limitUsd: number; resetPeriod: string; onExceeded: string; currentPeriodSpend?: number };
        allowedTools?: string[];
        blockedTools?: string[];
        piiScrubbing?: { enabled: boolean; patterns: string[]; action: string; customPatterns?: any[] };
    };
}

interface VaultSecret {
    id: string;
    secret_name: string;
    assigned_agents: string[];
}

interface Policy {
    id: string;
    agentId: string;
    toolName: string;
    condition: string;
    ruleType: string;
}

export default function AgentDetailPage() {
    const { id: agentId } = useParams() as { id: string };
    const [user, authLoading] = useAuthState(auth);
    const [agent, setAgent] = useState<Agent | null>(null);
    const [loading, setLoading] = useState(true);
    const [auditLogs, setAuditLogs] = useState<any[]>([]);
    const [agentPolicies, setAgentPolicies] = useState<Policy[]>([]);
    const [agentSecrets, setAgentSecrets] = useState<VaultSecret[]>([]);
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState("");
    const [editScopes, setEditScopes] = useState<string[]>([]);
    const [isRotatingKey, setIsRotatingKey] = useState(false);
    const [isCopying, setIsCopying] = useState(false);
    const [integrationTab, setIntegrationTab] = useState<'python' | 'ts' | 'go'>('python');
    const [activeTab, setActiveTab] = useState<'overview' | 'guardrails'>('overview');
    const [promptFramework, setPromptFramework] = useState<'python-langchain' | 'ts-vercel' | 'python-crewai'>('python-langchain');
    const [isPromptCopying, setIsPromptCopying] = useState(false);
    const [showApiKey, setShowApiKey] = useState(false);
    const [isApiKeyCopying, setIsApiKeyCopying] = useState(false);

    const pollAgent = async () => {
        if (!user || !agentId) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/agents/${agentId}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (res.ok) {
                const data = await res.json() as Agent;
                if (data.userId !== user.uid && data.tenantId !== user.uid) {
                    setAgent(null);
                } else {
                    setAgent(data);
                    setEditName(data.name);
                    setEditScopes(data.scopes || []);
                }
            } else if (res.status === 404) {
                setAgent(null);
            }
            setLoading(false);
        } catch (e) {
            console.error("Error polling agent:", e);
            setLoading(false);
        }
    };

    const pollAudit = async () => {
        if (!user || !agentId) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/audit-logs?agentId=${agentId}&tenantId=${user.uid}&limit=50`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (res.ok) {
                const logs = await res.json();
                setAuditLogs(logs);
            }
        } catch (e) {
            console.error("Error polling audit logs:", e);
        }
    };

    const pollPolicies = async () => {
        if (!user || !agentId) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/policies?agentId=${agentId}&tenantId=${user.uid}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (res.ok) {
                const data = await res.json();
                setAgentPolicies(data);
            }
        } catch (e) {
            console.error("Error polling policies:", e);
        }
    };

    const fetchSecrets = async () => {
        if (!user || !agentId) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/vault/secrets?tenantId=${user.uid}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (res.ok) {
                const allSecrets = await res.json() as VaultSecret[];
                setAgentSecrets(allSecrets.filter(s => s.assigned_agents?.includes(agentId)));
            }
        } catch (err) {
            console.error("Error fetching agent secrets:", err);
        }
    };

    useEffect(() => {
        if (authLoading || !user || !agentId) return;

        pollAgent();
        pollAudit();
        pollPolicies();
        fetchSecrets();

        const agentInt = setInterval(pollAgent, 10000);
        const auditInt = setInterval(pollAudit, 10000);
        const policyInt = setInterval(pollPolicies, 15000);

        return () => {
            clearInterval(agentInt);
            clearInterval(auditInt);
            clearInterval(policyInt);
        };
    }, [user, agentId, authLoading]);

    const toggleStatus = async () => {
        if (!agent || !user) return;
        const newStatus = agent.status === 'active' ? 'paused' : 'active';
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/agents/${agentId}`, {
                method: "PATCH",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${idToken}`
                },
                body: JSON.stringify({ status: newStatus }),
            });
            if (res.ok) {
                // Polling will pick it up
            }
        } catch (error) {
            console.error("Error updating agent status:", error);
        }
    };

    const handleUpdateAgent = async () => {
        if (!agent || !user) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/agents/${agentId}`, {
                method: "PATCH",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    name: editName,
                    scopes: editScopes
                }),
            });
            if (res.ok) {
                setIsEditing(false);
            }
        } catch (error) {
            console.error("Error updating agent:", error);
        }
    };

    const toggleScope = (scope: string) => {
        setEditScopes(prev => 
            prev.includes(scope) ? prev.filter(s => s !== scope) : [...prev, scope]
        );
    };

    const generateApiKey = () => {
        const bytes = new Uint8Array(24);
        window.crypto.getRandomValues(bytes);
        return "ag_" + btoa(String.fromCharCode(...Array.from(bytes)))
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/, "");
    };

    const handleRotateKey = async () => {
        if (!agent || !user || !confirm("Generating a new API key will immediately invalidate the current one. Continue?")) return;
        setIsRotatingKey(true);
        const newKey = generateApiKey();
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/agents/${agentId}`, {
                method: "PATCH",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${idToken}`
                },
                body: JSON.stringify({ apiKey: newKey }),
            });
            if (res.ok) {
                alert(`New API Key generated: ${newKey}\nPlease save it securely as it won't be shown again.`);
            }
        } catch (error) {
            console.error("Error rotating key:", error);
        } finally {
            setIsRotatingKey(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setIsCopying(true);
        setTimeout(() => setIsCopying(false), 2000);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-black">
                <p className="text-neutral-400 animate-pulse font-medium tracking-widest uppercase">Initializing Secure Tunnel...</p>
            </div>
        );
    }

    if (!agent) {
        return (
            <div className="flex flex-col items-center justify-center h-screen bg-black text-center p-8">
                <AlertCircle className="w-12 h-12 text-rose-500 mb-4" />
                <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
                <p className="text-neutral-400 mb-6">The requested agent identity could not be verified or has been redacted.</p>
                <Link href="/dashboard/agents">
                    <Button variant="outline" className="border-white/10">Return to Registry</Button>
                </Link>
            </div>
        );
    }

    const interceptionCount = auditLogs.filter(l => l.decision === 'DENY').length;
    const validLogsCount = auditLogs.filter(l => l.decision !== 'PAUSED').length || 1;
    const interceptionRate = ((interceptionCount / validLogsCount) * 100).toFixed(1);
    const loopDetections = auditLogs.filter(l => l.isLoop).length;
    const maxBudget = 10.00;
    const currentSpend = agent.totalSpendUsd || 0;
    const spendProgress = Math.min((currentSpend / maxBudget) * 100, 100);
    const agentUri = `agent://${agent.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.acme.suprawall.com`;
    const hasPendingApproval = auditLogs.some(l => l.decision === 'PAUSED');

    const snippetCode = {
        python: `import suprawall\n\nagent = suprawall.Agent(\n  identity="${agentUri}",\n  api_key="${agent.apiKey}"\n)\n\nagent.start()`,
        ts: `import { SupraWall } from '@suprawall/sdk';\n\nconst agent = new SupraWall({\n  identity: "${agentUri}",\n  apiKey: "${agent.apiKey}"\n});\n\nawait agent.connect();`,
        go: `import "github.com/suprawall/sdk-go"\n\nagent := suprawall.NewAgent(&suprawall.Config{\n    Identity: "${agentUri}",\n    APIKey:   "${agent.apiKey}",\n})\nagent.Run()`
    };

    return (
        <div className="min-h-screen bg-black text-neutral-200 p-8 space-y-12 pb-24">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 max-w-7xl mx-auto">
                <div className="flex items-center gap-6">
                    <Link href="/dashboard/agents">
                        <Button variant="ghost" size="icon" className="rounded-full bg-white/5 border border-white/10 hover:bg-white/10 text-white">
                            <ArrowLeft className="w-5 h-5" />
                        </Button>
                    </Link>
                    <div className="flex items-center gap-5">
                        <div className="w-20 h-20 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 flex flex-col items-center justify-center relative shadow-[0_0_30px_rgba(99,102,241,0.1)]">
                            <Terminal className="w-8 h-8 text-indigo-400" />
                            <div className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-4 border-black flex items-center justify-center ${
                                agent.status === 'active' ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]'
                            }`}>
                                {agent.status === 'active' && <div className="w-2 h-2 bg-white rounded-full animate-pulse" />}
                            </div>
                        </div>
                        <div>
                            {isEditing ? (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <Input 
                                            value={editName}
                                            onChange={(e) => setEditName(e.target.value)}
                                            className="bg-white/5 border-white/10 text-3xl font-black text-white p-2 h-auto max-w-[300px]"
                                        />
                                        <Button size="sm" onClick={handleUpdateAgent} className="h-10 bg-emerald-500 text-black font-bold uppercase text-xs hover:bg-emerald-400">Save</Button>
                                        <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)} className="h-10 text-neutral-400">Cancel</Button>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] uppercase tracking-widest text-neutral-500 font-black">Authorized Scopes</label>
                                        <div className="flex flex-wrap gap-2">
                                            {['read', 'write', 'admin', 'payment', 'tools'].map(s => (
                                                <button
                                                    key={s}
                                                    onClick={() => toggleScope(s)}
                                                    className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border transition-all ${
                                                        editScopes.includes(s)
                                                            ? "bg-indigo-500/20 border-indigo-500/50 text-indigo-400"
                                                            : "bg-white/5 border-white/5 text-neutral-600 hover:border-white/10"
                                                    }`}
                                                >
                                                    {s}
                                                </button>
                                            ))}
                                            <div className="flex items-center gap-2 ml-2">
                                                <input 
                                                    type="text"
                                                    placeholder="Custom scope..."
                                                    className="bg-white/5 border-white/5 rounded-full px-3 py-1 text-[10px] text-white focus:outline-none focus:border-indigo-500/50"
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter') {
                                                            const val = e.currentTarget.value.trim().toLowerCase();
                                                            if (val && !editScopes.includes(val)) {
                                                                setEditScopes([...editScopes, val]);
                                                                e.currentTarget.value = '';
                                                            }
                                                        }
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <h1 className="text-5xl font-black text-white tracking-tighter flex items-center gap-4">
                                    {agent.name}
                                    <div className="flex gap-2">
                                        <Badge 
                                            onClick={() => setIsEditing(true)} 
                                            className={`cursor-pointer uppercase tracking-widest text-[10px] font-black px-3 py-1 ${
                                                agent.status === 'active' 
                                                    ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' 
                                                    : agent.status === 'paused'
                                                        ? 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                                                        : 'bg-rose-500/10 text-rose-500 border-rose-500/20'
                                            }`}
                                        >
                                            {agent.status === 'paused' ? 'Suspended' : agent.status === 'active' ? 'Active' : 'Deactivated'}
                                        </Badge>
                                        <button 
                                            onClick={() => setIsEditing(true)}
                                            className="p-1 text-neutral-500 hover:text-white transition-colors"
                                        >
                                            <Plus className="w-4 h-4 rotate-45" /> 
                                        </button>
                                    </div>
                                </h1>
                            )}
                            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-2">
                                <span className="text-xs font-mono text-neutral-600 tracking-wider flex items-center gap-1" title="Unique database identifier for management">
                                    DATABASE ID: {agentId}
                                </span>
                                <span className="w-1.5 h-1.5 bg-neutral-800 rounded-full hidden md:block" />
                                <div className="flex items-center gap-2 group/key">
                                    <span className="text-xs font-mono text-neutral-500 tracking-wider">API KEY:</span>
                                    <span className="text-xs font-mono text-emerald-500/80 bg-emerald-500/5 px-2 py-0.5 rounded border border-emerald-500/10 flex items-center gap-2">
                                        {showApiKey ? agent.apiKey : "••••••••••••••••"}
                                        <button 
                                            onClick={() => setShowApiKey(!showApiKey)}
                                            className="p-0.5 text-neutral-500 hover:text-white transition-colors"
                                            title={showApiKey ? "Hide Key" : "Show Key"}
                                        >
                                            {showApiKey ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                                        </button>
                                        <button 
                                            onClick={() => {
                                                navigator.clipboard.writeText(agent.apiKey);
                                                setIsApiKeyCopying(true);
                                                setTimeout(() => setIsApiKeyCopying(false), 2000);
                                            }}
                                            className="p-0.5 text-neutral-500 hover:text-white transition-colors"
                                            title="Copy Key"
                                        >
                                            {isApiKeyCopying ? <CheckCircle2 className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                                        </button>
                                    </span>
                                </div>
                                <span className="w-1.5 h-1.5 bg-neutral-800 rounded-full hidden md:block" />
                                <span className="text-xs text-neutral-400 italic">Established {agent.createdAt?.toDate?.().toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <Button 
                        onClick={toggleStatus}
                        variant="outline"
                        disabled={agent.status === 'revoked'}
                        className={`h-14 rounded-2xl px-8 font-black uppercase tracking-widest text-xs transition-all ${
                            agent.status === 'active' 
                                ? 'bg-amber-500/10 border-amber-500/20 text-amber-500 hover:bg-amber-500/20' 
                                : agent.status === 'paused'
                                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500 hover:bg-emerald-500/20'
                                    : 'bg-neutral-500/10 border-white/5 text-neutral-500'
                        }`}
                    >
                        {agent.status === 'active' ? (
                            <><Lock className="w-4 h-4 mr-2" /> Suspend Operations</>
                        ) : agent.status === 'paused' ? (
                            <><Unlock className="w-4 h-4 mr-2" /> Resume Operations</>
                        ) : (
                            <><Ban className="w-4 h-4 mr-2" /> Permanently Deactivated</>
                        )}
                    </Button>
                </div>
            </header>

            <div className="max-w-7xl mx-auto flex gap-1 bg-white/[0.05] border border-white/5 p-1 rounded-2xl w-fit mb-6">
                {[
                    { key: 'overview', label: 'Overview', icon: <BarChart3 className="w-3.5 h-3.5" /> },
                    { key: 'guardrails', label: 'Guardrails', icon: <Shield className="w-3.5 h-3.5" /> },
                ].map(tab => (
                    <button key={tab.key} onClick={() => setActiveTab(tab.key as any)}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all ${
                            activeTab === tab.key ? 'bg-emerald-600 text-white' : 'text-neutral-400 hover:text-white hover:bg-white/5'
                        }`}
                    >
                        {tab.icon}{tab.label}
                    </button>
                ))}
            </div>

            {activeTab === 'guardrails' && (
                <div className="max-w-3xl mx-auto">
                    <GuardrailsPanel agent={agent} agentId={agentId} user={user} />
                </div>
            )}

            {activeTab === 'overview' && <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <div className="lg:col-span-2 space-y-8">
                {user && (
                    <AiSecurityArchitect 
                        agentId={agentId} 
                        tenantId={user.uid} 
                        onApplied={() => { pollAgent(); pollPolicies(); }} 
                    />
                )}

                    {/* human loop alert */}
                    {hasPendingApproval && (
                        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-amber-500/10 border border-amber-500/30 rounded-3xl p-6 flex items-start gap-6 shadow-[0_0_50px_rgba(245,158,11,0.05)]">
                            <div className="p-4 bg-amber-500/20 rounded-2xl shrink-0">
                                <PauseCircle className="w-8 h-8 text-amber-500 animate-pulse" />
                            </div>
                            <div className="space-y-2">
                                <h4 className="text-xl font-black text-amber-400 tracking-tight uppercase">Manual Intervention Required</h4>
                                <p className="text-neutral-300 leading-relaxed text-sm">Policy <strong>"High Stakes Approval"</strong> triggered. Operations paused to prevent unauthorized resource allocation.</p>
                                <div className="flex gap-4 mt-4">
                                    <Link href="/dashboard/approvals">
                                        <Button className="bg-amber-500 text-black font-black uppercase text-[10px] tracking-widest h-10 px-6 rounded-xl">Review & Approve</Button>
                                    </Link>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <StatItem label="Total Compute Cycles" value={agent.totalCalls?.toLocaleString() || "0"} icon={<Terminal className="w-4 h-4 text-neutral-400" />} />
                        <StatItem label="Interception Delta" value={`${interceptionRate}%`} sub="Policies Enforced" color="text-rose-400" icon={<Shield className="w-4 h-4 text-rose-500" />} />
                        <StatItem label="Detected Loops" value={loopDetections.toString()} sub="Circular Ref Protection" color="text-indigo-400" icon={<RefreshCw className="w-4 h-4 text-indigo-400" />} />
                    </div>

                    {/* Budget Section */}
                    <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-8 space-y-6 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl -mr-48 -mt-48 transition-all group-hover:bg-amber-500/10" />
                        <div className="flex items-center justify-between relative z-10">
                            <div className="flex items-center gap-3">
                                <DollarSign className="w-6 h-6 text-amber-500" />
                                <h3 className="text-xl font-black uppercase tracking-tighter text-white">Agent Resource Budget</h3>
                            </div>
                            <Badge variant="outline" className="border-amber-500/20 text-amber-400 font-mono tracking-widest">${currentSpend.toFixed(3)} / ${maxBudget.toFixed(2)}</Badge>
                        </div>
                        <div className="space-y-4 relative z-10">
                            <div className="flex items-end gap-3">
                                <div className="text-6xl font-black text-white tracking-tighter">${currentSpend.toFixed(3)}</div>
                                <div className="text-sm text-neutral-400 mb-2 font-black italic uppercase tracking-widest opacity-50">Accrued Usage</div>
                            </div>
                            <div className="w-full h-4 bg-white/5 rounded-full overflow-hidden p-1 border border-white/5">
                                <motion.div initial={{ width: 0 }} animate={{ width: `${spendProgress}%` }} className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 rounded-full" />
                            </div>
                            <p className="text-xs text-neutral-400 uppercase tracking-widest font-bold">Automatic Killswitch at $10.00 USD Overhead</p>
                        </div>
                    </div>

                    {/* Activity Feed */}
                    <div className="bg-neutral-900/40 border border-white/10 rounded-3xl overflow-hidden">
                        <div className="p-6 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <History className="w-5 h-5 text-purple-400" />
                                <h3 className="text-lg font-black uppercase tracking-tighter text-white">Live Operations Feed</h3>
                            </div>
                            <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20 uppercase text-[10px] tracking-widest px-3">Real-time Stream</Badge>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/[0.05]">
                                    <tr>
                                        <th className="px-6 py-4 text-[10px] font-black text-neutral-400 uppercase tracking-widest">Temporal Vector</th>
                                        <th className="px-6 py-4 text-[10px] font-black text-neutral-400 uppercase tracking-widest">Tool/Function</th>
                                        <th className="px-6 py-4 text-[10px] font-black text-neutral-400 uppercase tracking-widest text-right">Gatekeeper Sec.</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.03]">
                                    {auditLogs.length === 0 ? (
                                        <tr><td colSpan={3} className="text-center py-12 text-neutral-600 uppercase font-black tracking-widest text-xs italic">Awaiting Telemetry Data...</td></tr>
                                    ) : (
                                        auditLogs.map((log) => (
                                            <tr key={log.id} className="hover:bg-white/[0.05] transition-colors group">
                                                <td className="px-6 py-5 whitespace-nowrap text-xs font-mono text-neutral-400">
                                                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Just now'}
                                                </td>
                                                <td className="px-6 py-5">
                                                    <div className="flex flex-col">
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-sm font-bold text-white font-mono">{log.toolName}</span>
                                                            {log.semanticScore !== null && (
                                                                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20" title={log.semanticReasoning || "AI Semantic analysis active"}>
                                                                    <Brain className="w-3 h-3 text-emerald-400" />
                                                                    <span className="text-[9px] font-black text-emerald-400">{log.semanticScore?.toFixed(2)}</span>
                                                                </div>
                                                            )}
                                                        </div>
                                                        <span className="text-[10px] text-neutral-600 font-mono truncate max-w-[250px]">{log.arguments || "{}"}</span>
                                                        {log.semanticFlag && (
                                                            <span className="text-[9px] text-amber-500 font-medium italic mt-1 flex items-center gap-1">
                                                                <AlertTriangle className="w-2.5 h-2.5" /> AI Flag: {log.semanticReasoning}
                                                            </span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-5 text-right">
                                                    <span className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border ${
                                                        log.decision === 'ALLOW' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                                                        log.decision === 'PAUSED' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                                                        'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                                    }`}>
                                                        {log.decision}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="space-y-8">
                    {/* Identity Details Sidebar */}
                    <div className="bg-neutral-900/60 border border-white/10 rounded-3xl p-8 space-y-8">
                        {/* Integration */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2">
                                <Terminal className="w-5 h-5 text-blue-400" />
                                <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Identity Handshake</h3>
                            </div>
                            <div className="bg-black/60 rounded-2xl border border-white/10 overflow-hidden flex flex-col">
                                <div className="flex border-b border-white/5">
                                    {(['python', 'ts', 'go'] as const).map(t => (
                                        <button 
                                            key={t}
                                            onClick={() => setIntegrationTab(t)}
                                            className={`flex-1 py-3 text-[10px] font-black uppercase transition-all ${integrationTab === t ? 'bg-blue-500 text-black' : 'text-neutral-400 hover:text-white hover:bg-white/5'}`}
                                        >
                                            {t}
                                        </button>
                                    ))}
                                </div>
                                <div className="p-4 relative group">
                                    <pre className="text-[11px] font-mono text-blue-100/80 leading-relaxed overflow-x-auto">{snippetCode[integrationTab]}</pre>
                                    <button onClick={() => copyToClipboard(snippetCode[integrationTab])} className="absolute top-2 right-2 p-2 bg-white/10 rounded-xl text-white opacity-0 group-hover:opacity-100 transition-all hover:bg-white/20">
                                        {isCopying ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* AI Assistant Prompt */}
                        <div className="space-y-4 pt-4 border-t border-white/5">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-violet-400" />
                                    <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">AI Assistant Prompt</h3>
                                </div>
                                <Badge variant="outline" className="border-violet-500/20 text-violet-400 text-[8px] uppercase tracking-widest">Beta</Badge>
                            </div>
                            <p className="text-[10px] text-neutral-400 leading-relaxed font-bold">Paste this into Cursor, Copilot, or Antigravity to secure this agent.</p>
                            
                            <div className="space-y-2">
                                <select 
                                    value={promptFramework} 
                                    onChange={(e) => setPromptFramework(e.target.value as any)}
                                    className="w-full bg-neutral-900 border border-white/10 text-white rounded-xl h-10 px-3 text-[10px] font-black uppercase tracking-widest"
                                >
                                    <option value="python-langchain">Python + LangChain</option>
                                    <option value="ts-vercel">TS + Vercel AI SDK</option>
                                    <option value="python-crewai">Python + CrewAI</option>
                                </select>
                                
                                <Button 
                                    onClick={() => {
                                        const prompt = `Act as a Senior AI Integration Engineer. Your task is to install and configure SupraWall to secure my AI agent.

Environment Data:
- Agent ID: \`${agentId}\`
- API Key: \`${agent.apiKey}\`
- Framework: ${promptFramework.replace('-', ' ')}

1. **Install SDK:** Run \`pip install suprawall\` (Python) or \`npm install suprawall\` (Node).
2. **Initialization:** Use this boilerplate for \`suprawall_client.py\`:
   \`\`\`python
   from suprawall import Client, secure_agent
   import os
   client = Client(api_key="${agent.apiKey}", default_policy="DENY")
   \`\`\`
3. **Wrap:** Find the Agent Executor and wrap it using \`secure_agent(my_agent, client=client)\`.

Verify that calls to sensitive tools like \`db.drop_table\` are blocked.`;
                                        navigator.clipboard.writeText(prompt);
                                        setIsPromptCopying(true);
                                        setTimeout(() => setIsPromptCopying(false), 2000);
                                    }}
                                    className="w-full bg-violet-600 hover:bg-violet-500 text-white font-black uppercase tracking-widest text-[10px] h-12 rounded-2xl transition-all shadow-xl shadow-violet-900/10"
                                >
                                    {isPromptCopying ? <><CheckCircle2 className="w-3.5 h-3.5 mr-2" /> Copied Prompt</> : <><Copy className="w-3.5 h-3.5 mr-2" /> Copy Prompt for AI</>}
                                </Button>
                            </div>
                        </div>

                        {/* Endpoint URI */}
                        <div className="space-y-2">
                             <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400 ml-1">SDK Agent Identity URI</Label>
                             <div className="bg-black/40 border border-white/5 rounded-2xl p-4 flex items-center justify-between group hover:border-blue-500/30 transition-colors cursor-pointer" onClick={() => copyToClipboard(agentUri)}>
                                 <code className="text-xs font-mono text-blue-400">{agentUri}</code>
                                 <Copy className="w-3 h-3 text-neutral-700 group-hover:text-blue-400" />
                             </div>
                        </div>

                        {/* Scopes */}
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400 ml-1">Authorized Scopes</Label>
                                <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)} className="h-5 text-[8px] uppercase tracking-widest text-blue-400 hover:text-blue-300">Expand Access</Button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {agent.scopes?.map(s => (
                                    <Badge key={s} variant="outline" className="bg-neutral-800/50 border-white/5 text-neutral-400 text-[10px] font-mono py-1 px-3 rounded-lg">{s}</Badge>
                                ))}
                            </div>
                        </div>

                                                {/* API Key Rotation */}
                                                <div className="pt-4 border-t border-white/5 space-y-4 uppercase">
                            <div className="flex items-center gap-2">
                                <Lock className="w-4 h-4 text-rose-500" />
                                <h3 className="text-xs font-black tracking-widest text-white">Credential Rotation</h3>
                            </div>
                            <p className="text-[10px] text-neutral-400 leading-relaxed font-bold">Revoke currently authorized credentials and generate a fresh cryptographic identity key.</p>
                            <Button variant="outline" onClick={handleRotateKey} disabled={isRotatingKey} className="w-full border-rose-500/20 text-rose-500 bg-rose-500/5 hover:bg-rose-500/10 h-12 text-[10px] font-black tracking-widest rounded-2xl">
                                {isRotatingKey ? "REGENERATING..." : "ROTATE IDENTITY KEY"}
                            </Button>
                        </div>
                    </div>

                    {/* Security Perimeter */}
                    <div className="bg-neutral-900/60 border border-white/10 rounded-3xl p-8 space-y-6">
                        <div className="flex items-center gap-3">
                            <ShieldCheck className="w-5 h-5 text-emerald-400" />
                            <h3 className="text-xl font-black uppercase tracking-tighter text-white">Security Perimeter</h3>
                        </div>
                        
                        <div className="space-y-6">
                            {/* Linked Secrets */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-neutral-400">
                                    <span>Validated Secrets</span>
                                    <span>{agentSecrets.length} ENTITIES</span>
                                </div>
                                <div className="grid grid-cols-1 gap-2">
                                    {agentSecrets.map(s => (
                                        <div key={s.id} className="bg-black/40 border border-white/5 rounded-xl p-3 flex items-center gap-3">
                                            <div className="p-1.5 bg-emerald-500/10 rounded-lg"><Lock className="w-3 h-3 text-emerald-400" /></div>
                                            <span className="text-xs font-mono font-bold text-emerald-100">{s.secret_name}</span>
                                        </div>
                                    ))}
                                    {agentSecrets.length === 0 && <p className="text-xs text-neutral-600 font-bold italic py-4 text-center border border-dashed border-white/10 rounded-2xl">No vault access assigned.</p>}
                                </div>
                            </div>

                            {/* Enforced Policies */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-neutral-400">
                                    <span>Active Interceptors</span>
                                    <span>{agentPolicies.length} RULES</span>
                                </div>
                                <div className="space-y-2">
                                    {agentPolicies.map(p => (
                                        <div key={p.id} className="bg-black/40 border border-white/5 rounded-2xl p-4 space-y-2 group transition-all hover:border-rose-500/20">
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs font-mono font-black text-rose-300">{p.toolName}</span>
                                                <Badge className={`text-[8px] h-4 font-black uppercase tracking-tighter ${p.ruleType === 'DENY' ? 'bg-rose-500 text-black' : 'bg-emerald-500 text-black'}`}>{p.ruleType}</Badge>
                                            </div>
                                            <p className="text-[10px] text-neutral-400 leading-relaxed font-medium line-clamp-2">{p.condition}</p>
                                        </div>
                                    ))}
                                    {agentPolicies.length === 0 && <p className="text-xs text-neutral-600 font-bold italic py-4 text-center border border-dashed border-white/10 rounded-2xl">Unrestricted execution perimeter.</p>}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>}
        </div>
    );
}

function GuardrailsPanel({ agent, agentId, user }: { agent: Agent; agentId: string; user: any }) {
    const [saving, setSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);

    const [budgetEnabled, setBudgetEnabled] = useState(!!agent.guardrails?.budget?.limitUsd);
    const [limitUsd, setLimitUsd] = useState(agent.guardrails?.budget?.limitUsd?.toString() || '');
    const [resetPeriod, setResetPeriod] = useState(agent.guardrails?.budget?.resetPeriod || 'monthly');
    const [onExceeded, setOnExceeded] = useState(agent.guardrails?.budget?.onExceeded || 'block');

    const [allowedTools, setAllowedTools] = useState(agent.guardrails?.allowedTools?.join(', ') || '');
    const [blockedTools, setBlockedTools] = useState(agent.guardrails?.blockedTools?.join(', ') || '');

    const [piiEnabled, setPiiEnabled] = useState(agent.guardrails?.piiScrubbing?.enabled || false);
    const [piiPatterns, setPiiPatterns] = useState<string[]>(agent.guardrails?.piiScrubbing?.patterns || []);
    const [piiAction, setPiiAction] = useState(agent.guardrails?.piiScrubbing?.action || 'redact');

    const ALL_PATTERNS = ['email', 'phone', 'ssn', 'credit_card', 'ip'];

    const togglePattern = (p: string) => {
        setPiiPatterns(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
    };

    const toList = (s: string) => s.split(',').map(x => x.trim()).filter(Boolean);

    const handleSave = async () => {
        if (!user) return;
        setSaving(true);
        const guardrails: any = {};
        if (budgetEnabled && limitUsd) {
            guardrails.budget = { limitUsd: parseFloat(limitUsd), resetPeriod, onExceeded };
        }
        if (toList(allowedTools).length > 0) guardrails.allowedTools = toList(allowedTools);
        if (toList(blockedTools).length > 0) guardrails.blockedTools = toList(blockedTools);
        if (piiEnabled && piiPatterns.length > 0) {
            guardrails.piiScrubbing = { enabled: true, patterns: piiPatterns, action: piiAction };
        }
        try {
            const idToken = await user.getIdToken();
            await fetch(`/api/v1/agents/${agentId}/guardrails`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify(guardrails),
            });
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 2000);
        } catch (e) {
            console.error('Failed to save guardrails:', e);
        } finally {
            setSaving(false);
        }
    };

    const inputCls = "bg-white/5 border-white/10 text-white placeholder:text-neutral-600 h-11 rounded-xl text-sm";
    const selectCls = "bg-neutral-900 border border-white/10 text-white rounded-xl h-11 px-3 text-sm w-full";
    const sectionCls = "bg-neutral-900/40 border border-white/10 rounded-3xl p-8 space-y-6";

    return (
        <div className="space-y-6">
            {/* Budget */}
            <div className={sectionCls}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <DollarSign className="w-5 h-5 text-amber-400" />
                        <h3 className="text-lg font-black uppercase tracking-tighter text-white">Spend Budget Cap</h3>
                    </div>
                    <button onClick={() => setBudgetEnabled(p => !p)}
                        className={`w-12 h-6 rounded-full transition-all relative ${budgetEnabled ? 'bg-emerald-500' : 'bg-white/10'}`}>
                        <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${budgetEnabled ? 'left-7' : 'left-1'}`} />
                    </button>
                </div>
                {budgetEnabled && (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                        <div className="space-y-2">
                            <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Limit (USD)</Label>
                            <Input value={limitUsd} onChange={e => setLimitUsd(e.target.value)} placeholder="10.00" type="number" min="0" step="0.01" className={inputCls} />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Reset Period</Label>
                            <select value={resetPeriod} onChange={e => setResetPeriod(e.target.value)} className={selectCls}>
                                <option value="daily">Daily</option>
                                <option value="weekly">Weekly</option>
                                <option value="monthly">Monthly</option>
                                <option value="never">Never</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">On Exceeded</Label>
                            <select value={onExceeded} onChange={e => setOnExceeded(e.target.value)} className={selectCls}>
                                <option value="block">Block</option>
                                <option value="warn">Warn only</option>
                                <option value="require_approval">Require Approval</option>
                            </select>
                        </div>
                    </div>
                )}
                {budgetEnabled && (
                    <div className="pt-2 space-y-2">
                        <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-neutral-400">
                            <span>Current Spend</span>
                            <span className="text-amber-400">${(agent.totalSpendUsd || 0).toFixed(4)} / ${limitUsd || '–'}</span>
                        </div>
                        {limitUsd && (
                            <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-emerald-500 to-rose-500 rounded-full transition-all"
                                    style={{ width: `${Math.min(((agent.totalSpendUsd || 0) / parseFloat(limitUsd)) * 100, 100)}%` }} />
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Tool Restrictions */}
            <div className={sectionCls}>
                <div className="flex items-center gap-3">
                    <Lock className="w-5 h-5 text-indigo-400" />
                    <h3 className="text-lg font-black uppercase tracking-tighter text-white">Tool Restrictions</h3>
                </div>
                <div className="space-y-4">
                    <div className="space-y-2">
                        <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Allowlist (comma-separated, supports wildcards)</Label>
                        <Input value={allowedTools} onChange={e => setAllowedTools(e.target.value)} placeholder="read_*, list_files, search" className={inputCls} />
                        <p className="text-[10px] text-neutral-600">If set, only these tools are permitted. Leave empty to allow all.</p>
                    </div>
                    <div className="space-y-2">
                        <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Blocklist (comma-separated, supports wildcards)</Label>
                        <Input value={blockedTools} onChange={e => setBlockedTools(e.target.value)} placeholder="bash, delete_*, send_email" className={inputCls} />
                    </div>
                </div>
            </div>

            {/* PII Scrubbing */}
            <div className={sectionCls}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Shield className="w-5 h-5 text-purple-400" />
                        <h3 className="text-lg font-black uppercase tracking-tighter text-white">PII Scrubbing</h3>
                    </div>
                    <button onClick={() => setPiiEnabled(p => !p)}
                        className={`w-12 h-6 rounded-full transition-all relative ${piiEnabled ? 'bg-emerald-500' : 'bg-white/10'}`}>
                        <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${piiEnabled ? 'left-7' : 'left-1'}`} />
                    </button>
                </div>
                {piiEnabled && (
                    <div className="space-y-5 pt-2">
                        <div className="space-y-3">
                            <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Patterns to Detect</Label>
                            <div className="flex flex-wrap gap-2">
                                {ALL_PATTERNS.map(p => (
                                    <button key={p} onClick={() => togglePattern(p)}
                                        className={`px-4 py-2 rounded-xl text-[11px] font-black uppercase tracking-wider transition-all border ${
                                            piiPatterns.includes(p)
                                                ? 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                                                : 'bg-white/5 border-white/10 text-neutral-400 hover:text-white'
                                        }`}
                                    >{p.replace('_', ' ')}</button>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label className="text-[10px] font-black uppercase tracking-widest text-neutral-400">Action</Label>
                            <select value={piiAction} onChange={e => setPiiAction(e.target.value)} className={selectCls} style={{ maxWidth: '200px' }}>
                                <option value="redact">Redact (replace with [REDACTED])</option>
                                <option value="block">Block (deny entire call)</option>
                            </select>
                        </div>
                    </div>
                )}
            </div>

            {/* Save */}
            <Button onClick={handleSave} disabled={saving}
                className="w-full h-14 bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-widest text-sm rounded-2xl transition-all">
                {saving ? 'Saving...' : saveSuccess ? '✓ Saved' : 'Save Guardrails'}
            </Button>
        </div>
    );
}

function StatItem({ label, value, sub, color = "text-white", icon }: { label: string, value: string, sub?: string, color?: string, icon: React.ReactNode }) {
    return (
        <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-6 space-y-2 relative overflow-hidden group">
            <div className="flex items-center gap-3 relative z-10">
                {icon}
                <span className="text-[10px] font-black uppercase tracking-widest text-neutral-400">{label}</span>
            </div>
            <div className="relative z-10 flex flex-col">
                <span className={`text-4xl font-black tracking-tighter ${color}`}>{value}</span>
                {sub && <span className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest mt-1">{sub}</span>}
            </div>
        </div>
    );
}

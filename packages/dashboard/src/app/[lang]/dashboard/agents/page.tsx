// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion, AnimatePresence } from "framer-motion";
import { 
    Users, 
    Shield, 
    Activity, 
    Search, 
    MoreHorizontal, 
    ExternalLink, 
    Lock, 
    Unlock,
    AlertCircle,
    CheckCircle2,
    Clock,
    DollarSign,
    Terminal,
    X,
    BarChart3,
    History,
    Settings2,
    ShieldCheck,
    ArrowRight,
    Loader2,
    AlertOctagon,
    Download,
    Check
} from "lucide-react";
import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { collection, query, where, onSnapshot, doc, updateDoc, serverTimestamp } from "firebase/firestore";
import { useAuthState } from "react-firebase-hooks/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription,
    DialogFooter 
} from "@/components/ui/dialog";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Copy, Plus, Key as KeyIcon, Trash2, Ban, PauseCircle, Code, Server, Play, RefreshCw, Layers } from "lucide-react";
import { TierBanner } from "@/components/TierBanner";

const SCOPE_PRESETS = [
    { label: "Full Access", value: "*:*" },
    { label: "Read Only", value: "read:*" },
    { label: "Finance Only", value: "finance:*" },
    { label: "Identity Only", value: "identity:*" },
];

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
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: [0, 0.25, 0] }}
                transition={{ duration: 1.2 }}
                className="absolute inset-0 bg-emerald-500/10"
            />
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

interface Agent {
    id: string;
    name: string;
    status: 'active' | 'paused' | 'revoked';
    scopes?: string[];
    totalCalls: number;
    totalSpendUsd: number;
    lastUsedAt?: any;
    verifiedAt?: any; // Added for connection status tracking
    apiKey: string;
    createdAt: any;
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

export default function AgentsPage() {
    const [user, authLoading] = useAuthState(auth);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);
    const [agentToVerify, setAgentToVerify] = useState<Agent | null>(null);
    const [newAgentName, setNewAgentName] = useState("");
    const [generatedKey, setGeneratedKey] = useState<string | null>(null);
    const [isCopying, setIsCopying] = useState(false);
    const [selectedScopes, setSelectedScopes] = useState<string[]>(["*:*"]);
    const [customScope, setCustomScope] = useState("");
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [auditLogs, setAuditLogs] = useState<any[]>([]);
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState("");
    const [editScopes, setEditScopes] = useState<string[]>([]);
    const [isRotatingKey, setIsRotatingKey] = useState(false);
    const [agentPolicies, setAgentPolicies] = useState<Policy[]>([]);
    const [agentSecrets, setAgentSecrets] = useState<VaultSecret[]>([]);
    const [integrationTab, setIntegrationTab] = useState<'python' | 'ts' | 'go'>('python');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const [createError, setCreateError] = useState("");
    const router = useRouter();
    const [selectedAgentIds, setSelectedAgentIds] = useState<Set<string>>(new Set());
    const [isBulkDeleting, setIsBulkDeleting] = useState(false);
    const [showBulkConfirm, setShowBulkConfirm] = useState(false);
    const [copiedAgentId, setCopiedAgentId] = useState<string | null>(null);

    useEffect(() => {
        if (!user) return;

        // Poll Agents from our internal API (bypasses ad-blockers)
        const loadAgents = async () => {
            try {
                const idToken = await user.getIdToken();
                const res = await fetch(`/api/v1/agents?tenantId=${user.uid}`, {
                    headers: {
                        'Authorization': `Bearer ${idToken}`
                    }
                });
                if (res.ok) {
                    const data = await res.json();
                    console.info(`[AgentsPage] Successfully loaded ${data.length} agents.`);
                    setAgents(data.sort((a: Agent, b: Agent) => {
                        const dateA = new Date(a.createdAt).getTime();
                        const dateB = new Date(b.createdAt).getTime();
                        return dateB - dateA;
                    }));
                } else {
                    console.error(`[AgentsPage] API returned ${res.status}:`, await res.text().catch(() => "N/A"));
                }
                setLoading(false);
            } catch (e) {
                console.error("[AgentsPage] Failed to poll agents:", e);
                setLoading(false);
            }
        };

        loadAgents();
        const interval = setInterval(loadAgents, 10000);

        return () => clearInterval(interval);
    }, [user]);

    useEffect(() => {
        if (!selectedAgent || !isDrawerOpen) {
            setAuditLogs([]);
            setIsEditing(false);
            return;
        }

        setEditName(selectedAgent.name);
        setEditScopes(selectedAgent.scopes || []);

        const qaudit = query(
            collection(db, "audit_logs"),
            where("agentId", "==", selectedAgent.id)
        );

        const unsubscribeAudit = onSnapshot(qaudit, (snapshot) => {
            const logs = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data() as any
            }));

            setAuditLogs(logs.sort((a, b) => {
                const dateA = a.timestamp?.toDate?.() || new Date(0);
                const dateB = b.timestamp?.toDate?.() || new Date(0);
                return dateB - dateA;
            }).slice(0, 50));
        });

        // Fetch Policies
        const qPolicies = query(
            collection(db, "policies"),
            where("agentId", "==", selectedAgent.id)
        );
        const unsubscribePolicies = onSnapshot(qPolicies, (snapshot) => {
            setAgentPolicies(snapshot.docs.map(d => ({ id: d.id, ...d.data() } as Policy)));
        });

        // Fetch Vault Secrets
        const fetchSecrets = async () => {
            try {
                if (!user?.uid) return;
                const res = await fetch(`/api/v1/vault/secrets?tenantId=${user.uid}`);
                if (res.ok) {
                    const allSecrets = await res.json() as VaultSecret[];
                    setAgentSecrets(allSecrets.filter(s => s.assigned_agents?.includes(selectedAgent.id)));
                }
            } catch (err) {
                console.error("Error fetching agent secrets:", err);
            }
        };
        fetchSecrets();

        return () => {
            unsubscribeAudit();
            unsubscribePolicies();
        };
    }, [selectedAgent, isDrawerOpen, user]);

    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    const toggleStatus = async (agent: Agent) => {
        const newStatus = agent.status === 'active' ? 'paused' : 'active';
        try {
            await updateDoc(doc(db, "agents", agent.id), {
                status: newStatus,
                updatedAt: serverTimestamp()
            });
        } catch (error) {
            console.error("Error updating agent status:", error);
        }
    };

    const filteredAgents = agents.filter(a => 
        a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.id.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const generateApiKey = () => {
        const bytes = new Uint8Array(24);
        window.crypto.getRandomValues(bytes);
        return "ag_" + btoa(String.fromCharCode(...Array.from(bytes)))
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/, "");
    };

    const handleCreateAgent = async () => {
        if (!user || !newAgentName) return;

        setCreateError("");
        setIsSubmitting(true);
        const apiKey = generateApiKey();

        try {
            const idToken = await user.getIdToken();
            const res = await fetch('/api/v1/agents', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    name: newAgentName,
                    userId: user.uid,
                    apiKey,
                    scopes: selectedScopes.length > 0 ? selectedScopes : ["*:*"],
                }),
            });
            const data = await res.json();
            if (!res.ok) {
                setCreateError(data.error || "Failed to create agent. Please try again.");
                setIsSubmitting(false);
                return;
            }
        } catch (err: any) {
            setCreateError(err.message || "Network error. Please try again.");
            setIsSubmitting(false);
            return;
        }

        setGeneratedKey(apiKey);
        setShowSuccess(true);
        setIsSubmitting(false);
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setIsCopying(true);
        setTimeout(() => setIsCopying(false), 2000);
    };

    const deleteAgent = async (agentId: string) => {
        if (!user || !confirm("Are you sure you want to delete this agent? This action is irreversible.")) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/agents/${agentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${idToken}`
                }
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.error || "Failed to delete agent");
            }
            // Also update local state for immediate feedback
            setAgents(prev => prev.filter(a => a.id !== agentId));
        } catch (error) {
            console.error("Error revoking agent:", error);
            alert("Failed to delete agent. Please try again.");
        }
    };

    const toggleSelectAgent = (agentId: string) => {
        setSelectedAgentIds(prev => {
            const next = new Set(prev);
            if (next.has(agentId)) next.delete(agentId);
            else next.add(agentId);
            return next;
        });
    };

    const toggleSelectAll = () => {
        if (selectedAgentIds.size === filteredAgents.length) {
            setSelectedAgentIds(new Set());
        } else {
            setSelectedAgentIds(new Set(filteredAgents.map(a => a.id)));
        }
    };

    const bulkDeleteAgents = async () => {
        if (!confirm(`Are you sure you want to delete ${selectedAgentIds.size} agents?`)) return;
        setIsBulkDeleting(true);
        try {
            await Promise.all(
                Array.from(selectedAgentIds).map(id =>
                    fetch(`/api/v1/agents/${id}`, {
                        method: 'DELETE',
                    })
                )
            );
            // Update local state
            setAgents(prev => prev.filter(a => !selectedAgentIds.has(a.id)));
            setSelectedAgentIds(new Set());
        } catch (error) {
            console.error("Error bulk revoking agents:", error);
            alert("Some agents could not be deleted.");
        } finally {
            setIsBulkDeleting(false);
            setShowBulkConfirm(false);
        }
    };
    const handleUpdateAgent = async () => {
        if (!selectedAgent) return;
        try {
            await updateDoc(doc(db, "agents", selectedAgent.id), {
                name: editName,
                scopes: editScopes,
                updatedAt: serverTimestamp()
            });
            setIsEditing(false);
        } catch (error) {
            console.error("Error updating agent:", error);
        }
    };

    const handleRotateKey = async () => {
        if (!selectedAgent || !confirm("Generating a new API key will immediately invalidate the current one. Continue?")) return;
        
        setIsRotatingKey(true);
        const newKey = generateApiKey();
        
        try {
            await updateDoc(doc(db, "agents", selectedAgent.id), {
                apiKey: newKey,
                updatedAt: serverTimestamp()
            });
            alert(`New API Key generated: ${newKey}\nPlease save it securely as it won't be shown again.`);
            setSelectedAgent(prev => prev ? { ...prev, apiKey: newKey } : null);
        } catch (error) {
            console.error("Error rotating key:", error);
        } finally {
            setIsRotatingKey(false);
        }
    };

    const handleDownloadEnv = async (agent: Agent) => {
        if (!user) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/tenants/${user.uid}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            let adminKey = "";
            if (res.ok) {
                const data = await res.json();
                adminKey = data.master_api_key || "";
            }
            const envContent = `BASE_URL=https://www.supra-wall.com
ADMIN_KEY=${adminKey}
AGENT_KEY=${agent.apiKey}
AGENT_ID=${agent.id}`;

            await navigator.clipboard.writeText(envContent);
            setCopiedAgentId(agent.id);
            setTimeout(() => setCopiedAgentId(null), 2000);
        } catch (e) {
            console.error("Error copying env", e);
        }
    };

    const handleBulkDownloadEnv = async (agentList: Agent[]) => {
        if (!user || agentList.length === 0) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/api/v1/tenants/${user.uid}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            let adminKey = "";
            if (res.ok) {
                const data = await res.json();
                adminKey = data.master_api_key || "";
            }

            const sections = agentList.map((agent) => [
                `# Agent: ${agent.name}`,
                `BASE_URL=https://www.supra-wall.com`,
                `ADMIN_KEY=${adminKey}`,
                `AGENT_KEY=${agent.apiKey}`,
                `AGENT_ID=${agent.id}`,
            ].join('\n'));

            const fileContent = sections.join('\n\n');
            await navigator.clipboard.writeText(fileContent);
            setCopiedAgentId('bulk');
            setTimeout(() => setCopiedAgentId(null), 2000);
        } catch (e) {
            console.error("Error bulk copying env", e);
        }
    };

    // Minimum scanning animation time for UX feel
    const [isScanning, setIsScanning] = useState(true);
    
    useEffect(() => {
        const timer = setTimeout(() => {
            setIsScanning(false);
        }, 1200); // Snappy but visible scan
        return () => clearTimeout(timer);
    }, []);

    if (loading || isScanning) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-8 relative overflow-hidden">
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="relative"
                >
                    <motion.div
                        animate={{ 
                            rotate: 360,
                            scale: [1, 1.1, 1],
                        }}
                        transition={{ 
                            rotate: { duration: 4, repeat: Infinity, ease: "linear" },
                            scale: { duration: 2, repeat: Infinity }
                        }}
                        className="w-24 h-24 rounded-full border-2 border-dashed border-blue-500/20 flex items-center justify-center"
                    >
                        <div className="w-16 h-16 rounded-full border border-blue-500/10" />
                    </motion.div>
                    
                    <motion.div
                        animate={{ 
                            top: ["0%", "100%", "0%"],
                            opacity: [0, 1, 0]
                        }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent shadow-[0_0_15px_rgba(59,130,246,0.5)]"
                    />
                    
                    <motion.div className="absolute inset-0 flex items-center justify-center">
                        <Users className="w-8 h-8 text-blue-400/50" />
                    </motion.div>
                </motion.div>

                <div className="text-center space-y-3">
                    <motion.p 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-white font-black italic uppercase tracking-[0.4em] text-[10px] drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                    >
                        {loading ? "Decrypting Identities..." : "Syncing Access..."}
                    </motion.p>
                    <div className="flex justify-center gap-1.5">
                        {[0, 1, 2].map((i) => (
                            <motion.div
                                key={i}
                                animate={{ 
                                    scale: [1, 1.5, 1],
                                    opacity: [0.3, 1, 0.3]
                                }}
                                transition={{ 
                                    duration: 1,
                                    repeat: Infinity,
                                    delay: i * 0.2
                                }}
                                className="w-1.5 h-1.5 rounded-full bg-blue-500/50"
                            />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8 pb-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                            <Users className="w-5 h-5 text-blue-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Agent Identities</h1>
                    </div>
                    <p className="text-neutral-400 max-w-xl">
                        Manage autonomous credentials and granular permissions for all connected AI agents in your ecosystem.
                    </p>
                </motion.div>

                <div className="flex items-center gap-3">
                    <div className="relative w-full md:w-80">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                        <input 
                            type="text"
                            placeholder="Search by name or ID..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-neutral-900/50 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all shadow-inner"
                        />
                    </div>
                    <Button
                        onClick={() => handleBulkDownloadEnv(agents)}
                        disabled={agents.length === 0}
                        className={`${copiedAgentId === 'bulk' ? 'bg-emerald-500 text-black border-emerald-500' : 'bg-white/5 text-neutral-300 border-white/10 hover:bg-white/10'} border font-black uppercase tracking-wider text-[11px] h-[42px] px-5 rounded-xl transition-all flex items-center gap-2`}
                    >
                        {copiedAgentId === 'bulk' ? <Check className="w-3.5 h-3.5" /> : <Download className="w-3.5 h-3.5" />}
                        {copiedAgentId === 'bulk' ? 'Copied All!' : 'Export All'}
                    </Button>
                    <Button 
                        onClick={() => {
                            setGeneratedKey(null);
                            setIsCreateModalOpen(true);
                        }}
                        className="bg-emerald-500 hover:bg-emerald-600 text-black font-black uppercase tracking-wider text-[11px] h-[42px] px-6 rounded-xl border-b-4 border-emerald-700 active:border-b-0 active:translate-y-1 transition-all flex items-center gap-2"
                    >
                        <Plus className="w-3.5 h-3.5" />
                        Register Agent
                    </Button>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatCard 
                    icon={<Activity className="w-4 h-4 text-emerald-400" />}
                    label="Active Agents"
                    value={agents.filter(a => a.status === 'active').length.toString()}
                    subtext="Currently authorized"
                />
                <StatCard 
                    icon={<Terminal className="w-4 h-4 text-blue-400" />}
                    label="Total Tool Calls"
                    value={agents.reduce((acc, curr) => acc + (curr.totalCalls || 0), 0).toLocaleString()}
                    subtext="Across all sessions"
                />
                <StatCard 
                    icon={<DollarSign className="w-4 h-4 text-amber-400" />}
                    label="Managed Spend"
                    value={`$${agents.reduce((acc, curr) => acc + (curr.totalSpendUsd || 0), 0).toFixed(2)}`}
                    subtext="Estimated API overhead"
                />
            </div>

            {/* Tier Upgrade Nudge */}
            <TierBanner
                tier="developer"
                usages={[
                    { current: agents.filter(a => a.status !== 'revoked').length, max: 3, label: 'Agents', upgradeFeature: 'Unlimited on Cloud' },
                ]}
            />

            {/* Agents Table */}
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-neutral-900/40 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
            >
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white/5 bg-white/[0.05]">
                                <th className="pl-4 pr-0 py-4 w-10">
                                    <button
                                        onClick={toggleSelectAll}
                                        className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                                            selectedAgentIds.size > 0 && selectedAgentIds.size === filteredAgents.length
                                                ? 'bg-emerald-500 border-emerald-400'
                                                : selectedAgentIds.size > 0
                                                ? 'bg-emerald-500/30 border-emerald-500/50'
                                                : 'border-white/20 hover:border-white/40'
                                        }`}
                                    >
                                        {selectedAgentIds.size > 0 && selectedAgentIds.size === filteredAgents.length && (
                                            <CheckCircle2 className="w-3 h-3 text-black" />
                                        )}
                                        {selectedAgentIds.size > 0 && selectedAgentIds.size < filteredAgents.length && (
                                            <div className="w-2 h-0.5 bg-emerald-200 rounded-full" />
                                        )}
                                    </button>
                                </th>
                                <th className="px-6 py-4 text-xs font-bold text-neutral-400 uppercase tracking-widest">Identity & Scopes</th>
                                <th className="px-6 py-4 text-xs font-bold text-neutral-400 uppercase tracking-widest text-center">Status</th>
                                <th className="px-6 py-4 text-xs font-bold text-neutral-400 uppercase tracking-widest">Usage Metrics</th>
                                <th className="px-6 py-4 text-xs font-bold text-neutral-400 uppercase tracking-widest">Identity ID</th>
                                <th className="px-6 py-4 text-xs font-bold text-neutral-400 uppercase tracking-widest text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {filteredAgents.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-neutral-400 italic">
                                        No agents found. Register your first agent using the SDK.
                                    </td>
                                </tr>
                            ) : (
                                filteredAgents.map((agent) => (
                                        <tr 
                                            key={agent.id} 
                                            className={`hover:bg-white/[0.04] transition-colors group cursor-pointer ${selectedAgentIds.has(agent.id) ? 'bg-emerald-500/[0.04]' : ''}`}
                                            onClick={() => {
                                                router.push(`/dashboard/agents/${agent.id}`);
                                            }}
                                        >
                                        <td className="pl-4 pr-0 py-5 w-10">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    toggleSelectAgent(agent.id);
                                                }}
                                                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                                                    selectedAgentIds.has(agent.id)
                                                        ? 'bg-emerald-500 border-emerald-400'
                                                        : 'border-white/20 hover:border-white/40'
                                                }`}
                                            >
                                                {selectedAgentIds.has(agent.id) && <CheckCircle2 className="w-3 h-3 text-black" />}
                                            </button>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1.5">
                                                <span className="text-white font-bold tracking-tight text-base group-hover:text-blue-400 transition-colors">
                                                    {agent.name}
                                                </span>
                                                <div className="flex flex-wrap gap-1">
                                                    {agent.scopes?.slice(0, 3).map(scope => (
                                                        <Badge key={scope} variant="outline" className="text-[10px] bg-white/5 border-white/10 text-neutral-400 font-mono">
                                                            {scope}
                                                        </Badge>
                                                    ))}
                                                    {(agent.scopes?.length || 0) > 3 && (
                                                        <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-white/5 text-neutral-400">
                                                            +{(agent.scopes?.length || 0) - 3} more
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="flex justify-center">
                                                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border ${
                                                    agent.status === 'active' 
                                                        ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]' 
                                                        : agent.status === 'paused'
                                                            ? 'bg-amber-500/10 text-amber-500 border-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.1)]'
                                                            : 'bg-rose-500/10 text-rose-500 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
                                                }`}>
                                                    <div className={`w-1.5 h-1.5 rounded-full ${
                                                        agent.status === 'active' 
                                                            ? 'bg-emerald-400 animate-pulse' 
                                                            : agent.status === 'paused'
                                                                ? 'bg-amber-400'
                                                                : 'bg-rose-400'
                                                    }`} />
                                                    {agent.status === 'paused' ? 'Suspended' : agent.status === 'active' ? 'Active' : 'Deactivated'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1.5 mb-1.5">
                                                    <span className="text-white font-mono text-sm">{agent.totalCalls || 0} calls</span>
                                                    <span className="text-neutral-600">/</span>
                                                    <span className="text-emerald-400/80 font-mono text-xs">${(agent.totalSpendUsd || 0).toFixed(4)}</span>
                                                </div>
                                                {agent.lastUsedAt && (
                                                    <div className="flex items-center gap-1.5 text-[10px] text-neutral-400 uppercase font-bold tracking-wider">
                                                        <Clock className="w-3 h-3" />
                                                        {agent.lastUsedAt.toDate?.().toLocaleString()}
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <code className="text-xs text-neutral-400 bg-black/30 px-2 py-1 rounded border border-white/5 font-mono">
                                                {agent.id}
                                            </code>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <div className="flex justify-end items-center gap-2">
                                                <button 
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setSelectedAgent(agent);
                                                        setIsDrawerOpen(true);
                                                    }}
                                                    title="View Analytics"
                                                    className="p-2 bg-indigo-500/5 border border-indigo-500/10 rounded-lg text-indigo-500/60 hover:text-indigo-400 hover:bg-indigo-500/20 transition-all"
                                                >
                                                    <BarChart3 className="w-4 h-4" />
                                                </button>
                                                <button 
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setAgentToVerify(agent);
                                                        setIsVerifyModalOpen(true);
                                                    }}
                                                    title={agent.verifiedAt ? `Verified ${new Date(agent.verifiedAt).toLocaleDateString()} — Click to verify again` : "Click to verify connection"}
                                                    className={`p-2 rounded-lg border transition-all ${
                                                        (agent.verifiedAt && (new Date().getTime() - new Date(agent.verifiedAt).getTime() < 15 * 60 * 1000))
                                                            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                                                            : 'bg-neutral-500/5 border-white/10 text-neutral-500 hover:text-white hover:bg-white/10'
                                                    }`}
                                                >
                                                    {(agent.verifiedAt && (new Date().getTime() - new Date(agent.verifiedAt).getTime() < 15 * 60 * 1000)) ? (
                                                        <ShieldCheck className="w-4 h-4" />
                                                    ) : (
                                                        <Shield className="w-4 h-4" />
                                                    )}
                                                </button>
                                                <button 
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDownloadEnv(agent);
                                                    }}
                                                    title="Copy config to clipboard"
                                                    className={`p-2 border rounded-lg transition-all ${
                                                        copiedAgentId === agent.id 
                                                            ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400' 
                                                            : 'bg-emerald-500/5 border-emerald-500/10 text-emerald-500/60 hover:text-emerald-400 hover:bg-emerald-500/20'
                                                    }`}
                                                >
                                                    {copiedAgentId === agent.id ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
                                                </button>
                                                <button 
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        deleteAgent(agent.id);
                                                    }}
                                                    className="p-2 bg-rose-500/5 border border-rose-500/10 rounded-lg text-rose-500/60 hover:text-rose-400 hover:bg-rose-500/20 transition-all"
                                                    title="Revoke Agent"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </motion.div>

            {/* Bulk Action Bar */}
            <AnimatePresence>
                {selectedAgentIds.size > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 40 }}
                        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                        className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 bg-neutral-900/95 backdrop-blur-xl border border-white/10 rounded-2xl px-6 py-4 flex items-center gap-6 shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                                <span className="text-emerald-400 font-black text-sm">{selectedAgentIds.size}</span>
                            </div>
                            <span className="text-sm text-neutral-300 font-medium">
                                agent{selectedAgentIds.size > 1 ? 's' : ''} selected
                            </span>
                        </div>
                        <div className="w-px h-8 bg-white/10" />
                        <button
                            onClick={() => setSelectedAgentIds(new Set())}
                            className="text-xs text-neutral-400 hover:text-white transition-colors font-bold uppercase tracking-wider"
                        >
                            Clear
                        </button>
                        <Button
                                    onClick={() => {
                                        const selectedAgents = agents.filter(a => selectedAgentIds.has(a.id));
                                        handleBulkDownloadEnv(selectedAgents);
                                    }}
                                    className={`${copiedAgentId === 'bulk' ? 'bg-emerald-500 text-black border-emerald-500' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'} font-black uppercase tracking-wider text-[11px] h-10 px-5 rounded-xl flex items-center gap-2 transition-all`}
                                >
                                    {copiedAgentId === 'bulk' ? <Check className="w-3.5 h-3.5" /> : <Download className="w-3.5 h-3.5" />}
                                    {copiedAgentId === 'bulk' ? 'Copied Selected!' : 'Copy Config'}
                                </Button>
                        <Button
                            onClick={() => setShowBulkConfirm(true)}
                            className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 font-black uppercase tracking-wider text-[11px] h-10 px-5 rounded-xl flex items-center gap-2"
                        >
                            <Trash2 className="w-3.5 h-3.5" />
                            Delete Selected
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Bulk Delete Confirmation Dialog */}
            <Dialog open={showBulkConfirm} onOpenChange={setShowBulkConfirm}>
                <DialogContent className="bg-neutral-950 border-white/10 shadow-2xl sm:max-w-[420px]">
                    <DialogHeader>
                        <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto mb-4">
                            <AlertOctagon className="w-7 h-7 text-rose-400" />
                        </div>
                        <DialogTitle className="text-xl font-black text-white text-center uppercase tracking-tight">
                            Confirm Bulk Delete
                        </DialogTitle>
                        <DialogDescription className="text-center text-neutral-400 text-sm leading-relaxed">
                            You are about to revoke <strong className="text-white">{selectedAgentIds.size} agent{selectedAgentIds.size > 1 ? 's' : ''}</strong>. This will immediately invalidate their API keys and prevent any further operations.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="max-h-40 overflow-y-auto bg-black/30 rounded-xl border border-white/5 p-3 space-y-1">
                        {Array.from(selectedAgentIds).map(id => {
                            const ag = agents.find(a => a.id === id);
                            return (
                                <div key={id} className="flex items-center gap-2 text-xs text-neutral-400 py-1">
                                    <Trash2 className="w-3 h-3 text-rose-400/60 flex-shrink-0" />
                                    <span className="font-medium text-white">{ag?.name || id}</span>
                                    <code className="ml-auto text-[10px] text-neutral-500 font-mono">{id.slice(0, 12)}…</code>
                                </div>
                            );
                        })}
                    </div>
                    <DialogFooter className="flex gap-3 sm:justify-center">
                        <Button
                            onClick={() => setShowBulkConfirm(false)}
                            variant="outline"
                            className="border-white/10 text-neutral-400 hover:text-white font-bold uppercase tracking-wider text-[11px] h-12 px-6 rounded-xl"
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={bulkDeleteAgents}
                            disabled={isBulkDeleting}
                            className="bg-rose-600 hover:bg-rose-500 text-white font-black uppercase tracking-wider text-[11px] h-12 px-6 rounded-xl flex items-center gap-2"
                        >
                            {isBulkDeleting ? (
                                <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                                <>
                                    <Trash2 className="w-3.5 h-3.5" />
                                    Delete {selectedAgentIds.size} Agent{selectedAgentIds.size > 1 ? 's' : ''}
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Create Agent Modal */}
            <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
                <DialogContent className="bg-neutral-950 border-white/10 shadow-2xl space-y-6 sm:max-w-[450px]">
                    <DialogHeader className="relative">
                        <DialogTitle className="text-2xl font-black text-white italic uppercase tracking-tighter">
                            Register AI Identity
                        </DialogTitle>
                        <DialogDescription className="text-neutral-400 text-xs font-medium uppercase tracking-widest">
                            Authorize a new autonomous entity in your ecosystem.
                        </DialogDescription>
                        {showSuccess && <DollarConfetti />}
                    </DialogHeader>

                    {!generatedKey ? (
                        <div className="space-y-6 py-4">
                            <div className="space-y-2">
                                <Label htmlFor="name" className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/70 ml-1">
                                    Agent Name
                                </Label>
                                <Input
                                    id="name"
                                    placeholder="e.g. Finance Intelligence Agent"
                                    value={newAgentName}
                                    onChange={(e) => setNewAgentName(e.target.value)}
                                    className="bg-white/[0.05] border-white/10 h-12 rounded-xl text-white focus:ring-emerald-500/50 focus:border-emerald-500/50"
                                />
                            </div>

                            <div className="space-y-4">
                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/70 ml-1">
                                    Authorization Scopes
                                </Label>
                                <p className="text-[11px] text-neutral-400 px-1 italic">Restrict what this agent can access. Leave empty for full access (*:*).</p>
                                
                                <div className="grid grid-cols-2 gap-2">
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
                                                ? 'bg-emerald-500 border-emerald-400'
                                                : 'border-white/20'
                                                }`}>
                                                {selectedScopes.includes(scope) && <CheckCircle2 className="w-2.5 h-2.5 text-black" />}
                                            </div>
                                            <span className="font-mono tracking-tight">{label}</span>
                                        </label>
                                    ))}
                                </div>

                                <div className="flex gap-2">
                                    <Input 
                                        placeholder="Add custom scope (e.g. tools:*)"
                                        value={customScope}
                                        onChange={(e) => setCustomScope(e.target.value)}
                                        className="bg-white/[0.05] border-white/10 h-10 rounded-xl text-white text-xs font-mono"
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && customScope) {
                                                e.preventDefault();
                                                const scopeToAdd = customScope.includes(':') ? customScope : `custom:${customScope}`;
                                                if (!selectedScopes.includes(scopeToAdd)) {
                                                    setSelectedScopes([...selectedScopes, scopeToAdd]);
                                                }
                                                setCustomScope("");
                                            }
                                        }}
                                    />
                                    <Button 
                                        type="button"
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            if (customScope) {
                                                const scopeToAdd = customScope.includes(':') ? customScope : `custom:${customScope}`;
                                                if (!selectedScopes.includes(scopeToAdd)) {
                                                    setSelectedScopes([...selectedScopes, scopeToAdd]);
                                                }
                                                setCustomScope("");
                                            }
                                        }}
                                        className="border-white/10 h-10 px-4 hover:bg-white/5 font-black uppercase text-[10px] tracking-widest"
                                    >
                                        Add
                                    </Button>
                                </div>

                                <div className="flex flex-wrap gap-1.5 mt-2">
                                    {selectedScopes.map(scope => (
                                        <Badge key={scope} variant="secondary" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1 pr-1 border text-[10px] font-mono">
                                            {scope}
                                            <X 
                                                className="w-3 h-3 cursor-pointer hover:text-white" 
                                                onClick={() => setSelectedScopes(selectedScopes.filter(s => s !== scope))}
                                            />
                                        </Badge>
                                    ))}
                                </div>
                            </div>

                            {createError && (
                                <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">{createError}</p>
                            )}
                            <Button
                                onClick={() => handleCreateAgent()}
                                disabled={!newAgentName || isSubmitting}
                                className="w-full h-14 bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-[0.2em] rounded-xl shadow-[0_10px_30px_rgba(16,185,129,0.2)] disabled:opacity-50 disabled:cursor-not-allowed group"
                            >
                                {isSubmitting ? (
                                    <RefreshCw className="w-5 h-5 animate-spin" />
                                ) : (
                                    <span className="flex items-center gap-2">
                                        Generate Identity <ShieldCheck className="w-4 h-4 group-hover:scale-110 transition-transform" />
                                    </span>
                                )}
                            </Button>
                        </div>
                    ) : (
                        <div className="space-y-6 py-4">
                            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl space-y-2">
                                <div className="flex items-center gap-2">
                                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                                    <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider">Secure Discovery</span>
                                </div>
                                <p className="text-[11px] text-neutral-400 leading-relaxed font-medium">
                                    Store this API key safely. For security reasons, <span className="text-white italic">it will never be shown again</span> in the dashboard.
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400/70 ml-1">
                                    Agent API Key
                                </Label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <KeyIcon className="h-4 w-4 text-neutral-400" />
                                    </div>
                                    <div className="w-full bg-black/40 border border-white/10 rounded-xl pl-10 pr-12 py-3 text-xs font-mono text-blue-100 shadow-inner break-all">
                                        {generatedKey}
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(generatedKey)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-white/5 rounded-lg transition-colors group-hover:bg-white/10"
                                    >
                                        {isCopying ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-neutral-400" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                    <DialogFooter>
                        {generatedKey && (
                            <Button
                                onClick={() => {
                                    setIsCreateModalOpen(false);
                                    setGeneratedKey(null);
                                    router.push("/dashboard");
                                }}
                                className="w-full bg-emerald-500 hover:bg-emerald-400 text-black font-black uppercase tracking-widest text-[11px] h-14 rounded-xl transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] border-b-4 border-emerald-700 active:border-b-0 active:translate-y-1 group"
                            >
                                <span className="flex items-center gap-2">
                                    Go to Command Center <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </span>
                            </Button>
                        )}
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Verify Connection Dialog */}
            <Dialog open={isVerifyModalOpen} onOpenChange={setIsVerifyModalOpen}>
                <DialogContent className="bg-neutral-950 border-white/10 shadow-2xl space-y-6 sm:max-w-[500px]">
                    <DialogHeader className="relative">
                        <div className="absolute -top-10 -right-4 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full" />
                        <DialogTitle className="text-2xl font-black text-white italic uppercase tracking-tighter flex items-center gap-3">
                            <ShieldCheck className="w-8 h-8 text-emerald-400" />
                            Verify Connection
                        </DialogTitle>
                        <DialogDescription className="text-neutral-400 text-xs font-medium uppercase tracking-widest">
                            Agent: {agentToVerify?.name}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4">
                        <p className="text-sm text-neutral-300 leading-relaxed">
                            To verify your agent is correctly integrated with SupraWall, run a test evaluation call using the command below. 
                            The shield icon for this agent will turn green once a heartbeat is detected.
                        </p>

                        <div className="p-4 bg-black/40 border border-white/10 rounded-xl font-mono text-xs text-neutral-400 relative group">
                            <pre className="whitespace-pre-wrap break-all">
                                {`curl -X POST https://www.supra-wall.com/api/v1/evaluate \\
  -H "Content-Type: application/json" \\
  -d '{
    "apiKey": "${agentToVerify?.apiKey || 'AG_KEY'}",
    "toolName": "suprawall:verify",
    "args": { "ping": true }
  }'`}
                            </pre>
                            <button
                                onClick={() => {
                                    const text = `curl -X POST https://www.supra-wall.com/api/v1/evaluate \\
  -H "Content-Type: application/json" \\
  -d '{
    "apiKey": "${agentToVerify?.apiKey || 'AG_KEY'}",
    "toolName": "suprawall:verify",
    "args": { "ping": true }
  }'`;
                                    navigator.clipboard.writeText(text);
                                }}
                                className="absolute top-3 right-3 p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                            >
                                <Copy className="w-3.5 h-3.5" />
                            </button>
                        </div>

                        <div className="flex items-center gap-3 p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-xl text-xs text-emerald-400/80">
                            <Clock className="w-4 h-4" />
                            <span>Status: Waiting for heartbeat... (Updates every 10s)</span>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            onClick={() => setIsVerifyModalOpen(false)}
                            className="w-full bg-white/5 hover:bg-white/10 text-white border-white/10 font-bold uppercase tracking-widest text-[10px]"
                        >
                            Done
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Agent Detail Sheet */}
            <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
                <SheetContent side="right" className="w-full sm:max-w-3xl bg-neutral-950 border-white/10 p-0 overflow-hidden flex flex-col">
                    {selectedAgent && (() => {
                        const interceptionCount = auditLogs.filter(l => l.decision === 'DENY').length;
                        const validLogsCount = auditLogs.filter(l => l.decision !== 'PAUSED').length || 1;
                        const interceptionRate = ((interceptionCount / validLogsCount) * 100).toFixed(1);
                        const loopDetections = auditLogs.filter(l => l.isLoop).length;
                        const maxBudget = 10.00; // Arbitrary cap for presentation
                        const currentSpend = selectedAgent.totalSpendUsd || 0;
                        const spendProgress = Math.min((currentSpend / maxBudget) * 100, 100);
                        const agentUri = `agent://${selectedAgent.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.acme.suprawall.com`;
                        const hasPendingApproval = auditLogs.some(l => l.decision === 'PAUSED');

                        const snippetCode = {
                            python: `import suprawall\n\nagent = suprawall.Agent(\n  identity="${agentUri}",\n  api_key="ag_xxxxxxxxxxx"\n)\n\nagent.start()`,
                            ts: `import { SupraWall } from '@suprawall/sdk';\n\nconst agent = new SupraWall({\n  identity: "${agentUri}",\n  apiKey: "ag_xxxxxxxxxxx"\n});\n\nawait agent.connect();`,
                            go: `import "github.com/suprawall/sdk-go"\n\nagent := suprawall.NewAgent(&suprawall.Config{\n    Identity: "${agentUri}",\n    APIKey:   "ag_xxxxxxxxxxx",\n})\nagent.Run()`
                        };

                        return (
                            <>
                                <div className="p-8 pb-4 border-b border-white/5 bg-black/20">
                                    <SheetHeader className="space-y-1">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-4">
                                                <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex flex-col items-center justify-center relative shadow-[0_0_15px_rgba(99,102,241,0.15)]">
                                                    <Terminal className="w-6 h-6 text-indigo-400" />
                                                    <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-neutral-950 flex items-center justify-center ${
                                                        selectedAgent.status === 'active' ? 'bg-emerald-500' : 'bg-amber-500'
                                                    }`}>
                                                        {selectedAgent.status === 'active' && <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />}
                                                    </div>
                                                </div>
                                                <div>
                                                    {isEditing ? (
                                                        <Input 
                                                            value={editName}
                                                            onChange={(e) => setEditName(e.target.value)}
                                                            className="bg-white/5 border-white/10 text-2xl font-black text-white p-2 h-auto"
                                                        />
                                                    ) : (
                                                        <SheetTitle className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                                                            {selectedAgent.name}
                                                            {selectedAgent.status === 'active' ? (
                                                                <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] tracking-widest font-bold uppercase transition-colors hover:bg-emerald-500/20">Active</Badge>
                                                            ) : selectedAgent.status === 'paused' ? (
                                                                <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-[10px] tracking-widest font-bold uppercase transition-colors hover:bg-amber-500/20">Suspended</Badge>
                                                            ) : (
                                                                <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20 text-[10px] tracking-widest font-bold uppercase transition-colors hover:bg-rose-500/20">Deactivated</Badge>
                                                            )}
                                                        </SheetTitle>
                                                    )}
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <Badge variant="outline" className="text-[10px] font-mono tracking-widest uppercase text-neutral-400 bg-white/5 border-white/5">
                                                            ID: {selectedAgent.id}
                                                        </Badge>
                                                        {isEditing && (
                                                            <Button size="sm" onClick={handleUpdateAgent} className="h-6 bg-emerald-500 text-black font-bold uppercase text-[10px] hover:bg-emerald-400">
                                                                Save
                                                            </Button>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </SheetHeader>
                                </div>

                                <div className="flex-1 overflow-y-auto p-8 space-y-12">
                                    {/* Human-in-the-loop Notification */}
                                    {hasPendingApproval && (
                                        <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-start gap-4 shadow-[0_0_20px_rgba(245,158,11,0.1)]">
                                            <div className="p-2 bg-amber-500/20 rounded-lg shrink-0 mt-0.5">
                                                <PauseCircle className="w-5 h-5 text-amber-400 animate-pulse" />
                                            </div>
                                            <div className="space-y-1">
                                                <h4 className="text-amber-400 font-bold tracking-tight">Human Approval Required</h4>
                                                <p className="text-xs text-neutral-300">This agent has paused an action that violates its policy thresholds. It is currently waiting for human intervention.</p>
                                                <Link href="/dashboard/forensics" className="text-[10px] uppercase tracking-widest text-amber-300 font-black inline-flex items-center gap-1 hover:text-white transition-colors mt-2">
                                                    Review paused actions <ExternalLink className="w-3 h-3" />
                                                </Link>
                                            </div>
                                        </div>
                                    )}

                                    {/* --- 1. Identity & Integration --- */}
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                                            <Layers className="w-4 h-4 text-blue-400" />
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Identity & Integration</h3>
                                        </div>
                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {/* Left Col */}
                                            <div className="space-y-4">
                                                <div className="space-y-2">
                                                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">Agent URI</Label>
                                                    <div className="flex bg-black/40 border border-white/5 rounded-xl h-10 items-center px-3 group transition-colors hover:border-white/10">
                                                        <code className="text-[11px] text-blue-300 font-mono w-full truncate">{agentUri}</code>
                                                        <button onClick={() => copyToClipboard(agentUri)} className="shrink-0 p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/10 transition">
                                                            <Copy className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                </div>
                                                <div className="space-y-2">
                                                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">API Key</Label>
                                                    <div className="flex items-center justify-between bg-black/40 border border-white/5 rounded-xl h-10 px-3 group transition-colors hover:border-white/10">
                                                        <div className="flex items-center gap-2">
                                                            <KeyIcon className={`w-3.5 h-3.5 ${isRotatingKey ? 'animate-spin' : 'text-emerald-400'}`} />
                                                            <code className="text-[11px] text-neutral-400 font-mono">
                                                                {isRotatingKey ? "GENERATING..." : "••••••••••••••••••••••••"}
                                                            </code>
                                                        </div>
                                                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <Button size="sm" variant="ghost" onClick={handleRotateKey} disabled={isRotatingKey} className="h-6 px-2 border border-rose-500/20 text-[9px] font-black uppercase text-rose-500 hover:bg-rose-500/10">Rotate</Button>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">Scopes</Label>
                                                        <Button variant="ghost" size="sm" onClick={() => setIsEditing(!isEditing)} className="h-5 text-[9px] uppercase px-2 bg-white/5 hover:bg-white/10">{isEditing ? "Editing..." : "Edit"}</Button>
                                                    </div>
                                                    {isEditing ? (
                                                        <div className="p-3 bg-white/5 rounded-lg border border-white/10 space-y-2">
                                                            <div className="flex gap-2">
                                                                <Input placeholder="Add custom scope" value={customScope} onChange={(e) => setCustomScope(e.target.value)} className="h-7 text-[10px] bg-black/40" />
                                                                <Button size="sm" variant="outline" className="h-7 px-2" onClick={() => { if(customScope) { setEditScopes([...editScopes, customScope]); setCustomScope(""); }}}>Add</Button>
                                                            </div>
                                                            <div className="flex flex-wrap gap-1">
                                                                {editScopes.map(scope => (
                                                                    <Badge key={scope} variant="outline" className="text-[9px] font-mono group cursor-pointer">{scope} <X className="w-2.5 h-2.5 ml-1 opacity-50 group-hover:opacity-100" onClick={()=>setEditScopes(editScopes.filter(s=>s!==scope))}/></Badge>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <div className="flex flex-wrap gap-1">
                                                            {selectedAgent.scopes?.map(scope => (
                                                                <Badge key={scope} variant="outline" className="bg-black/40 border-white/10 text-neutral-400 font-mono py-0.5 px-2 text-[10px]">{scope}</Badge>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            {/* Right Col */}
                                            <div className="space-y-2 flex flex-col">
                                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">Quick Integration</Label>
                                                <div className="flex-1 bg-black/40 border border-white/5 rounded-xl overflow-hidden flex flex-col shadow-inner">
                                                    <div className="flex border-b border-white/5 bg-white/[0.05]">
                                                        {(['python', 'ts', 'go'] as const).map(t => (
                                                            <button 
                                                                key={t}
                                                                onClick={() => setIntegrationTab(t)}
                                                                className={`flex-1 py-1.5 text-[10px] font-black uppercase text-center transition-colors ${integrationTab === t ? 'text-blue-400 border-b-2 border-blue-400 bg-blue-400/5' : 'text-neutral-400 hover:text-neutral-300'}`}
                                                            >
                                                                {t === 'python' ? 'Python' : t === 'ts' ? 'TypeScript' : 'Go'}
                                                            </button>
                                                        ))}
                                                    </div>
                                                    <div className="p-3 flex-1 relative group">
                                                        <pre className="text-[10px] font-mono text-neutral-300 leading-relaxed whitespace-pre-wrap">{snippetCode[integrationTab]}</pre>
                                                        <button onClick={() => copyToClipboard(snippetCode[integrationTab])} className="absolute top-2 right-2 p-1.5 bg-white/10 rounded border border-white/10 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/20">
                                                            <Copy className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* --- 2. Telemetry & Health Metrics --- */}
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                                            <Activity className="w-4 h-4 text-emerald-400" />
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Telemetry & Health Metrics</h3>
                                        </div>
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                            <div className="p-4 bg-white/[0.05] border border-white/5 rounded-2xl flex flex-col justify-between">
                                                <div className="flex gap-2 items-center text-neutral-400 mb-2">
                                                    <Terminal className="w-3.5 h-3.5" />
                                                    <span className="text-[9px] uppercase tracking-widest font-black">Total Calls</span>
                                                </div>
                                                <div className="text-2xl font-black text-white">{selectedAgent.totalCalls || 0}</div>
                                            </div>
                                            <div className="p-4 bg-white/[0.05] border border-white/5 rounded-2xl flex flex-col justify-between">
                                                <div className="flex gap-2 items-center text-neutral-400 mb-2">
                                                    <Shield className="w-3.5 h-3.5 text-rose-400/50" />
                                                    <span className="text-[9px] uppercase tracking-widest font-black">Interception</span>
                                                </div>
                                                <div className="flex items-baseline gap-1">
                                                    <div className="text-2xl font-black text-rose-400">{interceptionRate}%</div>
                                                    <div className="text-[10px] text-neutral-400">blocked</div>
                                                </div>
                                            </div>
                                            <div className="p-4 bg-white/[0.05] border border-white/5 rounded-2xl flex flex-col justify-between col-span-2 md:col-span-2 group relative overflow-hidden">
                                                <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-amber-500/10 transition-colors" />
                                                <div className="flex justify-between items-start mb-2 relative z-10">
                                                    <div className="flex gap-2 items-center text-neutral-400">
                                                        <DollarSign className="w-3.5 h-3.5 text-amber-500" />
                                                        <span className="text-[9px] uppercase tracking-widest font-black">Budget Cap</span>
                                                    </div>
                                                    <div className="text-[10px] font-mono text-neutral-400 bg-black/40 px-1.5 py-0.5 rounded border border-white/5">${currentSpend.toFixed(3)} / ${maxBudget.toFixed(2)}</div>
                                                </div>
                                                <div className="relative z-10 space-y-1.5">
                                                    <div className="flex items-end gap-1.5">
                                                        <div className="text-2xl font-black text-amber-400 tracking-tighter">${currentSpend.toFixed(3)}</div>
                                                        <div className="text-xs text-neutral-400 mb-1 font-bold">SPENT</div>
                                                    </div>
                                                    <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden shadow-inner flex">
                                                        <div className="h-full bg-gradient-to-r from-amber-500/50 to-rose-500/80 transition-all duration-1000" style={{ width: `${spendProgress}%` }} />
                                                    </div>
                                                </div>
                                            </div>
                                            {/* Loop Detections Row Extension */}
                                            <div className="p-3 bg-white/[0.05] border border-white/5 rounded-2xl flex items-center justify-between col-span-2 md:col-span-4">
                                                <div className="flex gap-3 items-center">
                                                    <div className="p-2 bg-indigo-500/10 rounded-lg">
                                                        <RefreshCw className="w-4 h-4 text-indigo-400" />
                                                    </div>
                                                    <div>
                                                        <div className="text-[10px] uppercase tracking-widest font-black text-neutral-400">Circuit Breaker: Loop Detections</div>
                                                        <div className="text-[11px] text-neutral-400 mt-0.5">Times the agent was halted from repeating identical flawed API requests.</div>
                                                    </div>
                                                </div>
                                                <div className="text-xl font-black text-indigo-400 bg-indigo-500/10 px-4 py-1.5 rounded-xl border border-indigo-500/20">{loopDetections}</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* --- 3. Access Control & Perimeter --- */}
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                                            <ShieldCheck className="w-4 h-4 text-amber-500" />
                                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Access Control & Perimeter</h3>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="border border-white/5 bg-white/[0.01] rounded-2xl p-5 space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Lock className="w-4 h-4 text-emerald-400" />
                                                        <span className="text-xs font-bold text-white tracking-widest uppercase">Linked Vault Secrets</span>
                                                    </div>
                                                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">{agentSecrets.length}</Badge>
                                                </div>
                                                <div className="space-y-2">
                                                    {agentSecrets.length > 0 ? agentSecrets.map(s => (
                                                        <div key={s.id} className="flex justify-between items-center bg-black/40 p-2 rounded-lg border border-white/5">
                                                            <span className="text-[11px] font-mono text-emerald-300">{s.secret_name}</span>
                                                            <span className="text-[9px] text-neutral-400">Accessible</span>
                                                        </div>
                                                    )) : (
                                                        <div className="text-center p-4 border border-dashed border-white/10 rounded-xl bg-black/20 text-neutral-600 text-[10px] uppercase font-bold tracking-widest">
                                                            No secrets linked
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            <div className="border border-white/5 bg-white/[0.01] rounded-2xl p-5 space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Ban className="w-4 h-4 text-rose-400" />
                                                        <span className="text-xs font-bold text-white tracking-widest uppercase">Active Policies</span>
                                                    </div>
                                                    <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20">{agentPolicies.length}</Badge>
                                                </div>
                                                <div className="space-y-2">
                                                    {agentPolicies.length > 0 ? agentPolicies.map(p => (
                                                        <div key={p.id} className="flex flex-col bg-black/40 p-2 rounded-lg border border-white/5 gap-1">
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[10px] font-mono font-bold text-rose-300 truncate pr-2">{p.toolName}</span>
                                                                <Badge variant="outline" className="text-[8px] h-4 leading-none bg-rose-500/10 text-rose-400 border-rose-500/20 uppercase tracking-widest">{p.ruleType}</Badge>
                                                            </div>
                                                            <span className="text-[9px] text-neutral-400 truncate">{p.condition}</span>
                                                        </div>
                                                    )) : (
                                                        <div className="text-center p-4 border border-dashed border-white/10 rounded-xl bg-black/20 text-neutral-600 text-[10px] uppercase font-bold tracking-widest">
                                                            No policies assigned
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* --- 4. Real-Time Activity Feed --- */}
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between border-b border-white/10 pb-2">
                                            <div className="flex items-center gap-2">
                                                <History className="w-4 h-4 text-purple-400" />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white">Real-Time Activity Feed</h3>
                                            </div>
                                            <Link href="/dashboard/forensics">
                                                <Button variant="ghost" size="sm" className="h-6 text-[9px] font-black uppercase tracking-widest text-neutral-400 hover:text-white hover:bg-white/5">
                                                    View All <ExternalLink className="w-3 h-3 ml-1" />
                                                </Button>
                                            </Link>
                                        </div>
                                        
                                        <div className="overflow-hidden border border-white/5 rounded-2xl bg-black/20">
                                            <table className="w-full text-left border-collapse">
                                                <thead>
                                                    <tr className="border-b border-white/5 bg-white/[0.05]">
                                                        <th className="px-4 py-3 text-[9px] font-black text-neutral-400 uppercase tracking-widest">Time</th>
                                                        <th className="px-4 py-3 text-[9px] font-black text-neutral-400 uppercase tracking-widest">Tool</th>
                                                        <th className="px-4 py-3 text-[9px] font-black text-neutral-400 uppercase tracking-widest">Parameters</th>
                                                        <th className="px-4 py-3 text-[9px] font-black text-neutral-400 uppercase tracking-widest text-right">Decision</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-white/[0.02]">
                                                    {auditLogs.length === 0 ? (
                                                        <tr><td colSpan={4} className="text-center py-6 text-neutral-600 italic text-xs">No activity recorded yet in this session window.</td></tr>
                                                    ) : (
                                                        auditLogs.map((log) => {
                                                            const isAllow = log.decision === 'ALLOW';
                                                            const isPaused = log.decision === 'PAUSED';
                                                            return (
                                                                <tr key={log.id} className="hover:bg-white/[0.05] transition-colors group">
                                                                    <td className="px-4 py-3 whitespace-nowrap text-[10px] font-mono text-neutral-400">
                                                                        {log.timestamp?.toDate?.().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                                    </td>
                                                                    <td className="px-4 py-3 whitespace-nowrap">
                                                                        <span className="text-[11px] font-bold text-neutral-300 font-mono tracking-tight">{log.toolName}</span>
                                                                    </td>
                                                                    <td className="px-4 py-3 text-[10px] text-neutral-400 font-mono truncate max-w-[180px]">
                                                                        {log.arguments ? log.arguments.replace(/[{}]/g, '').substring(0, 50) + (log.arguments.length > 50 ? '...' : '') : '{}'}
                                                                    </td>
                                                                    <td className="px-4 py-3 whitespace-nowrap text-right">
                                                                        <Badge className={`px-2 py-0 h-5 text-[9px] font-black uppercase tracking-widest ${
                                                                            isAllow ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                                                                            isPaused ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                                                                            'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                                                        }`}>
                                                                            {log.decision}
                                                                        </Badge>
                                                                    </td>
                                                                </tr>
                                                            );
                                                        })
                                                    )}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                {/* Shared Footer Controls */}
                                <div className="p-6 border-t border-white/5 bg-black z-10 flex items-center justify-between mt-auto">
                                    <div className="flex gap-4">
                                        <Button 
                                            variant="outline" 
                                            className={`h-11 rounded-xl px-6 border-white/10 font-bold transition-all shadow-[0_0_15px_rgba(255,255,255,0.02)] ${
                                                selectedAgent.status === 'active' 
                                                    ? 'text-amber-400 bg-amber-500/5 hover:bg-amber-500/10 hover:border-amber-500/20' 
                                                    : 'text-emerald-400 bg-emerald-500/5 hover:bg-emerald-500/10 hover:border-emerald-500/20'
                                            }`}
                                            onClick={() => toggleStatus(selectedAgent)}
                                        >
                                            {selectedAgent.status === 'active' ? (
                                                <><Lock className="w-4 h-4 mr-2" /> Suspend Operations</>
                                            ) : (
                                                <><Unlock className="w-4 h-4 mr-2" /> Resume Operations</>
                                            )}
                                        </Button>
                                        <Button 
                                            variant="outline"
                                            className={`h-11 rounded-xl px-6 font-bold transition-all ${
                                                copiedAgentId === selectedAgent.id 
                                                    ? 'bg-emerald-500 text-black border-emerald-500 hover:bg-emerald-500' 
                                                    : 'border-white/10 hover:bg-white/10 text-white'
                                            }`}
                                            onClick={() => handleDownloadEnv(selectedAgent)}
                                        >
                                            {copiedAgentId === selectedAgent.id ? <Check className="w-4 h-4 mr-2" /> : <Download className="w-4 h-4 mr-2" />}
                                            {copiedAgentId === selectedAgent.id ? "Copied!" : "Copy Config"}
                                        </Button>
                                    </div>
                                    <Button 
                                        variant="ghost" 
                                        className="h-11 rounded-xl px-6 text-rose-500 font-bold hover:bg-rose-500/10 uppercase tracking-widest text-[10px]"
                                        onClick={() => deleteAgent(selectedAgent.id)}
                                    >
                                        Revoke Entirely
                                    </Button>
                                </div>
                            </>
                        );
                    })()}
                </SheetContent>
            </Sheet>
        </div>
    );
}

function StatCard({ icon, label, value, subtext }: { icon: React.ReactNode, label: string, value: string, subtext: string }) {
    return (
        <motion.div 
            whileHover={{ y: -2 }}
            className="p-6 bg-neutral-900/50 backdrop-blur-xl border border-white/10 rounded-2xl shadow-xl space-y-3 relative overflow-hidden group"
        >
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-full -mr-12 -mt-12 blur-2xl group-hover:bg-white/10 transition-all" />
            <div className="flex items-center gap-3">
                <div className="p-2 bg-white/5 rounded-lg border border-white/5">
                    {icon}
                </div>
                <span className="text-sm font-bold text-neutral-400 tracking-tight uppercase">{label}</span>
            </div>
            <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-white tracking-tighter">{value}</span>
                <span className="text-[10px] text-neutral-400 font-bold tracking-widest uppercase">{subtext}</span>
            </div>
        </motion.div>
    );
}

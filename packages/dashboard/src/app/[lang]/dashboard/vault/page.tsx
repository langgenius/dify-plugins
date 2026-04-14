// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect } from "react";
import { Lock, Plus, RotateCcw, Trash2, Copy, Check, Shield, AlertCircle, Clock, Users, FileUp, X, Search } from "lucide-react";
import { auth, db } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import { collection, query, where, onSnapshot } from "firebase/firestore";
import { motion, AnimatePresence } from "framer-motion";
import { parseEnvFile, ParsedSecret } from "@/lib/parse-env";
import { TierBanner } from "@/components/TierBanner";

const API_BASE = "/api/v1/vault";

type Tab = "secrets" | "rules" | "log";

interface VaultSecret {
    id: string;
    secret_name: string;
    secret_type: "api_key" | "credentials" | "oauth" | "custom";
    description: string | null;
    expires_at: string | null;
    last_rotated_at: string;
    created_at: string;
    assigned_agents: string[];
}

interface VaultRule {
    id: string;
    agent_id: string;
    secret_name: string;
    allowed_tools: string[];
    max_uses_per_hour: number;
    requires_approval: boolean;
}

interface VaultLogEntry {
    id: number;
    agent_id: string;
    secret_name: string;
    tool_name: string;
    action: string;
    created_at: string;
}

const ACTION_ICON: Record<string, string> = {
    INJECTED: "✅",
    DENIED: "❌",
    RATE_LIMITED: "⚠️",
    EXPIRED: "⏰",
    NOT_FOUND: "❓",
    ROTATED: "🔄",
    DELETED: "🗑️",
};

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

export default function VaultPage() {
    const [user, authLoading] = useAuthState(auth);

    const [tab, setTab] = useState<Tab>("secrets");
    const [secrets, setSecrets] = useState<VaultSecret[]>([]);
    const [rules, setRules] = useState<VaultRule[]>([]);
    const [agents, setAgents] = useState<any[]>([]);
    const [log, setLog] = useState<VaultLogEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [showCreateSecret, setShowCreateSecret] = useState(false);
    const [showCreateRule, setShowCreateRule] = useState(false);
    const [showRotate, setShowRotate] = useState<string | null>(null);
    const [showImportEnv, setShowImportEnv] = useState(false);
    const [importData, setImportData] = useState<{ valid: ParsedSecret[], invalid: any[] } | null>(null);
    const [importResults, setImportResults] = useState<{ created: number, skipped: number, errors: number } | null>(null);
    const [copied, setCopied] = useState<string | null>(null);

    // Form state
    const [newSecretName, setNewSecretName] = useState("");
    const [newSecretType, setNewSecretType] = useState<VaultSecret["secret_type"]>("api_key");
    const [newSecretValue, setNewSecretValue] = useState("");
    const [templateFields, setTemplateFields] = useState<Record<string, string>>({});
    const [customFields, setCustomFields] = useState<{key: string, value: string}[]>([]);
    const [newSecretDesc, setNewSecretDesc] = useState("");
    const [newSecretExpiry, setNewSecretExpiry] = useState("");
    const [newSecretAgents, setNewSecretAgents] = useState<string[]>([]);
    const [newRuleAgent, setNewRuleAgent] = useState("");
    const [newRuleSecret, setNewRuleSecret] = useState("");
    const [newRuleTools, setNewRuleTools] = useState("");
    const [newRuleRate, setNewRuleRate] = useState("100");
    const [newRuleApproval, setNewRuleApproval] = useState(false);
    const [rotateValue, setRotateValue] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [agentSearch, setAgentSearch] = useState("");
    const [editingSecretId, setEditingSecretId] = useState<string | null>(null);
    const [showNextStepModal, setShowNextStepModal] = useState(false);
    const [dontShowNextStep, setDontShowNextStep] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem("suprawall_vault_onboarding_done");
        if (saved === "true") setDontShowNextStep(true);
    }, []);

    const getAuthHeaders = async (): Promise<Record<string, string>> => {
        if (!user) return {};
        const token = await user.getIdToken();
        return {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        };
    };

    const fetchSecrets = async () => {
        if (!user) return;
        const headers = await getAuthHeaders();
        const res = await fetch(`${API_BASE}/secrets?tenantId=${user.uid}`, { headers });
        if (res.ok) setSecrets(await res.json());
    };

    const fetchRules = async () => {
        if (!user) return;
        const headers = await getAuthHeaders();
        const res = await fetch(`${API_BASE}/rules?tenantId=${user.uid}`, { headers });
        if (res.ok) setRules(await res.json());
    };

    const fetchLog = async () => {
        if (!user) return;
        const headers = await getAuthHeaders();
        const res = await fetch(`${API_BASE}/log?tenantId=${user.uid}&limit=50`, { headers });
        if (res.ok) setLog(await res.json());
    };

    useEffect(() => {
        if (!user) return;

        const pollAgents = async () => {
            if (document.hidden) return; // Skip polling when tab is not visible
            try {
                const headers = await getAuthHeaders();
                const res = await fetch(`/api/v1/agents?tenantId=${user.uid}`, { headers });
                if (res.ok) {
                    const data = await res.json();
                    setAgents(data);
                }
            } catch (err) {
                console.error("Error polling agents:", err);
            }
        };

        pollAgents();
        const int = setInterval(pollAgents, 10000);

        // Pause/resume polling on visibility change
        const onVisibility = () => { if (!document.hidden) pollAgents(); };
        document.addEventListener("visibilitychange", onVisibility);

        if (tab === "secrets") fetchSecrets();
        else if (tab === "rules") { fetchRules(); fetchSecrets(); }
        else if (tab === "log") fetchLog();

        return () => { clearInterval(int); document.removeEventListener("visibilitychange", onVisibility); };
    }, [tab, user]);

    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <RotateCcw className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    const isSecretValueValid = () => {
        switch (newSecretType) {
            case "api_key":
                return !!newSecretValue;
            case "credentials":
                return !!templateFields.username && !!templateFields.password;
            case "oauth":
                return !!templateFields.access_token;
            case "custom":
                return customFields.length > 0 && customFields.every(f => !!f.key && !!f.value);
            default:
                return false;
        }
    };

    const copyToken = (secretName: string) => {
        const token = `$SUPRAWALL_VAULT_${secretName}`;
        navigator.clipboard.writeText(token);
        setCopied(secretName);
        setTimeout(() => setCopied(null), 2000);
    };

    const handleCreateOrUpdateSecret = async () => {
        if (!user?.uid) { setError("Not authenticated"); return; }
        setError(null);
        setLoading(true);
        try {
            let finalValue = newSecretValue;
            
            if (!editingSecretId) {
                if (newSecretType === "credentials") {
                    finalValue = JSON.stringify({
                        username: templateFields.username || "",
                        password: templateFields.password || ""
                    });
                } else if (newSecretType === "oauth") {
                    finalValue = JSON.stringify({
                        access_token: templateFields.access_token || "",
                        refresh_token: templateFields.refresh_token || "",
                        expires_at: templateFields.oauth_expiry || ""
                    });
                } else if (newSecretType === "custom") {
                    const obj: Record<string, string> = {};
                    customFields.forEach(f => { if (f.key) obj[f.key] = f.value; });
                    finalValue = JSON.stringify(obj);
                }
            }

            const headers = await getAuthHeaders();
            const url = editingSecretId ? `${API_BASE}/secrets/${editingSecretId}?tenantId=${user?.uid}` : `${API_BASE}/secrets`;
            const method = editingSecretId ? "PATCH" : "POST";
            
            const body: any = {
                tenantId: user?.uid,
                secretName: newSecretName,
                secretType: newSecretType,
                description: newSecretDesc || undefined,
                expiresAt: newSecretExpiry || undefined,
                assignedAgents: newSecretAgents,
            };

            if (!editingSecretId) {
                body.secretValue = finalValue;
            }

            const res = await fetch(url, {
                method,
                headers,
                body: JSON.stringify(body),
            });
            if (!res.ok) {
              try {
                const data = await res.json();
                setError(data.error + (data.message ? ": " + data.message : ""));
              } catch { setError(`Request failed (${res.status})`); }
              return;
            }
            setShowCreateSecret(false);
            setEditingSecretId(null);
            setNewSecretName(""); setNewSecretValue(""); setNewSecretDesc(""); setNewSecretExpiry("");
            setNewSecretAgents([]);
            await fetchSecrets();
            
            // Show onboarding modal for new secrets if not opted out
            if (!editingSecretId && !dontShowNextStep) {
                setShowNextStepModal(true);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteSecret = async (id: string) => {
        if (!user?.uid) { setError("Not authenticated"); return; }
        if (!confirm("Delete this secret? All associated access rules will also be removed.")) return;
        try {
            const headers = await getAuthHeaders();
            const res = await fetch(`${API_BASE}/secrets/${id}?tenantId=${user.uid}`, {
                method: "DELETE",
                headers
            });
            if (!res.ok) {
                try { const data = await res.json(); setError(data.error || `Delete failed (${res.status})`); }
                catch { setError(`Delete failed (${res.status})`); }
                return;
            }
            await fetchSecrets();
        } catch (err) {
            setError("Failed to delete secret");
            console.error("Delete secret error:", err);
        }
    };

    const handleRotate = async (id: string) => {
        if (!user?.uid) { setError("Not authenticated"); return; }
        setError(null);
        setLoading(true);
        try {
            const headers = await getAuthHeaders();
            const res = await fetch(`${API_BASE}/secrets/${id}/rotate`, {
                method: "PUT",
                headers,
                body: JSON.stringify({ tenantId: user?.uid, newValue: rotateValue }),
            });
            if (!res.ok) {
                try { const data = await res.json(); setError(data.error); }
                catch { setError(`Rotation failed (${res.status})`); }
                return;
            }
            setShowRotate(null);
            setRotateValue("");
            await fetchSecrets();
        } finally {
            setLoading(false);
        }
    };

    const handleCreateRule = async () => {
        if (!user?.uid) { setError("Not authenticated"); return; }
        setError(null);
        setLoading(true);
        try {
            const secret = secrets.find(s => s.secret_name === newRuleSecret);
            if (!secret) { setError("Select a valid secret"); return; }
            const headers = await getAuthHeaders();
            const res = await fetch(`${API_BASE}/rules`, {
                method: "POST",
                headers,
                body: JSON.stringify({
                    tenantId: user?.uid,
                    agentId: newRuleAgent,
                    secretId: secret.id,
                    allowedTools: newRuleTools.split(",").map(t => t.trim()).filter(Boolean),
                    maxUsesPerHour: Number(newRuleRate),
                    requiresApproval: newRuleApproval,
                }),
            });
            if (!res.ok) {
                try { const data = await res.json(); setError(data.error); }
                catch { setError(`Rule creation failed (${res.status})`); }
                return;
            }
            setShowCreateRule(false);
            setNewRuleAgent(""); setNewRuleSecret(""); setNewRuleTools(""); setNewRuleRate("100"); setNewRuleApproval(false);
            await fetchRules();
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteRule = async (id: string) => {
        if (!user?.uid) { setError("Not authenticated"); return; }
        try {
            const headers = await getAuthHeaders();
            const res = await fetch(`${API_BASE}/rules/${id}?tenantId=${user.uid}`, {
                method: "DELETE",
                headers
            });
            if (!res.ok) {
                try { const data = await res.json(); setError(data.error || `Delete failed (${res.status})`); }
                catch { setError(`Delete failed (${res.status})`); }
                return;
            }
            await fetchRules();
        } catch (err) {
            setError("Failed to delete rule");
            console.error("Delete rule error:", err);
        }
    };

    const handleBulkImport = async () => {
        if (!importData || !user) return;
        setLoading(true);
        setError(null);
        try {
            const headers = await getAuthHeaders();
            const res = await fetch(`${API_BASE}/secrets/bulk`, {
                method: "POST",
                headers,
                body: JSON.stringify({
                    tenantId: user.uid,
                    secrets: importData.valid.map(s => ({
                        secretName: s.key,
                        secretValue: s.value,
                        description: s.description
                    }))
                }),
            });
            const data = await res.json();
            if (!res.ok) {
                setError(data.error || "Bulk import failed");
                return;
            }
            setImportResults({
                created: data.created.length,
                skipped: data.skipped.length,
                errors: data.errors.length
            });
            // Don't close immediately so they can see results
            await fetchSecrets();
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleOnboardingPreference = (checked: boolean) => {
        setDontShowNextStep(checked);
        if (checked) {
            localStorage.setItem("suprawall_vault_onboarding_done", "true");
        } else {
            localStorage.removeItem("suprawall_vault_onboarding_done");
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[9px] font-black tracking-[0.2em] text-emerald-400 uppercase">Zero-Knowledge Storage</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <Lock className="w-5 h-5 text-emerald-400" />
                        <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Vault</h1>
                    </div>
                </div>
            </div>

            {/* Info banner */}
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-5 py-4">
                <p className="text-sm text-emerald-300">
                    Your AI agents never see real secrets. SupraWall injects credentials at runtime using{" "}
                    <code className="font-mono text-emerald-200">$SUPRAWALL_VAULT_*</code> tokens and scrubs all traces from responses.
                </p>
            </div>

            {/* Tier Upgrade Nudge */}
            <TierBanner
                tier="open_source"
                usages={[
                    { current: secrets.length, max: 3, label: 'Vault Secrets', upgradeFeature: '15 Secrets on Developer ($39)' },
                ]}
            />

            {/* Tabs */}
            <div className="flex gap-1 border-b border-emerald-500/10">
                {(["secrets", "rules", "log"] as Tab[]).map(t => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`px-4 py-2 text-[10px] font-black uppercase tracking-wider rounded-t-lg transition-all ${
                            tab === t
                                ? "bg-emerald-500/10 text-emerald-400 border-b-2 border-emerald-400"
                                : "text-neutral-400 hover:text-neutral-200"
                        }`}
                    >
                        {t === "log" ? "Access Log" : t === "rules" ? "Access Rules" : "Secrets"}
                    </button>
                ))}
            </div>

            {/* Secrets tab */}
            {tab === "secrets" && (
                <div className="space-y-4">
                    <div className="flex justify-end gap-3">
                        <button
                            onClick={() => { 
                                setShowImportEnv(true); 
                                setImportData(null); 
                                setImportResults(null);
                                setError(null); 
                            }}
                            className="flex items-center gap-2 px-4 py-2 border border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/10 text-emerald-400 text-sm font-medium rounded-lg transition-colors"
                        >
                            <FileUp className="w-4 h-4" /> Import .env
                        </button>
                        <button
                            onClick={() => { setShowCreateSecret(true); setError(null); }}
                            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" /> Create Secret
                        </button>
                    </div>

                    {secrets.length === 0 ? (
                        <div className="text-center py-16 text-neutral-400">No secrets stored yet.</div>
                    ) : (
                        <div className="rounded-xl border border-white/10 overflow-hidden">
                            <table className="w-full text-sm">
                                <thead className="bg-white/5 text-neutral-400 text-xs uppercase tracking-wider">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Secret Name</th>
                                        <th className="px-4 py-3 text-left">Type</th>
                                        <th className="px-4 py-3 text-left">Assigned Agents</th>
                                        <th className="px-4 py-3 text-left">Expires</th>
                                        <th className="px-4 py-3 text-left">Last Rotated</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {secrets.map(s => (
                                        <tr key={s.id} className="hover:bg-white/[0.05]">
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <Lock className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                                                    <span className="font-mono text-white text-xs">{s.secret_name}</span>
                                                </div>
                                                {s.description && <div className="text-[10px] text-neutral-400 mt-0.5 ml-5">{s.description}</div>}
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="px-2 py-0.5 rounded border border-white/10 bg-white/5 text-[9px] font-bold uppercase tracking-wider text-neutral-400">
                                                    {s.secret_type?.replace("_", " ") || "API KEY"}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex flex-wrap gap-1">
                                                    {s.assigned_agents?.length > 0 ? (
                                                        s.assigned_agents.map(aid => (
                                                            <span key={aid} className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono">
                                                                {agents.find(a => a.id === aid)?.name || aid.slice(0, 8)}
                                                            </span>
                                                        ))
                                                    ) : (
                                                        <span className="text-neutral-600 italic text-[10px]">Unrestricted (Global)</span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-neutral-400">
                                                {s.expires_at ? new Date(s.expires_at).toLocaleDateString() : "Never"}
                                            </td>
                                            <td className="px-4 py-3 text-neutral-400">{timeAgo(s.last_rotated_at)}</td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2 justify-end">
                                                    <button
                                                        onClick={() => copyToken(s.secret_name)}
                                                        title="Copy vault token"
                                                        className="flex items-center gap-1 px-2 py-1 text-xs text-neutral-400 hover:text-white bg-white/5 hover:bg-white/10 rounded transition-colors"
                                                    >
                                                        {copied === s.secret_name ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                                        Token
                                                    </button>
                                                     <button
                                                         onClick={() => {
                                                             setEditingSecretId(s.id);
                                                             setNewSecretName(s.secret_name);
                                                             setNewSecretType(s.secret_type || "api_key");
                                                             setNewSecretDesc(s.description || "");
                                                             setNewSecretExpiry(s.expires_at || "");
                                                             setNewSecretAgents(s.assigned_agents || []);
                                                             setShowCreateSecret(true);
                                                             setError(null);
                                                         }}
                                                         className="flex items-center gap-1 px-2 py-1 text-xs text-neutral-400 hover:text-emerald-400 bg-white/5 hover:bg-emerald-500/10 rounded transition-colors"
                                                     >
                                                         <Shield className="w-3 h-3" /> Edit
                                                     </button>
                                                     <button
                                                         onClick={() => { setShowRotate(s.id); setRotateValue(""); setError(null); }}
                                                        className="flex items-center gap-1 px-2 py-1 text-xs text-neutral-400 hover:text-yellow-400 bg-white/5 hover:bg-yellow-500/10 rounded transition-colors"
                                                    >
                                                        <RotateCcw className="w-3 h-3" /> Rotate
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteSecret(s.id)}
                                                        className="flex items-center gap-1 px-2 py-1 text-xs text-neutral-400 hover:text-red-400 bg-white/5 hover:bg-red-500/10 rounded transition-colors"
                                                    >
                                                        <Trash2 className="w-3 h-3" /> Delete
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Access Rules tab */}
            {tab === "rules" && (
                <div className="space-y-4">
                    <div className="flex justify-end">
                        <button
                            onClick={() => { setShowCreateRule(true); setError(null); }}
                            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" /> Create Rule
                        </button>
                    </div>

                    {rules.length === 0 ? (
                        <div className="text-center py-16 text-neutral-400">No access rules defined yet.</div>
                    ) : (
                        <div className="rounded-xl border border-white/10 overflow-hidden">
                            <table className="w-full text-sm">
                                <thead className="bg-white/5 text-neutral-400 text-xs uppercase tracking-wider">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Agent</th>
                                        <th className="px-4 py-3 text-left">Secret</th>
                                        <th className="px-4 py-3 text-left">Allowed Tools</th>
                                        <th className="px-4 py-3 text-left">Rate Limit</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {rules.map(r => (
                                        <tr key={r.id} className="hover:bg-white/[0.05]">
                                            <td className="px-4 py-3 font-mono text-xs text-white">
                                                {agents.find(a => a.id === r.agent_id)?.name || r.agent_id}
                                            </td>
                                            <td className="px-4 py-3 font-mono text-xs text-emerald-300">{r.secret_name}</td>
                                            <td className="px-4 py-3 text-neutral-400 text-xs">
                                                {r.allowed_tools.length > 0 ? r.allowed_tools.join(", ") : "All tools"}
                                            </td>
                                            <td className="px-4 py-3 text-neutral-400">{r.max_uses_per_hour}/hr</td>
                                            <td className="px-4 py-3 text-right">
                                                <button
                                                    onClick={() => handleDeleteRule(r.id)}
                                                    className="flex items-center gap-1 px-2 py-1 text-xs text-neutral-400 hover:text-red-400 bg-white/5 hover:bg-red-500/10 rounded transition-colors ml-auto"
                                                >
                                                    <Trash2 className="w-3 h-3" /> Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Access Log tab */}
            {tab === "log" && (
                <div className="space-y-4">
                    {log.length === 0 ? (
                        <div className="text-center py-16 text-neutral-400">No vault access events yet.</div>
                    ) : (
                        <div className="rounded-xl border border-white/10 overflow-hidden">
                            <table className="w-full text-sm">
                                <thead className="bg-white/5 text-neutral-400 text-xs uppercase tracking-wider">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Timestamp</th>
                                        <th className="px-4 py-3 text-left">Agent</th>
                                        <th className="px-4 py-3 text-left">Secret</th>
                                        <th className="px-4 py-3 text-left">Tool</th>
                                        <th className="px-4 py-3 text-left">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {log.map(entry => (
                                        <tr key={entry.id} className="hover:bg-white/[0.05]">
                                            <td className="px-4 py-3 text-neutral-400 text-xs whitespace-nowrap">
                                                {new Date(entry.created_at).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-3 font-mono text-xs text-white">{entry.agent_id}</td>
                                            <td className="px-4 py-3 font-mono text-xs text-emerald-300">{entry.secret_name}</td>
                                            <td className="px-4 py-3 font-mono text-xs text-neutral-400">{entry.tool_name}</td>
                                            <td className="px-4 py-3">
                                                <span className="text-base">{ACTION_ICON[entry.action] || "•"}</span>{" "}
                                                <span className="text-xs text-neutral-400">{entry.action}</span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Create Secret Modal */}
            {showCreateSecret && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                    <div className="w-full max-w-md bg-neutral-900 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
                        <h2 className="text-lg font-bold text-white flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Lock className="w-5 h-5 text-emerald-400" /> {editingSecretId ? "Update Secret Metadata" : "Create Secret"}
                            </div>
                            <button onClick={() => { setShowCreateSecret(false); setEditingSecretId(null); }} className="text-neutral-500 hover:text-white"><X className="w-5 h-5" /></button>
                        </h2>

                        {editingSecretId && (
                            <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400">
                                Note: You are updating the name, type, and assigned agents. To change the actual secret value (like a password), use the <strong>Rotate</strong> action in the main table.
                            </div>
                        )}

                        {error && (
                            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
                            </div>
                        )}

                        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-none">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs text-neutral-400 mb-1 block">Secret Name <span className="text-red-400">*</span></label>
                                    <input
                                        value={newSecretName}
                                        onChange={e => setNewSecretName(e.target.value.toUpperCase().replace(/[^A-Z0-9_]/g, ""))}
                                        placeholder="GITHUB_TOKEN"
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono placeholder-neutral-600 focus:outline-none focus:border-emerald-500"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-neutral-400 mb-1 block">Template / Type</label>
                                    <select
                                        value={newSecretType}
                                        onChange={e => setNewSecretType(e.target.value as any)}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                    >
                                        <option value="api_key">API Key (Single Field)</option>
                                        <option value="credentials">Credentials (User/Pass)</option>
                                        <option value="oauth">OAuth Token</option>
                                        <option value="custom">Custom JSON Object</option>
                                    </select>
                                </div>
                            </div>

                            {/* Dynamic Fields based on Type */}
                            {!editingSecretId && (
                                <div className="p-4 rounded-xl bg-black/40 border border-white/5 space-y-3">
                                    {newSecretType === "api_key" && (
                                        <div>
                                            <label className="text-xs text-neutral-400 mb-1 block">Secret Value / Key <span className="text-red-400">*</span></label>
                                            <input
                                                type="password"
                                                value={newSecretValue}
                                                onChange={e => setNewSecretValue(e.target.value)}
                                                placeholder="Paste value here..."
                                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-emerald-500"
                                            />
                                        </div>
                                    )}

                                    {newSecretType === "credentials" && (
                                        <div className="grid grid-cols-1 gap-3">
                                            <div>
                                                <label className="text-xs text-neutral-400 mb-1 block">Username</label>
                                                <input
                                                    value={templateFields.username || ""}
                                                    onChange={e => setTemplateFields({...templateFields, username: e.target.value})}
                                                    placeholder="admin"
                                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs text-neutral-400 mb-1 block">Password / Secret</label>
                                                <input
                                                    type="password"
                                                    value={templateFields.password || ""}
                                                    onChange={e => setTemplateFields({...templateFields, password: e.target.value})}
                                                    placeholder="••••••••"
                                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                                />
                                            </div>
                                        </div>
                                    )}

                                    {newSecretType === "oauth" && (
                                        <div className="space-y-3">
                                            <div>
                                                <label className="text-xs text-neutral-400 mb-1 block">Access Token</label>
                                                <input
                                                    type="password"
                                                    value={templateFields.access_token || ""}
                                                    onChange={e => setTemplateFields({...templateFields, access_token: e.target.value})}
                                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-emerald-500"
                                                />
                                            </div>
                                            <div className="grid grid-cols-2 gap-3">
                                                <div>
                                                    <label className="text-xs text-neutral-400 mb-1 block">Refresh Token</label>
                                                    <input
                                                        type="password"
                                                        value={templateFields.refresh_token || ""}
                                                        onChange={e => setTemplateFields({...templateFields, refresh_token: e.target.value})}
                                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-emerald-500"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-xs text-neutral-400 mb-1 block">Expires (optional)</label>
                                                    <input
                                                        value={templateFields.oauth_expiry || ""}
                                                        onChange={e => setTemplateFields({...templateFields, oauth_expiry: e.target.value})}
                                                        placeholder="3600"
                                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {newSecretType === "custom" && (
                                        <div className="space-y-2">
                                            {customFields.map((f, i) => (
                                                <div key={i} className="flex gap-2">
                                                    <input
                                                        placeholder="Field Name"
                                                        value={f.key}
                                                        onChange={e => {
                                                            const next = [...customFields];
                                                            next[i].key = e.target.value;
                                                            setCustomFields(next);
                                                        }}
                                                        className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none focus:border-emerald-500"
                                                    />
                                                    <input
                                                        type={f.key.toLowerCase().includes("key") || f.key.toLowerCase().includes("pass") ? "password" : "text"}
                                                        placeholder="Value"
                                                        value={f.value}
                                                        onChange={e => {
                                                            const next = [...customFields];
                                                            next[i].value = e.target.value;
                                                            setCustomFields(next);
                                                        }}
                                                        className="flex-[2] bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none focus:border-emerald-500"
                                                    />
                                                    <button onClick={() => setCustomFields(customFields.filter((_, idx) => idx !== i))} className="text-red-400 p-1">
                                                        <Trash2 className="w-3 h-3" />
                                                    </button>
                                                </div>
                                            ))}
                                            <button
                                                onClick={() => setCustomFields([...customFields, {key: "", value: ""}])}
                                                className="text-[10px] text-emerald-400 font-bold uppercase hover:bg-emerald-500/10 px-2 py-1 rounded transition-colors"
                                            >
                                                + Add Field
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div>
                                <label className="text-xs text-neutral-400 mb-1 block">Description</label>
                                <input
                                    value={newSecretDesc}
                                    onChange={e => setNewSecretDesc(e.target.value)}
                                    placeholder="Purpose of this secret..."
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs text-neutral-400 mb-1 block">Expires At</label>
                                    <input
                                        type="datetime-local"
                                        value={newSecretExpiry}
                                        onChange={e => setNewSecretExpiry(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-neutral-400 mb-1 block">Scoped Agents</label>
                                    <div className="space-y-2">
                                        <div className="relative">
                                            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-neutral-500" />
                                            <input 
                                                type="text"
                                                placeholder="Search agents..."
                                                value={agentSearch}
                                                onChange={(e) => setAgentSearch(e.target.value)}
                                                className="w-full bg-black/40 border border-white/10 rounded-lg pl-8 pr-3 py-2 text-[11px] text-white focus:outline-none focus:border-emerald-500"
                                            />
                                        </div>
                                        <div className="flex flex-wrap gap-1 p-2 rounded-lg bg-black/20 border border-white/5 max-h-[120px] overflow-y-auto scrollbar-thin scrollbar-thumb-emerald-500/20">
                                            {agents.filter(a => a.name.toLowerCase().includes(agentSearch.toLowerCase())).map(a => (
                                                <button
                                                    key={a.id}
                                                    type="button"
                                                    onClick={() => {
                                                        setNewSecretAgents(prev => 
                                                            prev.includes(a.id) ? prev.filter(id => id !== a.id) : [...prev, a.id]
                                                        );
                                                    }}
                                                    className={`px-2 py-1 rounded text-[10px] font-mono border transition-all flex items-center gap-1.5 ${
                                                        newSecretAgents.includes(a.id)
                                                            ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-400"
                                                            : "bg-white/5 border-white/10 text-neutral-500 hover:border-white/20"
                                                    }`}
                                                >
                                                    <span className={`w-1.5 h-1.5 rounded-full ${newSecretAgents.includes(a.id) ? "bg-emerald-500" : "bg-neutral-700"}`} />
                                                    {a.name}
                                                </button>
                                            ))}
                                            {agents.length === 0 && <span className="text-[9px] text-neutral-600 p-2">No agents found</span>}
                                            {agents.length > 0 && agents.filter(a => a.name.toLowerCase().includes(agentSearch.toLowerCase())).length === 0 && (
                                                <span className="text-[9px] text-neutral-600 p-2">No matches for "{agentSearch}"</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-3 pt-2">
                                <button
                                    onClick={() => { setShowCreateSecret(false); setEditingSecretId(null); }}
                                    className="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 text-white text-xs font-black uppercase tracking-widest rounded-xl transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreateOrUpdateSecret}
                                    disabled={loading || !newSecretName || (!editingSecretId && !isSecretValueValid())}
                                    className="flex-1 px-4 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-black uppercase tracking-widest rounded-xl transition-colors shadow-lg shadow-emerald-900/20"
                                >
                                    {loading ? "Processing..." : editingSecretId ? "Update Secret" : "Create Secret"}
                                </button>
                            </div>
                        </div>

                        {newSecretName && (
                            <div className="rounded-lg bg-black/40 border border-white/10 p-3">
                                <p className="text-xs text-neutral-400 mb-1">Agent token (safe to share):</p>
                                <div className="flex items-center gap-2">
                                    <code className="text-xs text-emerald-300 font-mono flex-1 break-all">
                                        $SUPRAWALL_VAULT_{newSecretName}
                                    </code>
                                    <button
                                        onClick={() => copyToken(newSecretName)}
                                        className="text-neutral-400 hover:text-white"
                                    >
                                        {copied === newSecretName ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Rotate Modal */}
            {showRotate && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                    <div className="w-full max-w-sm bg-neutral-900 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <RotateCcw className="w-5 h-5 text-yellow-400" /> Rotate Secret
                        </h2>
                        {error && (
                            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2">
                                <AlertCircle className="w-4 h-4" /> {error}
                            </div>
                        )}
                        <div>
                            <label className="text-xs text-neutral-400 mb-1 block">New Value</label>
                            <input
                                type="password"
                                value={rotateValue}
                                onChange={e => setRotateValue(e.target.value)}
                                placeholder="New secret value"
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono placeholder-neutral-600 focus:outline-none focus:border-yellow-500"
                            />
                        </div>
                        <div className="flex gap-3">
                            <button onClick={() => { setShowRotate(null); setError(null); }}
                                className="flex-1 px-4 py-2 text-sm text-neutral-400 hover:text-white bg-white/5 rounded-lg transition-colors">
                                Cancel
                            </button>
                            <button onClick={() => handleRotate(showRotate!)} disabled={loading || !rotateValue}
                                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 rounded-lg transition-colors">
                                {loading ? "Rotating…" : "Rotate"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Create Rule Modal */}
            {showCreateRule && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                    <div className="w-full max-w-md bg-neutral-900 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                            <Shield className="w-5 h-5 text-emerald-400" /> Create Access Rule
                        </h2>
                        {error && (
                            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2">
                                <AlertCircle className="w-4 h-4" /> {error}
                            </div>
                        )}
                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-neutral-400 mb-1 block">Agent <span className="text-red-400">*</span></label>
                                <select value={newRuleAgent} onChange={e => setNewRuleAgent(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
                                    <option value="">Select agent…</option>
                                    {agents.map(a => <option key={a.id} value={a.id}>{a.name} ({a.id.slice(0, 8)})</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="text-xs text-neutral-400 mb-1 block">Secret <span className="text-red-400">*</span></label>
                                <select value={newRuleSecret} onChange={e => setNewRuleSecret(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500">
                                    <option value="">Select secret…</option>
                                    {secrets.map(s => <option key={s.id} value={s.secret_name}>{s.secret_name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="text-xs text-neutral-400 mb-1 block">Allowed Tools (comma-separated, empty = all)</label>
                                <input value={newRuleTools} onChange={e => setNewRuleTools(e.target.value)}
                                    placeholder="process_payment, refund_payment"
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-emerald-500" />
                            </div>
                            <div>
                                <label className="text-xs text-neutral-400 mb-1 block">Rate Limit (uses/hour)</label>
                                <input type="number" value={newRuleRate} onChange={e => setNewRuleRate(e.target.value)} min="1"
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500" />
                            </div>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" checked={newRuleApproval} onChange={e => setNewRuleApproval(e.target.checked)}
                                    className="rounded border-white/20 bg-white/5 text-emerald-500" />
                                <span className="text-sm text-neutral-300">Require human approval before injecting</span>
                            </label>
                        </div>
                        <div className="flex gap-3 pt-2">
                            <button onClick={() => { setShowCreateRule(false); setError(null); }}
                                className="flex-1 px-4 py-2 text-sm text-neutral-400 hover:text-white bg-white/5 rounded-lg transition-colors">
                                Cancel
                            </button>
                            <button onClick={handleCreateRule} disabled={loading || !newRuleAgent || !newRuleSecret}
                                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-lg transition-colors">
                                {loading ? "Creating…" : "Create Rule"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {/* Import .env Modal */}
            {showImportEnv && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                    <div className="w-full max-w-2xl bg-neutral-900 border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <FileUp className="w-5 h-5 text-emerald-400" /> Bulk Import .env
                            </h2>
                            <button onClick={() => setShowImportEnv(false)} className="text-neutral-500 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
                            </div>
                        )}

                        {importResults ? (
                            <div className="space-y-6 py-4">
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-center">
                                        <div className="text-2xl font-black text-emerald-400">{importResults.created}</div>
                                        <div className="text-[10px] text-emerald-500/70 uppercase tracking-widest font-bold">Created</div>
                                    </div>
                                    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-center">
                                        <div className="text-2xl font-black text-yellow-400">{importResults.skipped}</div>
                                        <div className="text-[10px] text-yellow-500/70 uppercase tracking-widest font-bold">Skipped</div>
                                    </div>
                                    <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-center">
                                        <div className="text-2xl font-black text-red-400">{importResults.errors}</div>
                                        <div className="text-[10px] text-red-500/70 uppercase tracking-widest font-bold">Errors</div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowImportEnv(false)}
                                    className="w-full py-3 bg-white text-black font-black uppercase tracking-widest rounded-xl hover:bg-neutral-200 transition-all text-sm"
                                >
                                    Done
                                </button>
                            </div>
                        ) : !importData ? (
                            <div 
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={(e) => {
                                    e.preventDefault();
                                    const file = e.dataTransfer.files[0];
                                    if (file) {
                                        const reader = new FileReader();
                                        reader.onload = (ev) => {
                                            const res = parseEnvFile(ev.target?.result as string);
                                            setImportData(res);
                                        };
                                        reader.readAsText(file);
                                    }
                                }}
                                className="border-2 border-dashed border-emerald-500/20 bg-emerald-500/5 rounded-2xl py-20 flex flex-col items-center justify-center space-y-4 hover:bg-emerald-500/10 transition-colors cursor-pointer"
                                onClick={() => {
                                    const input = document.createElement('input');
                                    input.type = 'file';
                                    input.onchange = (e) => {
                                        const file = (e.target as any).files[0];
                                        if (file) {
                                            const reader = new FileReader();
                                            reader.onload = (ev) => {
                                                const res = parseEnvFile(ev.target?.result as string);
                                                setImportData(res);
                                            };
                                            reader.readAsText(file);
                                        }
                                    };
                                    input.click();
                                }}
                            >
                                <div className="p-4 bg-emerald-500/10 rounded-2xl">
                                    <FileUp className="w-8 h-8 text-emerald-400" />
                                </div>
                                <div className="text-center">
                                    <p className="text-white font-bold">Click or drag `.env` file to upload</p>
                                    <p className="text-neutral-500 text-xs">Parsing happens entirely in your browser</p>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="max-h-[300px] overflow-y-auto border border-white/5 rounded-xl bg-black/40">
                                    <table className="w-full text-[11px]">
                                        <thead className="sticky top-0 bg-neutral-900 border-b border-white/10">
                                            <tr>
                                                <th className="px-4 py-2 text-left text-neutral-500 uppercase">Key</th>
                                                <th className="px-4 py-2 text-left text-neutral-500 uppercase">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {importData.valid.map((s, i) => (
                                                <tr key={i}>
                                                    <td className="px-4 py-2 font-mono text-emerald-400">{s.key}</td>
                                                    <td className="px-4 py-2 text-emerald-500/70 font-bold uppercase text-[9px]">Ready</td>
                                                </tr>
                                            ))}
                                            {importData.invalid.map((s, i) => (
                                                <tr key={i}>
                                                    <td className="px-4 py-2 font-mono text-rose-400">{s.key || "UNPARSEABLE"}</td>
                                                    <td className="px-4 py-2 text-rose-500/70 font-bold uppercase text-[9px]">{s.reason}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>

                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setImportData(null)}
                                        className="flex-1 px-4 py-2 text-sm text-neutral-400 hover:text-white bg-white/5 rounded-lg transition-colors"
                                    >
                                        Back
                                    </button>
                                    <button
                                        onClick={handleBulkImport}
                                        disabled={loading || importData.valid.length === 0}
                                        className="flex-[2] px-4 py-2 text-sm font-black uppercase tracking-widest text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-lg transition-colors shadow-2xl"
                                    >
                                        {loading ? "Importing…" : `Import ${importData.valid.length} Secrets`}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Next Steps Onboarding Modal */}
            <AnimatePresence>
                {showNextStepModal && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-md p-4"
                    >
                        <motion.div 
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="w-full max-w-lg bg-neutral-900 border border-emerald-500/30 rounded-3xl p-8 shadow-[0_0_50px_-12px_rgba(16,185,129,0.3)] space-y-6 relative overflow-hidden"
                        >
                            {/* Decorative background flare */}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 blur-[100px] -mr-32 -mt-32 pointer-events-none" />
                            
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                                    <Shield className="w-8 h-8 text-emerald-400" />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-black text-white tracking-tight leading-tight uppercase italic">Secret created! <br/><span className="text-emerald-400">What's next?</span></h2>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <p className="text-neutral-300 leading-relaxed text-sm">
                                    In our <span className="text-white font-bold">Zero-Trust architecture</span>, simply creating a secret isn't enough. Your agents are currently blocked from "asking" for it until you authorize them.
                                </p>
                                
                                <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-3">
                                    <div className="flex items-start gap-3">
                                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] font-black text-emerald-400 border border-emerald-500/30">1</div>
                                        <p className="text-xs text-neutral-400"><span className="text-emerald-300 font-bold uppercase tracking-wider">Authorize</span>: Go to the Access Rules tab.</p>
                                    </div>
                                    <div className="flex items-start gap-3">
                                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] font-black text-emerald-400 border border-emerald-500/30">2</div>
                                        <p className="text-xs text-neutral-400"><span className="text-emerald-300 font-bold uppercase tracking-wider">Map</span>: Connect this secret to a specific agent and tool.</p>
                                    </div>
                                    <div className="flex items-start gap-3">
                                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] font-black text-emerald-400 border border-emerald-500/30">3</div>
                                        <p className="text-xs text-neutral-400"><span className="text-emerald-300 font-bold uppercase tracking-wider">Lock</span>: Set rate limits to prevent accidental data leaks.</p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex flex-col gap-4">
                                <button
                                    onClick={() => {
                                        setTab("rules");
                                        setShowNextStepModal(false);
                                    }}
                                    className="w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-black font-black uppercase tracking-widest rounded-2xl transition-all shadow-lg shadow-emerald-500/20 text-sm flex items-center justify-center gap-2 group"
                                >
                                    Take me to Access Rules
                                    <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform" />
                                </button>
                                
                                <div className="flex items-center justify-between px-2">
                                    <label className="flex items-center gap-2 cursor-pointer group">
                                        <input 
                                            type="checkbox" 
                                            checked={dontShowNextStep}
                                            onChange={(e) => toggleOnboardingPreference(e.target.checked)}
                                            className="w-4 h-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500/50" 
                                        />
                                        <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 group-hover:text-neutral-300 transition-colors">Don't show this again</span>
                                    </label>
                                    <button 
                                        onClick={() => setShowNextStepModal(false)}
                                        className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 hover:text-white transition-colors"
                                    >
                                        I'll do it later
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

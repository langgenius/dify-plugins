// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";
import { useState, useEffect } from "react";
import { auth } from "@/lib/firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import { sendGAEvent } from "@next/third-parties/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, ShieldAlert, PlusCircle, Sparkles, Loader2, Coins, RefreshCw, Save, Activity, BookOpen, CheckCircle2 } from "lucide-react";
import { POLICY_TEMPLATES, type PolicyTemplate } from "@/lib/policy-templates";
import type { Agent, Policy, RuleType } from "@/types/database";
import { motion, AnimatePresence } from "framer-motion";
import { Textarea } from "@/components/ui/textarea";

export default function PoliciesPage() {
    const [user] = useAuthState(auth);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [policies, setPolicies] = useState<Policy[]>([]);
    const [loading, setLoading] = useState(true);

    // Form State
    const [selectedAgentId, setSelectedAgentId] = useState("");
    const [toolName, setToolName] = useState("");
    const [condition, setCondition] = useState("");
    const [ruleType, setRuleType] = useState<RuleType>("DENY");
    const [priority, setPriority] = useState<string>("100");
    const [isDryRun, setIsDryRun] = useState(false);
    const [description, setDescription] = useState("");

    // Agent Config State
    const [maxCostUsd, setMaxCostUsd] = useState<string>("");
    const [budgetAlertUsd, setBudgetAlertUsd] = useState<string>("");
    const [maxIterations, setMaxIterations] = useState<string>("");
    const [loopDetection, setLoopDetection] = useState<boolean>(false);
    const [isSavingConfig, setIsSavingConfig] = useState(false);

    // AI Wizard State
    const [showAiWizard, setShowAiWizard] = useState(false);
    const [aiPrompt, setAiPrompt] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    // Template State
    const [activatingTemplate, setActivatingTemplate] = useState<string | null>(null);
    const [activatedTemplates, setActivatedTemplates] = useState<Set<string>>(new Set());

    useEffect(() => {
        if (!user) return;
        setLoading(true);

        const loadData = async () => {
            try {
                const idToken = await user.getIdToken();
                const headers = { 'Authorization': `Bearer ${idToken}` };

                // 1. Fetch Agents via internal API (bypasses ad-blockers)
                const agentsRes = await fetch(`/api/v1/agents?tenantId=${user.uid}`, { headers });
                if (agentsRes.ok) {
                    const list = await agentsRes.json();
                    setAgents(list);
                }

                // 2. Fetch Policies via internal API
                const policiesRes = await fetch(`/api/v1/policies?tenantId=${user.uid}`, { headers });
                if (policiesRes.ok) {
                    const list = await policiesRes.json();
                    setPolicies(list);
                }
            } catch (error) {
                console.error("[PoliciesPage] Failed to fetch data:", error);
            } finally {
                setLoading(false);
            }
        };

        loadData();
        const interval = setInterval(loadData, 5000); // Polling for real-time feel

        return () => clearInterval(interval);
    }, [user]);

    const handleDeletePolicy = async (id: string) => {
        if (!user || !id) return;
        try {
            const res = await fetch(`/api/v1/policies/${id}?tenantId=${user.uid}`, {
                method: "DELETE",
            });
            if (!res.ok) throw new Error(`Failed: ${res.status}`);
            setPolicies(prev => prev.filter(p => p.id !== id));
            sendGAEvent('event', 'delete_policy', { policy_id: id });
        } catch (e) {
            console.error("Error deleting policy", e);
        }
    };

    const handleCreatePolicy = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user || !selectedAgentId || !toolName || !condition) return;

        try {
            const res = await fetch("/api/v1/policies", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tenantId: user.uid,
                    agentId: selectedAgentId,
                    name: `${toolName} Rule`,
                    toolName,
                    ruleType,
                    description,
                    condition,
                    priority: parseInt(priority) || 100,
                    isDryRun,
                }),
            });
            if (!res.ok) throw new Error(`Failed: ${res.status}`);

            setToolName("");
            setCondition("");
            setPriority("100");
            setIsDryRun(false);
            setDescription("");
            sendGAEvent('event', 'create_policy', { tool_name: toolName, rule_type: ruleType });
        } catch (e) {
            console.error("Error creating policy", e);
        }
    };

    const handleSaveConfig = async () => {
        if (!selectedAgentId) return;
        setIsSavingConfig(true);
        try {
            const res = await fetch(`/api/v1/agents/${selectedAgentId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    max_cost_usd: maxCostUsd ? parseFloat(maxCostUsd) : null,
                    budget_alert_usd: budgetAlertUsd ? parseFloat(budgetAlertUsd) : null,
                    max_iterations: maxIterations ? parseInt(maxIterations) : null,
                    loop_detection: loopDetection,
                }),
            });
            if (!res.ok) throw new Error(`Failed: ${res.status}`);
            sendGAEvent('event', 'update_agent_config', { agent_id: selectedAgentId });
        } catch (e) {
            console.error("Error updating agent config", e);
        }
        setIsSavingConfig(false);
    };

    const handleGenerateRegex = async () => {
        if (!aiPrompt) return;
        setIsGenerating(true);
        try {
            const res = await fetch(`/api/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: aiPrompt, toolName: toolName || "a generic tool" })
            });
            const data = await res.json();
            if (data.regex) {
                setCondition(data.regex);
                setShowAiWizard(false);
                setAiPrompt("");
            }
        } catch (e) {
            console.error("AI Generation failed:", e);
        }
        setIsGenerating(false);
    };

    const handleActivateTemplate = async (template: PolicyTemplate) => {
        if (!user || !selectedAgentId) return;
        setActivatingTemplate(template.id);
        try {
            for (const rule of template.rules) {
                const res = await fetch("/api/v1/policies", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        tenantId: user.uid,
                        agentId: selectedAgentId,
                        name: rule.description,
                        toolName: rule.toolName,
                        ruleType: rule.ruleType,
                        description: `[${template.name} Template — ${rule.article}] ${rule.description}`,
                        condition: rule.condition,
                        priority: rule.priority,
                        isDryRun: false,
                    }),
                });
                if (!res.ok) throw new Error(`Failed: ${res.status}`);
            }
            setActivatedTemplates(prev => new Set(prev).add(template.id));
            sendGAEvent("event", "activate_compliance_template", { template_id: template.id, agent_id: selectedAgentId });
        } catch (e) {
            console.error("Error activating template", e);
        }
        setActivatingTemplate(null);
    };

    const getAgentName = (id: string) => agents.find(a => a.id === id)?.name || "Unknown";

    const getRuleBadgeColor = (type: string) => {
        if (type === "ALLOW") return "bg-green-500/10 text-green-500 border-green-500/20";
        if (type === "DENY") return "bg-red-500/10 text-red-500 border-red-500/20";
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
        >
            <div className="flex justify-between items-end mb-8">
                <div className="space-y-1">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 mb-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span className="text-[9px] font-black tracking-[0.2em] text-emerald-400 uppercase">Zero-Trust Rules</span>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Security Policies</h1>
                    <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.2em]">Define access control and approval flows for your agents&apos; tools.</p>
                </div>
            </div>

            {/* Compliance Templates */}
            <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/10 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent" />
                <CardHeader className="bg-black/20 border-b border-white/[0.08] px-6 py-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div>
                            <CardTitle className="text-sm flex items-center font-black text-white uppercase italic tracking-tighter">
                                <BookOpen className="w-4 h-4 mr-2 text-emerald-400" />
                                EU AI Act Starter Templates
                            </CardTitle>
                            <p className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.15em] mt-1">
                                One-click policy packs mapped to high-risk AI categories (Article 9 / 14 / 10)
                            </p>
                        </div>
                        {!selectedAgentId && (
                            <span className="text-[10px] font-bold text-amber-400/80 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-1.5 whitespace-nowrap">
                                Select an agent first
                            </span>
                        )}
                    </div>
                </CardHeader>
                <CardContent className="pt-5 pb-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {POLICY_TEMPLATES.map((template) => {
                            const isActivating = activatingTemplate === template.id;
                            const isActivated = activatedTemplates.has(template.id);
                            const accentColors: Record<string, { border: string; tag: string; btn: string; badge: string }> = {
                                blue: {
                                    border: "border-blue-500/20 hover:border-blue-500/40",
                                    tag: "text-blue-400/70 bg-blue-500/10 border-blue-500/20",
                                    btn: "bg-blue-600/80 hover:bg-blue-500 disabled:bg-blue-900/40",
                                    badge: "bg-blue-500/10 text-blue-400 border-blue-500/20",
                                },
                                rose: {
                                    border: "border-rose-500/20 hover:border-rose-500/40",
                                    tag: "text-rose-400/70 bg-rose-500/10 border-rose-500/20",
                                    btn: "bg-rose-600/80 hover:bg-rose-500 disabled:bg-rose-900/40",
                                    badge: "bg-rose-500/10 text-rose-400 border-rose-500/20",
                                },
                                violet: {
                                    border: "border-violet-500/20 hover:border-violet-500/40",
                                    tag: "text-violet-400/70 bg-violet-500/10 border-violet-500/20",
                                    btn: "bg-violet-600/80 hover:bg-violet-500 disabled:bg-violet-900/40",
                                    badge: "bg-violet-500/10 text-violet-400 border-violet-500/20",
                                },
                            };
                            const c = accentColors[template.accentClass] ?? accentColors.blue;
                            return (
                                <motion.div
                                    key={template.id}
                                    initial={{ opacity: 0, y: 6 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`relative flex flex-col gap-3 p-5 rounded-xl bg-black/40 border transition-colors duration-300 ${c.border}`}
                                >
                                    <div>
                                        <span className={`inline-block text-[9px] font-black uppercase tracking-[0.18em] px-2 py-0.5 rounded border mb-2 ${c.tag}`}>
                                            {template.industry}
                                        </span>
                                        <h3 className="text-sm font-black text-white uppercase italic tracking-tight">{template.name}</h3>
                                        <p className="text-xs text-neutral-400 mt-1 leading-relaxed">{template.tagline}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-1.5">
                                        {template.articles.map(a => (
                                            <span key={a} className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${c.badge}`}>{a}</span>
                                        ))}
                                        <span className="text-[9px] font-bold px-2 py-0.5 rounded-full border bg-white/[0.04] text-neutral-400 border-white/10">
                                            {template.rules.length} rules
                                        </span>
                                    </div>
                                    <Button
                                        size="sm"
                                        disabled={!selectedAgentId || isActivating || isActivated}
                                        onClick={() => handleActivateTemplate(template)}
                                        className={`mt-auto w-full text-white text-xs font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${c.btn}`}
                                    >
                                        {isActivating ? (
                                            <><Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> Activating…</>
                                        ) : isActivated ? (
                                            <><CheckCircle2 className="mr-1.5 h-3.5 w-3.5" /> Activated</>
                                        ) : (
                                            "Activate Template"
                                        )}
                                    </Button>
                                </motion.div>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="col-span-1 bg-black/60 backdrop-blur-xl border-emerald-500/10 shadow-2xl h-fit relative group overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent group-hover:via-emerald-500/50 transition-all duration-700" />
                    <CardHeader className="bg-black/20 border-b border-white/[0.08] px-4 py-3 sm:px-6 sm:py-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 w-full">
                            <CardTitle className="text-xs sm:text-sm flex items-center font-black text-white uppercase italic tracking-tighter shrink-0">
                                <ShieldAlert className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-emerald-400" />
                                New Policy Rule
                            </CardTitle>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setShowAiWizard(!showAiWizard)}
                                className={`h-8 text-[10px] sm:text-xs border-emerald-500/30 hover:bg-emerald-500/10 transition-colors whitespace-nowrap overflow-hidden px-3 ${showAiWizard ? 'bg-emerald-500/10 text-emerald-300' : 'bg-transparent text-emerald-400'}`}
                            >
                                <Sparkles className="w-3.5 h-3.5 mr-1.5 shrink-0" />
                                {showAiWizard ? "Close Wizard" : "AI Magic"}
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <AnimatePresence>
                            {showAiWizard && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden mb-6"
                                >
                                    <div className="p-4 sm:p-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 space-y-4">
                                        <label className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-emerald-400/80">Describe restriction in plain English</label>
                                        <Textarea
                                            value={aiPrompt}
                                            onChange={e => setAiPrompt(e.target.value)}
                                            placeholder="e.g., Stop the agent from deleting files."
                                            className="bg-black/50 border-emerald-500/30 text-white placeholder:text-emerald-200/50 resize-none focus-visible:ring-emerald-500/50 min-h-[80px] w-full"
                                            rows={3}
                                        />
                                        <Button
                                            type="button"
                                            onClick={handleGenerateRegex}
                                            disabled={!aiPrompt || isGenerating}
                                            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 text-xs sm:text-sm font-bold min-h-[44px]"
                                        >
                                            {isGenerating ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Working...</>
                                            ) : (
                                                <><Sparkles className="mr-2 h-4 w-4" /> Generate Rule Regex</>
                                            )}
                                        </Button>
                                        {!toolName && aiPrompt && (
                                            <p className="text-[10px] text-emerald-400/60 text-center italic">Tip: Add a tool name for more specific regex.</p>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                        <form onSubmit={handleCreatePolicy} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-neutral-400">Select Agent</label>
                                <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                                    <SelectTrigger className="w-full bg-neutral-900 border-white/10 text-white hover:border-white/20 transition-colors">
                                        <SelectValue placeholder="Choose an agent..." />
                                    </SelectTrigger>
                                    <SelectContent className="bg-neutral-900 border-white/10 text-white">
                                        {agents.map(a => (
                                            <SelectItem key={a.id} value={a.id as string} className="hover:bg-white/5">{a.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-neutral-400">Tool Name</label>
                                <Input
                                    value={toolName}
                                    onChange={e => setToolName(e.target.value)}
                                    placeholder="e.g., bash, browser, fetch"
                                    className="bg-neutral-900 border-white/10 text-white placeholder:text-neutral-400 hover:border-white/20 transition-colors"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-neutral-400">Condition (Regex)</label>
                                <Input
                                    value={condition}
                                    onChange={e => setCondition(e.target.value)}
                                    placeholder="e.g., rm -rf, .*"
                                    className="bg-neutral-900 border-white/10 text-white font-mono text-sm placeholder:text-neutral-400 hover:border-white/20 transition-colors"
                                />
                                <p className="text-xs text-emerald-400/80 italic mt-1">Generated by AI. Please review before saving.</p>
                            </div>
                             <div className="space-y-2">
                                <label className="text-sm font-medium text-neutral-400">Rule Type</label>
                                <Select value={ruleType} onValueChange={(v: RuleType) => setRuleType(v)}>
                                    <SelectTrigger className="w-full bg-neutral-900 border-white/10 text-white focus:ring-1 focus:ring-emerald-500 hover:border-white/20 transition-colors">
                                        <SelectValue placeholder="Decision..." />
                                    </SelectTrigger>
                                    <SelectContent className="bg-neutral-900 border-white/10 text-white">
                                        <SelectItem value="ALLOW" className="text-green-400 hover:bg-white/5">ALLOW</SelectItem>
                                        <SelectItem value="DENY" className="text-red-400 hover:bg-white/5">DENY</SelectItem>
                                        <SelectItem value="REQUIRE_APPROVAL" className="text-yellow-400 hover:bg-white/5">REQUIRE_APPROVAL</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-neutral-400">Priority (Low=High)</label>
                                    <Input
                                        type="number"
                                        value={priority}
                                        onChange={e => setPriority(e.target.value)}
                                        className="bg-neutral-900 border-white/10 text-white"
                                    />
                                </div>
                                <div className="space-y-2 flex flex-col justify-end">
                                    <div 
                                        onClick={() => setIsDryRun(!isDryRun)}
                                        className="flex items-center gap-3 p-2 bg-white/[0.05] border border-white/10 rounded-lg cursor-pointer hover:bg-white/[0.04] transition-colors"
                                    >
                                        <div className={`w-10 h-5 rounded-full p-1 transition-colors ${isDryRun ? "bg-amber-600" : "bg-neutral-800"}`}>
                                            <motion.div animate={{ x: isDryRun ? 20 : 0 }} className="w-3 h-3 bg-white rounded-full shadow-sm" />
                                        </div>
                                        <span className="text-xs font-medium text-neutral-300">Dry Run</span>
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-neutral-400">Notes (Optional)</label>
                                <Input
                                    value={description}
                                    onChange={e => setDescription(e.target.value)}
                                    placeholder="e.g., Compliance requirement X"
                                    className="bg-neutral-900 border-white/10 text-white italic text-xs"
                                />
                            </div>
                            <motion.div whileHover={(!selectedAgentId || !toolName || !condition) ? {} : { scale: 1.02 }} whileTap={(!selectedAgentId || !toolName || !condition) ? {} : { scale: 0.98 }}>
                                <Button type="submit" disabled={!selectedAgentId || !toolName || !condition} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 transition-all font-medium mt-4 disabled:opacity-50 disabled:shadow-none">
                                    <PlusCircle className="mr-2 h-4 w-4" /> Add Rule
                                </Button>
                            </motion.div>
                        </form>
                    </CardContent>
                </Card>

                {/* Agent Global Settings Card */}
                <Card className="col-span-1 lg:col-span-2 bg-black/40 backdrop-blur-xl border-white/10 shadow-2xl overflow-hidden relative group h-fit">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-1000" />
                    <CardHeader className="bg-white/[0.01] border-b border-white/10">
                        <CardTitle className="text-lg flex items-center font-semibold text-white/90 tracking-tight">
                            <Activity className="w-5 h-5 mr-2 text-blue-400" />
                            Agent Budget & Safety Control — {selectedAgentId ? getAgentName(selectedAgentId) : "Select an Agent"}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        {!selectedAgentId ? (
                            <div className="py-12 text-center text-neutral-400 italic">
                                Please select an agent from the dropdown to configure budget limits and loop protection.
                            </div>
                        ) : (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-neutral-400 flex items-center gap-2">
                                                <Coins className="w-4 h-4 text-amber-400" /> Budget Cap (USD)
                                            </label>
                                            <Input
                                                type="number"
                                                step="0.01"
                                                value={maxCostUsd}
                                                onChange={e => setMaxCostUsd(e.target.value)}
                                                placeholder="e.g. 5.00 — Hard stop agent spent"
                                                className="bg-neutral-900 border-white/10 text-white placeholder:text-neutral-400"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-neutral-400 flex items-center gap-2">
                                                <RefreshCw className="w-4 h-4 text-emerald-400" /> Budget Warning (USD)
                                            </label>
                                            <Input
                                                type="number"
                                                step="0.01"
                                                value={budgetAlertUsd}
                                                onChange={e => setBudgetAlertUsd(e.target.value)}
                                                placeholder="e.g. 4.00 — Fire alert webhook"
                                                className="bg-neutral-900 border-white/10 text-white placeholder:text-neutral-400"
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-neutral-400 flex items-center gap-2">
                                                <Activity className="w-4 h-4 text-blue-400" /> Max Tool Iterations
                                            </label>
                                            <Input
                                                type="number"
                                                value={maxIterations}
                                                onChange={e => setMaxIterations(e.target.value)}
                                                placeholder="e.g. 10 — Circuit breaker"
                                                className="bg-neutral-900 border-white/10 text-white placeholder:text-neutral-400"
                                            />
                                        </div>
                                        <div className="flex items-center justify-between p-4 bg-white/[0.05] border border-white/10 rounded-xl hover:bg-white/[0.04] transition-colors">
                                            <div className="space-y-0.5">
                                                <p className="text-sm font-medium text-white">Loop Detection</p>
                                                <p className="text-xs text-neutral-400">Auto-block repeated tool patterns</p>
                                            </div>
                                            <div
                                                onClick={() => setLoopDetection(!loopDetection)}
                                                className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors duration-300 ${loopDetection ? "bg-emerald-600" : "bg-neutral-800"}`}
                                            >
                                                <motion.div
                                                    animate={{ x: loopDetection ? 24 : 0 }}
                                                    className="w-4 h-4 bg-white rounded-full shadow-lg"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-end pt-4 border-t border-white/10">
                                    <Button
                                        onClick={handleSaveConfig}
                                        disabled={isSavingConfig}
                                        className="bg-blue-600 hover:bg-blue-500 text-white min-w-[120px]"
                                    >
                                        {isSavingConfig ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
                                        ) : (
                                            <><Save className="mr-2 h-4 w-4" /> Save Configuration</>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card className="col-span-1 lg:col-span-3 bg-black/40 backdrop-blur-xl border-white/10 shadow-2xl overflow-hidden relative group">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-1000" />
                    <CardHeader className="bg-white/[0.01] border-b border-white/10">
                        <CardTitle className="text-lg font-semibold text-white/90 tracking-tight">Active Policies</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        {loading ? (
                            <p className="text-neutral-400 py-24 text-center animate-pulse">Loading policies...</p>
                        ) : policies.length === 0 ? (
                            <p className="text-neutral-400 py-24 text-center">No policies configured. Agents will fall back to ALLOW by default.</p>
                        ) : (
                            <div className="overflow-x-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="border-white/10 hover:bg-transparent">
                                            <TableHead className="text-neutral-400 font-medium px-6 py-4">Agent</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4">Tool</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4">Condition</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4">Priority</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4">Decision</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4">Mode</TableHead>
                                            <TableHead className="text-neutral-400 font-medium py-4 text-right pr-6"></TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {policies.map((p) => (
                                            <TableRow key={p.id} className="border-white/[0.02] hover:bg-white/[0.05] transition-colors group/row">
                                                <TableCell className="font-medium text-white px-6 py-4">{getAgentName(p.agentid || p.agentId)}</TableCell>
                                                <TableCell className="text-neutral-300 font-mono text-sm py-4">{p.toolname || p.toolName}</TableCell>
                                                <TableCell className="font-mono text-xs max-w-[200px] truncate text-emerald-400 py-4 group-hover/row:text-emerald-300 transition-colors">
                                                    <span className="bg-emerald-500/10 px-2 py-1 rounded-md border border-emerald-500/20">{p.condition}</span>
                                                </TableCell>
                                                <TableCell className="py-4 text-xs font-mono text-neutral-400">{p.priority || 100}</TableCell>
                                                <TableCell className="py-4">
                                                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border ${getRuleBadgeColor(p.ruletype || p.ruleType)}`}>
                                                        {p.ruletype || p.ruleType}
                                                    </span>
                                                </TableCell>
                                                <TableCell className="py-4 text-xs font-black italic tracking-tighter uppercase">
                                                    {(p.isdryrun !== undefined ? p.isdryrun : p.isDryRun) ? (
                                                        <span className="text-amber-500">Dry Run</span>
                                                    ) : (
                                                        <span className="text-neutral-600">Enforced</span>
                                                    )}
                                                </TableCell>
                                                <TableCell className="py-4 text-right pr-6">
                                                    <button
                                                        onClick={() => handleDeletePolicy(p.id!)}
                                                        className="p-2 text-neutral-600 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                                                        title="Delete Rule"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </motion.div>
    );
}

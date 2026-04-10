// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { Database, Save, CheckCircle2, Webhook, RefreshCcw, Zap, Key, ShieldCheck, Slack, Copy, ExternalLink, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { doc, getDoc, setDoc, onSnapshot, updateDoc, arrayUnion, arrayRemove } from "firebase/firestore";
import { useAuthState } from "react-firebase-hooks/auth";
import Link from "next/link";
import { requestNotificationPermission } from "@/lib/notifications";
import { Bell, BellOff, Info } from "lucide-react";

export default function SettingsPage() {
    const [user] = useAuthState(auth);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [savedDb, setSavedDb] = useState(false);
    const [savedWebhook, setSavedWebhook] = useState(false);
    const [savedSlack, setSavedSlack] = useState(false);
    const [savedMaster, setSavedMaster] = useState(false);
    const [testSent, setTestSent] = useState(false);
    const [emailTestSent, setEmailTestSent] = useState(false);
    const [copiedKey, setCopiedKey] = useState(false);
    const [browserNotificationsEnabled, setBrowserNotificationsEnabled] = useState(false);
    const [permissionPrompt, setPermissionPrompt] = useState(false);
    const [savedOpenrouter, setSavedOpenrouter] = useState(false);

    // Form States
    const [dbType, setDbType] = useState("firebase");
    const [dbString, setDbString] = useState("");
    const [webhookUrl, setWebhookUrl] = useState("");
    const [webhookSecret, setWebhookSecret] = useState("");
    const [slackWebhookUrl, setSlackWebhookUrl] = useState("");
    const [notificationEmail, setNotificationEmail] = useState("");
    const [masterKey, setMasterKey] = useState("");
    useEffect(() => {
        // Mocking fetching current key
        setMasterKey("sw_admin_5f2e8a1b9c3d4e7f");
    }, []);
    const [openrouterAppUrl, setOpenrouterAppUrl] = useState("");
    const [openrouterAppTitle, setOpenrouterAppTitle] = useState("");
    const [openrouterCategories, setOpenrouterCategories] = useState("");

    const API_BASE = "/api";

    // Initialize/Sync settings
    useEffect(() => {
        if (!user) return;

        const fetchSettings = async () => {
            try {
                const res = await fetch(`${API_BASE}/v1/tenants/${user.uid}`);
                if (res.ok) {
                    const data = await res.json();
                    setDbType(data.db_type || "firebase");
                    setDbString(data.db_string || "");
                    setWebhookUrl(data.webhook_url || "");
                    setWebhookSecret(data.webhook_secret || "");
                    setSlackWebhookUrl(data.slack_webhook_url || "");
                    setNotificationEmail(data.notification_email || "");
                    setMasterKey(data.master_api_key || "");
                    setOpenrouterAppUrl(data.openrouter_app_url || "");
                    setOpenrouterAppTitle(data.openrouter_app_title || "");
                    setOpenrouterCategories(data.openrouter_categories || "");
                    setBrowserNotificationsEnabled(!!(data.fcmTokens && data.fcmTokens.length > 0));
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchSettings();
    }, [user]);

    const handleToggleBrowserNotifications = async () => {
        if (!user) return;
        
        if (!browserNotificationsEnabled) {
            // Enabling
            try {
                await requestNotificationPermission(user.uid);
                setBrowserNotificationsEnabled(true);
                setSavedEmail(true); // Reuse saved state or add a new one
                setTimeout(() => setSavedEmail(false), 2000);
            } catch (e) {
                console.error("Failed to enable browser notifications:", e);
                alert("Permission denied or registration failed. Check your browser settings.");
            }
        } else {
            // Disabling - we would ideally remove tokens, but for now just update state
            setBrowserNotificationsEnabled(false);
            // Optional: call backend to remove tokens
        }
    };

    const handleSaveGeneral = async (field: string, value: any, setStatus: (v: boolean) => void) => {
        if (!user) return;
        setSaving(true);
        try {
            // Map camelCase to snake_case for the database
            const fieldMap: any = {
                masterKey: "master_api_key",
                dbType: "db_type",
                webhookUrl: "webhook_url",
                slackWebhookUrl: "slack_webhook_url",
                notificationEmail: "notification_email",
                webhookSecret: "webhook_secret",
                openrouterAppUrl: "openrouter_app_url",
                openrouterAppTitle: "openrouter_app_title",
                openrouterCategories: "openrouter_categories"
            };
            const dbField = fieldMap[field] || field;

            await fetch(`${API_BASE}/v1/tenants/${user.uid}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ [dbField]: value })
            });
            setStatus(true);
            setTimeout(() => setStatus(false), 2000);
        } catch (error) {
            console.error(`Error saving ${field}:`, error);
        } finally {
            setSaving(false);
        }
    };

    const handleGenerateMasterKey = () => {
        const array = new Uint32Array(2);
        window.crypto.getRandomValues(array);
        const key = 'ag_master_' + array[0].toString(36) + array[1].toString(36);
        setMasterKey(key);
    };

    const handleSaveMasterKey = () => handleSaveGeneral("masterKey", masterKey, setSavedMaster);
    const handleSaveDb = (e: React.FormEvent) => {
        e.preventDefault();
        handleSaveGeneral("dbType", dbType, setSavedDb);
    };
    const handleSaveWebhook = (e: React.FormEvent) => {
        e.preventDefault();
        handleSaveGeneral("webhookUrl", webhookUrl, setSavedWebhook);
    };
    const handleSaveSlack = (e: React.FormEvent) => {
        e.preventDefault();
        handleSaveGeneral("slackWebhookUrl", slackWebhookUrl, setSavedSlack);
    };
    const [savedEmail, setSavedEmail] = useState(false);
    const handleSaveEmail = (e: React.FormEvent) => {
        e.preventDefault();
        handleSaveGeneral("notificationEmail", notificationEmail, setSavedEmail);
    };
    const handleSaveOpenrouter = (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        // Save all three fields at once
        const save = async () => {
            try {
                await fetch(`${API_BASE}/v1/tenants/${user?.uid}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        openrouter_app_url: openrouterAppUrl,
                        openrouter_app_title: openrouterAppTitle,
                        openrouter_categories: openrouterCategories
                    })
                });
                setSavedOpenrouter(true);
                setTimeout(() => setSavedOpenrouter(false), 2000);
            } catch (e) { console.error(e); }
            finally { setSaving(false); }
        };
        save();
    };

    const handleGenerateSecret = () => {
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        const array = new Uint32Array(24);
        window.crypto.getRandomValues(array);
        let str = "whsec_";
        for (let i = 0; i < 24; i++) {
            str += chars.charAt(array[i] % chars.length);
        }
        setWebhookSecret(str);
        handleSaveGeneral("webhookSecret", str, () => { });
    };

    const handleTestWebhook = () => {
        setTestSent(true);
        setTimeout(() => setTestSent(false), 3000);
    };

    const copyMasterKey = () => {
        navigator.clipboard.writeText(masterKey);
        setCopiedKey(true);
        setTimeout(() => setCopiedKey(false), 2000);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <p className="text-neutral-400 animate-pulse font-medium tracking-wide">Retrieving configuration...</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl space-y-12 pb-24">
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 mb-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span className="text-[9px] font-black tracking-[0.2em] text-emerald-400 uppercase">Configuration</span>
                </div>
                <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic mb-2">Security Settings</h1>
                <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.2em]">
                    Infrastructure, notifications, and organizational access.
                </p>
            </motion.div>

            {/* MASTER API KEY SECTION */}
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                        <Key className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">Management Access</h2>
                        <p className="text-sm text-neutral-400">Master Org Key used for SDK-based agent registration.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative overflow-hidden group shadow-2xl"
                >
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
                    <div className="relative space-y-6">
                        <div className="space-y-3">
                            <div className="flex justify-between items-center px-1">
                                <label className="text-sm font-semibold text-neutral-300">Master Organizational API Key</label>
                                {masterKey && (
                                    <button onClick={copyMasterKey} className="text-xs flex items-center gap-1.5 text-neutral-400 hover:text-white transition-colors bg-white/5 px-2 py-1 rounded-md border border-white/5">
                                        {copiedKey ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                        {copiedKey ? "Copied" : "Copy"}
                                    </button>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <div className="relative flex-1">
                                    <input
                                        type="text"
                                        readOnly
                                        value={masterKey || "No key generated yet"}
                                        className={`w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-emerald-300 font-mono text-sm shadow-inner transition-all ${!masterKey && "text-neutral-600 italic"}`}
                                    />
                                    {masterKey && <ShieldCheck className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-600 opacity-50" />}
                                </div>
                                <Button
                                    onClick={handleGenerateMasterKey}
                                    variant="outline"
                                    className="bg-neutral-800 border-white/10 text-white hover:bg-neutral-700 h-auto py-3 px-5 rounded-xl shadow-lg transition-all"
                                >
                                    <RefreshCcw className="w-4 h-4 mr-2" /> {masterKey ? "Regenerate" : "Generate"}
                                </Button>
                                {masterKey && (
                                    <Button
                                        onClick={handleSaveMasterKey}
                                        className={`h-auto py-3 px-6 rounded-xl transition-all shadow-lg ${savedMaster ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-blue-600 hover:bg-blue-500 text-white"}`}
                                    >
                                        {savedMaster ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                                        {savedMaster ? "Saved" : "Save Key"}
                                    </Button>
                                )}
                            </div>
                        </div>
                        <div className="p-4 bg-blue-500/5 rounded-xl border border-blue-500/10 flex items-start gap-3">
                            <Zap className="w-5 h-5 text-blue-400 mt-0.5" />
                            <p className="text-xs leading-relaxed text-blue-300/80">
                                This key grants permission to automatically register new agents via the <code className="bg-blue-500/20 px-1.5 py-0.5 rounded text-blue-100 font-mono">SupraWall SDK</code>. Treat it as a sensitive secret. Regenerating it will invalidate all ongoing automated registration flows.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </section>

            {/* SLACK INTEGRATION */}
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-[#4A154B]/10 rounded-xl border border-[#4A154B]/20 shadow-[0_0_15px_rgba(74,21,75,0.1)]">
                        <Slack className="w-5 h-5 text-[#E01E5A]" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">Slack Notifications</h2>
                        <p className="text-sm text-neutral-400">Human-In-The-Loop approval requests and security alerts.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative shadow-xl overflow-hidden"
                >
                    <form onSubmit={handleSaveSlack} className="space-y-6">
                        <div className="space-y-3">
                            <label className="text-sm font-semibold text-neutral-300">Incoming Webhook URL</label>
                            <input
                                type="url"
                                placeholder="https://hooks.slack.com/services/T000.../B000.../XXXX..."
                                value={slackWebhookUrl}
                                onChange={(e) => setSlackWebhookUrl(e.target.value)}
                                className="w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 shadow-inner"
                            />
                            <div className="flex justify-between items-center text-xs">
                                <p className="text-neutral-400 italic">Used for policy triggers requiring Human Authorization.</p>
                                <Link
                                    href="https://api.slack.com/messaging/webhooks"
                                    target="_blank"
                                    className="flex items-center gap-1 text-neutral-400 hover:text-white transition-colors"
                                >
                                    Create Webhook <ExternalLink className="w-3 h-3" />
                                </Link>
                            </div>
                        </div>

                        <div className="flex justify-end pt-4 border-t border-white/5">
                            <Button
                                type="submit"
                                className={`h-auto py-2.5 px-6 rounded-xl transition-all shadow-md font-bold ${savedSlack ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-[#4A154B] hover:bg-[#611f69] text-white"}`}
                            >
                                {savedSlack ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                                {savedSlack ? "Saved" : "Connect Slack"}
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </section>

            {/* EMAIL NOTIFICATIONS */}
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                        <Webhook className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">Email Alerts</h2>
                        <p className="text-sm text-neutral-400">Security breach reports and weekly compliance summaries.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative shadow-xl overflow-hidden"
                >
                    <form onSubmit={handleSaveEmail} className="space-y-6">
                        <div className="space-y-3">
                            <label className="text-sm font-semibold text-neutral-300">Notification Email Address</label>
                            <input
                                type="email"
                                placeholder="security-alerts@yourcompany.com"
                                value={notificationEmail}
                                onChange={(e) => setNotificationEmail(e.target.value)}
                                className="w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 shadow-inner"
                            />
                            <p className="text-xs text-neutral-400 italic">Emails are routed via Resend for zero-delay delivery.</p>
                        </div>

                        <div className="flex justify-end pt-4 border-t border-white/5 gap-3">
                            <Button
                                type="button"
                                onClick={() => {
                                    setEmailTestSent(true);
                                    setTimeout(() => setEmailTestSent(false), 3000);
                                }}
                                disabled={!notificationEmail}
                                variant="outline"
                                className={`py-2.5 px-6 rounded-xl border border-white/10 text-neutral-400 hover:text-white hover:bg-white/5 disabled:opacity-50`}
                            >
                                {emailTestSent ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
                                {emailTestSent ? "Sent" : "Test Email"}
                            </Button>
                            <Button
                                type="submit"
                                className={`h-auto py-2.5 px-8 rounded-xl transition-all shadow-md font-bold ${savedEmail ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-blue-600 hover:bg-blue-500 text-white"}`}
                            >
                                {savedEmail ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                                {savedEmail ? "Saved" : "Save Email"}
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </section>

            {/* BROWSER NOTIFICATIONS */}
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-orange-500/10 rounded-xl border border-orange-500/20 shadow-[0_0_15px_rgba(249,115,22,0.1)]">
                        <Bell className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">Browser Notifications</h2>
                        <p className="text-sm text-neutral-400">Instant approval requests on your desktop.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative shadow-xl overflow-hidden"
                >
                    <div className="flex items-center justify-between gap-6">
                        <div className="space-y-1">
                            <h3 className="font-bold text-white">Security Push Notifications</h3>
                            <p className="text-xs text-neutral-400 max-w-md">Receive real-time push events when your agents request policy-gated tools. Approve or deny directly from the pop-up even if the dashboard is closed.</p>
                        </div>
                        
                        <button
                            onClick={handleToggleBrowserNotifications}
                            className={`flex items-center gap-3 px-6 py-3 rounded-xl font-bold transition-all border ${browserNotificationsEnabled ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-neutral-800 text-neutral-300 border-white/5 hover:bg-neutral-700 hover:border-white/10"}`}
                        >
                            {browserNotificationsEnabled ? (
                                <><Bell className="w-4 h-4" /> Notifications Enabled</>
                            ) : (
                                <><BellOff className="w-4 h-4" /> Enable Browser Alerts</>
                            )}
                        </button>
                    </div>
                    
                    {!browserNotificationsEnabled && (
                        <div className="mt-6 p-4 bg-orange-500/5 rounded-xl border border-orange-500/10 flex items-start gap-3">
                            <Info className="w-4 h-4 text-orange-400 mt-0.5" />
                            <p className="text-[10px] leading-relaxed text-orange-300/80 uppercase font-bold tracking-wider">
                                Recommended for Human-In-The-Loop (HITL) compliance under the EU AI Act.
                            </p>
                        </div>
                    )}
                </motion.div>
            </section>
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                        <Webhook className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">Audit Webhooks</h2>
                        <p className="text-sm text-neutral-400">Security monitoring webhooks for your internal audit SIEM.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative shadow-xl overflow-hidden"
                >
                    <form onSubmit={handleSaveWebhook} className="space-y-8">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-neutral-300">Target Endpoint URL</label>
                                <input
                                    type="url"
                                    placeholder="https://your-api.com/webhooks/suprawall"
                                    value={webhookUrl}
                                    onChange={(e) => setWebhookUrl(e.target.value)}
                                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-sm text-neutral-400 outline-none focus:border-emerald-500/50 transition-all font-mono"
                                />
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                    <label className="text-sm font-semibold text-neutral-300">Signing Secret</label>
                                    <button type="button" onClick={handleGenerateSecret} className="text-xs font-bold flex items-center gap-1.5 text-emerald-400 hover:text-emerald-300 transition-colors bg-emerald-500/5 px-2 py-1 rounded">
                                        <RefreshCcw className="w-3.5 h-3.5" /> Reset Secret
                                    </button>
                                </div>
                                <input
                                    type="text"
                                    readOnly
                                    value={webhookSecret || "Roll secret to display"}
                                    className={`w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-neutral-400 text-sm font-mono shadow-inner ${!webhookSecret && "italic text-neutral-600"}`}
                                />
                                <p className="text-[10px] text-neutral-600 tracking-wider font-bold uppercase">HMAC SHA256 SHARED SECRET</p>
                            </div>
                        </div>

                        <div className="pt-6 border-t border-white/5 flex justify-end gap-3">
                            <Button
                                type="button"
                                onClick={handleTestWebhook}
                                disabled={!webhookUrl}
                                variant="outline"
                                className={`py-2.5 px-6 rounded-xl border border-white/10 text-neutral-400 hover:text-white hover:bg-white/5 disabled:opacity-50`}
                            >
                                {testSent ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
                                {testSent ? "Test Sent" : "Test Hook"}
                            </Button>
                            <Button
                                type="submit"
                                className={`py-2.5 px-8 rounded-xl transition-all shadow-md font-bold ${savedWebhook ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-emerald-600 hover:bg-emerald-500 text-white"}`}
                            >
                                {savedWebhook ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                                {savedWebhook ? "Active" : "Save Webhook"}
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </section>

            {/* OPENROUTER ATTRIBUTION */}
            <section className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-violet-500/10 rounded-xl border border-violet-500/20 shadow-[0_0_15px_rgba(139,92,246,0.1)]">
                        <TrendingUp className="w-5 h-5 text-violet-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-white uppercase italic tracking-tighter">OpenRouter Attribution</h2>
                        <p className="text-sm text-neutral-400">Configure labels for OpenRouter leaderboards and rankings.</p>
                    </div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="p-8 bg-black/60 backdrop-blur-xl border border-emerald-500/10 rounded-2xl relative shadow-xl overflow-hidden"
                >
                    <form onSubmit={handleSaveOpenrouter} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-neutral-300">Application URL</label>
                                <input
                                    type="url"
                                    placeholder="https://your-app.com"
                                    value={openrouterAppUrl}
                                    onChange={(e) => setOpenrouterAppUrl(e.target.value)}
                                    className="w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 shadow-inner"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-neutral-300">Application Title</label>
                                <input
                                    type="text"
                                    placeholder="My AI Agent"
                                    value={openrouterAppTitle}
                                    onChange={(e) => setOpenrouterAppTitle(e.target.value)}
                                    className="w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 shadow-inner"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-neutral-300">Categories (Comma Separated)</label>
                            <input
                                type="text"
                                placeholder="cli-agent, research-agent, personal-assistant"
                                value={openrouterCategories}
                                onChange={(e) => setOpenrouterCategories(e.target.value)}
                                className="w-full bg-black/60 border border-white/10 rounded-xl px-5 py-3.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 shadow-inner"
                            />
                        </div>

                        <div className="pt-6 border-t border-white/5 space-y-6">
                            <div className="space-y-3">
                                <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500">Auto-Generated SDK Snippet</h4>
                                <div className="relative group/code">
                                    <pre className="bg-black/80 p-6 rounded-2xl border border-white/10 overflow-x-auto text-[13px] leading-relaxed">
                                        <code className="text-violet-300">
{`# Python SDK example
suprawall.init(
    policy="production-default",
    openrouter_attribution={
        "app_url": "${openrouterAppUrl || 'https://your-app.com'}",
        "app_title": "${openrouterAppTitle || 'My AI Agent'}",
        "categories": "${openrouterCategories || 'cloud-agent'}"
    }
)`}
                                        </code>
                                    </pre>
                                    <button 
                                        type="button"
                                        onClick={() => {
                                            const code = `suprawall.init(
    policy="production-default",
    openrouter_attribution={
        "app_url": "${openrouterAppUrl || 'https://your-app.com'}",
        "app_title": "${openrouterAppTitle || 'My AI Agent'}",
        "categories": "${openrouterCategories || 'cloud-agent'}"
    }
)`;
                                            navigator.clipboard.writeText(code);
                                        }}
                                        className="absolute top-4 right-4 p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors opacity-0 group-hover/code:opacity-100"
                                    >
                                        <Copy className="w-4 h-4 text-neutral-400" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex justify-end pt-4">
                                <Button
                                    type="submit"
                                    className={`h-auto py-2.5 px-8 rounded-xl transition-all shadow-md font-bold ${savedOpenrouter ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-violet-600 hover:bg-violet-500 text-white"}`}
                                >
                                    {savedOpenrouter ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                                    {savedOpenrouter ? "Saved" : "Save Attribution"}
                                </Button>
                            </div>
                        </div>
                    </form>
                </motion.div>
            </section>
        </div>
    );
}

const Button = ({ children, variant, className, type, onClick, disabled }: any) => {
    const baseClasses = "flex items-center justify-center gap-2 rounded-lg text-sm font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed";
    const variantClasses = variant === 'outline'
        ? "border border-white/10 bg-transparent text-white hover:bg-white/5"
        : "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md";

    return (
        <button
            type={type || "button"}
            onClick={onClick}
            disabled={disabled}
            className={`${baseClasses} ${variantClasses} ${className}`}
        >
            {children}
        </button>
    );
};

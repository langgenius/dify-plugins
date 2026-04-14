// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Zap, 
    Key, 
    Copy, 
    CheckCircle2, 
    Shield, 
    ShieldAlert, 
    Lock,
    Command,
    Terminal,
    KeySquare,
    Check,
    ShieldCheck
} from "lucide-react";
import { useState, useEffect } from "react";
import { auth, db } from "@/lib/firebase";
import { collection, query, where, onSnapshot, addDoc, serverTimestamp, getDocs } from "firebase/firestore";
import { useAuthState } from "react-firebase-hooks/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

interface Agent {
    id: string;
    name: string;
    apiKey: string;
}

export default function ConnectIntegrationPage() {
    const [user] = useAuthState(auth);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [selectedAgentId, setSelectedAgentId] = useState("");
    const [subKeyName, setSubKeyName] = useState("");
    const [generatedSubKey, setGeneratedSubKey] = useState<string | null>(null);
    const [isCopying, setIsCopying] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!user) return;
        const q = query(collection(db, "agents"), where("userId", "==", user.uid));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            setAgents(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Agent)));
        });
        return () => unsubscribe();
    }, [user]);

    const handleGenerateSubKey = async () => {
        if (!user || !selectedAgentId || !subKeyName) return;
        setIsLoading(true);

        const parentAgent = agents.find(a => a.id === selectedAgentId);
        if (!parentAgent) return;

        // In a real implementation, this would be a secure server-side call.
        // For the demo, we generate it on the client.
        const bytes = new Uint8Array(16);
        window.crypto.getRandomValues(bytes);
        const randomHex = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
        const newSubKey = `agc_${randomHex}`;

        try {
            await addDoc(collection(db, "connect_keys"), {
                name: subKeyName,
                parentId: selectedAgentId,
                parentName: parentAgent.name,
                apiKey: newSubKey,
                userId: user.uid,
                createdAt: serverTimestamp(),
                status: 'active'
            });
            setGeneratedSubKey(newSubKey);
        } catch (error) {
            console.error("Error generating sub-key:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setIsCopying(true);
        setTimeout(() => setIsCopying(false), 2000);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-12 pb-20">
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                        <Zap className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic">SupraWall Connect</h1>
                        <p className="text-neutral-400 text-sm font-medium uppercase tracking-widest">Universal Integration Sub-Keys</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-8"
                >
                    <div className="bg-neutral-900/50 border border-white/10 rounded-[32px] p-8 space-y-6 shadow-2xl">
                        <div className="space-y-2">
                            <h2 className="text-xl font-black text-white uppercase tracking-tight">Generate Sub-Key</h2>
                            <p className="text-neutral-400 text-xs">Authorize specific services or frameworks without exposing your root Agent Key.</p>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label className="text-[10px] font-black uppercase tracking-widest text-emerald-500/70 ml-1">Parent Identity</Label>
                                <select 
                                    value={selectedAgentId}
                                    onChange={(e) => setSelectedAgentId(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 h-12 rounded-xl px-4 text-sm text-white focus:ring-emerald-500 focus:border-emerald-500 transition-all outline-none"
                                >
                                    <option value="" disabled className="bg-neutral-900">Select an Agent Identity...</option>
                                    {agents.map(agent => (
                                        <option key={agent.id} value={agent.id} className="bg-neutral-900">{agent.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-[10px] font-black uppercase tracking-widest text-emerald-500/70 ml-1">Sub-Key Name / Service</Label>
                                <Input 
                                    placeholder="e.g. LangChain Production"
                                    value={subKeyName}
                                    onChange={(e) => setSubKeyName(e.target.value)}
                                    className="bg-black/40 border border-white/10 h-12 rounded-xl text-white outline-none focus:ring-emerald-500"
                                />
                            </div>

                            <Button 
                                onClick={handleGenerateSubKey}
                                disabled={!selectedAgentId || !subKeyName || isLoading}
                                className="w-full bg-emerald-500 hover:bg-emerald-600 text-black font-black uppercase tracking-widest text-xs h-12 rounded-xl transition-all shadow-[0_0_20px_rgba(16,185,129,0.2)]"
                            >
                                {isLoading ? "Processing..." : "Generate Connect Key"}
                            </Button>
                        </div>

                        {generatedSubKey && (
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="p-6 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl space-y-4"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                                        <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest font-mono">Sub-Key Active</span>
                                    </div>
                                    <Badge variant="outline" className="text-[10px] border-emerald-500/20 text-emerald-500 bg-emerald-500/5">Production-Ready</Badge>
                                </div>
                                <div className="relative group">
                                    <div className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm font-mono text-white shadow-inner break-all pr-12">
                                        {generatedSubKey}
                                    </div>
                                    <button 
                                        onClick={() => copyToClipboard(generatedSubKey)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-white/5 rounded-lg transition-colors"
                                    >
                                        {isCopying ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-neutral-400" />}
                                    </button>
                                </div>
                                <p className="text-[10px] text-neutral-400 leading-tight">
                                    This key inherits policies from the parent identity but allows isolated tracking and revocation.
                                </p>
                            </motion.div>
                        )}
                    </div>
                </motion.div>

                <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                >
                    <div className="bg-neutral-900/30 border border-white/10 rounded-[32px] p-8 space-y-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <Command className="w-4 h-4 text-blue-400" />
                            </div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-white">How it works</h3>
                        </div>

                        <div className="space-y-4">
                        {[
                            { icon: KeySquare, title: "Identity Inheritance", desc: "Sub-keys map directly to a root Agent Identity, inheriting all defined governance policies." },
                            { icon: Shield, title: "Risk Isolation", desc: "If a specific integration is compromised, revoke the sub-key without affecting your whole fleet." },
                            { icon: Terminal, title: "Granular Logging", desc: "Audit logs will explicitly label actions with the specific sub-key name for forensic clarity." }
                        ].map((item, idx) => (
                            <div key={idx} className="flex gap-4">
                                <div className="shrink-0 mt-1">
                                    <item.icon className="w-4 h-4 text-neutral-400" />
                                </div>
                                <div className="space-y-1">
                                    <h4 className="text-xs font-bold text-white uppercase tracking-tight">{item.title}</h4>
                                    <p className="text-[11px] text-neutral-400 leading-relaxed">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                        </div>
                    </div>

                    <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-[32px] p-8 space-y-4">
                        <div className="flex items-center gap-2">
                            <Lock className="w-4 h-4 text-indigo-400" />
                            <h3 className="text-xs font-black uppercase tracking-widest text-indigo-400">Security Best Practice</h3>
                        </div>
                        <p className="text-[11px] text-neutral-400 leading-relaxed italic">
                            "Never use your root API key in client-side code or public cloud functions. Always generate a SupraWall Connect sub-key for each isolated service in your workload."
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth, db } from "@/lib/firebase";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, ShieldCheck, Loader2, AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function PolicyCreationForm() {
    const [user] = useAuthState(auth);
    const searchParams = useSearchParams();
    const router = useRouter();
    
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const agentId = searchParams.get("agentId");
    const toolName = searchParams.get("tool");
    const decision = searchParams.get("decision") || "REQUIRE_APPROVAL";

    const handleCreate = async () => {
        if (!user || !agentId || !toolName) return;
        setLoading(true);
        setError(null);

        try {
            await addDoc(collection(db, "policies"), {
                agentId,
                toolName,
                ruleType: decision,
                condition: ".*", // Default to all as proxy for quick setup
                tenantId: user.uid,
                createdAt: serverTimestamp(),
                description: `Automated policy for ${toolName}`
            });
            setSuccess(true);
            setTimeout(() => router.push("/dashboard/policies"), 2000);
        } catch (e: any) {
            console.error(e);
            setError(e.message || "Failed to create policy");
        } finally {
            setLoading(false);
        }
    };

    if (!agentId || !toolName) {
        return (
            <Card className="bg-black/60 border-red-500/20">
                <CardContent className="p-6 text-center space-y-4">
                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
                    <h2 className="text-xl font-bold text-white">Missing Parameters</h2>
                    <p className="text-neutral-400 text-sm">This link is invalid or incomplete. Please ensure agentId and tool are provided.</p>
                    <Button onClick={() => router.push("/dashboard/policies")} variant="outline">
                        Back to Policies
                    </Button>
                </CardContent>
            </Card>
        );
    }

    return (
        <AnimatePresence mode="wait">
            {!success ? (
                <motion.div
                    key="form"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 1.05 }}
                >
                    <Card className="bg-black/80 backdrop-blur-2xl border-emerald-500/20 overflow-hidden relative">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />
                        <CardHeader className="text-center space-y-2">
                            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-full w-fit mx-auto mb-2">
                                <Shield className="w-8 h-8 text-emerald-400" />
                            </div>
                            <CardTitle className="text-2xl font-black italic uppercase tracking-tighter text-white">
                                Authorize Policy
                            </CardTitle>
                            <p className="text-xs text-neutral-400 uppercase tracking-widest font-black">
                                Compliance Gate Configuration
                            </p>
                        </CardHeader>
                        <CardContent className="p-8 space-y-8">
                            <div className="grid grid-cols-1 gap-4">
                                <div className="p-4 bg-white/5 border border-white/10 rounded-xl space-y-1">
                                    <p className="text-[10px] font-black uppercase text-neutral-500 tracking-widest">Agent Identity</p>
                                    <p className="text-sm font-mono text-emerald-400">{agentId}</p>
                                </div>
                                <div className="p-4 bg-white/5 border border-white/10 rounded-xl space-y-1 text-right">
                                    <p className="text-[10px] font-black uppercase text-neutral-500 tracking-widest text-right">Target Tool</p>
                                    <p className="text-sm font-mono text-blue-400">{toolName}</p>
                                </div>
                            </div>

                            <div className="flex items-center justify-center gap-6 py-4">
                                <div className="flex flex-col items-center gap-1">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                    <div className="w-px h-8 bg-emerald-500/20" />
                                    <div className="w-2 h-2 rounded-full bg-emerald-500/20" />
                                </div>
                                <div className="flex-1 border-t border-dashed border-white/10 relative">
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 bg-black text-[10px] font-black uppercase tracking-widest text-neutral-500">
                                        Policy Logic
                                    </div>
                                </div>
                                <div className="px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                                    <span className="text-[10px] font-black uppercase tracking-wider text-amber-400">{decision}</span>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <Button 
                                    onClick={handleCreate} 
                                    disabled={loading}
                                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-wider h-12 rounded-xl border-b-4 border-emerald-800 active:border-b-0 active:translate-y-1 transition-all"
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ShieldCheck className="w-5 h-5 mr-2" />}
                                    Deploy Policy
                                </Button>
                                {error && <p className="text-center text-xs text-red-400 font-medium">Error: {error}</p>}
                                <p className="text-center text-[10px] text-neutral-600 uppercase font-black tracking-widest">
                                    Secured by SupraWall Perimeter
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            ) : (
                <motion.div
                    key="success"
                    initial={{ opacity: 0, scale: 1.1 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center space-y-6 py-12"
                >
                    <div className="relative inline-block">
                        <motion.div
                            animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                            transition={{ duration: 0.5 }}
                        >
                            <CheckCircle2 className="w-20 h-20 text-emerald-500 mx-auto drop-shadow-[0_0_20px_rgba(16,185,129,0.5)]" />
                        </motion.div>
                    </div>
                    <div>
                        <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">Policy Deployed</h2>
                        <p className="text-neutral-400 text-sm mt-2">The security gate is now active for {toolName}.</p>
                    </div>
                    <div className="flex items-center justify-center gap-2 text-[10px] font-black uppercase text-emerald-500/60 tracking-widest">
                        Redirecting to Governance <ArrowRight className="w-3 h-3" />
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

export default function NewPolicyPage() {
    return (
        <div className="max-w-md mx-auto py-12 px-4">
            <Suspense fallback={
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
                </div>
            }>
                <PolicyCreationForm />
            </Suspense>
        </div>
    );
}

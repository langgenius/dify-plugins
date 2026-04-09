// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BrickWall, ArrowRight, Lock, Mail, Loader2, ShieldAlert } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function AdminLoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);
        try {
            await signInWithEmailAndPassword(auth, email, password);
            // On success, redirect directly to admin overview
            router.push("/admin");
        } catch (err: unknown) {
            console.error("[SupraWall Admin] Login failed:", err);
            if (err instanceof Error) {
                if (err.message.includes("auth/invalid-credential")) {
                    setError("Invalid admin credentials.");
                } else {
                    setError(err.message);
                }
            } else {
                setError("An unknown error occurred");
            }
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#050505] selection:bg-red-500/30">
            {/* Dark Tech Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-red-950/10 blur-[150px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-red-900/5 blur-[120px] rounded-full" />
            </div>

            <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md px-6 relative z-10"
            >
                <div className="mb-10 text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 mb-6">
                        <BrickWall className="w-8 h-8 text-red-500" />
                    </div>
                    <h1 className="text-4xl font-black text-white italic uppercase tracking-tighter mb-2">
                        Admin <span className="text-red-500">Console</span>
                    </h1>
                    <p className="text-neutral-500 font-bold uppercase tracking-[0.2em] text-[10px]">
                        Restricted Access Area • Level 4 Clearance
                    </p>
                </div>

                <div className="bg-[#0A0A0A] border border-red-500/20 rounded-[2.5rem] p-8 md:p-10 shadow-2xl shadow-red-500/5 backdrop-blur-3xl relative overflow-hidden">
                    <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-red-500/40 to-transparent" />

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Admin Identity</label>
                            <div className="relative group/input">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within/input:text-red-400 transition-colors" />
                                <Input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="admin@supra-wall.com"
                                    required
                                    className="h-14 pl-12 bg-black border-white/5 focus:border-red-500/50 text-white placeholder:text-neutral-800 rounded-xl transition-all font-medium"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Master Key</label>
                            <div className="relative group/input">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within/input:text-red-400 transition-colors" />
                                <Input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    className="h-14 pl-12 bg-black border-white/5 focus:border-red-500/50 text-white placeholder:text-neutral-800 rounded-xl transition-all font-medium"
                                />
                            </div>
                        </div>

                        <AnimatePresence mode="wait">
                            {error && (
                                <motion.div 
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3"
                                >
                                    <ShieldAlert className="w-5 h-5 text-red-500 shrink-0" />
                                    <p className="text-red-400 text-xs font-bold uppercase tracking-tight">{error}</p>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <Button 
                            disabled={isLoading}
                            type="submit" 
                            className="w-full h-14 bg-red-600 hover:bg-red-500 text-white font-black uppercase tracking-widest rounded-xl transition-all shadow-xl shadow-red-500/20 active:scale-[0.98] group"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Establish Master Link
                                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-600 italic">
                             Automated Forensic Logging Enabled
                        </p>
                    </div>
                </div>

                <div className="mt-8 text-center opacity-30">
                    <p className="text-[10px] font-black uppercase tracking-[0.5em] text-neutral-600 italic">
                        SUPRAWALL SECURE ADMIN GATEWAY
                    </p>
                </div>
            </motion.div>
        </div>
    );
}

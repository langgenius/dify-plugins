// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect } from "react";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { useRouter } from "next/navigation";
import { sendGAEvent } from "@next/third-parties/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Shield, ArrowRight, Lock, Mail, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { getAuthMode, isAdminEmail } from "@/lib/auth-config";

export default function LoginPage() {
    const authMode = getAuthMode();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isRegistering, setIsRegistering] = useState(false);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);
        try {
            if (isRegistering) {
                if (authMode === "stealth" && !isAdminEmail(email)) {
                    setError("Public registration is currently closed. Please join our beta waitlist.");
                    setIsLoading(false);
                    setTimeout(() => router.push("/beta"), 2000);
                    return;
                }
                await createUserWithEmailAndPassword(auth, email, password);
                sendGAEvent('event', 'sign_up', { method: 'email' });
            } else {
                const userCredential = await signInWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;

                if (authMode === "stealth" && !isAdminEmail(user.email)) {
                    await auth.signOut();
                    setError("Authorized personnel only. Redirecting to beta...");
                    setTimeout(() => router.push("/beta"), 2000);
                    return;
                }

                sendGAEvent('event', 'login', { method: 'email' });
            }
            router.push("/dashboard");
        } catch (err: unknown) {
            if (err instanceof Error) {
                // Friendly error messages
                const msg = err.message;
                if (msg.includes("auth/invalid-credential")) setError("Invalid email or password.");
                else if (msg.includes("auth/email-already-in-use")) setError("This email is already registered.");
                else if (msg.includes("auth/weak-password")) setError("Password should be at least 6 characters.");
                else setError(msg);
            } else {
                setError("An unknown error occurred");
            }
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#020202] selection:bg-emerald-500/30">
            {/* Background Orbs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-600/5 blur-[120px] rounded-full" />
            </div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="w-full max-w-md px-6 relative z-10"
            >
                <div className="mb-10 text-center">
                    <motion.div 
                        initial={{ scale: 0.8 }}
                        animate={{ scale: 1 }}
                        className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-6"
                    >
                        <Shield className="w-8 h-8 text-emerald-400" />
                    </motion.div>
                    <h1 className="text-4xl font-black text-white italic uppercase tracking-tighter mb-2">
                        SupraWall
                    </h1>
                    <p className="text-neutral-500 font-bold uppercase tracking-[0.2em] text-[10px]">
                        Secure Runtime Guardrails
                    </p>
                </div>

                <div className="bg-[#0A0A0A] border border-white/10 rounded-[2.5rem] p-8 md:p-10 shadow-2xl shadow-emerald-500/5 backdrop-blur-3xl relative overflow-hidden group">
                    {/* Top accent line */}
                    <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />

                    <h2 className="text-2xl font-black text-white italic uppercase tracking-tight mb-2">
                        {isRegistering ? "Create Account" : (authMode === "stealth" ? "Operator Login" : "Sign In")}
                    </h2>
                    <p className="text-[9px] font-black uppercase tracking-[0.2em] text-emerald-500/60 mb-8 italic">
                        {authMode === "stealth"
                            ? "Stealth Launch Active \u2022 Authorized Admins Only"
                            : isRegistering ? "Self-Hosted Instance \u2022 Create Your Account" : "Self-Hosted Instance \u2022 Sign In to Continue"}
                    </p>

                    <form onSubmit={handleAuth} className="space-y-6">
                        <div className="space-y-2">
                            <label htmlFor="email" className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Email Identifier</label>
                            <div className="relative group/input">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within/input:text-emerald-400 transition-colors" />
                                <Input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="operator@supra-wall.com"
                                    required
                                    className="h-14 pl-12 bg-black border-white/10 focus:border-emerald-500/50 text-white placeholder:text-neutral-700 rounded-xl transition-all font-medium"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="password" className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Secure Key</label>
                            <div className="relative group/input">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within/input:text-emerald-400 transition-colors" />
                                <Input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    className="h-14 pl-12 bg-black border-white/10 focus:border-emerald-500/50 text-white placeholder:text-neutral-700 rounded-xl transition-all font-medium"
                                />
                            </div>
                        </div>

                        <AnimatePresence mode="wait">
                            {error && (
                                <motion.div 
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-bold uppercase tracking-wide text-center"
                                >
                                    {error}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <Button 
                            disabled={isLoading}
                            type="submit" 
                            className="w-full h-14 bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_0_20px_rgba(16,185,129,0.1)] active:scale-[0.98] group"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    {isRegistering ? "Initialize Account" : "Establish Link"}
                                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="mt-10 text-center">
                        {authMode === "open" ? (
                            <button
                                type="button"
                                onClick={() => { setIsRegistering(!isRegistering); setError(""); }}
                                className="text-[10px] font-black uppercase tracking-[0.1em] text-emerald-500/60 italic hover:text-emerald-400 transition-colors"
                            >
                                {isRegistering ? "Already have an account? Sign in" : "Don\u2019t have an account? Create one"}
                            </button>
                        ) : (
                            <p className="text-[10px] font-black uppercase tracking-[0.1em] text-neutral-600 italic">
                                Authorized Access Only &bull; System Locked
                            </p>
                        )}
                    </div>
                </div>

                <div className="mt-8 text-center opacity-30">
                    <p className="text-[10px] font-black uppercase tracking-[0.5em] text-neutral-600 italic">
                        © 2026 SUPRAWALL • SECURE RUNTIME PROTOCOL
                    </p>
                </div>
            </motion.div>
        </div>
    );
}

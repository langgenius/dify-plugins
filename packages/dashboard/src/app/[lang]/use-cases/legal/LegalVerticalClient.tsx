// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Scale, ShieldCheck, ArrowRight, ShieldAlert, 
    Lock, CheckCircle2, EyeOff, LayoutDashboard, 
    Briefcase, Network, Database, Share2, Zap, AlertTriangle, 
    FileText, Settings, Plus, Key, Code, Info, 
    MessageSquare, Check, X, MousePointer2, History, Fingerprint
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { TagBadge } from "@/app/HomeClient";

export default function LegalVerticalClient() {
    const [activeTab, setActiveTab] = useState("insecure");

    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none text-glow">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-blue-500/20 blur-[150px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Legal & Privilege</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Privilege Secured. <br />
                             <span className="text-blue-500 font-bold italic underline decoration-white/10 uppercase italic">Audits Automated.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Law firms don&apos;t just use AI — they manage evidence. SupraWall is the deterministic safety layer that ensures attorney-client privilege is never compromised by an autonomous tool.
                        </p>
                    </div>
                </div>
            </section>

             {/* ⚔️ VISUAL COMPARISON — Insecure vs Secure */}
             <section className="py-20 px-6 bg-black border-y border-white/5 relative">
                <div className="max-w-4xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <TagBadge>The Privilege Leak Threat</TagBadge>
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">Deterministic vs Probabilistic</h2>
                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto text-glow">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white shadow-[0_0_20px_rgba(225,29,72,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The Leaky Agent</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(59,130,246,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The Privilege-Shielded Agent</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Action Side */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-10 font-mono text-sm min-h-[400px] relative overflow-hidden shadow-2xl space-y-6">
                             <div className="absolute top-4 right-10 text-[10px] font-black uppercase text-neutral-600 tracking-widest italic">Outbound Tool Call Monitor</div>
                             <div className="space-y-4 pt-10">
                                <p className="text-neutral-500 italic uppercase italic tracking-tighter leading-snug">{"> agent.call_tool(\"legal_research.find_citations\", { ... })"}</p>
                                
                                {activeTab === "insecure" ? (
                                    <motion.div initial={{opacity: 0, scale: 0.95}} animate={{opacity: 1, scale: 1}} className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 font-mono text-xs shadow-glow-rose-slow">
                                        <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black italic shadow-text-glow">JSON Research Header (⚠️ EXPOSED PRIVILEGE)</p>
                                        {`{\n  \"query\": \"Find citations for Case-942.\",\n  \"context\": \"Client Jane Doe admitted to fraud...\",\n  \"privilege_level\": \"CONFIDENTIAL\"\n}`}
                                        <div className="mt-4 flex items-center gap-2 font-black italic uppercase italic tracking-tighter">
                                            <AlertTriangle className="w-4 h-4" /> PRIVILEGE ESCAPED: SENSITIVE ADMISSION REMAINED IN PAYLOAD.
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} className="p-6 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-blue-400 font-mono text-xs shadow-glow-blue-slow">
                                        <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black italic tracking-tighter italic">JSON Research Header (🛡️ PRIVILEGE REDACTED)</p>
                                        {`{\n  \"query\": \"Find citations for Case-942.\",\n  \"context\": \"[PRIVILEGED_CLIENT_DATA_REDACTED]\",\n  \"privilege_level\": \"SECURED\"\n}`}
                                        <div className="mt-4 flex items-center gap-2 font-black italic uppercase italic tracking-tighter bg-blue-600/20 p-2 rounded-lg">
                                            <ShieldCheck className="w-4 h-4" /> PRIVILEGE SHIELD ACTIVE: 1 SENSITIVE BLOCK SCRUBBED.
                                        </div>
                                    </motion.div>
                                )}
                             </div>
                        </div>

                        {/* Explained Side */}
                        <div className="flex flex-col justify-center space-y-8">
                             <div className="space-y-4 text-glow-blue">
                                <h3 className="text-3xl font-black italic uppercase tracking-tighter leading-none italic uppercase italic text-glow-blue">Attorney-Client Integrity.</h3>
                                <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">
                                    Legal research agents often need broad context to be effective. But that context can&apos;t be leaked to external search tools or model providers. SupraWall enforces redaction of privileged data at the binary SDK level — where no prompt bypass can reach.
                                </p>
                             </div>
                             <div className="grid grid-cols-1 gap-4">
                                {[
                                    { title: "Immutable Audit Trails", desc: "Verifiable, signed logs of every action taken by the agent.", icon: <Fingerprint className="w-6 h-6 text-blue-500" /> },
                                    { title: "Deterministic Scrubbing", desc: "Automated redaction for PII/PHI and privileged patterns.", icon: <EyeOff className="w-6 h-6 text-purple-500" /> }
                                ].map(item => (
                                    <div key={item.title} className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                        <div className="p-3 bg-white/5 rounded-xl group-hover:scale-110 transition-transform">{item.icon}</div>
                                        <div>
                                            <p className="text-white text-sm font-black italic uppercase tracking-tighter italic uppercase italic tracking-tighter">{item.title}</p>
                                            <p className="text-neutral-600 text-[10px] font-bold uppercase tracking-widest italic font-bold uppercase tracking-widest">{item.desc}</p>
                                        </div>
                                    </div>
                                ))}
                             </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-[#030303] relative text-center">
                <div className="absolute inset-0 bg-blue-500/5 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Legal Case Study</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow text-glow-blue">
                        Privilege Kept. <br />
                        <span className="text-blue-500 underline decoration-white/20 font-bold italic underline decoration-white/10 uppercase italic">Audits Done.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t wait for an ethics board investigation. Secure your autonomous legal pipelines with deterministic safety today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-blue-600 text-white font-black text-3xl rounded-3xl hover:bg-blue-500 transition-all shadow-[0_0_100px_rgba(59,130,246,0.2)] tracking-tighter flex items-center gap-4 group">
                             Implement LawSec Node <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

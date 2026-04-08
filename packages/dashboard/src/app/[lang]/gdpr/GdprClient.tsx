// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    EyeOff, ShieldCheck, ArrowRight, Lock, 
    CheckCircle2, FileText, Fingerprint, 
    ShieldAlert, Search, ClipboardList, Zap,
    Scale, UserCheck, Database
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";
import { useState } from "react";

export default function GdprClient({ dictionary, lang }: { dictionary: any, lang: string }) {
    const [activeTab, setActiveTab] = useState("insecure");
    const t = dictionary.gdpr;

    return (
        <main className="overflow-hidden bg-[#030303] text-white">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-purple-500/20 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>{t.hero.badge}</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             {t.hero.title} <br />
                             <span className="text-purple-500 font-bold italic underline decoration-white/10 italic">{t.hero.emphasis}</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             {t.hero.description}
                        </p>
                    </div>
                </div>
            </section>

             {/* ⚔️ VISUAL COMPARISON — Insecure vs Secure */}
             <section className="py-20 px-6 bg-black border-y border-white/5 relative">
                <div className="max-w-7xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">
                            {t.comparison.title}
                        </h2>

                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto text-glow">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white' : 'text-neutral-500 hover:text-white'}`}>{t.comparison.insecureLabel}</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-purple-600 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)]' : 'text-neutral-500 hover:text-white'}`}>{t.comparison.secureLabel}</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Terminal Side */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-10 font-mono text-sm min-h-[400px] relative overflow-hidden shadow-2xl">
                             <div className="absolute top-4 right-10 text-[10px] font-black uppercase text-neutral-600 tracking-widest">{t.comparison.terminal.header}</div>
                             <div className="space-y-4 pt-10">
                                <p className="text-neutral-500">{"> agent.tool_call(\"external_crm.update_record\", { ... })"}</p>
                                
                                {activeTab === "insecure" ? (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} key="insecure" className="space-y-4">
                                        <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 font-mono text-xs">
                                            <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black">{t.comparison.terminal.insecure.status}</p>
                                            {`{\n  \"name\": \"Jane Doe\",\n  \"email\": \"jane@example.com\",\n  \"ssn\": \"942-12-XXXX\",\n  \"details\": \"Customer discussed health plan.\"\n}`}
                                        </div>
                                        <div className="flex items-center gap-3 text-rose-500 font-black uppercase text-[10px] italic">
                                            <ShieldAlert className="w-4 h-4" /> {t.comparison.terminal.insecure.violation}
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} key="secure" className="space-y-4">
                                        <div className="p-6 bg-purple-500/10 border border-purple-500/20 rounded-2xl text-purple-400 font-mono text-xs">
                                            <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black">{t.comparison.terminal.secure.status}</p>
                                            {`{\n  \"name\": \"[REDACTED_NAME]\",\n  \"email\": \"[REDACTED_EMAIL]\",\n  \"ssn\": \"[REDACTED_SSN]\",\n  \"details\": \"Customer discussed health plan.\"\n}`}
                                        </div>
                                        <div className="flex items-center gap-3 text-emerald-500 font-black uppercase text-[10px] italic">
                                            <ShieldCheck className="w-4 h-4" /> {t.comparison.terminal.secure.protection}
                                        </div>
                                    </motion.div>
                                )}
                             </div>
                        </div>

                        {/* Explained Side */}
                        <div className="flex flex-col justify-center space-y-8">
                             <div className="space-y-4">
                                <h3 className="text-3xl font-black italic uppercase tracking-tighter leading-none italic uppercase italic">{t.comparison.explain.title}</h3>
                                <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">
                                    {t.comparison.explain.p}
                                </p>
                             </div>
                             <div className="grid grid-cols-1 gap-4">
                                {[
                                    { title: t.comparison.explain.features.scrubbing.title, desc: t.comparison.explain.features.scrubbing.desc, icon: <EyeOff className="w-6 h-6 text-purple-400" /> },
                                    { title: t.comparison.explain.features.logs.title, desc: t.comparison.explain.features.logs.desc, icon: <FileText className="w-6 h-6 text-blue-400" /> }
                                ].map(item => (
                                    <div key={item.title} className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                        <div className="p-3 bg-purple-500/10 rounded-xl group-hover:scale-110 transition-transform">{item.icon}</div>
                                        <div>
                                            <p className="text-white text-sm font-black italic uppercase tracking-widest">{item.title}</p>
                                            <p className="text-neutral-600 text-[10px] font-bold uppercase tracking-widest">{item.desc}</p>
                                        </div>
                                    </div>
                                ))}
                             </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 📑 DEEP DIVE SECTIONS: Articles 5, 22, 30 */}
             <section className="py-32 px-6">
                <div className="max-w-7xl mx-auto space-y-32">
                    {/* Article 5: Minimization */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                        <div className="space-y-8">
                            <TagBadge>GDPR Art. 5(1)(c)</TagBadge>
                            <h2 className="text-5xl md:text-6xl font-black uppercase italic tracking-tighter leading-none">{t.deep.titles.art5}</h2>
                            <p className="text-xl text-neutral-400 font-medium italic">{t.deep.desc.art5}</p>
                            <ul className="space-y-6">
                                {[
                                    "Automated identification of PII in tool call payloads.",
                                    "Deterministic redaction before data leaves server.",
                                    "Custom exclusion patterns for sensitive sectors."
                                ].map((item: string, i: number) => (
                                    <li key={i} className="flex gap-4 items-start">
                                        <div className="mt-1 p-1 bg-purple-500/20 rounded-full"><CheckCircle2 className="w-4 h-4 text-purple-500" /></div>
                                        <span className="text-neutral-300 font-bold uppercase text-xs tracking-tight">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="relative group">
                             <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/50 to-emerald-500/50 rounded-[3rem] blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                             <div className="relative aspect-square rounded-[3rem] bg-neutral-900 border border-white/10 overflow-hidden flex flex-col p-12 space-y-8">
                                <Database className="w-16 h-16 text-purple-500" />
                                <div className="space-y-4">
                                    <div className="h-4 w-3/4 bg-white/5 rounded-full" />
                                    <div className="h-4 w-full bg-white/5 rounded-full" />
                                    <div className="h-4 w-5/6 bg-white/5 rounded-full" />
                                    <div className="h-4 w-1/2 bg-purple-500/20 rounded-full animate-pulse" />
                                </div>
                                <div className="p-6 bg-black/40 rounded-2xl border border-white/5">
                                    <p className="text-[10px] font-black uppercase text-neutral-500 tracking-widest mb-2">SupraWall Policy Enforcement</p>
                                    <p className="text-xs font-mono text-emerald-500 uppercase italic tracking-tighter">PII_REDACTION: SUCCESS</p>
                                </div>
                             </div>
                        </div>
                    </div>

                    {/* Article 22: Automated Decision Making */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                        <div className="relative group order-last lg:order-first">
                             <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/50 to-blue-500/50 rounded-[3rem] blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                             <div className="relative aspect-square rounded-[3rem] bg-neutral-900 border border-white/10 overflow-hidden flex flex-col p-12 space-y-8">
                                <UserCheck className="w-16 h-16 text-emerald-500" />
                                <div className="p-6 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                                    <p className="text-[10px] font-black uppercase text-emerald-500 tracking-widest mb-4">Human-in-the-loop required</p>
                                    <div className="flex justify-between items-center bg-black/40 p-4 rounded-xl">
                                        <span className="text-xs font-bold">Approve Action?</span>
                                        <div className="flex gap-2">
                                            <div className="w-8 h-8 rounded-lg bg-emerald-600" />
                                            <div className="w-8 h-8 rounded-lg bg-rose-600" />
                                        </div>
                                    </div>
                                </div>
                             </div>
                        </div>
                        <div className="space-y-8">
                            <TagBadge>GDPR Art. 22</TagBadge>
                            <h2 className="text-5xl md:text-6xl font-black uppercase italic tracking-tighter leading-none">{t.deep.titles.art22}</h2>
                            <p className="text-xl text-neutral-400 font-medium italic">{t.deep.desc.art22}</p>
                            <ul className="space-y-6">
                                {[
                                    "Mandatory human review for automated high-impact actions.",
                                    "Zero-trust tool execution boundaries.",
                                    "Real-time policy interception and denial."
                                ].map((item: string, i: number) => (
                                    <li key={i} className="flex gap-4 items-start">
                                        <div className="mt-1 p-1 bg-emerald-500/20 rounded-full"><CheckCircle2 className="w-4 h-4 text-emerald-500" /></div>
                                        <span className="text-neutral-300 font-bold uppercase text-xs tracking-tight">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Article 30: Processing Logs */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                        <div className="space-y-8">
                            <TagBadge>GDPR Art. 30</TagBadge>
                            <h2 className="text-5xl md:text-6xl font-black uppercase italic tracking-tighter leading-none">{t.deep.titles.art30}</h2>
                            <p className="text-xl text-neutral-400 font-medium italic">{t.deep.desc.art30}</p>
                            <ul className="space-y-6">
                                {[
                                    "RSA-signed audit logs for all agent behavior.",
                                    "Tamper-proof record of data processing activities.",
                                    "One-click ROPA reporting for audit readiness."
                                ].map((item: string, i: number) => (
                                    <li key={i} className="flex gap-4 items-start">
                                        <div className="mt-1 p-1 bg-blue-500/20 rounded-full"><CheckCircle2 className="w-4 h-4 text-blue-500" /></div>
                                        <span className="text-neutral-300 font-bold uppercase text-xs tracking-tight">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="relative group">
                             <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/50 to-purple-500/50 rounded-[3rem] blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                             <div className="relative aspect-square rounded-[3rem] bg-neutral-900 border border-white/10 overflow-hidden flex flex-col p-12 space-y-6">
                                <ClipboardList className="w-16 h-16 text-blue-500" />
                                <div className="space-y-3 font-mono text-[10px] text-neutral-500 overflow-hidden">
                                     <p className="text-blue-400">{"{\"timestamp\": \"2026-04-06T12:00:00Z\","}</p>
                                     <p>{" \"action\": \"api_call\","}</p>
                                     <p>{" \"purpose\": \"customer_support\","}</p>
                                     <p className="text-emerald-400 text-[8px]">{" \"compliance\": \"VALIDATED\"}"}</p>
                                </div>
                                <div className="mt-auto px-6 py-4 bg-blue-500 text-white font-black uppercase tracking-widest text-xs rounded-2xl text-center italic">
                                    Export Audit Kit
                                </div>
                             </div>
                        </div>
                    </div>
                </div>
             </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-purple-500/5 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>{t.final.badge}</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        {t.final.title} <br />
                        <span className="text-purple-500 underline decoration-white/20 font-bold italic underline decoration-white/10 uppercase italic">{t.final.emphasis}</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        {t.final.description}
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href={`/${lang}/beta`} className="px-16 py-8 bg-purple-600 text-white font-black text-3xl rounded-3xl hover:bg-purple-500 transition-all shadow-[0_0_100px_rgba(168,85,247,0.3)] tracking-tighter flex items-center gap-4 group">
                             {t.final.cta} <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                    <Link href={`/${lang}/learn/eu-ai-act-compliance-ai-agents`} className="block text-xs font-black uppercase tracking-widest text-neutral-500 underline underline-offset-8 mt-10">{t.final.guide} &rarr;</Link>
                </div>
            </section>
        </main>
    );
}

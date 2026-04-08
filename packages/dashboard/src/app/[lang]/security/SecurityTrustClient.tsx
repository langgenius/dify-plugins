// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Key, ShieldCheck, ArrowRight, History, 
    Lock, CheckCircle2, CloudLightning, Database, 
    Share2, Zap, LayoutDashboard, Fingerprint, 
    ShieldAlert, Globe, Server, FileText
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

export default function SecurityTrustClient() {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-500/10 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Trust Center</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Built for <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10 uppercase italic">Mission Critical.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Standardize your agentic architecture on our world-class security infrastructure. From SOC2 to zero-knowledge secret injection.
                        </p>
                    </div>
                </div>
            </section>

             {/* 🎯 INFRASTRUCTURE SECTION */}
             <section className="py-24 px-6 md:px-0 bg-black border-y border-white/5 relative">
                <div className="max-w-7xl mx-auto space-y-24">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-20">
                         <div className="flex flex-col justify-center space-y-10 group">
                             <TagBadge>Architecture Resilience</TagBadge>
                             <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter leading-none group-hover:text-glow transition-all">
                                 Total <br />
                                 <span className="text-emerald-500 font-bold italic underline decoration-white/10 italic">Integrity.</span>
                             </h2>
                             <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-relaxed">
                                 The SupraWall SDK is designed with performance and integrity at its core. Our interception nodes are built in Rust, ensuring sub-ms latency while handling millions of tool-call requests and deterministic safety checks every second.
                             </p>
                             <div className="grid grid-cols-1 gap-4">
                                 {[
                                     { title: "Point-to-Point TLS 1.3 Encryption", icon: <Lock className="w-5 h-5 text-emerald-400" /> },
                                     { title: "24/7 Availability Monitoring", icon: <Server className="w-5 h-5 text-emerald-400" /> },
                                     { title: "Automated Pentesting Loops", icon: <ShieldAlert className="w-5 h-5 text-emerald-400" /> }
                                 ].map(item => (
                                     <div key={item.title} className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                                         <div className="p-2 bg-emerald-500/10 rounded-lg group-hover:scale-110 transition-transform">{item.icon}</div>
                                         <p className="text-white text-xs font-black italic uppercase tracking-widest">{item.title}</p>
                                     </div>
                                 ))}
                             </div>
                         </div>
                         <div className="flex items-center justify-center relative">
                             <div className="p-12 bg-neutral-900 border border-white/10 rounded-[4rem] backdrop-blur-3xl shadow-2xl relative overflow-hidden group hover:border-emerald-500/20 transition-all rotate-[2deg] hover:rotate-0">
                                 <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 blur-[80px] pointer-events-none" />
                                 <div className="space-y-10 relative z-10 text-center">
                                     <div className="p-5 bg-white/5 rounded-2xl w-fit mx-auto group-hover:scale-110 transition-transform"><CheckCircle2 className="w-10 h-10 text-emerald-400" /></div>
                                     <div className="space-y-4">
                                         <h4 className="text-center text-4xl font-black italic uppercase italic tracking-tighter leading-none">Security Maturity</h4>
                                         <div className="h-px w-full bg-white/5" />
                                         <div className="grid grid-cols-2 gap-4">
                                            <div className="p-4 rounded-xl bg-white/5 space-y-2 opacity-100 grayscale hover:grayscale-0 transition-all">
                                                <div className="text-[10px] font-black uppercase text-neutral-500 tracking-widest">SOC2 TYPE-II</div>
                                                 <div className="text-[8px] font-bold text-emerald-500">In Progress (Expected Q3)</div>
                                            </div>
                                            <div className="p-4 rounded-xl bg-white/5 space-y-2 grayscale hover:grayscale-0 transition-all">
                                                <div className="text-[10px] font-black uppercase text-neutral-500 tracking-widest">GDPR COMPLIANT</div>
                                                 <div className="text-[8px] font-bold text-emerald-500">Certified Active</div>
                                            </div>
                                         </div>
                                     </div>
                                 </div>
                             </div>
                         </div>
                    </div>
                </div>
            </section>

             {/* 🎯 DATA SHIELD PILLARS */}
             <section className="py-40 px-6">
                <div className="max-w-7xl mx-auto space-y-24 text-center">
                    <div className="space-y-6">
                        <TagBadge>Institutional Standards</TagBadge>
                        <h2 className="text-5xl md:text-[6rem] font-black italic uppercase italic tracking-tighter leading-[0.8] text-glow">
                             Every Sector. <br />
                             <span className="text-neutral-500 font-bold italic underline decoration-white/10 italic font-bold">Total Resilience.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { title: "Zero-Knowledge", desc: "Secret keys never hit our servers. Injection happens in the SDK within your VPC boundary.", icon: <Fingerprint className="w-8 h-8 text-emerald-400" /> },
                            { title: "Immutable Trail", desc: "Every action is hashed and recorded. All logs are signed for regulatory evidence.", icon: <FileText className="w-8 h-8 text-emerald-400" /> },
                            { title: "Deterministic Guard", desc: "Our SDK literally binary-blocks tool calls. Not a &lsquo;suggestion&rsquo; to the agent.", icon: <ShieldCheck className="w-8 h-8 text-emerald-400" /> }
                        ].map((p, i) => (
                            <div key={p.title} className="p-12 rounded-[3.5rem] bg-neutral-900/40 border border-white/5 space-y-8 hover:border-emerald-500/30 transition-all group overflow-hidden relative text-left">
                                <div className="p-4 rounded-xl bg-white/5 border border-white/10 w-fit group-hover:scale-110 transition-transform">{p.icon}</div>
                                <div className="space-y-4">
                                     <h4 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{p.title}</h4>
                                     <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight italic leading-relaxed">{p.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-emerald-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>For Security Teams</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Move Fast. <br />
                        <span className="text-emerald-500 underline decoration-white/20 font-bold italic uppercase italic font-bold">Secure the Future.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t wait for a vendor risk questionnaire. Standardize your autonomous agent safety with SupraWall today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-emerald-600 text-white font-black text-3xl rounded-3xl hover:bg-emerald-500 transition-all shadow-[0_0_100px_rgba(16,185,129,0.3)] tracking-tighter flex items-center gap-4 group">
                             Implement Safety Layer <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

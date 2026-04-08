// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Zap, ShieldCheck, ArrowRight, ShieldAlert, 
    Lock, CheckCircle2, ChevronRight, LayoutDashboard, 
    X, Check, Info, MousePointer2, Layers, Cpu
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

interface CompetitorProps {
    competitor: string;
    focus: string;
}

export default function CompetitorVsClient({ competitor, focus }: CompetitorProps) {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[800px] opacity-10 pointer-events-none text-glow">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-blue-500/10 blur-[150px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>The Showdown</TagBadge>
                    <div className="space-y-6 text-glow-blue">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow-blue">
                             SupraWall vs. <br />
                             <span className="text-blue-500 font-bold italic underline decoration-white/10 italic">{competitor}.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Tools focused on <span className="text-white italic">{focus}</span> leave your <span className="text-white italic">runtime agent actions</span> exposed. SupraWall is the deterministic interception layer for what agents actually DO.
                        </p>
                    </div>
                </div>
            </section>

             {/* ⚔️ COMPARISON TABLE */}
             <section className="py-24 px-6 md:px-0 bg-black border-y border-white/5 relative">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="p-8 md:p-12 bg-neutral-900/40 rounded-[4rem] border border-white/5 overflow-hidden shadow-2xl relative group">
                        <table className="w-full text-left uppercase italic font-bold tracking-tighter">
                            <thead className="border-b border-white/10 text-neutral-500 text-[10px] tracking-widest">
                                <tr>
                                    <th className="pb-8">Capabilities</th>
                                    <th className="pb-8 text-neutral-500">{competitor}</th>
                                    <th className="pb-8 text-blue-500">SupraWall</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5 text-sm md:text-base">
                                {[
                                    { f: "Deterministic Tool Intercept", c: false, s: true },
                                    { f: "SDK-Level PII Scrubbing", c: false, s: true },
                                    { f: "Immutable Audit Records", c: true, s: true },
                                    { f: "Autonomous Budget Caps", c: false, s: true },
                                    { f: "Zero Prompt Dependencies", c: false, s: true }
                                ].map((row, i) => (
                                    <tr key={i} className="group/row hover:bg-white/[0.05] transition-colors">
                                        <td className="py-8 text-white/60 group-hover/row:text-white transition-colors">{row.f}</td>
                                        <td className="py-8"><X className="w-5 h-5 text-rose-500/30" /></td>
                                        <td className="py-8 text-blue-500 shadow-text-glow font-black"><Check className="w-6 h-6" /></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="text-center italic text-neutral-600 text-[10px] font-black uppercase tracking-[0.4em]">Comparison data as of March 2026. Reviewing current feature logs.</div>
                </div>
            </section>

             {/* 🎯 THE DIFFERENTIATION SECTION */}
             <section className="py-40 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                         <div className="p-12 rounded-[4rem] bg-neutral-900/20 border border-white/5 space-y-8 flex flex-col justify-between group hover:border-rose-500/20 transition-all">
                             <div className="space-y-6">
                                <TagBadge>{competitor} Focus</TagBadge>
                                <h3 className="text-4xl font-black italic uppercase italic tracking-tighter leading-none">{focus}</h3>
                                <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-relaxed">
                                    {competitor} specializes in the foundational model layer. This is vital for safety research but lacks the real-world hooks to stop a specific agent from executing a rogue API call in a production environment. 
                                </p>
                             </div>
                             <p className="text-neutral-700 text-[10px] font-black uppercase italic tracking-widest italic font-bold">Incomplete for agentic production fleets.</p>
                         </div>
                         <div className="p-12 rounded-[4rem] bg-blue-500/5 border border-blue-500/20 space-y-8 flex flex-col justify-between group hover:border-blue-500/40 transition-all shadow-glow-blue-slow">
                             <div className="space-y-6">
                                <TagBadge>SupraWall Focus</TagBadge>
                                <h3 className="text-4xl font-black italic text-blue-500 italic tracking-tighter leading-none shadow-text-glow uppercase italic font-bold">Runtime Inteception</h3>
                                <p className="text-white text-lg font-bold italic uppercase tracking-tighter leading-relaxed">
                                    SupraWall focuses on the action. We don&apos;t just scan for threats — we intercept the outbound byte-code. If a tool call violates your policy, we kill it before it leaves the SDK.
                                </p>
                             </div>
                             <p className="text-blue-500 text-[10px] font-black uppercase italic tracking-widest italic font-bold uppercase tracking-widest shadow-text-glow">The only production standard for agents.</p>
                         </div>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-[#030303] relative text-center">
                <div className="absolute inset-0 bg-blue-500/5 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Competitive Swap</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow text-glow-blue">
                        Stop Guessing. <br />
                        <span className="text-blue-500 underline decoration-white/20 font-bold italic underline decoration-white/10 uppercase italic font-bold">Secure the Action.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t build your agentic future on probabilistic vibes. Upgrade to the SupraWall Deterministic SDK today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-blue-600 text-white font-black text-3xl rounded-3xl hover:bg-blue-500 transition-all shadow-[0_0_100px_rgba(59,130,246,0.2)] tracking-tighter flex items-center gap-4 group">
                             Get Your Keys <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Code2, ArrowRight, Zap, Cpu, Lock, 
    ShieldCheck, Terminal, Coffee, Layers, Globe, Key, FileText
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

export default function ForDevelopersClient() {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-500/20 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Developer Landing</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Build Agents Fast. <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10 uppercase italic">Stay Secure.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Stop guessing if your agent is safe. SupraWall is the deterministic security layer that intercepts tool calls at the SDK level. No prompt engineering required.
                        </p>
                    </div>
                </div>
            </section>

             {/* 🎯 THE CODE PROMISE */}
             <section className="py-24 px-6 md:px-0 bg-black border-y border-white/5 relative">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="text-center space-y-6">
                        <TagBadge>Developer Experience</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-none text-glow">
                             One Command. <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10 italic font-bold">Total Security.</span>
                        </h2>
                    </div>

                     <div className="p-12 md:p-20 bg-neutral-900/40 rounded-[4rem] border border-white/5 space-y-12">
                         <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                             <div className="space-y-8">
                                 <h3 className="text-3xl font-black italic uppercase italic tracking-tighter text-white">Universal CLI Tool</h3>
                                 <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">
                                    Whether you use LangChain, CrewAI, AutoGen, or Vercel AI, SupraWall works the same. Wrap your agent in one command and instantly get vault, budget, and policy enforcement.
                                 </p>
                                 <div className="flex flex-wrap gap-4 items-center opacity-60 grayscale hover:grayscale-0 hover:opacity-100 transition-all">
                                     <span className="font-black italic uppercase text-xs tracking-widest text-emerald-500">Works with:</span>
                                     {["LangChain", "CrewAI", "AutoGen", "Vercel AI", "MCP"].map(tag => (
                                         <span key={tag} className="px-4 py-2 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase text-white">{tag}</span>
                                     ))}
                                 </div>
                             </div>
                             <div className="p-8 bg-[#0a0a0a] rounded-[2rem] border border-emerald-500/20 font-mono text-[13px] relative overflow-hidden group shadow-2xl hover:border-emerald-500/50 transition-all cursor-copy" onClick={() => navigator.clipboard.writeText('npx suprawall init')} title="Copy command">
                                <div className="absolute top-4 right-6 text-emerald-500/30 text-[10px] font-black uppercase tracking-widest italic group-hover:text-emerald-500 transition-colors">
                                    CLICK TO COPY
                                </div>
                                <pre className="text-emerald-100/80 leading-loose">
$ npx suprawall init

? Detected: my-agent.ts — secure it? (Y/n) y

[✓] .env updated with SUPRAWALL_API_KEY
[✓] my-agent.ts wrapped with protect()

🛡️  Your agent is now armored.
                                </pre>
                             </div>
                         </div>
                    </div>

                    {/* 🛠️ ARCHITECTURE FLOW */}
                    <div className="py-24 space-y-16">
                        <div className="text-center space-y-6">
                            <TagBadge>How it Works</TagBadge>
                            <h2 className="text-5xl font-black italic uppercase tracking-tighter">SDK-Level <span className="text-emerald-500 underline decoration-white/20 font-bold italic uppercase italic">Oversight Flow.</span></h2>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
                            {[
                                { step: "01", title: "Intercept", desc: "Tool call caught at SDK level.", icon: <Terminal className="w-8 h-8" /> },
                                { step: "02", title: "Govern", desc: "Policy engine run locally.", icon: <ShieldCheck className="w-8 h-8" /> },
                                { step: "03", title: "Enforce", desc: "Action blocked or allowed.", icon: <Zap className="w-8 h-8" /> }
                            ].map(s => (
                                <div key={s.step} className="p-10 rounded-[3rem] bg-neutral-900/20 border border-white/5 space-y-6 group hover:border-emerald-500/30 transition-all">
                                    <div className="p-4 bg-white/5 rounded-2xl w-fit text-emerald-500 group-hover:scale-110 transition-transform">{s.icon}</div>
                                    <div className="space-y-2">
                                        <div className="text-emerald-500 font-black text-2xl tracking-tighter italic">{s.step}</div>
                                        <h4 className="text-2xl font-black italic uppercase text-white tracking-tighter uppercase italic">{s.title}</h4>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase italic tracking-widest">{s.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

             {/* 🎯 DEV-FIRST PILLARS */}
             <section className="py-40 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    <div className="text-center space-y-6">
                        <TagBadge>Why SupraWall?</TagBadge>
                        <h2 className="text-5xl md:text-[6rem] font-black italic uppercase tracking-tighter leading-[0.8] text-glow">
                             Built for <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10 uppercase italic">Modern AI Engineers.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                         {[
                            { title: "No Context Leak", desc: "Security rules never touch the LLM prompt. Zero bypass from indirect injections.", icon: <Lock className="w-8 h-8 text-emerald-400" /> },
                            { title: "Sub-ms Latency", desc: "Local policy evaluation ensures your agents stay fast and responsive.", icon: <Zap className="w-8 h-8 text-blue-400" /> },
                            { title: "Vault Injection", desc: "Inject secrets directly into tool calls. Key rotation handled automatically by the SDK.", icon: <Key className="w-8 h-8 text-rose-400" /> },
                            { title: "Art. 12 Logs", desc: "Satisfy compliance with signed, immutable evidence logs generated locally.", icon: <FileText className="w-8 h-8 text-purple-400" /> }
                         ].map((p, i) => (
                             <div key={p.title} className="p-10 rounded-[3rem] bg-neutral-900/40 border border-white/5 hover:border-emerald-500/30 transition-all group overflow-hidden relative">
                                 <div className="p-4 rounded-xl bg-white/5 border border-white/10 w-fit group-hover:scale-110 transition-transform">{p.icon}</div>
                                 <div className="space-y-4 pt-8">
                                     <h4 className="text-2xl font-black italic uppercase text-white tracking-tighter">{p.title}</h4>
                                     <p className="text-neutral-500 text-xs font-bold uppercase tracking-tight italic leading-relaxed">{p.desc}</p>
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
                    <TagBadge>For Developers</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Arm Your Agents. <br />
                        <span className="text-emerald-500 underline decoration-white/20 font-bold italic uppercase">In One Command.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t build your security from scratch. Standardize your agentic architecture with the industry-standard SDK today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-emerald-600 text-white font-black text-3xl rounded-3xl hover:bg-emerald-500 transition-all shadow-[0_0_100px_rgba(16,185,129,0.3)] tracking-tighter flex items-center gap-4 group">
                             Get Started for Free <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

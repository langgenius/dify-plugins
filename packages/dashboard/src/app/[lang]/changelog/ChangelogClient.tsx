// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Zap, ShieldCheck, ArrowRight, History, 
    Layers, Cpu, Fingerprint, Lock, 
    Plus, Search, Box, Share2, Globe
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

const CHANGELOG_ITEMS = [
    {
        version: "v2.1.0",
        date: "March 18, 2026",
        title: "Deterministic PII Shielding",
        desc: "Automated redaction for PHI/PII in outbound tool calls. Native Article 25 enforcement.",
        type: "FEATURE"
    },
    {
        version: "v2.0.4",
        date: "March 12, 2026",
        title: "CrewAI Parallel Interception",
        desc: "Fixed a race condition when multiple agents in a crew called tools simultaneously.",
        type: "FIX"
    },
    {
        version: "v2.0.0",
        date: "Feb 23, 2026",
        title: "The Zero-Trust SDK Core",
        desc: "Complete rewrite of the SDK core in Rust. 1.2ms average policy latency across all platforms.",
        type: "UPGRADE"
    },
    {
        version: "v1.9.1",
        date: "Feb 05, 2026",
        title: "Signed PDF Evidence Exports",
        desc: "Automated report generation for EU AI Act conformity assessments. Article 12/14 ready.",
        type: "FEATURE"
    }
];

export default function ChangelogClient() {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6 border-b border-white/5">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] bg-rose-500/20 blur-[150px] rounded-full" />
                </div>

                <div className="max-w-4xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>What's New</TagBadge>
                    <h1 className="text-6xl md:text-[80px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                        Moving Fast. <br />
                        <span className="text-rose-500 font-bold italic underline decoration-white/10 uppercase italic">Securing Better.</span>
                    </h1>
                </div>
            </section>

             {/* 🎯 CHANGELOG FEED */}
            <section className="py-24 px-6">
                <div className="max-w-3xl mx-auto space-y-24">
                   {CHANGELOG_ITEMS.map((item, i) => (
                       <div key={item.version} className="relative group pl-12 border-l border-white/10">
                           <div className="absolute top-0 left-[-6px] w-3 h-3 bg-rose-600 rounded-full shadow-[0_0_20px_rgba(225,29,72,0.8)] group-hover:scale-125 transition-transform" />
                           <div className="space-y-6">
                               <div className="flex items-center gap-4">
                                   <span className="text-[10px] font-black uppercase text-rose-500 tracking-widest bg-rose-500/10 px-3 py-1.5 rounded-full">{item.type}</span>
                                   <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">{item.date}</span>
                                   <span className="text-[10px] font-black text-white/50 bg-white/5 px-2 py-1 rounded border border-white/10">{item.version}</span>
                               </div>
                               <h2 className="text-3xl font-black italic uppercase italic tracking-tighter leading-none group-hover:text-rose-400 transition-colors uppercase italic">{item.title}</h2>
                               <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">{item.desc}</p>
                           </div>
                       </div>
                   ))}
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-rose-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Stay in the Loop</TagBadge>
                    <h2 className="text-7xl font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        The Standard <br />
                        <span className="text-rose-500 underline decoration-white/10 font-bold italic underline decoration-white/10 uppercase italic">Never Static.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t build on stagnant tech. Join the world&apos;s most active agentic security community.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-rose-600 text-white font-black text-3xl rounded-3xl hover:bg-rose-500 transition-all shadow-[0_0_100px_rgba(225,29,72,0.3)] tracking-tighter flex items-center gap-4 group">
                             Get Your Keys <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

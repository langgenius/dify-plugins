// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Zap, DollarSign, Bug, ArrowRight, ShieldCheck, 
    Layers, Globe, Briefcase, Heart, Scale
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

const USE_CASE_CARDS = [
    {
        title: "Financial Services",
        href: "/use-cases/financial-services",
        desc: "Automate banking tools with deterministic oversight and KYC/AML compliance.",
        pill: "Finance",
        icon: <Briefcase className="w-8 h-8 text-blue-500" />
    },
    {
        title: "Healthcare Governance",
        href: "/use-cases/healthcare",
        desc: "HIPAA-grade PII scrubbing and audit logs for medical diagnosis agents.",
        pill: "Healthcare",
        icon: <Heart className="w-8 h-8 text-rose-500" />
    },
    {
        title: "Legal AI Oversight",
        href: "/use-cases/legal",
        desc: "Regulator-ready audit trails for firm-wide legal brief automation.",
        pill: "Legal",
        icon: <Scale className="w-8 h-8 text-emerald-500" />
    },
    {
        title: "Runaway Cost Control",
        href: "/use-cases/cost-control",
        desc: "Prevent agents from entering infinite spending loops on expensive models.",
        pill: "Operations",
        icon: <DollarSign className="w-8 h-8 text-amber-500" />
    },
    {
        title: "Prompt Injection Defense",
        href: "/use-cases/prompt-injection",
        desc: "Protect sensitive data from indirect prompt injection via tool exfiltration.",
        pill: "Security",
        icon: <Bug className="w-8 h-8 text-rose-500" />
    }
];

export default function UseCasesHubClient() {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6 border-b border-white/5">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[800px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-amber-500/20 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Real World Defense</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             The Chaos <br />
                             <span className="text-amber-500 font-bold italic underline decoration-white/10 uppercase italic">Intercepted.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             From financial circuit breakers to legal grade auditing, explore how SupraWall protects the most regulated agents on earth.
                        </p>
                    </div>
                </div>
            </section>

             {/* 🎯 CORE USE CASES GRID */}
            <section className="py-24 px-6">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                   {USE_CASE_CARDS.map((art, i) => (
                       <Link 
                            key={art.href} 
                            href={art.href}
                            className="group p-1 bg-neutral-900 border border-white/5 rounded-[4rem] hover:border-amber-500/30 transition-all hover:bg-neutral-900/60 overflow-hidden relative shadow-2xl"
                       >
                            <div className="p-12 space-y-8 h-full flex flex-col justify-between min-h-[400px]">
                                <div className="space-y-6">
                                    <div className="p-4 bg-white/5 rounded-2xl w-fit group-hover:scale-110 transition-transform">{art.icon}</div>
                                    <h3 className="text-4xl font-black italic uppercase text-white tracking-tighter leading-none group-hover:text-amber-400 transition-colors uppercase italic">{art.title}</h3>
                                    <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">{art.desc}</p>
                                </div>
                                <div className="flex items-center gap-2 text-white/50 font-black uppercase tracking-widest text-xs group-hover:text-amber-500 transition-all">
                                    READ CASE STUDY <ArrowRight className="w-4 h-4 ml-2" />
                                </div>
                            </div>
                       </Link>
                   ))}
                </div>
            </section>
        </main>
    );
}

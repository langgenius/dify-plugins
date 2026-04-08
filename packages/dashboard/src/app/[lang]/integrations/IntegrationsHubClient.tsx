// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Cpu, ArrowRight, Zap, Layers, Globe, 
    Share2, Workflow, Box, ShieldCheck, Database
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

const INTEGRATION_CARDS = [
    {
        title: "LangChain",
        href: "/integrations/langchain",
        desc: "Secure LangGraph and LangChain agents with a deterministic SDK interceptor for tools.",
        pill: "Framework",
        color: "emerald"
    },
    {
        title: "CrewAI",
        href: "/integrations/crewai",
        desc: "Add budget limits and credential vault to your autonomous multi-agent crews.",
        pill: "Framework",
        color: "rose"
    },
    {
        title: "AutoGen",
        href: "/integrations/autogen",
        desc: "Stop rogue tool calls and enforce policy boundaries in your Microsoft AutoGen fleets.",
        pill: "Microsoft",
        color: "blue"
    },
    {
        title: "Vercel AI",
        href: "/integrations/vercel",
        desc: "Enterprise governance and PII scrubbing for next-gen Vercel AI SDK applications.",
        pill: "Edge AI",
        color: "neutral"
    },
    {
        title: "Pydantic AI",
        href: "/integrations/pydanticai",
        desc: "Deterministic policy enforcement for static-typed AI agents.",
        pill: "Python Native",
        color: "amber"
    },
    {
        title: "LlamaIndex",
        href: "/integrations/llamaindex",
        desc: "Secure RAG pipelines and data engines with retrieval-level governance.",
        pill: "Data Framework",
        color: "cyan"
    },
    {
        title: "Claude",
        href: "/integrations/claude",
        desc: "Secure computer use and high-autonomy agent tool calls in Anthropic Claude 3.5.",
        pill: "Model",
        color: "orange"
    },
    {
        title: "Stripe",
        href: "/integrations/stripe",
        desc: "Enforce deterministic financial guardrails and limits on autonomous banking tools.",
        pill: "Financial",
        color: "blue"
    },
    {
        title: "OpenRouter",
        href: "/integrations/openrouter",
        desc: "Automatically inject attribution headers and get ranked on the OpenRouter leaderboard.",
        pill: "Routing",
        color: "violet"
    },
    {
        title: "OpenClaw",
        href: "/integrations/openclaw",
        desc: "The native runtime for OpenClaw agents in search and social automation.",
        pill: "Native",
        color: "purple"
    }
];

import { useState } from "react";

export default function IntegrationsHubClient() {
    const [activeFilter, setActiveFilter] = useState("All");

    const filteredIntegrations = activeFilter === "All" 
        ? INTEGRATION_CARDS 
        : INTEGRATION_CARDS.filter(a => a.pill.includes(activeFilter) || (activeFilter === "Frameworks" && a.pill === "Framework"));

    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6 border-b border-white/5">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[800px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-purple-500/20 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Universal Security SDK</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Every Framework. <br />
                             <span className="text-purple-500 font-bold italic underline decoration-white/10 italic">One Command.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             SupraWall is the universal safety layer for the AI ecosystem. Plug into your current stack and stabilize your agents today.
                        </p>
                    </div>

                    {/* Filters */}
                    <div className="flex flex-wrap justify-center gap-4 p-2 bg-neutral-900 border border-white/10 rounded-3xl w-fit">
                        {["All", "Framework", "Model", "Financial", "Edge AI", "Data Framework"].map(f => (
                            <button 
                                key={f}
                                onClick={() => setActiveFilter(f)}
                                className={`px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all ${activeFilter === f ? 'bg-purple-600 text-white shadow-[0_0_20px_rgba(147,51,234,0.4)]' : 'text-neutral-500 hover:text-white'}`}
                            >
                                {f === "Framework" ? "Frameworks" : f === "Model" ? "Models" : f}
                            </button>
                        ))}
                    </div>
                </div>
            </section>

             {/* 🎯 INTEGRATIONS GRID */}
            <section className="py-24 px-6">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {filteredIntegrations.map((art, i) => (
                        <Link 
                            key={art.href} 
                            href={art.href}
                            className="bg-neutral-900/40 p-10 border border-white/5 rounded-[4rem] group hover:border-purple-500/30 transition-all hover:translate-y-[-10px] space-y-8 flex flex-col justify-between"
                        >
                            <div className="space-y-6">
                                <div className="p-3 bg-purple-500/10 rounded-xl text-purple-500 w-fit text-[10px] font-black uppercase tracking-widest">{art.pill}</div>
                                <h3 className="text-4xl font-black italic uppercase text-white tracking-tighter leading-none group-hover:text-purple-400 transition-colors uppercase italic">{art.title}</h3>
                                <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">{art.desc}</p>
                            </div>
                            <div className="flex items-center gap-2 text-white/50 font-black uppercase tracking-widest text-xs group-hover:text-purple-500 transition-all">
                                INTEGRATION GUIDE <ArrowRight className="w-4 h-4" />
                            </div>
                        </Link>
                   ))}
                </div>
            </section>

             {/* 🎯 PLATFORM STATS */}
             <section className="py-40 px-6 bg-black relative border-y border-white/5 overflow-hidden">
                <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-20 relative z-10 text-center">
                    <div className="space-y-4">
                        <div className="text-6xl font-black italic uppercase tracking-tighter text-purple-500">12+</div>
                        <div className="text-sm font-black uppercase tracking-[0.4em] text-neutral-500 italic">Major Frameworks</div>
                    </div>
                    <div className="space-y-4">
                        <div className="text-6xl font-black italic uppercase tracking-tighter text-purple-500">20+</div>
                        <div className="text-sm font-black uppercase tracking-[0.4em] text-neutral-500 italic">Official Models</div>
                    </div>
                    <div className="space-y-4">
                        <div className="text-6xl font-black italic uppercase tracking-tighter text-purple-500">1.2ms</div>
                        <div className="text-sm font-black uppercase tracking-[0.4em] text-neutral-500 italic">Avg. Latency</div>
                    </div>
                </div>
            </section>
        </main>
    );
}

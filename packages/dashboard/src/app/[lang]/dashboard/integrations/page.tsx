// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Grid, Power, ShieldCheck, Cpu, Zap, 
    Workflow, Box, Users, Database, 
    CreditCard, Globe, Layers, Brain,
    ArrowRight
} from "lucide-react";
import Link from "next/link";

export default function IntegrationsDashboardPage() {
    return (
        <div className="space-y-12">
            <div className="space-y-2">
                <h1 className="text-4xl font-black text-white tracking-tight uppercase italic heading-glow">Framework Integrations</h1>
                <p className="text-neutral-400 text-sm">One-click security for your agentic ecosystem.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8">
                {frameworks.map((fw, i) => (
                    <motion.div
                        key={fw.name}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="group p-8 rounded-[32px] bg-neutral-900/50 border border-white/10 hover:border-emerald-500/30 transition-all flex flex-col items-start gap-4 card-hover light-sweep"
                    >
                        <div className="flex items-center justify-between w-full">
                            <div className={`p-3 rounded-2xl ${fw.color} bg-opacity-20 group-hover:ring-2 group-hover:ring-emerald-500/30 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] transition-all duration-300`}>
                                <fw.icon className={`w-6 h-6 ${fw.textColor}`} />
                            </div>
                            {fw.badge && (
                                <span className="text-[8px] font-black uppercase tracking-widest text-neutral-500 border border-white/10 px-2 py-1 rounded-lg">
                                    {fw.badge}
                                </span>
                            )}
                        </div>
                        <div className="space-y-1 mt-2">
                            <h3 className="text-[22px] font-black text-white uppercase italic tracking-tighter group-hover:text-emerald-400 transition-colors">{fw.name}</h3>
                            <p className="text-neutral-500 text-xs font-bold uppercase tracking-tight leading-relaxed">{fw.desc}</p>
                        </div>
                        <div className="w-full h-px bg-emerald-500/10 my-4" />
                        <Link href={fw.href} className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-emerald-400 hover:text-emerald-300 transition-colors">
                            Integration Guide <ArrowRight className="w-3 h-3" />
                        </Link>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

const frameworks = [
    {
        name: "SupraWall Connect",
        desc: "Universal sub-key generator for secure, one-click framework integration.",
        icon: Zap,
        color: "bg-emerald-500",
        textColor: "text-emerald-400",
        href: "/dashboard/integrations/connect",
        badge: "One-Click"
    },
    {
        name: "LangChain",
        desc: "Secure LangGraph and LCEL chains with native @secure decorators.",
        icon: Workflow,
        color: "bg-emerald-500",
        textColor: "text-emerald-400",
        href: "/integrations/langchain",
        badge: "Framework"
    },
    {
        name: "Vercel AI SDK",
        desc: "Zero-latency tool interception and PII scrubbing for Next.js AI apps.",
        icon: Box,
        color: "bg-zinc-800",
        textColor: "text-white",
        href: "/integrations/vercel",
        badge: "Edge AI"
    },
    {
        name: "CrewAI",
        desc: "Govern autonomous agent swarms and enterprise collaboration.",
        icon: Users,
        color: "bg-rose-500",
        textColor: "text-rose-400",
        href: "/integrations/crewai",
        badge: "Multi-Agent"
    },
    {
        name: "Stripe",
        desc: "Enterprise financial guardrails and budget limits for autonomous tools.",
        icon: CreditCard,
        color: "bg-blue-600",
        textColor: "text-blue-300",
        href: "/integrations/stripe",
        badge: "Financial"
    },
    {
        name: "MCP",
        desc: "Model Context Protocol security for standardized tool execution.",
        icon: Layers,
        color: "bg-indigo-600",
        textColor: "text-indigo-300",
        href: "/docs/mcp",
        badge: "Protocol"
    },
    {
        name: "AutoGen",
        desc: "Stop rogue tool calls and enforce policy boundaries in AutoGen fleets.",
        icon: Cpu,
        color: "bg-blue-500",
        textColor: "text-blue-300",
        href: "/integrations/autogen",
        badge: "Microsoft"
    },
    {
        name: "LlamaIndex",
        desc: "Secure RAG pipelines and data engines with retrieval-level governance.",
        icon: Database,
        color: "bg-cyan-600",
        textColor: "text-cyan-300",
        href: "/integrations/llamaindex",
        badge: "Data Engine"
    },
    {
        name: "Claude 3.5",
        desc: "Secure computer use and high-autonomy tool calls in Anthropic agents.",
        icon: Brain,
        color: "bg-orange-600",
        textColor: "text-orange-300",
        href: "/integrations/claude",
        badge: "Model"
    },
    {
        name: "Pydantic AI",
        desc: "Deterministic policy enforcement for static-typed AI agents.",
        icon: ShieldCheck,
        color: "bg-amber-600",
        textColor: "text-amber-300",
        href: "/integrations/pydanticai",
        badge: "Python Native"
    },
    {
        name: "OpenRouter",
        desc: "Inject attribution headers and get ranked on the leaderboard.",
        icon: Globe,
        color: "bg-violet-600",
        textColor: "text-violet-300",
        href: "/integrations/openrouter",
        badge: "Routing"
    },
    {
        name: "OpenClaw",
        desc: "Native browser-environment protection for autonomous browsing.",
        icon: Grid,
        color: "bg-purple-600",
        textColor: "text-purple-300",
        href: "/integrations/openclaw",
        badge: "Browser"
    }
];

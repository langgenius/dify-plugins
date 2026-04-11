// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, BrickWall, BookOpen, Key, Terminal, Code, Cpu, Activity, Lightbulb, ExternalLink, Zap, Puzzle, BadgeDollarSign, Sparkles, Search } from "lucide-react";
import { AskAI } from "@/components/AskAI";

export default function DocsLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const lang = pathname.split('/')[1] || 'en';

    const sections = [
        {
            title: "Getting Started",
            items: [
                { name: "Introduction", href: `/${lang}/docs`, icon: BookOpen },
                { name: "Quickstart", href: `/${lang}/docs/quickstart`, icon: Zap },
                { name: "AI Assistant Guide", href: `/${lang}/docs/ai-assistants`, icon: Sparkles },
            ]
        },
        {
            title: "Client Integrations",
            items: [
                { name: "Python SDK", href: `/${lang}/docs/python`, icon: Terminal },
                { name: "Claude (MCP)", href: `/${lang}/docs/mcp`, icon: Puzzle },
                { name: "Browser (OpenClaw)", href: `/${lang}/docs/integrations/openclaw`, icon: Terminal },
                { name: "GitHub Action", href: `/${lang}/docs/integrations/github-action`, icon: Activity },
                { name: "Stripe Marketplace", href: `/${lang}/docs/integrations/stripe`, icon: BadgeDollarSign },
            ]
        },
        {
            title: "Frameworks (Interactive)",
            items: [
                { name: "LangChain", href: `/${lang}/docs/frameworks/langchain`, icon: Code },
                { name: "LlamaIndex", href: `/${lang}/docs/frameworks/llamaindex`, icon: Code },
                { name: "Vercel AI SDK", href: `/${lang}/docs/frameworks/vercel-ai`, icon: Terminal },
                { name: "AutoGen", href: `/${lang}/docs/frameworks/autogen`, icon: Cpu },
                { name: "CrewAI", href: `/${lang}/docs/frameworks/crewai`, icon: Cpu },
            ]
        },
        {
            title: "Platform",
            items: [
                { name: "API Reference", href: `/${lang}/docs/api`, icon: Key },
                { name: "Policy Patterns", href: `/${lang}/docs/examples`, icon: Lightbulb },
                { name: "Open Spec (AGPS)", href: `/${lang}/spec`, icon: Shield },
            ]
        }
    ];

    return (
        <div className="flex h-screen bg-[#050505] text-white overflow-hidden relative font-sans">
            <aside className="w-64 border-r border-white/5 bg-neutral-950 flex flex-col z-20">
                <div className="h-16 flex items-center px-6 border-b border-white/5 bg-black/40">
                    <BrickWall className="w-6 h-6 text-emerald-500 mr-3" />
                    <Link href="/" className="font-bold text-lg tracking-tight text-white drop-shadow-sm hover:text-emerald-400 transition">
                        SupraWall <span className="text-emerald-500/80">Docs</span>
                    </Link>
                </div>

                <nav className="flex-1 py-6 px-4 flex flex-col gap-6 overflow-y-auto">
                    {sections.map((section) => (
                        <div key={section.title}>
                            <h4 className="px-2 mb-2 text-xs font-semibold text-neutral-500 uppercase tracking-widest">
                                {section.title}
                            </h4>
                            <div className="space-y-1">
                                {section.items.map((item) => {
                                    const Icon = item.icon || Activity;
                                    const isActive = pathname === item.href;
                                    return (
                                        <Link
                                            key={item.href}
                                            href={item.href}
                                            className={`group flex items-center px-3 py-2 rounded-lg transition-all duration-300 ${isActive ? "bg-white/[0.08] text-white shadow-sm ring-1 ring-white/10" : "text-neutral-400 hover:text-white hover:bg-white/[0.04]"
                                                }`}
                                        >
                                            <Icon className={`w-4 h-4 mr-3 transition-transform duration-300 ${isActive ? "text-emerald-400" : "group-hover:text-neutral-200"}`} />
                                            <span className="text-sm font-medium">{item.name}</span>
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </nav>

                <div className="p-4 border-t border-white/5 bg-black/40">
                    <Link href="/dashboard" className="w-full flex items-center justify-center gap-2 text-sm text-neutral-400 hover:text-white transition-colors py-2 border border-white/10 rounded-md hover:bg-white/5">
                        <ExternalLink className="w-4 h-4" /> Go to Dashboard
                    </Link>
                </div>
            </aside>
            <main className="flex-1 overflow-y-auto relative z-10 scroll-smooth">
                <header className="sticky top-0 z-30 h-16 w-full border-b border-white/5 bg-black/80 backdrop-blur-md px-8 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-bold text-neutral-500 uppercase tracking-widest">
                        Documentation / {pathname.split("/").pop() || "Index"}
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-600 group-focus-within:text-emerald-500 transition-colors" />
                            <input 
                                type="text" 
                                placeholder="Search documentation... (⌘K)"
                                className="h-9 w-64 pl-9 pr-4 bg-white/5 border border-white/10 rounded-lg text-xs placeholder:text-neutral-600 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all font-medium"
                            />
                        </div>
                        <AskAI />
                    </div>
                </header>
                <div id="docs-content" className="p-8 md:p-12 max-w-5xl mx-auto min-h-full">
                    {children}
                </div>
            </main>
        </div>
    );
}

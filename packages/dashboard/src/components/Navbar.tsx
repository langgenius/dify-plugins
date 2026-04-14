// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { sendGAEvent } from "@next/third-parties/google";
import { 
    Shield, ArrowRight, ChevronDown, KeyRound, DollarSign, 
    ShieldCheck, EyeOff, FileText, Bug, Book, Workflow, 
    Users, Globe, ShieldAlert, Zap, Layers, Code2, Lock, Github,
    ListCheck
} from "lucide-react";
import Link from "next/link";
import { Locale } from "../i18n/config";

export function Navbar({ lang = 'en', dictionary }: { lang?: Locale, dictionary?: any }) {
    const [openMenu, setOpenMenu] = useState<string | null>(null);

    // Fallback dictionary for safety
    const d = dictionary || {};
    const common = d.common || { starOnGithub: "Star on GitHub", deployOnCloud: "Deploy on Cloud" };
    const navbar = d.navbar || { platform: "Platform", solutions: "Solutions", integrations: "Integrations", resources: "Resources", company: "Company", pricing: "Pricing" };

    const prefix = (href: string) => href.startsWith('http') ? href : `/${lang}${href === '/' ? '' : href}`;

    const features = [
        { href: prefix("/features/vault"), icon: <KeyRound className="w-4 h-4 text-emerald-400" />, label: "Credential Vault", desc: "Zero-knowledge secrets" },
        { href: prefix("/features/budget-limits"), icon: <DollarSign className="w-4 h-4 text-amber-400" />, label: "Budget Limits", desc: "Hard caps on API spend" },
        { href: prefix("/features/policy-engine"), icon: <ShieldCheck className="w-4 h-4 text-blue-400" />, label: "Policy Engine", desc: "Deterministic ALLOW/BLOCK" },
        { href: prefix("/features/pii-shield"), icon: <EyeOff className="w-4 h-4 text-purple-400" />, label: "PII Shield", desc: "Outbound data scrubbing" },
        { href: prefix("/features/audit-trail"), icon: <FileText className="w-4 h-4 text-cyan-400" />, label: "Audit Trail", desc: "Regulator evidence reports" },
        { href: prefix("/features/prompt-shield"), icon: <Bug className="w-4 h-4 text-rose-400" />, label: "Injection Shield", desc: "SDK binary protection" },
        { href: prefix("/compliance-templates"), icon: <ListCheck className="w-4 h-4 text-emerald-400" />, label: "Annex III Templates", desc: "Sector-specific configs" },
    ];

    const resources = [
        { href: prefix("/quickstart"), icon: <Zap className="w-4 h-4 text-yellow-400" />, label: "Quickstart", desc: "30-second security setup" },
        { href: prefix("/docs"), icon: <Book className="w-4 h-4 text-emerald-400" />, label: "Documentation", desc: "SDK guides & API reference" },
        { href: prefix("/integrations"), icon: <Workflow className="w-4 h-4 text-purple-400" />, label: "Frameworks", desc: "LangChain, CrewAI, AutoGen" },
        { href: prefix("/blog"), icon: <FileText className="w-4 h-4 text-rose-400" />, label: "Engineering Blog", desc: "Latest research & insights" },
    ];

    const company = [
        { href: prefix("/about"), icon: <Users className="w-4 h-4 text-neutral-400" />, label: "About Us", desc: "Our mission & philosophy" },
        { href: prefix("/security"), icon: <ShieldAlert className="w-4 h-4 text-emerald-400" />, label: "Trust Center", desc: "Security & Compliance" },
        { href: prefix("/changelog"), icon: <Zap className="w-4 h-4 text-rose-500" />, label: "Changelog", desc: "Product updates" },
    ];

    const solutions = [
        { href: prefix("/for-developers"), icon: <Code2 className="w-4 h-4 text-emerald-400" />, label: "For Developers", desc: "SDK-first security" },
        { href: prefix("/for-compliance-officers"), icon: <ShieldCheck className="w-4 h-4 text-blue-400" />, label: "For Compliance", desc: "Regulator evidence" },
        { href: prefix("/for-enterprise"), icon: <Globe className="w-4 h-4 text-purple-400" />, label: "For Enterprise", desc: "Fleet-wide control" },
        { href: prefix("/gdpr"), icon: <Lock className="w-4 h-4 text-rose-400" />, label: "GDPR & Privacy", desc: "PII protection" },
        { href: prefix("/compliance-templates"), icon: <Shield className="w-4 h-4 text-blue-400" />, label: "Sector Templates", desc: "High-risk AI Act ready" },
    ];

    const integrations = [
        { type: "label", label: navbar.frameworks },
        { href: prefix("/integrations/langchain"), icon: <Workflow className="w-4 h-4 text-emerald-400" />, label: "LangChain", desc: "Secure agent executors" },
        { href: prefix("/integrations/crewai"), icon: <Users className="w-4 h-4 text-amber-400" />, label: "CrewAI", desc: "Task-level governance" },
        { href: prefix("/integrations/autogen"), icon: <Globe className="w-4 h-4 text-blue-400" />, label: "AutoGen", desc: "Multi-agent security" },
        { href: prefix("/integrations/llamaindex"), icon: <Layers className="w-4 h-4 text-cyan-400" />, label: "LlamaIndex", desc: "Data-aware protection" },
        
        { type: "label", label: navbar.platforms },
        { href: prefix("/integrations/stripe"), icon: <DollarSign className="w-4 h-4 text-emerald-500" />, label: "Stripe", desc: "Financial guardrails" },
        { href: prefix("/integrations/claude"), icon: <Zap className="w-4 h-4 text-orange-500" />, label: "Claude / Anthropic", desc: "Computer use security" },
        { href: prefix("/integrations/openclaw"), icon: <Globe className="w-4 h-4 text-purple-400" />, label: "OpenClaw", desc: "Browser-level firewall" },
    ];

    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/60 backdrop-blur-3xl">
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                <Link 
                    href={prefix("/")} 
                    onClick={() => sendGAEvent('event', 'nav_logo_click')}
                    className="flex items-center gap-3 group"
                >
                    <div className="p-1.5 bg-emerald-600 rounded-lg shadow-[0_0_20px_rgba(5,150,105,0.4)] group-hover:scale-110 transition-transform duration-500">
                        <Shield className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-white font-black text-2xl tracking-[-0.05em] uppercase italic">SupraWall</span>
                </Link>

                <div className="hidden md:flex items-center gap-10 text-[11px] font-black uppercase tracking-widest text-glow">
                    <Dropdown 
                        label={navbar.platform} 
                        isOpen={openMenu === "platform"} 
                        onOpen={() => setOpenMenu("platform")} 
                        onClose={() => setOpenMenu(null)}
                        items={features}
                    />

                    <Dropdown 
                        label={navbar.integrations} 
                        isOpen={openMenu === "integrations"} 
                        onOpen={() => setOpenMenu("integrations")} 
                        onClose={() => setOpenMenu(null)}
                        items={integrations}
                    />

                    <Dropdown 
                        label={navbar.solutions} 
                        isOpen={openMenu === "solutions"} 
                        onOpen={() => setOpenMenu("solutions")} 
                        onClose={() => setOpenMenu(null)}
                        items={solutions}
                    />

                    <Dropdown 
                        label={navbar.resources} 
                        isOpen={openMenu === "resources"} 
                        onOpen={() => setOpenMenu("resources")} 
                        onClose={() => setOpenMenu(null)}
                        items={resources}
                    />

                    <Dropdown 
                        label={navbar.company} 
                        isOpen={openMenu === "company"} 
                        onOpen={() => setOpenMenu("company")} 
                        onClose={() => setOpenMenu(null)}
                        items={company}
                    />

                    <Link 
                        href={prefix("/pricing")} 
                        onClick={() => sendGAEvent('event', 'nav_link_click', { path: '/pricing' })}
                        className="text-neutral-500 hover:text-white transition-colors"
                    >
                        {navbar.pricing}
                    </Link>

                    <div className="flex items-center gap-3">
                        <Link
                            href={prefix("/login")}
                            onClick={() => sendGAEvent('event', 'nav_cta_click', { type: 'deploy_cloud' })}
                            className="px-5 py-2.5 bg-white text-black font-black rounded-xl hover:bg-neutral-200 transition-all shadow-[0_4px_20px_rgba(255,255,255,0.15)] active:scale-95 flex items-center gap-2"
                        >
                            {common.deployOnCloud} <ArrowRight className="w-3 h-3" />
                        </Link>
                        <Link 
                            href="https://github.com/wiserautomation/SupraWall" 
                            target="_blank"
                            onClick={() => sendGAEvent('event', 'nav_cta_click', { type: 'self_host' })}
                            className="hidden sm:flex px-5 py-2.5 border border-white/10 text-white font-black rounded-xl hover:bg-white/5 transition-all items-center gap-2"
                        >
                            <Github className="w-4 h-4" /> {common.selfHost}
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}

function Dropdown({ label, isOpen, onOpen, onClose, items }: any) {
    return (
        <div className="relative" onMouseEnter={onOpen} onMouseLeave={onClose}>
            <button className="flex items-center gap-1 text-neutral-500 hover:text-white transition-colors uppercase italic font-bold">
                {label} <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`} />
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 6 }}
                        transition={{ duration: 0.15 }}
                        className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-80 bg-neutral-950 border border-emerald-500/15 rounded-[2.5rem] overflow-hidden shadow-[0_20px_60px_rgba(0,0,0,0.6)] ring-1 ring-white/[0.06] p-2"
                    >
                        {items.map((f: any, i: number) => (
                            f.type === "label" ? (
                                <div key={i} className="px-5 pt-4 pb-2 text-[9px] font-black uppercase tracking-[0.2em] text-neutral-500 italic opacity-50 border-b border-white/5 mb-1">
                                    {f.label}
                                </div>
                            ) : (
                                <Link
                                    key={i}
                                    href={f.href}
                                    onClick={() => sendGAEvent('event', 'nav_dropdown_click', { path: f.href, category: label })}
                                    className={`flex items-start gap-4 px-5 py-3 hover:bg-emerald-500/[0.06] transition-all group rounded-2xl`}
                                >
                                    <div className="mt-0.5 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                                        {f.icon}
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-white text-[10px] font-black uppercase tracking-widest group-hover:text-emerald-400 transition-colors uppercase italic">{f.label}</p>
                                        <p className="text-neutral-500 text-[9px] font-bold normal-case tracking-tight leading-relaxed uppercase italic opacity-80">{f.desc}</p>
                                    </div>
                                </Link>
                            )
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

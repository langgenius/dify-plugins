// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Key, DollarSign, ShieldCheck, EyeOff, FileText, Bug, 
    ArrowRight, Zap, Target, Lock, LayoutDashboard, Globe
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { TagBadge } from "@/app/HomeClient";

export default function FeaturesClient({ dictionary }: { dictionary: any }) {
    const params = useParams();
    const lang = (params?.lang as string) || 'en';
    const t = dictionary.features;
    const common = dictionary.common;

    const FEATURE_CARDS = [
        {
            id: "vault",
            title: t.pillars.vault.title,
            desc: t.pillars.vault.desc,
            icon: <Key className="w-8 h-8 text-emerald-400" />,
            href: "/features/vault",
            color: "emerald"
        },
        {
            id: "budget-limits",
            title: t.pillars.budget.title,
            desc: t.pillars.budget.desc,
            icon: <DollarSign className="w-8 h-8 text-amber-400" />,
            href: "/features/budget-limits",
            color: "amber"
        },
        {
            id: "policy-engine",
            title: t.pillars.policy.title,
            desc: t.pillars.policy.desc,
            icon: <ShieldCheck className="w-8 h-8 text-blue-400" />,
            href: "/features/policy-engine",
            color: "blue"
        },
        {
            id: "pii-shield",
            title: t.pillars.pii.title,
            desc: t.pillars.pii.desc,
            icon: <EyeOff className="w-8 h-8 text-purple-400" />,
            href: "/features/pii-shield",
            color: "purple"
        },
        {
            id: "audit-trail",
            title: t.pillars.audit.title,
            desc: t.pillars.audit.desc,
            icon: <FileText className="w-8 h-8 text-cyan-400" />,
            href: "/features/audit-trail",
            color: "cyan"
        },
        {
            id: "prompt-shield",
            title: t.pillars.prompt.title,
            desc: t.pillars.prompt.desc,
            icon: <Bug className="w-8 h-8 text-rose-400" />,
            href: "/features/prompt-shield",
            color: "rose"
        }
    ];

    return (
        <main className="overflow-hidden">
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-500/20 blur-[150px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>{t.hero.badge}</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             {t.hero.title} <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10">{t.hero.emphasis}</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             {t.hero.description}
                        </p>
                    </div>
                </div>
            </section>

            <section className="py-20 px-6 bg-black">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {FEATURE_CARDS.map((f, i) => (
                            <Link 
                                key={f.id} 
                                href={f.href}
                                className="group relative block p-10 rounded-[3rem] bg-neutral-900/40 border border-white/10 hover:border-emerald-500/30 transition-all overflow-hidden"
                            >
                                <div className={`absolute top-0 right-0 w-32 h-32 blur-[60px] opacity-10 group-hover:opacity-20 transition-opacity bg-${f.color}-500`} />
                                
                                <div className="relative z-10 space-y-8">
                                    <div className="p-4 rounded-2xl w-fit bg-white/5 border border-white/10 group-hover:scale-110 transition-transform">
                                        {f.icon}
                                    </div>
                                    <div className="space-y-4">
                                        <h3 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{f.title}</h3>
                                        <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight leading-relaxed italic">{f.desc}</p>
                                    </div>
                                    <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.2em] text-emerald-500 pt-4 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">
                                        {t.pillars.cta} <ArrowRight className="w-4 h-4" />
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

             {/* 🎯 THE GRAND SLAM CONVERGENCE */}
             <section className="py-40 px-6 bg-[#030303] border-y border-white/5">
                <div className="max-w-7xl mx-auto text-center space-y-24">
                    <div className="space-y-6">
                        <TagBadge>{t.convergence.badge}</TagBadge>
                        <h2 className="text-5xl md:text-[8rem] font-black italic tracking-tighter leading-[0.85] uppercase text-glow">
                             {t.convergence.title} <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10">{t.convergence.emphasis}</span>
                        </h2>
                    </div>

                     <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                         <div className="p-12 rounded-[4rem] bg-neutral-900/20 border border-white/5 space-y-8 text-left group hover:border-blue-500/30 transition-all">
                             <div className="flex items-center gap-4">
                                 <div className="p-4 bg-blue-500/10 rounded-2xl text-blue-400 group-hover:scale-110 transition-transform">
                                     <LayoutDashboard className="w-8 h-8" />
                                 </div>
                                 <h4 className="text-3xl font-black italic uppercase text-white">{t.convergence.dashboard.title}</h4>
                             </div>
                             <p className="text-neutral-500 text-lg leading-relaxed font-bold italic uppercase tracking-tighter">
                                 {t.convergence.dashboard.desc}
                             </p>
                             <Link href={`/${lang}/dashboard`} className="inline-flex items-center gap-2 text-blue-500 font-black uppercase tracking-widest text-sm hover:text-blue-400 transition-colors uppercase italic">{t.convergence.dashboard.cta} →</Link>
                         </div>
                         <div className="p-12 rounded-[4rem] bg-neutral-900/20 border border-white/5 space-y-8 text-left group hover:border-purple-500/30 transition-all">
                             <div className="flex items-center gap-4">
                                 <div className="p-4 bg-purple-500/10 rounded-2xl text-purple-400 group-hover:scale-110 transition-transform">
                                     <Globe className="w-8 h-8" />
                                 </div>
                                 <h4 className="text-3xl font-black italic uppercase text-white">{t.convergence.universal.title}</h4>
                             </div>
                             <p className="text-neutral-500 text-base leading-relaxed font-bold italic uppercase tracking-tighter">
                                 {t.convergence.universal.desc}
                             </p>
                             <Link href="/integrations" className="inline-flex items-center gap-2 text-purple-500 font-black uppercase tracking-widest text-sm hover:text-purple-400 transition-colors uppercase italic">{t.convergence.universal.cta} →</Link>
                         </div>
                    </div>

                    {/* 🛠️ TECHNICAL DEEP DIVE SECTION */}
                    <div className="py-24 space-y-16">
                        <div className="text-center space-y-6">
                            <TagBadge>{t.howItWorks.badge}</TagBadge>
                            <h2 className="text-5xl font-black italic uppercase tracking-tighter">{t.howItWorks.title} <span className="text-emerald-500">{t.howItWorks.emphasis}</span></h2>
                        </div>
                        <div className="max-w-4xl mx-auto p-12 bg-neutral-900/40 border border-white/10 rounded-[3rem] text-left space-y-10 relative overflow-hidden group">
                             <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:rotate-12 transition-transform"><Target className="w-48 h-48" /></div>
                             <div className="space-y-6 relative z-10">
                                 <p className="text-white text-xl font-bold italic uppercase tracking-tighter leading-relaxed">
                                     {t.howItWorks.p}
                                 </p>
                                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                     {[
                                         { step: "01", title: t.howItWorks.steps.s1.title, desc: t.howItWorks.steps.s1.desc },
                                         { step: "02", title: t.howItWorks.steps.s2.title, desc: t.howItWorks.steps.s2.desc },
                                         { step: "03", title: t.howItWorks.steps.s3.title, desc: t.howItWorks.steps.s3.desc }
                                     ].map(s => (
                                         <div key={s.step} className="p-6 rounded-2xl bg-white/5 border border-white/5">
                                             <div className="text-emerald-500 font-black text-2xl mb-2">{s.step}</div>
                                             <div className="text-white text-xs font-black uppercase tracking-widest mb-1">{s.title}</div>
                                             <div className="text-neutral-500 text-[10px] font-bold uppercase italic">{s.desc}</div>
                                         </div>
                                     ))}
                                 </div>
                             </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-emerald-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>{t.final.badge}</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                         {t.final.title} <br />
                         <span className="text-emerald-500 underline decoration-white/20 font-bold italic">{t.final.emphasis}</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                         {t.final.description}
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href={`/${lang}/beta`} className="px-16 py-8 bg-emerald-600 text-white font-black text-3xl rounded-3xl hover:bg-emerald-500 transition-all shadow-[0_0_100px_rgba(16,185,129,0.3)] tracking-tighter flex items-center gap-4 group">
                             {t.final.cta} <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
             {/* ⚡ TRY IN 30 SECONDS */}
             <section className="py-24 px-6 bg-[#030303] border-t border-white/5 relative z-10 text-center">
                <div className="max-w-4xl mx-auto space-y-12">
                    <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter text-glow">
                        {t.try.title} <span className="text-emerald-500 underline decoration-white/10">{t.try.emphasis}</span>
                    </h2>
                    <p className="text-xl md:text-2xl text-neutral-400 font-medium italic max-w-2xl mx-auto">
                        {t.try.description}
                    </p>
                    <div className="p-6 md:p-8 bg-[#0a0a0a] rounded-[2rem] border border-emerald-500/20 font-mono text-[13px] relative overflow-hidden group shadow-[0_0_80px_rgba(16,185,129,0.15)] text-left cursor-copy mx-auto max-w-2xl hover:border-emerald-500/50 transition-all" onClick={() => navigator.clipboard && navigator.clipboard.writeText('npx suprawall init')} title="Copy command">
                        <div className="absolute top-4 right-6 text-emerald-500/30 text-[10px] font-black uppercase tracking-widest italic group-hover:text-emerald-500 transition-colors">
                            {t.try.copy}
                        </div>
                        <pre className="text-emerald-100/80 leading-loose">
$ npx suprawall init

? {t.try.terminal.detected}: my-agent.ts — {t.try.terminal.secure} (Y/n) y

[✓] {t.try.terminal.env}
[✓] {t.try.terminal.wrapped}

🛡️  {t.try.terminal.footer}
                        </pre>
                    </div>
                </div>
            </section>
        </main>

    );
}

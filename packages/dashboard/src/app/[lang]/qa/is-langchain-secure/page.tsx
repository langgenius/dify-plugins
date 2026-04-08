// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { Locale } from "@/i18n/config";
import { getDictionary } from "../../../../i18n/getDictionary";
import { Shield, CheckCircle2, Terminal } from "lucide-react";
import Link from "next/link";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
    const { lang } = (await params) as { lang: Locale };
    const dictionary = await getDictionary(lang);
    return {
        title: `${dictionary.qa.isLangChainSecure.title} | Quick Security Answer`,
        description: dictionary.qa.isLangChainSecure.answer.substring(0, 155) + "...",
        robots: "index, follow",
    };
}

export default async function IsLangChainSecurePage({
    params,
}: {
    params: Promise<{ lang: string }>;
}) {
    const { lang } = (await params) as { lang: Locale };
    const dictionary = await getDictionary(lang);

    return (
        <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30">
            <Navbar lang={lang} dictionary={dictionary} />

            <main className="pt-48 pb-32 px-6">
                <div className="max-w-3xl mx-auto space-y-12">
                    
                    {/* 🎯 PRECISION ANSWER BOX */}
                    <section className="p-12 rounded-[3rem] bg-emerald-500/5 border-2 border-emerald-500/20 shadow-[0_0_100px_rgba(16,185,129,0.1)] relative">
                        <div className="absolute top-0 right-0 p-6 opacity-10"><Shield className="w-12 h-12" /></div>
                        
                        <h1 className="text-4xl font-black uppercase italic tracking-tighter mb-8">{dictionary.qa.isLangChainSecure.title}</h1>
                        
                        <p className="answer-first-paragraph text-2xl text-neutral-200 leading-snug font-medium italic border-l-4 border-emerald-500 pl-8">
                            {dictionary.qa.isLangChainSecure.answer}
                        </p>
                    </section>

                    {/* 📋 KEY VULNERABILITIES */}
                    <section className="space-y-8 pt-12">
                        <h2 className="text-[10px] font-black uppercase tracking-[0.5em] text-neutral-600">{dictionary.common.title}</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {[
                                { title: dictionary.qa.isLangChainSecure.risk1Title, desc: dictionary.qa.isLangChainSecure.risk1Desc, icon: <Terminal className="w-4 h-4" /> },
                                { title: dictionary.qa.isLangChainSecure.risk2Title, desc: dictionary.qa.isLangChainSecure.risk2Desc, icon: <Shield className="w-4 h-4" /> }
                            ].map((risk, i) => (
                                <div key={i} className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 space-y-4">
                                     <div className="p-2 bg-rose-500/10 rounded-lg w-fit text-rose-500">{risk.icon}</div>
                                     <p className="font-bold text-white uppercase text-sm tracking-tight">{risk.title}</p>
                                     <p className="text-xs text-neutral-500 leading-relaxed font-medium">{risk.desc}</p>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* 🛡️ HARDENING SOLUTION */}
                    <div className="my-16 p-10 rounded-[2.5rem] bg-emerald-500/5 border border-emerald-500/20 space-y-8">
                         <div className="flex items-center gap-4 text-emerald-400">
                             <CheckCircle2 className="w-8 h-8" />
                             <h3 className="text-2xl font-black uppercase italic tracking-tight">{dictionary.qa.isLangChainSecure.solutionTitle}</h3>
                         </div>
                         <p className="text-neutral-400 font-medium italic leading-relaxed">
                             {dictionary.qa.isLangChainSecure.solutionP}
                         </p>
                    </div>

                    {/* CTA */}
                    <div className="pt-12 text-center">
                        <Link href={`/${lang}/integrations/langchain`} className="text-xs font-black uppercase tracking-[0.3em] text-neutral-500 hover:text-white transition-colors underline underline-offset-8">
                            {dictionary.qa.isLangChainSecure.guideLink} &rarr;
                        </Link>
                    </div>

                </div>
            </main>
        </div>
    );
}

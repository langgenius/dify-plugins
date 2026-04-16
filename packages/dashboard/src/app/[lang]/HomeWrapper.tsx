// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { sendGAEvent } from "@next/third-parties/google";
import {
    ArrowRight,
    Github
} from "lucide-react";
import Link from "next/link";
import { SwarmVisualization, TechTabs, TagBadge, AttackDemo, LiveSavings, ThreatCardsGrid, ICPEntryPoints, ComplianceTemplatesSection, ResourceHub } from "@/app/HomeClient";
import { Locale } from "@/i18n/config";

export default function HomeWrapper({ dictionary, lang }: { dictionary: any, lang: Locale }) {
    // Note: In Phase 2, we will replace these hardcoded strings with dictionary.home.*
    
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "SupraWall",
        "url": `https://www.supra-wall.com/${lang}`,
        "description": dictionary.common.description,
        "applicationCategory": "SecurityApplication",
        "operatingSystem": "Any",
        "author": {
            "@type": "Organization",
            "name": "SupraWall"
        }
    };

    return (
        <div className="min-h-screen bg-[#000000] text-neutral-200 font-sans selection:bg-emerald-500/30 selection:text-white">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <Navbar lang={lang} dictionary={dictionary} />

            <main className="overflow-hidden">
                <section className="relative pt-48 pb-32 px-6">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-20 pointer-events-none">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-600/30 blur-[180px] rounded-full" />
                    </div>

                    <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                        <div className="animate-fade-in inline-flex items-center px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-[10px] font-black tracking-[0.2em] text-emerald-400 uppercase">
                            <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 mr-3 animate-pulse"></span>
                            {dictionary.home.hero.badge}
                        </div>

                        <div className="space-y-8">
                            <h1 className="text-6xl md:text-[110px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow filter drop-shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                                {dictionary.home.hero.headlinePrefix} <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600">{dictionary.home.hero.headlineEmphasis}</span> <br />
                                {dictionary.home.hero.headlineSuffix} <br />
                                <span className="underline decoration-emerald-800">{dictionary.home.hero.headlineAction}</span>
                            </h1>

                            <div className="text-xl md:text-2xl text-neutral-400 max-w-5xl mx-auto leading-relaxed font-medium">
                                <span className="text-white font-bold">{dictionary.home.features.vault}</span> {dictionary.home.features.vaultDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.cap}</span> {dictionary.home.features.capDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.block}</span> {dictionary.home.features.blockDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.scrub}</span> {dictionary.home.features.scrubDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.generate}</span> {dictionary.home.features.generateDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.stop}</span> {dictionary.home.features.stopDesc}{' '}
                                <span className="text-white font-bold">{dictionary.home.features.analyze}</span> {dictionary.home.features.analyzeDesc}{' '}
                                <br className="hidden md:block" />
                                <span className="text-emerald-400 italic">{dictionary.home.hero.subheadline}</span>
                            </div>
                            
                            <div className="flex flex-col sm:flex-row items-center gap-6 pt-4">
                                <Link
                                    id="cta-deploy-cloud"
                                    href={`/${lang}/beta`}
                                    onClick={() => sendGAEvent('event', 'hero_cta_click', { type: 'deploy_cloud' })}
                                    className="px-14 py-6 bg-white text-black font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-emerald-500 hover:text-white transition-all transform hover:scale-105 shadow-[0_20px_40px_rgba(255,255,255,0.15)] group flex items-center gap-3"
                                >
                                    {dictionary.home.hero.cta} <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                                </Link>
                                <Link
                                    id="cta-star-github"
                                    href="https://github.com/wiserautomation/SupraWall"
                                    target="_blank"
                                    prefetch={false}
                                    rel="noopener noreferrer"
                                    onClick={() => sendGAEvent('event', 'hero_cta_click', { type: 'star_github' })}
                                    className="px-14 py-6 border-2 border-white/10 text-white font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-white/5 transition-all flex items-center gap-3"
                                >
                                    <Github className="w-6 h-6" /> {dictionary.common.starOnGithub}
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="bg-black border-b border-white/5">
                    <div className="max-w-7xl mx-auto px-6">
                        <LiveSavings />
                    </div>
                </section>

                <section id="threats" className="py-40 px-6 bg-black relative overflow-hidden">
                    <ThreatCardsGrid />
                </section>

                <ComplianceTemplatesSection />

                <section id="how-it-works" className="py-40 px-6 bg-black">
                    <div className="max-w-7xl mx-auto space-y-24">
                         <TechTabs />
                    </div>
                </section>

                <section className="py-40 px-6 bg-[#030303] border-y border-white/5 relative overflow-hidden">
                    <ICPEntryPoints />
                </section>

                <ResourceHub lang={lang} />
            </main>

            <Footer />
        </div>
    );
}

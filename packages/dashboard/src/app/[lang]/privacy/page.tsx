// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { Shield, Lock, Eye, FileText, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";
import { Locale } from "@/i18n/config";

export const metadata: Metadata = {
    title: "Privacy Policy | SupraWall",
    description: "SupraWall Privacy Policy — How we handle data for AI agent security and compliance.",
};

export default async function PrivacyPage({
    params,
}: {
    params: Promise<{ lang: string }>;
}) {
    const { lang } = (await params) as { lang: Locale };
    return (
        <div className="min-h-screen bg-[#000000] text-neutral-200 font-sans selection:bg-emerald-500/30 selection:text-white">
            <Navbar lang={lang} />
            
            <main className="pt-32 pb-24 px-6">
                <div className="max-w-4xl mx-auto space-y-16">
                    {/* Header */}
                    <div className="space-y-6 text-center">
                        <div className="inline-flex items-center px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-[10px] font-black tracking-[0.2em] text-emerald-400 uppercase">
                            Legal & Compliance
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic">
                            Privacy <span className="text-emerald-500">Policy</span>
                        </h1>
                        <p className="text-neutral-500 font-bold uppercase tracking-widest text-sm">
                            Last Updated: March 20, 2026
                        </p>
                    </div>

                    {/* Content */}
                    <div className="space-y-12 bg-neutral-900/30 border border-white/5 p-10 md:p-16 rounded-[3rem] backdrop-blur-3xl">
                        
                        <section className="space-y-4">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <Shield className="w-6 h-6" />
                                <h2 className="text-xl font-black uppercase italic tracking-tight">Introduction</h2>
                            </div>
                            <p className="text-neutral-400 leading-relaxed font-medium italic">
                                SupraWall ("we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard data when you use our AI agent security platform, including our MCP plugins, SDKs, and dashboard.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <Eye className="w-6 h-6" />
                                <h2 className="text-xl font-black uppercase italic tracking-tight">Data Collection</h2>
                            </div>
                            <div className="space-y-4 text-neutral-400 leading-relaxed font-medium italic">
                                <p>To provide security and compliance services for AI agents, we collect the following types of information:</p>
                                <ul className="list-disc pl-6 space-y-2">
                                    <li><span className="text-white font-bold">Account Information:</span> Name, email, and organization details provided during signup.</li>
                                    <li><span className="text-white font-bold">Agent Telemetry:</span> Tool names, metadata, and risk scores generated during security evaluations.</li>
                                    <li><span className="text-white font-bold">Audit Logs:</span> Historical records of tool executions and policy decisions for compliance reporting.</li>
                                    <li><span className="text-white font-bold">Security Credentials:</span> API keys and vault tokens (encrypted at rest, zero-knowledge where applicable).</li>
                                </ul>
                            </div>
                        </section>

                        <section className="space-y-4">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <Lock className="w-6 h-6" />
                                <h2 className="text-xl font-black uppercase italic tracking-tight">How We Use Data</h2>
                            </div>
                            <p className="text-neutral-400 leading-relaxed font-medium italic">
                                We process data primarily to enforce security policies and generate compliance documentation. This includes:
                            </p>
                            <ul className="list-disc pl-6 space-y-2 text-neutral-400 leading-relaxed font-medium italic">
                                <li>Real-time evaluation of tool calls against user-defined policies.</li>
                                <li>Generating EU AI Act-compliant evidence logs (Art. 12 & 14).</li>
                                <li>Detecting anomalous agent behavior and infinite loops.</li>
                                <li>Providing human-in-the-loop approval workflows.</li>
                            </ul>
                        </section>

                        <section className="space-y-4">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <FileText className="w-6 h-6" />
                                <h2 className="text-xl font-black uppercase italic tracking-tight">Data Retention & Security</h2>
                            </div>
                            <p className="text-neutral-400 leading-relaxed font-medium italic">
                                We implement industry-standard security measures, including AES-256 encryption for secrets at rest and TLS 1.3 for data in transit. Retention periods depend on your subscription tier (up to 90 days for standard logs, custom for Enterprise).
                            </p>
                        </section>

                        <section className="space-y-4 pt-8 border-t border-white/10">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <ArrowLeft className="w-6 h-6" />
                                <Link href={`/${lang}`} className="text-sm font-black uppercase tracking-widest hover:text-white transition-colors">
                                    Back to Home
                                </Link>
                            </div>
                        </section>
                    </div>

                    <footer className="text-center text-[10px] font-black uppercase tracking-[0.4em] text-neutral-600 italic">
                        © 2026 SUPRAWALL • SECURING THE AI FRONTIER • GDPR COMPLIANT
                    </footer>
                </div>
            </main>
        </div>
    );
}

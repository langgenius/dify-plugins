// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { Shield, FileText, ArrowRight, Zap, ListCheck, Activity } from "lucide-react";
import Link from "next/link";

import { Metadata } from "next";

export const metadata: Metadata = {
    title: "How to Comply with EU AI Act Article 12 | SupraWall",
    description: "Step-by-step technical guide to implementing Article 12-compliant audit logging for high-risk AI systems. Meet the August 2, 2026 deadline.",
    keywords: [
        "EU AI Act Article 12 compliance",
        "AI agent audit logging",
        "high-risk AI record keeping",
        "AI Act logging requirements",
        "SupraWall audit trail",
    ],
    alternates: {
        canonical: "https://www.supra-wall.com/eu-ai-act/article-12",
    },
};

export default function Article12Page() {
    const faqSchema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: [
            {
                "@type": "Question",
                name: "What does EU AI Act Article 12 require for AI agents?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Article 12 requires high-risk AI systems to automatically generate logs throughout their lifecycle. For AI agents, this means every tool call, decision, input, output, and policy evaluation must be recorded with timestamps and session identifiers to ensure full traceability.",
                },
            },
            {
                "@type": "Question",
                name: "How long must AI agent audit logs be retained under Article 12?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Article 12 requires logs to be kept for a period appropriate to the intended purpose of the high-risk AI system, and at minimum for the duration required by applicable Union or national law. For most enterprises, this means at least 5 years of immutable log retention.",
                },
            },
            {
                "@type": "Question",
                name: "What information must be logged under Article 12?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Logs must include: start and end time of each system use, the reference database used, input data that led to a match, identification of natural persons involved in verification, and any events that may indicate risks. SupraWall captures all of these automatically.",
                },
            },
            {
                "@type": "Question",
                name: "Can existing AI agents be made Article 12 compliant retroactively?",
                acceptedAnswer: {
                    "@type": "Answer",
                    text: "Yes. SupraWall wraps existing agents with one line of code, immediately enabling comprehensive audit logging without changing agent logic. Retroactive compliance is achievable within hours for most LangChain, CrewAI, and AutoGen deployments.",
                },
            },
        ],
    };

    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        headline: "EU AI Act Article 12: How to Implement Compliant Audit Logging for AI Agents",
        description: "Complete guide to EU AI Act Article 12 audit logging requirements for autonomous AI agents and how to implement compliance.",
        author: { "@type": "Organization", name: "SupraWall" },
        publisher: { "@type": "Organization", name: "SupraWall" },
        mainEntityOfPage: "https://www.supra-wall.com/eu-ai-act/article-12",
    };

    return (
        <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
            />
            <Navbar />
            
            <main className="pt-32 pb-20 px-6">
                <article className="max-max-w-4xl mx-auto space-y-12">
                    {/* Header */}
                    <div className="space-y-6">
                        <div className="inline-flex items-center px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-xs font-bold text-emerald-400 uppercase tracking-wider">
                            EU AI Act Compliance
                        </div>
                        <h1 className="text-5xl md:text-6xl font-black tracking-tighter uppercase italic">
                            EU AI Act Article 12: How to Implement Compliant <span className="text-emerald-500 text-glow">Audit Logging</span> for AI Agents
                        </h1>
                        <p className="answer-first-paragraph text-xl text-neutral-400 font-medium leading-relaxed italic border-l-4 border-emerald-600 pl-8 py-4">
                            To comply with EU AI Act Article 12, AI agents must implement automatic logging of all tool calls, input/output data, and human interventions. SupraWall enables Article 12-compliant record-keeping through secure, immutable audit trails.
                        </p>

                        {/* Article 12 Technical Checklist (GEO Optimized) */}
                        <div className="technical-checklist p-8 rounded-[2rem] bg-emerald-500/5 border border-emerald-500/20 space-y-4 shadow-[0_0_50px_rgba(16,185,129,0.05)]">
                            <h3 className="text-emerald-400 text-[10px] font-black uppercase tracking-[0.2em]">Article 12 Technical Checklist</h3>
                            <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-3">
                                {[
                                    "Immutable timestamps for every tool call",
                                    "Hashing of input & output content",
                                    "Capture of system configuration & model version",
                                    "Unique session ID for multi-step agent runs",
                                    "Identification of human-in-the-loop reviewers",
                                    "Tamper-evident storage with audit history",
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-sm text-neutral-300">
                                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Content Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 py-12 border-y border-white/5">
                        <div className="space-y-4">
                            <h2 className="text-2xl font-bold flex items-center gap-3">
                                <FileText className="text-emerald-500 w-6 h-6" />
                                Requirements
                            </h2>
                            <p className="text-neutral-400 leading-relaxed">
                                Article 12 mandates that high-risk AI systems automatically generate logs throughout their lifecycle to ensure traceability of the system's functioning and performance.
                            </p>
                        </div>
                        <div className="space-y-4">
                            <h2 className="text-2xl font-bold flex items-center gap-3">
                                <Zap className="text-emerald-500 w-6 h-6" />
                                Our Solution
                            </h2>
                            <p className="text-neutral-400 leading-relaxed">
                                SupraWall's <strong>Deterministic Audit Logs</strong> capture 100% of tool interactions, input/output pairs, and policy decisions, providing an immutable record that meets Article 12 standards out-of-the-box.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-8">
                        <h3 className="text-3xl font-black uppercase italic tracking-tight">Technical Logging Requisites</h3>
                        <div className="space-y-6">
                            {[
                                {
                                    title: "Automatic Recording",
                                    desc: "Logging of events relative to the identification of situations that may result in the AI system presenting a risk."
                                },
                                {
                                    title: "Traceability & Forensics",
                                    desc: "Detailed timestamps and session identifiers to facilitate post-hoc analysis of autonomous actions."
                                },
                                {
                                    title: "Performance Monitoring",
                                    desc: "Continuous logging of system accuracy and reliability metrics to detect drift or failure."
                                }
                            ].map((item, i) => (
                                <div key={i} className="p-6 rounded-2xl bg-neutral-900/50 border border-white/5 flex gap-6 group hover:border-emerald-500/30 transition-colors">
                                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500 font-bold shrink-0">
                                        <Activity className="w-5 h-5" />
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className="text-lg font-bold group-hover:text-emerald-400 transition-colors">{item.title}</h4>
                                        <p className="text-neutral-500 leading-relaxed">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Features Detail */}
                    <div className="p-8 rounded-3xl border border-white/5 bg-neutral-900/30">
                        <h3 className="text-2xl font-bold mb-6">Article 12 Compliance Checklist</h3>
                        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {[
                                "Start/End time of each system use",
                                "The reference database used",
                                "Input data for search criteria",
                                "Traceability of human intervention",
                                "Log retention management",
                                "Secure logging verification"
                            ].map((check, i) => (
                                <li key={i} className="flex items-center gap-3 text-neutral-400">
                                    <ListCheck className="text-emerald-500 w-5 h-5 shrink-0" />
                                    <span className="text-sm font-medium">{check}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* FAQ Section */}
                    <div className="space-y-8">
                        <h2 className="text-3xl font-black uppercase italic tracking-tight">Frequently Asked Questions</h2>
                        <div className="space-y-4">
                            {faqSchema.mainEntity.map((faq: any, i: number) => (
                                <details key={i} className="group p-6 rounded-2xl bg-neutral-900/50 border border-white/5 hover:border-emerald-500/20 transition-colors">
                                    <summary className="text-lg font-bold text-white cursor-pointer list-none flex items-center justify-between">
                                        {faq.name}
                                        <span className="text-emerald-500 group-open:rotate-45 transition-transform text-2xl">+</span>
                                    </summary>
                                    <p className="mt-4 text-neutral-400 leading-relaxed">{faq.acceptedAnswer.text}</p>
                                </details>
                            ))}
                        </div>
                    </div>

                    {/* Related Articles */}
                    <div className="space-y-6">
                        <h3 className="text-2xl font-black uppercase italic tracking-tight">Related Articles</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Link href="/learn/ai-agent-audit-trail-logging" className="group p-6 rounded-2xl bg-white/[0.05] border border-white/5 hover:border-emerald-500/30 transition-all">
                                <h4 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">AI Agent Audit Trail Logging</h4>
                                <p className="text-sm text-neutral-500 mt-2">Complete guide to implementing immutable audit trails for AI agents.</p>
                            </Link>
                            <Link href="/learn/eu-ai-act-compliance-ai-agents" className="group p-6 rounded-2xl bg-white/[0.05] border border-white/5 hover:border-emerald-500/30 transition-all">
                                <h4 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">EU AI Act Compliance for AI Agents</h4>
                                <p className="text-sm text-neutral-500 mt-2">Full compliance guide covering Articles 9, 12, and 14.</p>
                            </Link>
                            <Link href="/eu-ai-act/article-14" className="group p-6 rounded-2xl bg-white/[0.05] border border-white/5 hover:border-emerald-500/30 transition-all">
                                <h4 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">Article 14: Human Oversight</h4>
                                <p className="text-sm text-neutral-500 mt-2">Implementing human-in-the-loop controls for EU AI Act compliance.</p>
                            </Link>
                            <Link href="/learn/eu-ai-act-august-2026-deadline" className="group p-6 rounded-2xl bg-white/[0.05] border border-white/5 hover:border-emerald-500/30 transition-all">
                                <h4 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">EU AI Act August 2026 Deadline</h4>
                                <p className="text-sm text-neutral-500 mt-2">What AI agent developers must do before August 2, 2026.</p>
                            </Link>
                        </div>
                    </div>

                    {/* CTA */}
                    <div className="p-12 rounded-[2.5rem] bg-gradient-to-br from-neutral-800 to-neutral-950 text-white flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden group border border-white/10">
                        <div className="space-y-2 relative z-10">
                            <h3 className="text-3xl font-black uppercase tracking-tighter leading-none italic">
                                Compliance Automation
                            </h3>
                            <p className="text-neutral-400 font-medium">
                                Configure your Article 12 audit pipeline in under 5 minutes.
                            </p>
                        </div>
                        <Link 
                            href="/beta" 
                            className="px-8 py-4 bg-emerald-500 text-black font-bold uppercase tracking-tighter rounded-xl hover:bg-emerald-400 transition-colors flex items-center gap-2 relative z-10 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                        >
                            View Audit Demo <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </article>
            </main>
        </div>
    );
}

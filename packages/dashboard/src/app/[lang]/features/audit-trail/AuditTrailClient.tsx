// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    FileText, ShieldCheck, ArrowRight, Download, 
    Lock, CheckCircle2, ChevronRight, LayoutDashboard, 
    Network, Database, Share2, Zap, AlertTriangle, 
    Users, Settings, Plus, Key, Code, Info, Cpu, 
    History, Fingerprint, Search
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { TagBadge } from "@/app/HomeClient";

// ── Comparison Table Data ──

const COMPARISON_DATA = [
    { feature: "Action Record", prompt: "Standard JSON logs (Easily modified)", supra: "Signed, Immutable Audit Feed" },
    { feature: "Policy Evidence", prompt: "None (Logs show 'what', not 'why')", supra: "Deterministic 'Decision Reason' for every action" },
    { feature: "EU AI Act Compliance", prompt: "Manual mapping required (Art. 12/14)", supra: "Pre-mapped Evidence Reports (One-Click PDF)" },
    { feature: "Human-in-the-Loop", prompt: "Missing (No proof of manual oversight)", supra: "Cryptographic proof of human approval" },
    { feature: "Storage Location", prompt: "Centralized logging server", supra: "Decentralized, local-first signing" }
];

export default function AuditTrailClient() {
    const params = useParams();
    const lang = (params?.lang as string) || 'en';
    const [activeTab, setActiveTab] = useState("insecure");

    return (
        <main className="overflow-hidden">
            {/* 🚀 HERO — Specific Threat */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-20 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-blue-600/30 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Governance Evidence</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Stop Dread the Audit. <br />
                             <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-600">Export the Evidence.</span> <br />
                             Compliance as Code.
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium">
                            Autonomous agents shouldn&apos;t be a &ldquo;black box.&rdquo; SupraWall Audit Trail automatically logs every policy decision, tool call, and blocked action in an immutable, signed feed mapped specifically to <span className="text-white italic text-glow">EU AI Act Articles 9, 11, 12, and 14</span>.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-6 pt-4">
                        <Link href={`/${lang}/beta`} className="px-14 py-6 bg-white text-black font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-blue-500 hover:text-white transition-all transform hover:scale-105 shadow-[0_20px_40px_rgba(255,255,255,0.1)] group flex items-center gap-3">
                             Start Building <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                        </Link>
                        <Link href="/docs/audit" className="px-14 py-6 border-2 border-white/10 text-white font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-white/5 transition-all underline decoration-white/10 underline-offset-8">
                             See Report Anatomy
                        </Link>
                    </div>
                </div>
            </section>

            {/* ⚔️ VISUAL COMPARISON — Zero Evidence vs Signed PDF */}
            <section className="py-20 px-6 bg-[#030303] border-y border-white/5">
                <div className="max-w-7xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">The Governance Gap</h2>
                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto text-glow">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white' : 'text-neutral-500 hover:text-white'}`}>The Black Box Agent</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(59,130,246,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The Evidence-Ready Agent</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Evidence View */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-10 min-h-[500px] relative overflow-hidden shadow-2xl flex flex-col justify-center items-center">
                             <div className="absolute top-4 left-6 text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Compliance Status: {activeTab === 'insecure' ? 'FAIL' : 'PASS'}</div>
                             
                                {activeTab === "insecure" ? (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="text-center space-y-6">
                                        <AlertTriangle className="w-20 h-20 text-rose-500 mx-auto animate-pulse" />
                                        <div className="space-y-2">
                                            <p className="text-white font-black uppercase italic text-3xl">Zero Evidence</p>
                                            <p className="text-neutral-500 text-sm font-bold leading-relaxed italic uppercase tracking-tight">An auditor asks: &ldquo;Show me the risk management results for last Tuesday.&rdquo; <br /><br /> You show them a blank screen. <br /> Potential Fine: up to €35M or 7% GTO.</p>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div initial={{opacity: 0, scale: 0.9}} animate={{opacity: 1, scale: 1}} className="w-full max-w-sm p-8 rounded-3xl bg-white text-black shadow-[0_0_100px_rgba(255,255,255,0.1)] space-y-6 rotate-[-1deg]">
                                        <div className="flex items-center justify-between border-b pb-4 border-black/10">
                                            <div className="flex items-center gap-2">
                                                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                                                <span className="font-black uppercase text-[10px] tracking-widest">SUPRAWALL.REPORT</span>
                                            </div>
                                            <span className="text-[10px] text-neutral-400 font-bold">PDF V1.2</span>
                                        </div>
                                        <div className="space-y-4">
                                            <h4 className="text-xl font-black italic uppercase leading-none">Evidence of Oversight</h4>
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50 text-emerald-700 text-[10px] font-black uppercase">
                                                    <span>Article 12 - Logging</span>
                                                    <span>COMPLIANT</span>
                                                </div>
                                                <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50 text-emerald-700 text-[10px] font-black uppercase">
                                                    <span>Article 14 - Human Oversight</span>
                                                    <span>COMPLIANT</span>
                                                </div>
                                            </div>
                                            <div className="p-4 rounded-xl bg-neutral-50 border space-y-3">
                                                <p className="text-[10px] font-bold text-neutral-400">SESSION ID: SW-284-911</p>
                                                <p className="text-[10px] font-medium leading-relaxed italic">&ldquo;Agent attempted db.delete_prod. Action was BLOCKED by Policy DP-9. Approved by human (JARVIS).&rdquo;</p>
                                            </div>
                                        </div>
                                        <button className="w-full py-4 bg-black text-white rounded-xl font-black uppercase text-xs tracking-widest flex items-center justify-center gap-2 group">
                                            Export PDF Evidence <Download className="w-4 h-4 group-hover:translate-y-1 transition-transform" />
                                        </button>
                                    </motion.div>
                                )}
                        </div>

                        {/* Explained Side */}
                        <div className="flex flex-col justify-center space-y-8">
                            <div className="space-y-4">
                                <h3 className="text-3xl font-black italic uppercase tracking-tighter">Your Audit Insurance</h3>
                                <p className="text-neutral-400 leading-relaxed font-medium italic">
                                    Autonomous systems are a regulatory nightmare. The EU AI Act (and similar global frameworks) requires developers to prove that risk was managed and human oversight was possible. SupraWall turns this from a &ldquo;consulting problem&rdquo; into a &ldquo;reporting feature.&rdquo;
                                </p>
                            </div>
                            <div className="grid grid-cols-1 gap-4">
                               <div className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover:scale-110 transition-transform">
                                        <Fingerprint className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">Signed Audit Feed</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Immutable records of every tool call decision, cryptographically signed locally.</p>
                                    </div>
                               </div>
                               <div className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 group-hover:scale-110 transition-transform">
                                        <History className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">One-Click Compliance Export</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Map your logs automatically to EU AI Act articles and export as regulator-ready PDFs.</p>
                                    </div>
                               </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 🎯 COMPARISON TABLE — The Reality Check */}
             <section className="py-24 px-6 bg-[#030303]">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="text-center space-y-6">
                        <TagBadge>Direct Comparison</TagBadge>
                        <h2 className="text-5xl font-black italic uppercase tracking-tighter">Probabilistic Logs vs. <span className="text-blue-500 font-bold italic underline decoration-white/10 uppercase italic">Deterministic Audit Trail</span></h2>
                    </div>

                    <div className="bg-neutral-900/40 border border-white/5 rounded-[3rem] overflow-hidden shadow-2xl">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 italic">Audit Feature</th>
                                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-white italic">Standard JSON Logging</th>
                                    <th className="p-8 text-[10px] font-black uppercase tracking-widest text-blue-500 italic bg-blue-500/5">SupraWall Evidence</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {COMPARISON_DATA.map((row, i) => (
                                    <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="p-8 text-sm font-black italic text-neutral-400 uppercase tracking-tighter">{row.feature}</td>
                                        <td className="p-8 text-sm font-bold italic text-neutral-500 uppercase tracking-tighter">{row.prompt}</td>
                                        <td className="p-8 text-sm font-black italic text-blue-400 uppercase tracking-tighter bg-blue-500/[0.02]">{row.supra}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
             </section>

             {/* 🛡️ EU AI ACT ARTICLES */}
             <section className="py-40 px-6 bg-black relative overflow-hidden">
                 <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-blue-500/[0.03] blur-[150px] rounded-full pointer-events-none" />
                 <div className="max-w-7xl mx-auto space-y-24 relative z-10">
                    <div className="text-center space-y-6">
                        <TagBadge>Regulator Ready</TagBadge>
                        <h2 className="text-5xl md:text-[7rem] font-black italic uppercase tracking-tighter leading-[0.85] text-glow">
                             Every Article Covered. <br />
                             <span className="text-blue-500 font-bold italic underline decoration-white/10">No Manual Mapping.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {[
                            { art: "Article 09", title: "Risk Management", desc: "Evidence that all potential high-risk tool calls were identified, assessed, and governed before execution.", icon: <ShieldCheck className="w-8 h-8 text-blue-400" /> },
                            { art: "Article 12", title: "Automatic Logging", desc: "Signed, immutable logs of continuous system monitoring and every state transition triggered by the agent.", icon: <History className="w-8 h-8 text-blue-400" /> },
                            { art: "Article 11", title: "Technical Documentation", desc: "Automatic generation of the system logs required for technical conformity assessment by regulatory bodies.", icon: <FileText className="w-8 h-8 text-blue-400" /> },
                            { art: "Article 14", title: "Human Oversight", desc: "Cryptographic proof that human approval was required and delivered for every non-trivial agent outcome.", icon: <Users className="w-8 h-8 text-blue-400" /> }
                        ].map((p, i) => (
                            <div key={i} className="p-10 rounded-[3rem] bg-neutral-900/40 border border-white/10 flex gap-8 hover:border-blue-500/30 transition-all group overflow-hidden relative">
                                <div className="p-6 rounded-3xl bg-blue-500/10 text-blue-500 h-fit group-hover:scale-110 transition-transform">
                                    {p.icon}
                                </div>
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2">
                                        <span className="text-blue-500 font-black italic uppercase text-xs tracking-widest">{p.art}</span>
                                        <CheckCircle2 className="w-4 h-4 text-emerald-500/50" />
                                    </div>
                                    <h4 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{p.title}</h4>
                                    <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight leading-relaxed italic">{p.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                 </div>
            </section>

            {/* 💻 CODE — The One-Line Fix */}
            <section id="code" className="py-40 px-6 bg-[#030303] border-y border-white/5">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="text-center space-y-6">
                        <TagBadge>Governance as Code</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-none text-glow">
                             The Compliance <br />
                             <span className="text-blue-500 italic">Configuration.</span>
                        </h2>
                    </div>

                    <div className="bg-[#0A0A0A] border-[3px] border-blue-500/40 rounded-[3rem] p-12 text-sm md:text-base font-mono relative overflow-hidden group shadow-[0_0_80px_rgba(59,130,246,0.15)]">
                        <div className="absolute top-6 right-8 text-blue-500/50 flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                            <Code className="w-4 h-4" /> COMPLIANCE_SETUP.TS
                        </div>
                        <pre className="text-blue-100/90 leading-loose">
                            {`import { secure_agent } from "suprawall";\n\nconst agent = secure_agent(my_base_agent, {\n  api_key: "ag_...",\n\n  // 🛡️ Automatic Compliance Logging\n  compliance: {\n    auto_log_tool_calls: true,\n    sign_logs_locally: true,\n    map_to_articles: [9, 11, 12, 14], // EU AI Act support\n    retention_days: 365\n  }\n});\n\n// Decision logs are now signed and stored in your SupraWall Node.`}
                        </pre>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-blue-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Ship Compliant</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                         Evidence Handed. <br />
                         <span className="text-blue-500 underline decoration-white/20 font-bold italic">Audit Won.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                         Don&apos;t build a compliance team. Enable SupraWall Audit Trail and get back to building the product. 
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href={`/${lang}/beta`} className="px-16 py-8 bg-blue-600 text-white font-black text-3xl rounded-3xl hover:bg-blue-500 transition-all shadow-[0_0_100px_rgba(59,130,246,0.3)] tracking-tighter flex items-center gap-4 group">
                             Get Your Node API Key <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
             {/* ⚡ TRY IN 30 SECONDS */}
             <section className="py-24 px-6 bg-[#030303] border-t border-white/5 relative z-10 text-center">
                <div className="max-w-4xl mx-auto space-y-12">
                    <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter text-glow">
                        Try It In <span className="text-emerald-500 underline decoration-white/10">30 Seconds.</span>
                    </h2>
                    <p className="text-xl md:text-2xl text-neutral-400 font-medium italic max-w-2xl mx-auto">
                        No account required. Auto-detect your framework and wrap your agent with security in one command.
                    </p>
                    <div className="p-6 md:p-8 bg-[#0a0a0a] rounded-[2rem] border border-emerald-500/20 font-mono text-[13px] relative overflow-hidden group shadow-[0_0_80px_rgba(16,185,129,0.15)] text-left cursor-copy mx-auto max-w-2xl hover:border-emerald-500/50 transition-all" onClick={() => navigator.clipboard && navigator.clipboard.writeText('npx suprawall init')} title="Copy command">
                        <div className="absolute top-4 right-6 text-emerald-500/30 text-[10px] font-black uppercase tracking-widest italic group-hover:text-emerald-500 transition-colors">
                            CLICK TO COPY
                        </div>
                        <pre className="text-emerald-100/80 leading-loose">
$ npx suprawall init

? Detected: my-agent.ts — secure it? (Y/n) y

[✓] .env updated with SUPRAWALL_API_KEY
[✓] my-agent.ts wrapped with protect()

🛡️  Your agent is now armored.
                        </pre>
                    </div>
                </div>
            </section>
        </main>

    );
}

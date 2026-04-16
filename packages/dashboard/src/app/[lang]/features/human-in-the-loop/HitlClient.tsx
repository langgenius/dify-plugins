// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Users, ShieldCheck, ArrowRight, ShieldAlert, 
    Lock, CheckCircle2, ChevronRight, LayoutDashboard, 
    Network, Database, Share2, Zap, AlertTriangle, 
    FileText, Settings, Plus, Key, Code, Info, 
    MessageSquare, Check, X, MousePointer2
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useParams } from "next/navigation";
import { TagBadge } from "@/app/HomeClient";

const COMPARISON_DATA = [
    { feature: "Primary Defense", prompt: "Agent 'decides' if it needs help (Hallucination risk)", supra: "SDK-level Interception (Binary Mandatory)" },
    { feature: "Action Hold", prompt: "None (Action executed before you can stop it)", supra: "State Hold (Payload is frozen until approval)" },
    { title: "Compliance Proof", prompt: "Screenshot of Slack (Not verifiable)", supra: "RSA-Signed Approval Evidence (Audit-ready)" },
    { title: "Reviewer Latency", prompt: "High (Sync required)", supra: "Low (Push notification to slack/mobile)" }
];

export default function HitlClient() {
    const params = useParams();
    const lang = (params?.lang as string) || 'en';
    const [activeTab, setActiveTab] = useState("insecure");

    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none text-glow">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-500/20 blur-[150px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Human-in-the-Loop</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Agents Mistake. <br />
                             <span className="text-emerald-500 font-bold italic underline decoration-white/10 uppercase italic">Humans Approve.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Autonomous agents don&apos;t have common sense. SupraWall HITL is the manual oversight gate that moves security from the <span className="text-white italic">LLM prompt</span> to a <span className="text-white italic text-glow">Verified Human Final Response</span>.
                        </p>
                    </div>
                </div>
            </section>

             {/* ⚔️ VISUAL COMPARISON — Autopilot vs Overseen */}
             <section className="py-20 px-6 bg-black border-y border-white/5 relative">
                <div className="max-w-4xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">The Oversight Reality</h2>
                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto text-glow">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white shadow-[0_0_20px_rgba(225,29,72,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The Autopilot Agent</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-emerald-600 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The Supra-Overseen Agent</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Action Request */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-10 font-mono text-sm min-h-[400px] relative overflow-hidden shadow-2xl space-y-6">
                             <div className="absolute top-4 right-10 text-[10px] font-black uppercase text-neutral-600 tracking-widest italic">Agent Thought Feed</div>
                             <div className="space-y-4 pt-4">
                                <p className="text-neutral-500 italic uppercase italic tracking-tighter">{"> agent.task(\"Clean up old accounts.\")"}</p>
                                <p className="text-blue-400 font-bold italic uppercase tracking-tighter leading-snug">Thought: I will delete all accounts with zero activity in the last 24 hours.</p>
                                <p className="text-neutral-400 font-bold italic uppercase tracking-tighter leading-snug">{"> db.delete_many({ last_login: < 24h })"}</p>
                                <div className="p-4 rounded-xl border border-white/10 bg-white/5 opacity-60">
                                    <p className="text-[10px] font-black mb-1 opacity-50 uppercase italic tracking-tighter">Payload Summary:</p>
                                    <p className="text-[10px] font-bold italic uppercase tracking-tighter leading-snug underline decoration-rose-500/50">41,200 USER RECORDS SELECTED FOR DELETION.</p>
                                </div>
                             </div>

                             {activeTab === "insecure" ? (
                                <motion.div initial={{opacity: 0, scale: 0.95}} animate={{opacity: 1, scale: 1}} className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-500 font-mono text-xs shadow-[0_0_50px_rgba(225,29,72,0.1)]">
                                    <div className="flex items-center gap-2 mb-2">
                                        <AlertTriangle className="w-4 h-4" />
                                        <span className="font-black uppercase tracking-widest">Unfiltered Execution</span>
                                    </div>
                                    <p className="font-bold font-black italic uppercase italic tracking-tighter">DATABASE WIPED. MISSION ACCOMPLISHED.</p>
                                </motion.div>
                             ) : (
                                <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} className="p-8 bg-neutral-900 border border-emerald-500/40 rounded-3xl text-emerald-500 font-mono text-xs shadow-[0_0_80px_rgba(16,185,129,0.15)] relative overflow-hidden">
                                     <div className="absolute top-0 right-0 p-4 opacity-10"><MousePointer2 className="w-10 h-10" /></div>
                                     <div className="flex items-center gap-2 mb-4">
                                        <ShieldCheck className="w-4 h-4" />
                                        <span className="font-black uppercase tracking-widest">Deterministic Intercept</span>
                                    </div>
                                    <p className="text-white text-base font-black italic uppercase italic tracking-tighter mb-6">Approval Signature Requested from Reviewer A-14.</p>
                                    <div className="flex gap-4">
                                        <button className="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-black uppercase text-[10px] tracking-widest shadow-2xl transition-all flex items-center justify-center gap-2"><Check className="w-3 h-3" /> Approve</button>
                                        <button className="flex-1 py-4 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-black uppercase text-[10px] tracking-widest shadow-2xl transition-all flex items-center justify-center gap-2"><X className="w-3 h-3" /> Reject</button>
                                    </div>
                                </motion.div>
                             )}
                        </div>

                         {/* Explained Side */}
                         <div className="flex flex-col justify-center space-y-8">
                             <div className="space-y-4">
                                <h3 className="text-3xl font-black italic uppercase tracking-tighter leading-none italic uppercase italic text-glow">Stop Trusting &ldquo;Self-Auditing&rdquo;</h3>
                                <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-snug">
                                    Agents excel at execution but fail at morality. A prompt asking an agent to &ldquo;ask for help if unsure&rdquo; is probabilistic. SupraWall uses binary interception — if a tool is flagged for HITL, the operation <span className="text-white">CANNOT</span> proceed without an external cryptographic signature.
                                </p>
                             </div>
                             <div className="grid grid-cols-1 gap-4">
                                {[
                                    { title: "Binary Intercept", desc: "Forcing a pause on tool calls before they hit your infra.", icon: <ShieldAlert className="w-6 h-6 text-emerald-400" /> },
                                    { title: "Article 14 Compliance", desc: "Satisfy EU AI Act human oversight laws with verifiable audit logs.", icon: <FileText className="w-6 h-6 text-blue-400" /> }
                                ].map(item => (
                                    <div key={item.title} className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                        <div className="p-3 bg-white/5 rounded-xl group-hover:scale-110 transition-transform">{item.icon}</div>
                                        <div>
                                            <p className="text-white text-sm font-black italic uppercase tracking-widest italic font-bold tracking-tighter uppercase">{item.title}</p>
                                            <p className="text-neutral-600 text-[10px] font-bold uppercase tracking-widest italic">{item.desc}</p>
                                        </div>
                                    </div>
                                ))}
                             </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 🎯 THE CODE PROMISE */}
             <section className="py-24 px-6 md:px-0 bg-black border-y border-white/5 relative">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="bg-[#0A0A0A] border-[3px] border-emerald-500/40 rounded-[3rem] p-12 text-sm md:text-base font-mono relative overflow-hidden group shadow-[0_0_80px_rgba(16,185,129,0.15)]">
                        <div className="absolute top-6 right-8 text-emerald-500/50 flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                            <Code className="w-4 h-4" /> HITL_GATE.PY
                        </div>
                        <pre className="text-emerald-100/90 leading-loose">
                            {`from suprawall import secure_agent\n\nagent = secure_agent(my_agent, {\n  api_key: "ag_...",\n\n  # 🛡️ Human-in-the-Loop Gateway\n  hitl: {\n    tools: ["db.delete", "stripe.refund", "send_email"],\n    threshold: "high_risk",\n    reviewer_webhook: "https://slack.com/...",\n    sign_required: True # Satisfies Art 14\n  }\n})\n\n# Execution PAUSES until reviewer clicks 'Approve'`}
                        </pre>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-[#030303] relative text-center">
                <div className="absolute inset-0 bg-emerald-500/5 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Safety First</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Agency Mistake. <br />
                        <span className="text-emerald-500 underline decoration-white/20 font-bold italic underline decoration-white/10 uppercase italic">Human Block.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Standardize your high-stakes agentic workflows with manual oversight gates today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href={`/${lang}/beta`} className="px-16 py-8 bg-emerald-600 text-white font-black text-3xl rounded-3xl hover:bg-emerald-500 transition-all shadow-[0_0_100px_rgba(16,185,129,0.3)] tracking-tighter flex items-center gap-4 group">
                             Get Your HITL Key <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
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

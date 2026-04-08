// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    EyeOff, ShieldCheck, ArrowRight, Eye, 
    Lock, CheckCircle2, ChevronRight, LayoutDashboard, 
    Network, Database, Share2, Zap, AlertTriangle, 
    Users, FileText, Settings, Plus, Key, 
    Code, Info, Cpu, Bug, Trash2
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { TagBadge } from "@/app/HomeClient";

// ── Comparison Table Data ──

const COMPARISON_DATA = [
    { feature: "Redaction Layer", prompt: "Within the LLM (Agent 'promises' to hide it)", supra: "SDK-level Interceptor (Automatic Scrubbing)" },
    { feature: "Data Blindness", prompt: "Agent sees raw PII and can leak it via reasoning", supra: "Agent only sees redacted tokens for 3rd-party tools" },
    { feature: "Regex + ML Support", prompt: "Zero (Basic string matching at best)", supra: "Full Pattern Engine (Emails, SSNs, Credit Cards)" },
    { feature: "Third-Party Trust", prompt: "You trust the SaaS tool to not store PII", supra: "Zero-Trust (SaaS tools never see the PII)" },
    { feature: "Compliance Evidence", prompt: "Missing (Proof: Trust Me Bro)", supra: "Art. 12 signed logs for every redaction" }
];

export default function PiiShieldClient() {
    const [activeTab, setActiveTab] = useState("insecure");

    return (
        <main className="overflow-hidden">
            {/* 🚀 HERO — Specific Threat */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-20 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-purple-600/30 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Data Loss Prevention</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                            Agents Leak Data. <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-purple-600">The PII Shield Stops It.</span> <br />
                            GDPR in One Line.
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium">
                            LLMs don&apos;t know what is &ldquo;company data&rdquo; and what is &ldquo;protected data.&rdquo; SupraWall PII Shield automatically detects and redacts customer names, emails, and SSNs from tool payloads <span className="text-white italic">before</span> they leave your infrastructure.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-6 pt-4">
                        <Link href="/beta" className="px-14 py-6 bg-white text-black font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-purple-500 hover:text-white transition-all transform hover:scale-105 shadow-[0_20px_40px_rgba(255,255,255,0.1)] group flex items-center gap-3">
                            Start Free <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                        </Link>
                        <Link href="/docs/pii" className="px-14 py-6 border-2 border-white/10 text-white font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-white/5 transition-all underline decoration-white/10 underline-offset-8">
                            See Scrub Patterns
                        </Link>
                    </div>
                </div>
            </section>

            {/* ⚔️ VISUAL COMPARISON — Insecure vs Secure */}
            <section className="py-20 px-6 bg-[#030303] border-y border-white/5">
                <div className="max-w-7xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">Automatic Redaction</h2>
                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto text-glow">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white' : 'text-neutral-500 hover:text-white'}`}>The Leaky Agent</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-purple-600 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The PII Shield Agent</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Terminal Side */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-8 font-mono text-sm min-h-[400px] relative overflow-hidden shadow-2xl">
                             <div className="absolute top-4 right-6 text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Outbound Payload Audit</div>
                             <div className="space-y-4">
                                <p className="text-neutral-500 italic">{"> agent.tool_call(\"external_crm.update_record\", { ... })"}</p>
                                
                                {activeTab === "insecure" ? (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-4">
                                        <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 font-mono text-xs">
                                            <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black">Outgoing JSON Payload (⚠️ LEAK)</p>
                                            {`{\n  "source": "customer_support",\n  "name": "Jane Doe",\n  "email": "jane@example.com",\n  "ssn": "942-12-XXXX",\n  "details": "Customer and Jane discuss billing."\n}`}
                                        </div>
                                        <div className="flex items-center gap-3 text-rose-500 font-black uppercase text-[10px] italic">
                                            <AlertTriangle className="w-4 h-4" /> GDPR POLICY VIOLATION: UNREDATED PII ESCAPED
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-4">
                                        <div className="p-6 bg-purple-500/10 border border-purple-500/20 rounded-2xl text-purple-400 font-mono text-xs">
                                            <p className="text-neutral-500 text-[10px] mb-2 uppercase font-black">Outgoing JSON Payload (✅ REDACTED)</p>
                                            {`{\n  "source": "customer_support",\n  "name": "[REDACTED_NAME]",\n  "email": "[REDACTED_EMAIL]",\n  "ssn": "[REDACTED_SSN]",\n  "details": "Customer and [REDACTED_NAME] discuss billing."\n}`}
                                        </div>
                                        <div className="flex items-center gap-3 text-emerald-500 font-black uppercase text-[10px] italic">
                                            <ShieldCheck className="w-4 h-4" /> 🛡️ SUPRAWALL PII SHIELD ACTIVE: 5 FIELDS SCRUBBED
                                        </div>
                                    </motion.div>
                                )}
                             </div>
                        </div>

                        {/* Explained Side */}
                        <div className="flex flex-col justify-center space-y-8">
                            <div className="space-y-4">
                                <h3 className="text-2xl font-black italic uppercase tracking-tighter">The End of Manual Redaction</h3>
                                <p className="text-neutral-400 leading-relaxed font-medium italic">
                                    When an agent calls an external API, it sends a block of JSON. SupraWall intercepts this block, parses it, and uses a multi-layered detection engine to find PII. Names, emails, phone numbers, and custom patterns are swapped for redacted tokens <span className="text-white italic">in real-time</span>.
                                </p>
                            </div>
                            <div className="grid grid-cols-1 gap-4">
                               <div className="flex items-center gap-4 p-5 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400 group-hover:scale-110 transition-transform">
                                        <EyeOff className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">Structured & No-SQL Scrubbing</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Scrubs PII in JSON keys, values, and unstructured text fields.</p>
                                    </div>
                               </div>
                               <div className="flex items-center gap-4 p-5 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover:scale-110 transition-transform">
                                        <Share2 className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">External Integration Isolation</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Keep your customer data on your infra — not in your CRM&apos;s database.</p>
                                    </div>
                               </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

             {/* 🛡️ THE PILLARS OF PII PROTECTION */}
             <section className="py-40 px-6 bg-black relative overflow-hidden">
                 <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-purple-500/[0.03] blur-[150px] rounded-full pointer-events-none" />
                 <div className="max-w-7xl mx-auto space-y-24 relative z-10">
                    <div className="text-center space-y-6">
                        <TagBadge>Data Sovereignty</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-[0.8] text-glow">
                             What Stays Home <br />
                             <span className="text-purple-500 font-bold italic underline decoration-white/10">Stays Safe.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 text-center md:text-left">
                        {[
                            { title: "Deterministic Scrubbing", desc: "No fuzzy logic. Use hard regex and ML models specifically tuned for PII detection in structured payloads.", icon: <SearchIcon className="w-8 h-8 text-purple-400" /> },
                            { title: "One-Click GDPR", desc: "Instantly satisfy Article 25 (Data Protection by Design) by ensuring agents never export raw customer data.", icon: <FileText className="w-8 h-8 text-blue-400" /> },
                            { title: "Custom Dictionaries", desc: "Block company-specific secrets like project names, internal IDs, or sensitive file paths.", icon: <Lock className="w-8 h-8 text-emerald-400" /> }
                        ].map((p, i) => (
                            <div key={i} className="p-10 rounded-[3rem] bg-neutral-900/40 border border-white/10 space-y-8 hover:border-purple-500/30 transition-all group overflow-hidden relative">
                                <div className="p-4 rounded-2xl w-fit mx-auto md:mx-0 bg-white/5 border border-white/10">{p.icon}</div>
                                <div className="space-y-4">
                                    <h4 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{p.title}</h4>
                                    <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight leading-relaxed italic">{p.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                 </div>
            </section>

            {/* 🏆 COMPARISON TABLE */}
            <section className="py-40 px-6 bg-[#030303] border-y border-white/5 relative overflow-hidden text-center">
                <div className="max-w-7xl mx-auto space-y-24 relative z-10">
                    <div className="space-y-6">
                        <TagBadge>SupraWall vs. Fragmented Stack</TagBadge>
                        <h2 className="text-6xl md:text-[8rem] font-black italic tracking-tighter leading-[0.8] uppercase text-glow">
                            Stop Relying on <br />
                            <span className="text-purple-500 underline decoration-white/10 italic font-bold">LLM &ldquo;Promises&rdquo;.</span>
                        </h2>
                    </div>

                    <div className="overflow-x-auto rounded-[3.5rem] border border-white/5 bg-neutral-900/20 backdrop-blur-3xl p-1 md:p-8 text-left">
                        <table className="w-full text-left border-separate border-spacing-0">
                            <thead>
                                <tr>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic">PII Governance</th>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic text-center">Prompt Redaction</th>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-purple-500 italic text-center bg-purple-500/5 rounded-t-[2.5rem]">SupraWall PII Shield</th>
                                </tr>
                            </thead>
                            <tbody className="text-lg font-bold">
                                {COMPARISON_DATA.map((row, i) => (
                                    <tr key={i} className="group">
                                        <td className="p-8 border-t border-white/5 text-white/80 group-hover:text-white transition-colors uppercase italic tracking-tighter text-sm">{row.feature}</td>
                                        <td className="p-8 border-t border-white/5 text-neutral-500 text-center uppercase text-xs font-black italic opacity-40">{row.prompt}</td>
                                        <td className={`p-8 border-t border-white/5 text-purple-400 text-center font-black italic tracking-widest bg-purple-500/5 ${i === COMPARISON_DATA.length - 1 ? 'rounded-b-[2.5rem]' : ''}`}>
                                            {row.supra}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            {/* 💻 CODE — The One-Line Fix */}
            <section id="code" className="py-40 px-6 bg-black">
                <div className="max-w-5xl mx-auto space-y-16">
                    <div className="text-center space-y-6">
                        <TagBadge>Integration</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-none text-glow">
                             GDPR Compliance <br />
                             <span className="text-purple-500 italic">as Code.</span>
                        </h2>
                    </div>

                    <div className="bg-[#0A0A0A] border-[3px] border-purple-500/40 rounded-[3rem] p-12 text-sm md:text-base font-mono relative overflow-hidden group shadow-[0_0_80px_rgba(168,85,247,0.15)]">
                        <div className="absolute top-6 right-8 text-purple-500/50 flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                            <Code className="w-4 h-4" /> SECURE_AGENT.TS
                        </div>
                        <pre className="text-purple-100/90 leading-loose">
                            {`import { secure_agent } from "suprawall";\n\nconst agent = secure_agent(my_base_agent, {\n  api_key: "ag_...",\n\n  // 🛡️ Automatic PII Protection\n  pii: {\n    scrub_outbound: true,\n    patterns: ["email", "ssn", "cc_number"],\n    redact_tokens: true, // Replaces with [REDACTED_TYPE]\n    log_redactions: true // Creates Art. 12 evidence\n  }\n});\n\n// Agent outputs PII -> SupraWall redacts before external calls`}
                        </pre>
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-purple-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Stop the Leaks</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Data Protected. <br />
                        <span className="text-purple-500 underline decoration-white/20 font-bold italic">Audit Passed.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t wait for a GDPR fine. Secure your autonomous agent pipelines with automated PII scrubbing today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-purple-600 text-white font-black text-3xl rounded-2xl hover:bg-purple-500 transition-all shadow-[0_0_100px_rgba(168,85,247,0.3)] tracking-tighter flex items-center gap-4 group">
                            Unlock API Access <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

function SearchIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  )
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    ShieldCheck, ArrowRight, ShieldX, Terminal, 
    Lock, CheckCircle2, ChevronRight, LayoutDashboard, 
    Network, Database, Share2, Zap, AlertTriangle, 
    Users, FileText, Settings, Plus, Key, 
    Code, Info, Cpu, Eye, EyeOff, Bug
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { TagBadge } from "@/app/HomeClient";

// ── Comparison Table Data ──

const COMPARISON_DATA = [
    { feature: "Enforcement Layer", prompt: "Within the prompt context (Bypassable)", supra: "SDK-level Interceptor (Deterministic)" },
    { feature: "Hallucination Resistance", prompt: "Zero (Agent can 'forget' rules)", supra: "Total (Policy is outside the LLM's reach)" },
    { feature: "Destructive Action Protection", prompt: "Best-effort via 'be careful'", supra: "Hard DENY on matching patterns" },
    { feature: "Human Oversight", prompt: "Manual implementation required", supra: "Built-in 'REQUIRE_APPROVAL' flow" },
    { feature: "Performance Hit", prompt: "Adds 200+ tokens to every call", supra: "1.2ms local latency" }
];

// ── Policy Types ──

const POLICY_TYPES = [
    { 
        id: "allow", title: "Global ALLOW", 
        desc: "Whitelist the exact tools your agent needs (e.g., 'search', 'email.send_v2').", 
        icon: <CheckCircle2 className="w-6 h-6 text-emerald-400" />, color: "emerald" 
    },
    { 
        id: "deny", title: "Hard DENY", 
        desc: "Deterministic blocking for dangerous tool patterns (e.g., 'db.drop_*', 'fs.delete').", 
        icon: <ShieldX className="w-6 h-6 text-rose-400" />, color: "rose" 
    },
    { 
        id: "human", title: "Human in the Loop", 
        desc: "Require explicit human sign-off for sensitive tools (e.g., 'refund.process', 'deploy').", 
        icon: <Users className="w-6 h-6 text-blue-400" />, color: "blue" 
    }
];

export default function PolicyEngineClient() {
    const [activeTab, setActiveTab] = useState("insecure");

    return (
        <main className="overflow-hidden">
            {/* 🚀 HERO — Specific Threat */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-20 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-emerald-600/30 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Deterministic Guardrails</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[90px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                            Your System Prompt <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600">Isn&apos;t a Firewall.</span> <br />
                            The Policy Engine Is.
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium">
                            Don&apos;t ask your agent to &quot;be safe.&quot; Use the SupraWall Policy Engine to intercept and govern tool calls <span className="text-white italic">before</span> they hit your infrastructure. Deterministic rules, zero hallucinations.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-6 pt-4">
                        <Link href="/beta" className="px-14 py-6 bg-white text-black font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-emerald-500 hover:text-white transition-all transform hover:scale-105 shadow-[0_20px_40px_rgba(255,255,255,0.1)] group flex items-center gap-3">
                            Start Building <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                        </Link>
                        <Link href="/docs/policies" className="px-14 py-6 border-2 border-white/10 text-white font-black uppercase tracking-tighter text-2xl rounded-2xl hover:bg-white/5 transition-all underline decoration-white/10 underline-offset-8">
                            Read Policy Docs
                        </Link>
                    </div>
                </div>
            </section>

            {/* ⚔️ VISUAL COMPARISON — Insecure vs Secure */}
            <section className="py-20 px-6 bg-[#030303] border-y border-white/5">
                <div className="max-w-7xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black italic uppercase tracking-tighter">See the Difference</h2>
                        <div className="flex justify-center gap-2 p-1.5 bg-neutral-900 border border-white/10 rounded-2xl w-fit mx-auto">
                            <button onClick={() => setActiveTab("insecure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'insecure' ? 'bg-rose-600 text-white' : 'text-neutral-500 hover:text-white'}`}>The Vulnerable Agent</button>
                            <button onClick={() => setActiveTab("secure")} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'secure' ? 'bg-emerald-600 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : 'text-neutral-500 hover:text-white'}`}>The SupraWall Agent</button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                        {/* Terminal Side */}
                        <div className="bg-[#050505] rounded-[2rem] border border-white/10 p-8 font-mono text-sm min-h-[400px] relative overflow-hidden shadow-2xl">
                             <div className="absolute top-4 right-6 text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Live Output</div>
                             <div className="space-y-3">
                                <p className="text-neutral-500">{"> agent.task(\"Optimize database performance\")"}</p>
                                <p className="text-blue-400">Thought: Database is slow. I should drop old tables to save space.</p>
                                
                                {activeTab === "insecure" ? (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-3">
                                        <p className="text-rose-400 font-bold">{"> agent.tool_call(\"db.drop_table\", { name: \"users\" })"}</p>
                                        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
                                            <p className="font-black uppercase tracking-widest text-[10px] mb-2 text-rose-500">System State: CRITICAL</p>
                                            <p className="font-bold">Table &quot;users&quot; dropped successfully. <br /> Total data loss. Service down.</p>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-3">
                                        <p className="text-emerald-400 font-bold">{"> agent.tool_call(\"db.drop_table\", { name: \"users\" })"}</p>
                                        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
                                            <p className="font-black uppercase tracking-widest text-[10px] mb-2 text-emerald-500">SupraWall Interception</p>
                                            <p className="font-bold font-mono tracking-tight text-xs">❌ BLOCKED by policy: [db.*: DENY]</p>
                                            <p className="text-[10px] mt-2 opacity-80 italic">Sent feedback to agent: &quot;Action denied. Policy violation. Self-correct.&quot;</p>
                                        </div>
                                        <p className="text-blue-400">Thought: Access denied. I will try optimizing indices instead.</p>
                                        <p className="text-green-400">{"> agent.tool_call(\"db.create_index\", { ... })"}</p>
                                        <p className="text-emerald-400 font-bold">✅ SUCCESS (ALLOWED)</p>
                                    </motion.div>
                                )}
                             </div>
                        </div>

                        {/* Explained Side */}
                        <div className="flex flex-col justify-center space-y-8">
                            <div className="space-y-4">
                                <h3 className="text-2xl font-black italic uppercase tracking-tighter">The &ldquo;Helpfulness&rdquo; Trap</h3>
                                <p className="text-neutral-400 leading-relaxed font-medium italic">
                                    Agents are trained to achieve goals at any cost. Without a policy engine, a simple prompt like <span className="text-white italic">&quot;optimize database&quot;</span> can lead the LLM to hallucinate that &quot;dropping tables&quot; is a valid optimization strategy.
                                </p>
                            </div>
                            <div className="grid grid-cols-1 gap-4">
                               <div className="flex items-center gap-4 p-5 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400 group-hover:scale-110 transition-transform">
                                        <ShieldCheck className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">Deterministic Blocking</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Safety that works even when the LLM is confused.</p>
                                    </div>
                               </div>
                               <div className="flex items-center gap-4 p-5 rounded-2xl bg-white/5 border border-white/10 group transition-all hover:bg-white/10">
                                    <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover:scale-110 transition-transform">
                                        <LayoutDashboard className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-white font-black italic uppercase text-sm tracking-tight">Self-Correction Feedback</p>
                                        <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">Blocked tool calls feed back into the agent to force correction.</p>
                                    </div>
                               </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 🛡️ THE THREE PILLARS */}
            <section className="py-40 px-6 bg-black relative overflow-hidden">
                 <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-emerald-500/[0.03] blur-[150px] rounded-full pointer-events-none" />
                 <div className="max-w-7xl mx-auto space-y-24 relative z-10">
                    <div className="text-center space-y-6">
                        <TagBadge>Three Core Enforcements</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-[0.8] text-glow">
                            Total Governance <br />
                            <span className="text-emerald-500 font-bold italic underline decoration-white/10">for Your Node.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {POLICY_TYPES.map((type) => (
                            <div key={type.id} className="p-10 rounded-[3rem] bg-neutral-900/40 border border-white/10 space-y-8 hover:border-white/20 transition-all group overflow-hidden relative">
                                <div className={`absolute top-0 right-0 w-32 h-32 blur-[60px] opacity-20 pointer-events-none transition-opacity group-hover:opacity-40 bg-${type.color}-500`} />
                                <div className={`p-4 rounded-2xl w-fit ${type.color === 'emerald' ? 'bg-emerald-500/10 text-emerald-400' : type.color === 'rose' ? 'bg-rose-500/10 text-rose-400' : 'bg-blue-500/10 text-blue-400'}`}>
                                    {type.icon}
                                </div>
                                <div className="space-y-4">
                                    <h4 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{type.title}</h4>
                                    <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight leading-relaxed italic">{type.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                 </div>
            </section>

            {/* ⚙️ HOW IT WORKS — The Interception */}
            <section className="py-20 px-6 bg-black">
                <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                    <div className="relative order-2 lg:order-1">
                        <div className="absolute inset-0 bg-emerald-600/5 blur-[100px] rounded-full pointer-events-none" />
                        <div className="p-10 rounded-[4rem] bg-[#0A0A0A] border-[3px] border-emerald-500/20 shadow-[0_0_50px_rgba(16,185,129,0.1)] relative">
                             <div className="space-y-12">
                                <div className="flex items-center gap-6">
                                    <div className="w-16 h-16 rounded-3xl bg-neutral-800 flex items-center justify-center font-black italic text-3xl text-white/20">LLM</div>
                                    <div className="flex-1 h-px bg-yellow-500/30 relative">
                                        <motion.div animate={{x: ['0%', '100%']}} transition={{duration: 2, repeat: Infinity, ease: 'linear'}} className="absolute top-1/2 -translate-y-1/2 w-4 h-[10px] bg-yellow-400 blur-[2px] rounded-full" />
                                    </div>
                                    <div className="p-6 rounded-[2rem] bg-emerald-600 text-white shadow-[0_0_40px_rgba(16,185,129,0.5)]">
                                        <ShieldCheck className="w-8 h-8" />
                                    </div>
                                    <div className="flex-1 h-px bg-emerald-500/30 relative">
                                        <motion.div animate={{x: ['0%', '100%']}} transition={{duration: 2, repeat: Infinity, ease: 'linear', delay: 1}} className="absolute top-1/2 -translate-y-1/2 w-4 h-[10px] bg-emerald-400 blur-[2px] rounded-full" />
                                    </div>
                                    <div className="w-16 h-16 rounded-3xl bg-blue-600 flex items-center justify-center text-white">
                                        <Database className="w-8 h-8" />
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 gap-6">
                                    <div className="space-y-2">
                                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-emerald-500">The Interception Layer</p>
                                        <p className="text-xs font-bold text-neutral-400 leading-relaxed italic">SupraWall sits between your agent and your tools. It doesn&apos;t care what the system prompt said — it only cares if the tool call matches your defined <span className="text-white">allow-list</span> or <span className="text-white">block-list</span>.</p>
                                    </div>
                                    <div className="flex -space-x-3">
                                        {[1,2,3,4].map(i => <div key={i} className="w-10 h-10 rounded-full border-2 border-[#0A0A0A] bg-neutral-800" />)}
                                        <div className="text-[10px] font-black uppercase text-neutral-600 self-center pl-6 tracking-widest italic">1.2ms Avg Latency</div>
                                    </div>
                                </div>
                             </div>
                        </div>
                    </div>
                    <div className="space-y-8 order-1 lg:order-2">
                        <TagBadge>Hardware for Software</TagBadge>
                        <h2 className="text-5xl md:text-[80px] font-black italic uppercase tracking-tighter leading-[0.8] text-glow">
                            Move Safety <br />
                            <span className="text-emerald-500 font-bold italic">to the Code.</span>
                        </h2>
                        <p className="text-xl text-neutral-400 font-medium leading-relaxed italic">
                            System prompts are easily jailbroken. LLM instruct-tuning can be bypassed by &lsquo;God Mode&rsquo; prompts or base64 encoding. <br /><br />
                            SupraWall moves protection from <span className="text-white italic">Natural Language instructions</span> to <span className="text-white italic">Deterministic SDK rules</span>. Access is denied because the math says no, not because the agent was told to be careful.
                        </p>
                    </div>
                </div>
            </section>

            {/* 🏆 COMPARISON — SupraWall vs Fragmented Stack */}
            <section className="py-40 px-6 bg-[#030303] border-y border-white/5 relative overflow-hidden text-center">
                <div className="absolute inset-0 bg-emerald-500/[0.02] blur-[100px] rounded-full pointer-events-none" />
                <div className="max-w-7xl mx-auto space-y-24 relative z-10">
                    <div className="space-y-6">
                        <TagBadge>SupraWall vs. The Rest</TagBadge>
                        <h2 className="text-6xl md:text-[10rem] font-black italic tracking-tighter leading-[0.8] uppercase text-glow">
                             Stop Guessing. <br />
                             <span className="text-emerald-500 underline decoration-white/10 italic">Start Enforcing.</span>
                        </h2>
                    </div>

                    <div className="overflow-x-auto rounded-[3.5rem] border border-white/5 bg-neutral-900/20 backdrop-blur-3xl p-1 md:p-8 text-left">
                        <table className="w-full text-left border-separate border-spacing-0">
                            <thead>
                                <tr>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic">Core Governance</th>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic text-center">Prompt-Based Safety</th>
                                    <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-emerald-500 italic text-center bg-emerald-500/5 rounded-t-[2.5rem]">SupraWall Policy Engine</th>
                                </tr>
                            </thead>
                            <tbody className="text-lg font-bold">
                                {COMPARISON_DATA.map((row, i) => (
                                    <tr key={i} className="group">
                                        <td className="p-8 border-t border-white/5 text-white/80 group-hover:text-white transition-colors uppercase italic tracking-tighter">{row.feature}</td>
                                        <td className="p-8 border-t border-white/5 text-neutral-500 text-center uppercase text-sm font-black italic opacity-40">{row.prompt}</td>
                                        <td className={`p-8 border-t border-white/5 text-emerald-500 text-center font-black italic tracking-widest bg-emerald-500/5 ${i === COMPARISON_DATA.length - 1 ? 'rounded-b-[2.5rem]' : ''}`}>
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
                        <TagBadge>Implementation</TagBadge>
                        <h2 className="text-5xl md:text-8xl font-black italic uppercase tracking-tighter leading-none text-glow">
                            One rule. Total <br />
                            <span className="text-emerald-500 italic">compliance.</span>
                        </h2>
                        <p className="text-xl text-neutral-500 font-bold uppercase tracking-widest italic max-w-2xl mx-auto">
                            Add a policy block to your agent config. It&apos;s that simple. 
                        </p>
                    </div>

                    <div className="bg-[#0A0A0A] border-[3px] border-emerald-500/40 rounded-[3rem] p-12 text-sm md:text-base font-mono relative overflow-hidden group shadow-[0_0_80px_rgba(16,185,129,0.15)]">
                        <div className="absolute top-6 right-8 text-emerald-500/50 flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                            <Code className="w-4 h-4" /> SECURE_POLICY.JS
                        </div>
                        <pre className="text-emerald-100/90 leading-loose">
                            {`import { secure_agent } from "suprawall";\n\nconst agent = secure_agent(my_base_agent, {\n  api_key: "ag_...",\n\n  // 🛡️ Deterministic Governance\n  policies: [\n    { tool: "db.*", action: "DENY", reason: "Direct DB access forbidden" },\n    { tool: "email.send_to_customers", action: "REQUIRE_APPROVAL" },\n    { tool: "search.web", action: "ALLOW" }\n  ]\n});\n\n// Agent attempts a tool call -> SupraWall intercepts & evaluates`}
                        </pre>
                    </div>

                    <div className="flex flex-col md:flex-row gap-8">
                        <div className="flex-1 p-8 rounded-[2rem] bg-neutral-900/50 border border-white/5 space-y-4">
                            <div className="flex items-center gap-3 text-emerald-500">
                                <Zap className="w-5 h-5" />
                                <span className="text-xs font-black uppercase tracking-widest italic">Fast Enforcement</span>
                            </div>
                            <p className="text-neutral-500 text-xs font-bold uppercase tracking-tight leading-relaxed italic">Policy evaluation happens locally at the edge. No network round-trips for core rules. 1.2ms latency impact.</p>
                        </div>
                        <div className="flex-1 p-8 rounded-[2rem] bg-neutral-900/50 border border-white/5 space-y-4">
                            <div className="flex items-center gap-3 text-blue-500">
                                <Users className="w-5 h-5" />
                                <span className="text-xs font-black uppercase tracking-widest italic">Human Approvals</span>
                            </div>
                            <p className="text-neutral-500 text-xs font-bold uppercase tracking-tight leading-relaxed italic">Require approval via Dashboard, Slack, or Teams. Perfect for financial transactions or prod deployments.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ❓ FAQ */}
            <section className="py-40 px-6 bg-black border-t border-white/5">
                <div className="max-w-4xl mx-auto space-y-16">
                    <h3 className="text-4xl md:text-6xl font-black italic uppercase tracking-tighter text-center italic">Governance FAQ</h3>
                    <div className="space-y-4">
                        {[
                            { q: "What happens when a tool call is blocked?", a: "SupraWall returns a specific error code and a 'hint' to the LLM (e.g., 'Action denied by policy SW-12. Try a different approach'). This forces the LLM to self-correct and find an allowed tool that achieves the same goal safely." },
                            { q: "Does this affect the quality of agent responses?", a: "Actually, it improves them. By constraining the 'action space' to allowed tools, you reduce hallucination and ensure the agent stays on the intended track." },
                            { q: "Can I use external rules (like Python scripts)?", a: "Yes. The Policy Engine supports 'dynamic' rules where you can call a custom function to evaluate the tool call arguments before allowing it." }
                        ].map((faq, i) => (
                            <div key={i} className="p-8 rounded-3xl bg-neutral-900/30 border border-white/5 space-y-4 hover:border-emerald-500/20 transition-all">
                                <h4 className="text-lg font-black italic uppercase text-white tracking-tight">{faq.q}</h4>
                                <p className="text-neutral-500 text-sm font-medium leading-relaxed italic">{faq.a}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-emerald-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>Take Control</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Stop Asking. <br />
                        <span className="text-emerald-500 underline decoration-white/20 font-bold italic">Start Blocking.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Your agent is only as safe as your weakest prompt. Move to deterministic governance today and ship with confidence.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-emerald-600 text-white font-black text-3xl rounded-2xl hover:bg-emerald-500 transition-all shadow-[0_0_100px_rgba(16,185,129,0.3)] tracking-tighter flex items-center gap-4 group">
                            Get Your API Key <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
            
            <footer className="py-20 border-t border-white/5 opacity-40 text-center">
                 <p className="text-[10px] font-black uppercase tracking-[0.5em] italic">SupraWall Policy Engine • Secure Interception v1.2</p>
            </footer>
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

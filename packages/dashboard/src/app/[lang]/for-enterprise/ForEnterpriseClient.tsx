// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { motion } from "framer-motion";
import { 
    Globe, ShieldCheck, ArrowRight, LayoutDashboard, 
    Lock, CheckCircle2, CloudLightning, Database, 
    Share2, Zap, Users, ShieldAlert, Cpu
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

export default function ForEnterpriseClient() {
    return (
        <main className="overflow-hidden bg-[#030303]">
            {/* 🚀 HERO */}
            <section className="relative pt-48 pb-32 px-6">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[1000px] opacity-10 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-purple-500/20 blur-[180px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto flex flex-col items-center text-center space-y-12 relative z-10">
                    <TagBadge>Enterprise Landing</TagBadge>
                    <div className="space-y-6">
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                             Scale Your Fleet. <br />
                             <span className="text-purple-500 font-bold italic underline decoration-white/10 uppercase italic">Control Your Risk.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-400 max-w-4xl mx-auto leading-relaxed font-medium italic">
                             Your developers can protect your AI agents in 30 seconds. Centralized security, private cloud deployments, and SLA-backed infrastructure for the autonomous enterprise.
                        </p>
                    </div>
                </div>
            </section>

             {/* 🎯 ENTERPRISE DIFFERENTIATORS SECTION */}
             <section className="py-24 px-6 md:px-0 bg-black border-y border-white/5 relative">
                <div className="max-w-7xl mx-auto space-y-24">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-20">
                         <div className="flex flex-col justify-center space-y-10">
                             <TagBadge>Consolidated Control</TagBadge>
                             <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter leading-none text-glow">
                                 The Governance <br />
                                 <span className="text-purple-500 font-bold italic underline decoration-white/10 uppercase italic">Command Center.</span>
                             </h2>
                             <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-relaxed">
                                 For large organizations, security isn&apos;t just one agent — it&apos;s managing thousands of them. SupraWall Enterprise provides a unified dashboard to enforce global policy sets, manage API quotas, and audit cross-departmental agent behavior.
                             </p>
                             <ul className="space-y-4">
                                 {[
                                     "Private VPC & On-Premise Support",
                                     "Centralized Key Management",
                                     "SAML/SSO Authentication",
                                     "Role-Based Access Control (RBAC)"
                                 ].map(item => (
                                     <li key={item} className="flex items-center gap-3 text-white text-sm font-black italic uppercase tracking-tighter">
                                         <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                         {item}
                                     </li>
                                 ))}
                             </ul>
                         </div>
                         <div className="flex items-center justify-center relative">
                             <div className="p-8 bg-neutral-900/60 border border-white/10 rounded-[4rem] backdrop-blur-3xl shadow-2xl relative overflow-hidden group">
                                 <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 blur-[80px] pointer-events-none" />
                                 <div className="space-y-8 relative z-10">
                                     <div className="flex items-center justify-between">
                                         <div className="p-3 bg-purple-500/20 text-purple-400 rounded-xl"><Globe className="w-6 h-6" /></div>
                                         <span className="text-[10px] font-black uppercase text-neutral-500 tracking-widest">Cross-Cloud Hub</span>
                                     </div>
                                     <div className="space-y-2">
                                         <div className="h-4 w-full bg-white/5 rounded-full overflow-hidden">
                                             <div className="h-full bg-purple-500 w-[70%]" />
                                         </div>
                                         <div className="flex justify-between text-[10px] font-black uppercase text-neutral-600">
                                             <span>Agent Cluster A (Azure)</span>
                                             <span>70% Compliance</span>
                                         </div>
                                     </div>
                                     <div className="space-y-2 opacity-50">
                                         <div className="h-4 w-full bg-white/5 rounded-full overflow-hidden">
                                             <div className="h-full bg-blue-500 w-[95%]" />
                                         </div>
                                         <div className="flex justify-between text-[10px] font-black uppercase text-neutral-600">
                                             <span>Agent Cluster B (AWS)</span>
                                             <span>95% Compliance</span>
                                         </div>
                                     </div>
                                 </div>
                             </div>
                         </div>
                    </div>
                </div>
            </section>

             {/* 🎯 TRUST PILLARS */}
             <section className="py-40 px-6">
                <div className="max-w-7xl mx-auto space-y-24 text-center">
                    <div className="space-y-6">
                        <TagBadge>Institutional Standards</TagBadge>
                        <h2 className="text-5xl md:text-[6rem] font-black italic uppercase tracking-tighter leading-[0.8] text-glow">
                             High Scale. <br />
                             <span className="text-purple-500 font-bold italic underline decoration-white/10 italic">Zero Latency.</span>
                        </h2>
                    </div>

                     <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { title: "SLA Guaranteed", desc: "Enterprise infrastructure with 99.99% uptime and dedicated support channels.", icon: <ShieldCheck className="w-8 h-8 text-purple-400" /> },
                            { title: "Custom Policies", desc: "Build industry-specific policy sets tailored to your unique internal tool sets.", icon: <Users className="w-8 h-8 text-purple-400" /> },
                            { title: "Secure Deployment", desc: "Native support for Kubernetes, VPC-native nodes, and private cloud architectures.", icon: <CloudLightning className="w-8 h-8 text-purple-400" /> }
                        ].map((p, i) => (
                            <div key={p.title} className="p-12 rounded-[3.5rem] bg-neutral-900/40 border border-white/5 space-y-8 hover:border-purple-500/30 transition-all group overflow-hidden relative text-left">
                                <div className="p-4 rounded-xl bg-white/5 border border-white/10 w-fit group-hover:scale-110 transition-transform">{p.icon}</div>
                                <div className="space-y-4">
                                     <h4 className="text-3xl font-black italic uppercase text-white tracking-tighter leading-none">{p.title}</h4>
                                     <p className="text-neutral-500 text-sm font-bold uppercase tracking-tight italic leading-relaxed">{p.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

             {/* 🎯 PROCUREMENT & COMPLIANCE */}
             <section className="py-24 px-6 md:px-0 bg-neutral-900/20 border-y border-white/5 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 blur-[120px] pointer-events-none" />
                <div className="max-w-7xl mx-auto space-y-16">
                    <div className="flex flex-col md:flex-row items-end justify-between gap-8">
                        <div className="space-y-4">
                            <TagBadge>Procurement Ready</TagBadge>
                            <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter leading-none text-glow">
                                Built for <br />
                                <span className="text-emerald-500 font-bold italic underline decoration-white/10 uppercase italic">Enterprise Paperwork.</span>
                            </h2>
                        </div>
                        <p className="text-neutral-500 text-lg font-bold italic uppercase tracking-tighter leading-relaxed max-w-xl text-right">
                            We understand that security is only half the battle. SupraWall Enterprise is designed to slide through procurement with standard-grade legal and compliance frameworks.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {[
                            { title: "Standard DPA", desc: "GDPR-compliant Data Processing Agreement signed and ready for your legal team." },
                            { title: "HIPAA BAA", desc: "Sign a Business Associate Agreement to process Protected Health Information (PHI)." },
                            { title: "Custom MSA", desc: "Flexible Master Service Agreements tailored to your organization's legal requirements." },
                            { title: "SOC 2 Type II", desc: "Full audit reports available upon request for security and availability trust principles." }
                        ].map(item => (
                            <div key={item.title} className="p-8 rounded-3xl bg-black/40 border border-white/5 space-y-4 hover:border-emerald-500/30 transition-all group">
                                <ShieldCheck className="w-8 h-8 text-emerald-400 group-hover:scale-110 transition-transform" />
                                <h4 className="text-xl font-black italic uppercase text-white tracking-tighter">{item.title}</h4>
                                <p className="text-neutral-500 text-[10px] font-bold uppercase tracking-widest leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
             </section>

             {/* 🎯 FINAL CTA */}
             <section className="py-48 px-6 bg-black relative text-center">
                <div className="absolute inset-0 bg-purple-500/10 blur-[150px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] pointer-events-none" />
                <div className="max-w-4xl mx-auto space-y-12 relative z-10">
                    <TagBadge>For Executives</TagBadge>
                    <h2 className="text-7xl md:text-[8rem] font-black uppercase italic leading-[0.8] tracking-tighter text-glow">
                        Move Fast. <br />
                        <span className="text-purple-500 underline decoration-white/20 font-bold italic uppercase italic">Stop Rogue AI.</span>
                    </h2>
                    <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-2xl mx-auto">
                        Don&apos;t let security be the bottleneck to your AI ROI. Standardize your autonomous infrastructure with SupraWall Enterprise today.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
                        <Link href="/beta" className="px-16 py-8 bg-purple-600 text-white font-black text-3xl rounded-3xl hover:bg-purple-500 transition-all shadow-[0_0_100px_rgba(168,85,247,0.3)] tracking-tighter flex items-center gap-4 group">
                             Talk to Enterprise Sales <ArrowRight className="w-10 h-10 group-hover:translate-x-4 transition-transform" />
                        </Link>
                    </div>
                </div>
            </section>
        </main>
    );
}

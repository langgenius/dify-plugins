// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { 
    Terminal, Download, Shield, Zap, CheckCircle2, 
    ArrowRight, Globe, Lock, Code2, Server, Github 
} from "lucide-react";
import Link from "next/link";
import { TagBadge } from "@/app/HomeClient";

export default function SelfHostPage() {
    const router = useRouter();

    useEffect(() => {
        // Stealth launch redirect
        router.push('/beta');
    }, [router]);

    return (
        <div className="min-h-screen bg-black text-neutral-200 font-sans selection:bg-emerald-500/30">
            <Navbar />

            <main className="pt-40 pb-32 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    
                    {/* 🚀 Header */}
                    <div className="text-center space-y-8">
                        <TagBadge>Developer Autonomy</TagBadge>
                        <h1 className="text-6xl md:text-[100px] font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                            Your Infra. <br />
                            <span className="text-emerald-500 font-bold">Your Control.</span>
                        </h1>
                        <p className="text-xl md:text-2xl text-neutral-500 max-w-3xl mx-auto font-medium italic">
                            SupraWall is open-source. Run it as a sidecar, a gateway, or a cluster. No telemetry. No phone-home. Just deterministic security.
                        </p>
                    </div>

                    {/* ⚙️ Deployment Options */}
                    <div className="grid lg:grid-cols-2 gap-12">
                        
                        {/* Option 1: Docker Compose */}
                        <div className="p-12 rounded-[3.5rem] bg-neutral-900/30 border border-white/5 backdrop-blur-3xl space-y-8 hover:border-emerald-500/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="p-4 bg-emerald-500/10 rounded-2xl text-emerald-500 group-hover:scale-110 transition-transform">
                                    <Server className="w-8 h-8" />
                                </div>
                                <span className="text-[10px] font-black uppercase tracking-widest text-neutral-600">Recommended</span>
                            </div>
                            <div className="space-y-4">
                                <h2 className="text-4xl font-black italic uppercase tracking-tighter text-white">Docker Compose</h2>
                                <p className="text-sm text-neutral-500 font-bold uppercase italic tracking-tight">Set up the full stack (Dashboard + Server + DB) in 60 seconds.</p>
                            </div>
                            
                            <div className="bg-black/50 rounded-2xl p-6 font-mono text-sm text-emerald-400 border border-white/5 relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-5">
                                    <Terminal className="w-12 h-12" />
                                </div>
                                <div className="space-y-2">
                                    <p className="text-neutral-600"># Clone the repo</p>
                                    <p>git clone https://github.com/wiserautomation/SupraWall</p>
                                    <p className="text-neutral-600"># Launch the stack</p>
                                    <p>cd suprawall && docker-compose up -d</p>
                                </div>
                            </div>

                            <ul className="space-y-3">
                                {["PostgreSQL 16", "Redis for Caching", "Dashboard UI", "API Gateway"].map((item, id) => (
                                    <li key={id} className="flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest italic text-neutral-400">
                                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Option 2: NPM / Sidecar */}
                        <div className="p-12 rounded-[3.5rem] bg-neutral-900/30 border border-white/5 backdrop-blur-3xl space-y-8 hover:border-blue-500/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="p-4 bg-blue-500/10 rounded-2xl text-blue-400 group-hover:scale-110 transition-transform">
                                    <Terminal className="w-8 h-8" />
                                </div>
                            </div>
                            <div className="space-y-4">
                                <h2 className="text-4xl font-black italic uppercase tracking-tighter text-white">NPM Sidecar</h2>
                                <p className="text-sm text-neutral-500 font-bold uppercase italic tracking-tight">Integrate the security engine directly into your Node.js app.</p>
                            </div>
                            
                            <div className="bg-black/50 rounded-2xl p-6 font-mono text-sm text-blue-400 border border-white/5 relative overflow-hidden">
                                <div className="space-y-2">
                                    <p className="text-neutral-600"># Install the core engine</p>
                                    <p>npm install @suprawall/server</p>
                                    <p className="text-neutral-600"># Start local server</p>
                                    <p>npx suprawall start --port 8080</p>
                                </div>
                            </div>

                            <ul className="space-y-3">
                                {["Low-latency local evaluation", "Minimal resource footprint", "Compatible with any DB", "Perfect for edge/lambda"].map((item, id) => (
                                    <li key={id} className="flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest italic text-neutral-400">
                                        <CheckCircle2 className="w-3 h-3 text-blue-500" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* 📊 Comparison Table */}
                    <div className="py-20 space-y-16">
                        <div className="text-center space-y-4">
                            <h2 className="text-4xl font-black italic uppercase tracking-tighter">Architecture Comparison</h2>
                            <p className="text-neutral-500 font-bold uppercase tracking-widest">Choose the model that fits your security requirements.</p>
                        </div>

                        <div className="overflow-x-auto rounded-[3.5rem] border border-white/5 bg-neutral-900/20 backdrop-blur-3xl p-8">
                            <table className="w-full text-left border-separate border-spacing-0">
                                <thead>
                                    <tr>
                                        <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic">Feature</th>
                                        <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-neutral-500 italic text-center">Self-Hosted</th>
                                        <th className="p-8 text-[11px] font-black uppercase tracking-[0.4em] text-emerald-500 italic text-center bg-emerald-500/5 rounded-t-[2.5rem]">SupraWall Cloud</th>
                                    </tr>
                                </thead>
                                <tbody className="text-lg font-bold">
                                    {[
                                        { feat: "Primary Database", self: "PostgreSQL 16", cloud: "PostgreSQL + Firebase" },
                                        { feat: "Billing Stack", self: "None (Free Forever)", cloud: "Stripe + Firebase Admin" },
                                        { feat: "Credential Vault", self: "Local / Env Var", cloud: "Cloud HSM / KMS" },
                                        { feat: "Infrastructure", self: "Docker / K8s", cloud: "Serverless (Vercel)" },
                                        { feat: "Updates", self: "Manual (Pull Repo)", cloud: "Autoscaled Managed" },
                                    ].map((row, i) => (
                                        <tr key={i} className="group">
                                            <td className="p-8 border-t border-white/5 text-white/80 group-hover:text-white transition-colors uppercase italic tracking-tighter">{row.feat}</td>
                                            <td className="p-8 border-t border-white/5 text-neutral-500 text-center uppercase text-sm font-black italic opacity-60">{row.self}</td>
                                            <td className={`p-8 border-t border-white/5 text-emerald-500 text-center font-black italic tracking-widest bg-emerald-500/5 ${i === 4 ? 'rounded-b-[2.5rem]' : ''}`}>
                                                {row.cloud}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="bg-rose-500/5 border border-rose-500/20 p-12 rounded-[2.5rem] space-y-6">
                            <h3 className="text-2xl font-black italic uppercase tracking-tighter text-rose-500 flex items-center gap-3">
                                <Zap className="w-6 h-6" /> ARCHITECTURE NOTE
                            </h3>
                            <p className="text-neutral-400 font-medium leading-relaxed italic">
                                SupraWall's cloud-managed version uses a <span className="text-white font-bold">dual-stack architecture</span>. While Postgres handles all core agent logic and security policies, Firebase + Stripe are exclusively used for usage-metering and subscription management. 
                                <br /><br />
                                <span className="text-white font-bold">Self-hosted environments</span> bypass the Firebase/Stripe layer entirely, requiring only Docker and Postgres to run.
                            </p>
                        </div>
                    </div>

                    {/* 🎯 Final CTA */}
                    <div className="p-20 rounded-[4rem] bg-gradient-to-br from-neutral-900 to-black border-2 border-white/5 relative overflow-hidden text-center space-y-12">
                        <div className="absolute top-0 right-0 p-12 opacity-5">
                            <Github className="w-64 h-64" />
                        </div>
                        <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter leading-none text-white">
                            Ready to <span className="text-emerald-500 underline decoration-white/10 font-bold italic">Shield</span> Your Swarm?
                        </h2>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                            <Link
                                href="https://github.com/wiserautomation/SupraWall"
                                target="_blank"
                                prefetch={false}
                                rel="noopener noreferrer"
                                className="px-16 py-8 bg-emerald-600 text-white font-black text-2xl rounded-3xl hover:bg-emerald-500 transition-all shadow-[0_20px_50px_rgba(16,185,129,0.3)] flex items-center gap-4 group"
                            >
                                <Github className="w-8 h-8" /> STAR THE REPO
                            </Link>
                            <Link 
                                href="/docs" 
                                className="px-16 py-8 border-2 border-white/10 text-white font-black text-2xl rounded-3xl hover:bg-white/5 transition-all text-center"
                            >
                                READ THE DOCS
                            </Link>
                        </div>
                    </div>

                </div>
            </main>

            <Footer />
        </div>
    );
}

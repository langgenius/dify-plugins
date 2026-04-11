// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { CodeBlock } from "@/components/CodeBlock";
import { Shield, Zap, Terminal, Activity, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function GitHubActionDocs() {
    return (
        <div className="space-y-10 animate-in fade-in zoom-in-95 duration-500 pb-20">
            <div className="space-y-4">
                <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-semibold uppercase tracking-wider">Integration</span>
                    <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-semibold uppercase tracking-wider">GitHub Marketplace</span>
                </div>
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white drop-shadow-sm">
                    GitHub Action: SupraWall Scan
                </h1>
                <p className="text-xl text-neutral-400 max-w-2xl leading-relaxed">
                    Automate agent security audits in your CI/CD pipeline. Detect hardcoded secrets, unsafe tool exposures, and policy violations in every PR.
                </p>
            </div>

            <div className="space-y-12">
                {/* Marketplace Link */}
                <section className="p-6 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex flex-col md:flex-row items-center gap-6 justify-between">
                    <div className="flex items-center gap-4">
                        <Activity className="w-10 h-10 text-blue-400" />
                        <div>
                            <h4 className="text-lg font-bold text-white">Live on GitHub Marketplace</h4>
                            <p className="text-sm text-neutral-400">The official SupraWall security scanner for your repositories.</p>
                        </div>
                    </div>
                    <Link 
                        href="https://github.com/marketplace/actions/suprawall-scan" 
                        target="_blank"
                        className="px-6 py-3 bg-blue-500 text-white rounded-xl font-bold hover:bg-blue-400 transition-all flex items-center gap-2"
                    >
                        View on Marketplace <ArrowRight className="w-4 h-4" />
                    </Link>
                </section>

                {/* Usage */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">1</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Usage</h2>
                    </div>
                    <p className="text-neutral-400">
                        Add the following step to your <code className="text-emerald-400 bg-emerald-400/10 px-1.5 py-0.5 rounded">.github/workflows/security.yml</code> file:
                    </p>
                    <CodeBlock 
                        language="yaml" 
                        code={`- name: SupraWall Security Scan
  uses: wiserautomation/SupraWall@v1.0.0
  with:
    api-key: \${{ secrets.SUPRAWALL_API_KEY }}
    scan-path: "./"
    fail-on-severity: "high"`} 
                    />
                </section>

                {/* Automation Features */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">2</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">CI/CD Guardrails</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {[
                            { title: "Secret Detection", desc: "Prevents leaking 'ag_live_...' or other provider keys in agent definitions.", icon: Shield },
                            { title: "Tool Audit", desc: "Flags tools with name-patterns known for prompt injection risks.", icon: Terminal },
                            { title: "Policy Validation", desc: "Ensures your locally defined AGPS policies meet syntax standards.", icon: CheckCircle2 },
                            { title: "EU AI Act Check", desc: "Verifies technical documentation completeness for high-risk agents.", icon: Activity }
                        ].map((b, i) => (
                            <div key={i} className="p-5 rounded-xl bg-neutral-900 border border-white/5 space-y-3">
                                <div className="flex items-center gap-3">
                                    <b.icon className="w-5 h-5 text-blue-400" />
                                    <h4 className="font-bold text-white">{b.title}</h4>
                                </div>
                                <p className="text-xs text-neutral-500 leading-relaxed">{b.desc}</p>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            <div className="flex justify-between items-center pt-8 border-t border-white/10">
                <Link href="/docs/integrations/openclaw" className="text-neutral-400 hover:text-white transition-colors text-sm">← OpenClaw</Link>
                <Link href="/docs/integrations/stripe" className="text-emerald-400 hover:text-emerald-300 font-semibold transition-colors flex items-center">Stripe Marketplace →</Link>
            </div>
        </div>
    );
}

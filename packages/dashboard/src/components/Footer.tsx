// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import Link from "next/link";
import { Shield, Triangle, Database, Lock } from "lucide-react";

export function Footer() {
    return (
        <footer className="bg-black border-t border-white/5 py-32 px-6 text-neutral-500 font-bold uppercase tracking-widest text-[10px]">
            <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-16">
                <div className="col-span-2 space-y-8">
                    <div className="flex items-center gap-3">
                        <Shield className="w-8 h-8 text-emerald-400" />
                        <span className="text-white font-black text-3xl uppercase italic tracking-tighter">SupraWall</span>
                    </div>
                    <p className="max-w-sm text-lg font-bold leading-tight uppercase italic opacity-60">
                        The security standard for autonomous AI agents. Scaling the zero-trust future with deterministic safety.
                    </p>
                </div>
                <div>
                    <h4 className="font-black text-white uppercase text-xs tracking-widest mb-8">Security Pillars</h4>
                    <ul className="space-y-4">
                        <li><Link href="/features/vault" className="hover:text-emerald-500 transition-colors">Credential Vault</Link></li>
                        <li><Link href="/features/budget-limits" className="hover:text-emerald-500 transition-colors">Budget Limits</Link></li>
                        <li><Link href="/features/policy-engine" className="hover:text-emerald-500 transition-colors">Policy Engine</Link></li>
                        <li><Link href="/features/pii-shield" className="hover:text-emerald-500 transition-colors">PII Shield</Link></li>
                        <li><Link href="/features/audit-trail" className="hover:text-emerald-500 transition-colors">Audit Trail</Link></li>
                        <li><Link href="/features/prompt-shield" className="hover:text-emerald-500 transition-colors">Injection Shield</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 className="font-black text-white uppercase text-xs tracking-widest mb-8">Ecosystem</h4>
                    <ul className="space-y-4">
                        <li><Link href="/integrations" className="hover:text-emerald-500 transition-colors">All Integrations</Link></li>
                        <li><Link href="/integrations/langchain" className="hover:text-emerald-500 transition-colors">LangChain</Link></li>
                        <li><Link href="/integrations/crewai" className="hover:text-emerald-500 transition-colors">CrewAI</Link></li>
                        <li><Link href="/integrations/autogen" className="hover:text-emerald-500 transition-colors">AutoGen</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 className="font-black text-white uppercase text-xs tracking-widest mb-8">Solutions</h4>
                    <ul className="space-y-4">
                        <li><Link href="/for-developers" className="hover:text-emerald-500 transition-colors">For Developers</Link></li>
                        <li><Link href="/for-compliance-officers" className="hover:text-emerald-500 transition-colors">Compliance Officers</Link></li>
                        <li><Link href="/for-enterprise" className="hover:text-emerald-500 transition-colors">For Enterprise</Link></li>
                        <li><Link href="/gdpr" className="hover:text-emerald-500 transition-colors">GDPR & Privacy</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 className="font-black text-white uppercase text-xs tracking-widest mb-8">Compliance</h4>
                    <ul className="space-y-4">
                        <li><Link href="/eu-ai-act" className="hover:text-emerald-500 transition-colors italic">EU AI Act Suite</Link></li>
                        <li><Link href="/security" className="hover:text-emerald-500 transition-colors">Trust Center</Link></li>
                        <li><Link href="/login" className="hover:text-neutral-800 transition-colors">Policy Regulations</Link></li>
                        <li><Link href="/legal/dpa" className="hover:text-emerald-500 transition-colors">Privacy DPA</Link></li>
                        <li><Link href="/privacy" className="hover:text-emerald-500 transition-colors">Privacy Policy</Link></li>
                        <li><Link href="/dashboard" className="hover:text-emerald-500 transition-colors">SOC 2 Portal</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 className="font-black text-white uppercase text-xs tracking-widest mb-8">Open Source</h4>
                    <ul className="space-y-4">
                        <li><Link href="https://github.com/wiserautomation/SupraWall" prefetch={false} rel="noopener noreferrer" target="_blank" className="hover:text-emerald-500 transition-colors">GitHub Repository</Link></li>
                        <li><Link href="/beta" className="hover:text-emerald-400 transition-colors">Self-Host Guide</Link></li>
                        <li><Link href="https://github.com/wiserautomation/SupraWall/blob/main/CONTRIBUTING.md" prefetch={false} rel="noopener noreferrer" target="_blank" className="hover:text-emerald-500 transition-colors">Contributing</Link></li>
                        <li><Link href="https://github.com/wiserautomation/SupraWall/blob/main/LICENSE" prefetch={false} rel="noopener noreferrer" target="_blank" className="hover:text-emerald-500 transition-colors">Apache 2.0</Link></li>
                    </ul>
                </div>
            </div>
            <div className="max-w-7xl mx-auto pt-32 flex flex-col items-center gap-4">
                <div className="flex gap-4 opacity-30">
                    <Triangle className="w-5 h-5 fill-white" />
                    <Database className="w-5 h-5 fill-white" />
                    <Lock className="w-5 h-5 fill-white" />
                </div>
                <div className="text-[10px] font-black uppercase tracking-[0.6em] text-center opacity-20 italic">
                    © 2026 SUPRAWALL • SECURING THE AUTONOMOUS FUTURE • BUILT FOR AUDITORS.
                </div>
            </div>
        </footer>
    );
}

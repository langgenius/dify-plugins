// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { ArrowRight, Code2, Shield, Zap, Terminal, CheckCircle2, FileText, Globe } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Security for OpenAI Agents SDK | Runtime Guardrails | SupraWall",
    description: "Secure your OpenAI Agents SDK deployments with runtime interception. Prevent unauthorized tool calls and exfiltration in autonomous system loops.",
    keywords: ["openai agents security", "secure openai sdk agents", "openai tool call guardrails", "agentic execution policy", "openai swarm security"],
    alternates: {
        canonical: 'https://www.supra-wall.com/integrations/openai-agents',
    },
};

export default function OpenAIAgentsIntegrationPage() {
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "SupraWall for OpenAI Agents",
        "applicationCategory": "SecurityApplication",
        "url": "https://www.supra-wall.com/integrations/openai-agents",
        "author": { "@type": "Organization", "name": "SupraWall" },
        "description": "Enterprise-grade runtime security and audit trailing for OpenAI Agents SDK and Swarms."
    };

    return (
        <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30 font-sans">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
            <Navbar />

            <main className="pt-40 pb-32 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    
                    {/* Hero */}
                    <div className="text-center space-y-10 group">
                        <div className="inline-flex items-center px-4 py-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-[10px] font-black text-emerald-400 tracking-[0.2em] uppercase">
                            Infrastructure • OpenAI Agents SDK Official
                        </div>
                        <h1 className="text-6xl md:text-9xl font-black tracking-tighter leading-[0.8] uppercase italic">
                            Security for <br />
                            <span className="text-emerald-500 group-hover:text-emerald-400 transition-colors italic">OpenAI</span> <br />
                            Agents
                        </h1>
                        <p className="text-2xl text-neutral-400 max-w-3xl mx-auto font-medium leading-[1.3] italic">
                            Preventing unauthorized tool calls and PII exfiltration in autonomous OpenAI agent loops.
                        </p>
                    </div>

                    {/* Quick Install */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight italic">Quick Install</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[2.5rem] p-4 flex flex-col md:flex-row items-stretch md:items-center gap-4">
                             <div className="flex-1 p-6 bg-black rounded-3xl border border-white/5 font-mono text-emerald-400 text-sm">
                                 pip install <span className="text-white">suprawall</span>
                             </div>
                             <div className="flex gap-4">
                                 <Link href="https://github.com/wiserautomation/SupraWall" prefetch={false} rel="noopener noreferrer" target="_blank" className="p-6 bg-white text-black rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-neutral-200 transition-all flex items-center gap-2">
                                     GitHub <ArrowRight className="w-4 h-4" />
                                 </Link>
                                 <Link href="https://docs.suprawall.com" className="p-6 bg-white/5 border border-white/10 text-white rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-white/10 transition-all italic">
                                     Documentation
                                 </Link>
                             </div>
                         </div>
                    </div>

                    {/* Code Example */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight italic text-right">Implementation</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[3rem] p-12 border border-white/5 font-mono text-sm leading-relaxed overflow-hidden relative group">
                             <pre className="text-emerald-400">{`from openai import OpenAI
from suprawall.openai import SupraWallProtector

# Initialize the protector
sw = SupraWallProtector(api_key="sw_live_...")

# Wrap your OpenAI Assistant or Agent
# This intercepts every tool execution at the SDK level
protected_client = sw.protect(OpenAI())

# Agent tool calls are now policy-governed
protected_client.beta.assistants.create(
    name="Financial Analyst",
    tools=[{"type": "function", "function": ...}],
    model="gpt-4-turbo"
)

# Intercept loops and block unauthorized tool actions
# No prompt-based security needed. It's deterministic.`}</pre>
                             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-emerald-500/5 blur-[120px] rounded-full group-hover:bg-emerald-500/10 transition-all duration-1000 -z-10" />
                         </div>
                    </div>

                    {/* Feature Highlights */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10 py-20 border-t border-white/5">
                         {[
                             { title: "Deterministic Interception", desc: "Native support for OpenAI Assistant tool calls. Block execution even if the model attempts to override prompt-based instructions." },
                             { title: "Real-time Auditing", desc: "Automatic logging of every tool call, argument, and result. Satisfies Article 12 of the EU AI Act." },
                             { title: "Human Override Queue", desc: "Establish human-in-the-loop approvals for sensitive operations like refund_payment or delete_user." },
                             { title: "Cross-Agent Observability", desc: "Single pane of glass for all OpenAI agents across your entire team or swarm." }
                         ].map((item, i) => (
                             <div key={i} className="p-10 rounded-[3rem] bg-neutral-900 border border-white/5 space-y-4 hover:border-emerald-500/30 transition-all">
                                  <CheckCircle2 className="w-7 h-7 text-emerald-500" />
                                  <h4 className="text-xl font-black uppercase italic tracking-tight text-white leading-none">{item.title}</h4>
                                  <p className="text-neutral-500 font-medium leading-[1.6] text-lg">{item.desc}</p>
                             </div>
                         ))}
                    </div>

                    {/* CTA */}
                    <div className="p-20 rounded-[4rem] bg-emerald-600 text-center space-y-12 shadow-2xl group">
                         <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic text-white leading-[0.85] group-hover:scale-105 transition-transform duration-700">
                              Secure Your <br />OpenAI Agents.
                         </h2>
                         <Link href="/beta" className="inline-flex px-12 py-5 bg-white text-black font-black uppercase tracking-widest rounded-3xl hover:bg-neutral-100 transition-all">
                              Start Building for Free
                         </Link>
                    </div>

                </div>
            </main>

            <footer className="py-20 border-t border-white/5 text-center">
                 <p className="text-neutral-800 text-[10px] font-black uppercase tracking-[0.5em]">
                    Real-time Agent Security • 2026
                 </p>
            </footer>
        </div>
    );
}

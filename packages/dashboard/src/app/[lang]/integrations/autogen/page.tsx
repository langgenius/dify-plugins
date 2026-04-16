// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { ArrowRight, Box, Shield, Zap, Terminal, CheckCircle2, FileText, Globe } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "AutoGen Agent Security | Real-time Guardrails | SupraWall",
    description: "Secure your AutoGen agents with runtime interception. Prevent unauthorized code execution and PII exfiltration in autonomous multi-agent conversations.",
    keywords: ["autogen security", "secure autogen agents", "autogen guardrails", "agentic code execution security", "microsoft autogen security"],
    alternates: {
        canonical: 'https://www.supra-wall.com/integrations/autogen',
    },
};

export default function AutoGenIntegrationPage() {
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "SupraWall for AutoGen",
        "applicationCategory": "SecurityApplication",
        "url": "https://www.supra-wall.com/integrations/autogen",
        "author": { "@type": "Organization", "name": "SupraWall" },
        "description": "Enterprise-grade runtime security for AutoGen agents."
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
                            Multi-Agent Governance • Microsoft AutoGen
                        </div>
                        <h1 className="text-6xl md:text-9xl font-black tracking-tighter leading-[0.8] uppercase italic">
                            Security for <br />
                            <span className="text-emerald-500 group-hover:text-emerald-400 transition-colors">AutoGen</span> <br />
                            Swarms
                        </h1>
                        <p className="text-2xl text-neutral-400 max-w-3xl mx-auto font-medium italic leading-relaxed">
                            Securing autonomous conversations from rogue code execution and unauthorized API access.
                        </p>
                    </div>

                    {/* One-Liner Install */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight">Quick Install</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[2.5rem] p-4 flex flex-col md:flex-row items-stretch md:items-center gap-4">
                             <div className="flex-1 p-6 bg-black rounded-3xl border border-white/5 font-mono text-emerald-400 text-sm">
                                 pip install <span className="text-white">suprawall</span>
                             </div>
                             <div className="flex gap-4">
                                 <Link href="https://github.com/wiserautomation/SupraWall" prefetch={false} rel="noopener noreferrer" target="_blank" className="p-6 bg-white text-black rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-neutral-200 transition-all flex items-center gap-2">
                                     GitHub <ArrowRight className="w-4 h-4" />
                                 </Link>
                                 <Link href="https://docs.suprawall.com" className="p-6 bg-white/5 border border-white/10 text-white rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-white/10 transition-all">
                                     Documentation
                                 </Link>
                             </div>
                         </div>
                    </div>

                    {/* Code Snippet */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight text-right">Implementation</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[3rem] p-12 border border-white/5 font-mono text-sm leading-relaxed overflow-hidden relative group">
                             <p className="text-neutral-500 mb-4"># Protecting AutoGen conversations with SupraWall</p>
                             <pre className="text-emerald-400">{`import autogen
from suprawall.autogen import SupraWallMiddleware

# Initialize firewall
sw = SupraWallMiddleware(api_key="sw_live_...")

# Configure your AutoGen agents
assistant = autogen.AssistantAgent("assistant", ...)
user_proxy = autogen.UserProxyAgent("user_proxy", ...)

# Register SupraWall to intercept every interaction
sw.register(assistant)
sw.register(user_proxy)

# Conversations are now audit-trailed and policy-governed
user_proxy.initiate_chat(assistant, message="Analyze this shell script...")`}</pre>
                             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-emerald-500/5 blur-[120px] rounded-full group-hover:bg-emerald-500/10 transition-all duration-1000 -z-10" />
                         </div>
                    </div>

                    {/* Detailed Content */}
                    <div className="prose prose-invert prose-emerald max-w-none grid grid-cols-1 md:grid-cols-2 gap-20 py-20 border-t border-white/5">
                         <div className="space-y-6">
                              <h3 className="text-3xl font-black uppercase italic tracking-tight text-white leading-none">Why AutoGen Needs SupraWall</h3>
                              <p className="text-neutral-300 font-medium italic leading-relaxed text-lg">
                                 AutoGen's power lies in the interaction between recursive agents. However, without a dedicated security layer, your user_proxy can easily be tricked into executing malicious code generated by an assistant model.
                              </p>
                              <p className="text-neutral-400 font-medium leading-relaxed">
                                 SupraWall intercepts the messaging layer of AutoGen. We verify the code blocks being passed between agents against your local or cloud-based policies, ensuring that even if an assistant generates a `rm -rf /` command, it is blocked before the user_proxy executes it.
                              </p>
                         </div>
                         <div className="space-y-4">
                              {[
                                  { title: "Code Sandboxing", detail: "Real-time inspection of Python/Bash code blocks." },
                                  { title: "Recursive Depth Guard", detail: "Prevent infinite message loops from draining model budget." },
                                  { title: "Identity Governance", detail: "Ensure agents correctly represent their assigned roles." },
                                  { title: "EU AI Act Compliance", detail: "Automatic logging and oversight for Article 12 accountability." }
                              ].map((item, i) => (
                                  <div key={i} className="flex items-center gap-4 p-6 rounded-3xl bg-neutral-900 border border-white/5 hover:border-emerald-500/30 transition-all">
                                       <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                       <div className="space-y-1">
                                            <p className="text-white font-black uppercase text-xs tracking-widest">{item.title}</p>
                                            <p className="text-neutral-500 text-xs font-medium italic">{item.detail}</p>
                                       </div>
                                  </div>
                              ))}
                         </div>
                    </div>

                    {/* CTA */}
                    <div className="p-16 rounded-[4rem] bg-emerald-600 text-center space-y-10 shadow-2xl relative overflow-hidden group">
                         <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic text-white leading-[0.85] group-hover:scale-105 transition-transform duration-700">
                              Secure Your <br />Conversations.
                         </h2>
                         <Link href="/beta" className="inline-flex px-12 py-5 bg-white text-black font-black uppercase tracking-widest rounded-3xl hover:bg-neutral-100 transition-all">
                              Start Building for Free
                         </Link>
                         <div className="absolute inset-0 bg-gradient-to-br from-emerald-400 to-transparent opacity-0 group-hover:opacity-20 transition-opacity" />
                    </div>

                </div>
            </main>

            <footer className="py-20 border-t border-white/5 text-center">
                 <p className="text-neutral-800 text-[10px] font-black uppercase tracking-[0.5em]">
                    Enterprise Agent Security • 2026
                 </p>
            </footer>
        </div>
    );
}

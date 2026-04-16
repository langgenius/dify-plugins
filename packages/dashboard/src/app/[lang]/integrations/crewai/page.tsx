// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { ArrowRight, Code2, Shield, Zap, Terminal, CheckCircle2, FileText, Globe } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Security for CrewAI Agents | Tool-Call Interception | SupraWall",
    description: "Secure your CrewAI swarms with runtime policy enforcement. Prevent prompt injection and rogue tool execution in autonomous multi-agent systems.",
    keywords: ["crewai security", "secure crewai", "crewai guardrails", "agentic tool policy", "multi-agent security"],
    alternates: {
        canonical: 'https://www.supra-wall.com/integrations/crewai',
    },
};

export default function CrewAIIntegrationPage() {
    const softwareAppSchema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "SupraWall for CrewAI",
        "applicationCategory": "SecurityApplication",
        "url": "https://www.supra-wall.com/integrations/crewai",
        "author": { "@type": "Organization", "name": "SupraWall" },
        "description": "Enterprise security and runtime guardrails for CrewAI multi-agent systems."
    };

    const howToSchema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "How to secure CrewAI agents",
        "step": [
            { "@type": "HowToStep", "name": "Install SDK", "text": "pip install suprawall" },
            { "@type": "HowToStep", "name": "Wrap Crew", "text": "Wrap your Crew object with the SupraWall protector." }
        ]
    };

    return (
        <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30 font-sans">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareAppSchema) }} />
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(howToSchema) }} />
            <Navbar />

            <main className="pt-40 pb-32 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    
                    {/* Hero */}
                    <div className="text-center space-y-10 group">
                        <div className="inline-flex items-center px-4 py-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-[10px] font-black text-emerald-400 tracking-[0.2em] uppercase">
                            Multi-Agent Governance • CrewAI
                        </div>
                        <h1 className="text-6xl md:text-9xl font-black tracking-tighter leading-[0.8] uppercase italic">
                            Security for <br />
                            <span className="text-emerald-500 group-hover:text-emerald-400 transition-colors">CrewAI</span> <br />
                            Swarms
                        </h1>
                        <p className="text-2xl text-neutral-400 max-w-3xl mx-auto font-medium italic">
                            Protecting multi-agent tool execution from recursive loops and rogue actions.
                        </p>
                    </div>

                    {/* Quick Install */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic">Quick Install</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[2.5rem] p-4 flex flex-col md:flex-row items-stretch md:items-center gap-4">
                             <div className="flex-1 p-6 bg-black rounded-3xl border border-white/5 font-mono text-emerald-400">
                                 pip install <span className="text-white">suprawall</span>
                             </div>
                             <div className="flex gap-4">
                                 <Link href="https://github.com/wiserautomation/SupraWall" prefetch={false} rel="noopener noreferrer" target="_blank" className="p-6 bg-white text-black rounded-3xl font-black uppercase tracking-widest text-xs hover:bg-neutral-200 transition-all flex items-center gap-2">
                                     GitHub <ArrowRight className="w-4 h-4" />
                                 </Link>
                                 <Link href="https://docs.suprawall.com" className="p-6 bg-white/5 border border-white/10 text-white rounded-3xl font-black uppercase tracking-widest text-xs hover:bg-white/10 transition-all flex items-center gap-2">
                                     Documentation
                                 </Link>
                             </div>
                         </div>
                    </div>

                    {/* Code Snippet */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic text-right">Implementation</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[3rem] p-12 border border-white/5 font-mono text-sm shadow-2xl overflow-hidden relative group">
                             <pre className="text-emerald-400 leading-relaxed">{`from crewai import Agent, Crew, Task
from suprawall.crewai import SupraWallProtector

# Initialize the protector
sw = SupraWallProtector(api_key="sw_live_...")

# Configure your agents normally
researcher = Agent(...)
analyst = Agent(...)

# Wrap the Crew to intercept all tool calls across all agents
crew = Crew(
    agents=[researcher, analyst],
    tasks=[task1, task2],
    step_callback=sw.step_callback  # Intercept each thought/action
)

# Deterministic security for the entire swarm
crew.kickoff()`}</pre>
                             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-emerald-500/5 blur-[120px] rounded-full group-hover:bg-emerald-500/10 transition-all duration-1000 -z-10" />
                         </div>
                    </div>

                    {/* Features Carousel/Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-20">
                         {[
                             { title: "Recursive Guard", desc: "Prevent agents from getting stuck in infinite tool-call loops that drain budget.", icon: Zap },
                             { title: "Tool Permissions", desc: "Restrict specific tools like 'Terminal' or 'FileWrite' to specific agents in the crew.", icon: Shield },
                             { title: "Swarm Audit", desc: "Unified audit trail for all agents within a crew, showing the complete chain of thought.", icon: FileText }
                         ].map((f, i) => (
                             <div key={i} className="p-10 rounded-[3rem] bg-neutral-900 border border-white/5 space-y-4 hover:border-emerald-500/20 transition-all">
                                 <f.icon className="w-8 h-8 text-emerald-500" />
                                 <h4 className="text-white font-black uppercase tracking-tight text-lg italic">{f.title}</h4>
                                 <p className="text-neutral-500 font-medium leading-relaxed">{f.desc}</p>
                             </div>
                         ))}
                    </div>

                    {/* CTA */}
                    <div className="mt-20 p-20 rounded-[4rem] bg-emerald-600 text-center space-y-10 group">
                         <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic text-white leading-[0.85] group-hover:scale-105 transition-transform duration-700">
                             Secure Your <br />Swarm Today.
                         </h2>
                         <Link href="/beta" className="inline-flex px-12 py-5 bg-white text-black font-black uppercase tracking-widest rounded-2xl hover:bg-neutral-100 transition-all shadow-2xl">
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

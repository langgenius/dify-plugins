// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Navbar } from "@/components/Navbar";
import { ArrowRight, Code2, Shield, Zap, Terminal, CheckCircle2, FileText, Globe, Server } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "SupraWall MCP Server | Claude Desktop Security | Official Integration",
    description: "Official Model Context Protocol (MCP) server for SupraWall. Add Article 14 human oversight and Article 12 audit trails to Claude Desktop and Anthropic agents.",
    keywords: ["mcp server security", "model context protocol security", "claude desktop guardrails", "anthropic mcp security", "suprawall mcp server"],
    alternates: {
        canonical: 'https://www.supra-wall.com/integrations/mcp',
    },
};

export default function MCPIntegrationPage() {
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "SupraWall MCP Server",
        "applicationCategory": "SecurityApplication",
        "url": "https://www.supra-wall.com/integrations/mcp",
        "author": { "@type": "Organization", "name": "SupraWall" },
        "description": "Compliance middleware for Model Context Protocol (MCP) agents."
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
                            Infrastructure • MCP Official
                        </div>
                        <h1 className="text-6xl md:text-9xl font-black tracking-tighter leading-[0.8] uppercase italic">
                            Security for <br />
                            <span className="text-emerald-500 group-hover:text-emerald-400 transition-colors italic">MCP</span> <br />
                            Swarms
                        </h1>
                        <p className="text-2xl text-neutral-400 max-w-3xl mx-auto font-medium leading-[1.3] italic">
                            The official Model Context Protocol server for real-time agent governance and EU AI Act compliance.
                        </p>
                    </div>

                    {/* Quick Install */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight italic">Quick Install</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[2.5rem] p-4 flex flex-col md:flex-row items-stretch md:items-center gap-4">
                             <div className="flex-1 p-6 bg-black rounded-3xl border border-white/5 font-mono text-emerald-400 text-sm">
                                 npm install <span className="text-white">suprawall-mcp</span>
                             </div>
                             <div className="flex gap-4">
                                 <Link href="https://github.com/wiserautomation/SupraWall" prefetch={false} rel="noopener noreferrer" target="_blank" className="p-6 bg-white text-black rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-neutral-200 transition-all flex items-center gap-2">
                                     GitHub <ArrowRight className="w-4 h-4" />
                                 </Link>
                                 <Link href="https://www.supra-wall.com/docs" className="p-6 bg-white/5 border border-white/10 text-white rounded-3xl font-black uppercase tracking-widest text-[10px] hover:bg-white/10 transition-all italic">
                                     Documentation
                                 </Link>
                             </div>
                         </div>
                    </div>

                    {/* Claude Desktop Config */}
                    <div className="max-w-4xl mx-auto space-y-8">
                         <div className="flex items-center gap-4 border-l-4 border-emerald-500 pl-6 h-12">
                             <h2 className="text-3xl font-black uppercase italic tracking-tight italic text-right">Claude Desktop Config</h2>
                         </div>
                         <div className="bg-neutral-900 rounded-[3rem] p-12 border border-white/5 font-mono text-sm leading-relaxed overflow-hidden relative group">
                             <p className="text-neutral-500 mb-4">// ~/Library/Application Support/Claude/claude_desktop_config.json</p>
                             <pre className="text-emerald-400">{`{
  "mcpServers": {
    "suprawall": {
      "command": "npx",
      "args": ["-y", "suprawall-mcp"],
      "env": {
        "SUPRAWALL_API_KEY": "ag_live_..."
      }
    }
  }
}`}</pre>
                             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-emerald-500/5 blur-[120px] rounded-full group-hover:bg-emerald-500/10 transition-all duration-1000 -z-10" />
                         </div>
                    </div>

                    {/* Available Tools */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10 py-20 border-t border-white/5">
                         {[
                             { title: "check_policy", desc: "Instantly check whether an intent or tool call is permitted under current governance rules." },
                             { title: "request_approval", desc: "Routes high-stakes actions to human reviewers with a full context of the agent's thought process." },
                             { title: "log_compliance", desc: "Directly log manual agent steps to the cryptographically signed audit trail (Article 12)." },
                             { title: "get_governance_rules", desc: "Allows the agent to self-correct based on known organizational constraints." }
                         ].map((item, i) => (
                             <div key={i} className="p-10 rounded-[3rem] bg-neutral-900 border border-white/5 space-y-4 hover:border-emerald-500/30 transition-all">
                                  <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                                       <Terminal className="w-6 h-6 text-emerald-500" />
                                  </div>
                                  <h4 className="text-xl font-black uppercase italic tracking-tight text-white leading-none">{item.title}</h4>
                                  <p className="text-neutral-500 font-medium leading-[1.6] text-lg">{item.desc}</p>
                             </div>
                         ))}
                    </div>

                    {/* CTA */}
                    <div className="p-24 rounded-[4rem] bg-emerald-600 text-center space-y-12 shadow-2xl relative overflow-hidden group">
                         <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic text-white leading-[0.85] group-hover:scale-105 transition-transform duration-700">
                              Secure Your <br />MCP Agents.
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
                    Official MCP Infrastructure • 2026
                 </p>
            </footer>
        </div>
    );
}

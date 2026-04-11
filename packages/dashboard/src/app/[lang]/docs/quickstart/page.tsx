// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { CodeBlock } from "@/components/CodeBlock";
import { Zap, Key, Terminal, Shield, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function QuickstartDocs() {
    return (
        <div className="space-y-10 animate-in fade-in zoom-in-95 duration-500 pb-20">
            <div className="space-y-4">
                <div className="inline-flex p-3 bg-emerald-500/10 rounded-full mb-2">
                    <Zap className="w-8 h-8 text-emerald-400" />
                </div>
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white drop-shadow-sm">
                    5-Minute Quickstart
                </h1>
                <p className="text-xl text-neutral-400 max-w-2xl leading-relaxed">
                    Secure your AI agent with one install command and fewer than 5 lines of code.
                </p>
            </div>

            <div className="space-y-12">
                {/* Step 1 */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">1</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Get your API key</h2>
                    </div>
                    <p className="text-neutral-400">
                        Create an account in the SupraWall Dashboard and copy your API key. Keys are prefixed with <code className="text-emerald-400 bg-emerald-400/10 px-1.5 py-0.5 rounded">ag_live_...</code>.
                    </p>
                    <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-400 hover:text-emerald-300 transition-colors">
                        Go to Dashboard <ArrowRight className="w-4 h-4" />
                    </Link>
                </section>

                {/* Step 2 */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">2</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Install the SDK</h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <p className="text-xs font-bold text-neutral-500 uppercase tracking-widest">TypeScript / Node.js</p>
                            <CodeBlock code="npm install suprawall" language="bash" />
                        </div>
                        <div className="space-y-2">
                            <p className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Python</p>
                            <CodeBlock code="pip install suprawall" language="bash" />
                        </div>
                    </div>
                </section>

                {/* Step 3 */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">3</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Wrap your Agent</h2>
                    </div>
                    <p className="text-neutral-400">
                        SupraWall intercepts and policy-checks every tool call. Wrap your existing agent runtime in just one line.
                    </p>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <p className="text-xs font-bold text-neutral-500 uppercase tracking-widest">TypeScript (SDK)</p>
                            <CodeBlock 
                                language="typescript" 
                                code={`import { protect } from "suprawall";

const agent = createMyAgent();
const secured = protect(agent, {
  apiKey: "ag_your_key_here",
});

await secured.invoke({ ... });`} 
                            />
                        </div>
                        <div className="space-y-2">
                            <p className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Python (Decorator)</p>
                            <CodeBlock 
                                language="python" 
                                code={`from suprawall import secure

@secure(api_key="ag_your_key_here")
def my_agent_action():
    # Your agent logic here
    pass`} 
                            />
                        </div>
                    </div>
                </section>

                {/* Step 4 */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">4</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Configure Policies</h2>
                    </div>
                    <p className="text-neutral-400">
                        Head back to the dashboard to define which tools are safe, which need approval, and which are hard-blocked.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {[
                            { title: "ALLOW", text: "Safe tools (search, read)", color: "text-emerald-400" },
                            { title: "DENY", text: "Blocked tools (delete, drop)", color: "text-rose-400" },
                            { title: "APPROVE", text: "Sensitive tools (pay, send)", color: "text-amber-400" },
                        ].map((p) => (
                            <div key={p.title} className="p-4 rounded-xl bg-neutral-900 border border-white/5">
                                <h4 className={`font-bold mb-1 ${p.color}`}>{p.title}</h4>
                                <p className="text-xs text-neutral-500">{p.text}</p>
                            </div>
                        ))}
                    </div>
                {/* Step 5 */}
                <section className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold border border-emerald-500/30">5</div>
                        <h2 className="text-2xl font-bold text-white tracking-wide">Automate with GitHub Actions</h2>
                    </div>
                    <p className="text-neutral-400">
                        Enable continuous security auditing by adding the SupraWall Scan action to your repository. Detect risks before they reach production.
                    </p>
                    <Link href={`/docs/integrations/github-action`} className="inline-flex items-center gap-2 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors">
                        Setup GitHub Action <ArrowRight className="w-4 h-4" />
                    </Link>
                </section>
            </div>

            <div className="flex justify-between items-center pt-8 border-t border-white/10">
                <Link href="/docs" className="text-neutral-400 hover:text-white transition-colors text-sm">← Introduction</Link>
                <Link href="/docs/mcp" className="text-emerald-400 hover:text-emerald-300 font-semibold transition-colors flex items-center">Claude (MCP) →</Link>
            </div>
        </div>
    );
}

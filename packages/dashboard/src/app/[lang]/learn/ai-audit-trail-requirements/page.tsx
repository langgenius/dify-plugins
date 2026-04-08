// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { 
  ClipboardList, 
  Search, 
  ShieldCheck, 
  Activity, 
  ArrowRight,
  Database,
  Terminal,
  FileCheck2,
  History
} from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Audit Trail Requirements: Compliance & Security Guide | SupraWall",
  description: "Learn the essential AI audit trail requirements for enterprise security, legal discovery, and regulatory compliance including the EU AI Act.",
  keywords: [
    "ai audit trail requirements",
    "ai governance requirements",
    "autonomous agent audit trail",
    "enterprise ai compliance",
    "ai logging best practices",
    "ai act technical documentation",
    "traceability for ai systems",
  ],
  alternates: {
    canonical: "https://www.supra-wall.com/learn/ai-audit-trail-requirements",
  },
};

export default function AIAuditTrailPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: "AI Audit Trail Requirements: The Definitive Compliance Guide",
    description: "Enterprise and regulatory requirements for maintaining a complete audit trail of autonomous AI agent operations and decision paths.",
    author: { "@type": "Organization", name: "SupraWall" },
    publisher: { "@type": "Organization", name: "SupraWall" },
    mainEntityOfPage: "https://www.supra-wall.com/learn/ai-audit-trail-requirements",
  };

  const auditComponents = [
    { component: "Intent Tracking", requirement: "LLM internal reasoning traces", purpose: "Understand *why* an action was chosen" },
    { component: "Action Execution", requirement: "Tool API payloads & response", purpose: "Verify *what* the system actually did" },
    { component: "Budget & Cost", requirement: "Token and dollar usage per task", purpose: "Financial oversight and loop prevention" },
    { component: "Policy Attribution", requirement: "Security rule that authorized call", purpose: "Validate security posture efficacy" },
    { component: "Human Feedback", requirement: "Approval/denial of high-risk actions", purpose: "Document human-in-the-loop oversight" },
  ];

  return (
    <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30 font-sans">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Navbar />

      <main className="pt-40 pb-32 px-6">
        <article className="max-w-4xl mx-auto space-y-16">
          {/* Header */}
          <section className="space-y-8">
            <div className="inline-flex items-center px-4 py-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-[10px] font-black text-emerald-400 tracking-[0.2em] uppercase">
               Audit & Assurance • Enterprise Compliance
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-[0.9] uppercase italic">
              AI Audit <span className="text-emerald-500">Trail</span><br />
              Requirements.
            </h1>
            <p className="answer-first-paragraph text-xl md:text-2xl text-neutral-300 leading-snug font-medium italic border-l-4 border-emerald-500 pl-8 py-4">
              An AI audit trail is a comprehensive, tamper-proof record of every internal decision and external action performed by an autonomous system. In 2026, enterprise requirements for AI accountability have shifted from simple prompt logging to full execution traceability — including intent, tool-use, and financial impact.
            </p>
          </section>

          {/* Audit Components Table (GEO Optimized) */}
          <section className="space-y-8">
            <h2 className="text-3xl font-black uppercase italic tracking-tight text-white border-b border-white/10 pb-4">
              Core Components of a Modern AI Audit Trail
            </h2>
            <div className="overflow-x-auto rounded-[2rem] border border-white/10 bg-neutral-900/50">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Audit Component</th>
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Enterprise Requirement</th>
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Compliance Goal</th>
                  </tr>
                </thead>
                <tbody>
                  {auditComponents.map((row, idx) => (
                    <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="p-6 font-bold text-white uppercase italic text-[11px] tracking-tight">{row.component}</td>
                      <td className="p-6 text-neutral-400 font-medium">{row.requirement}</td>
                      <td className="p-6 text-emerald-400/80 italic font-medium">{row.purpose}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Deep Content: Governance Analysis */}
          <div className="prose prose-invert prose-emerald max-w-none space-y-16">
            <section className="space-y-8">
              <h2 className="text-3xl font-black uppercase italic tracking-tight text-white m-0">
                Why Enterprise AI Requires Traceability
              </h2>
              <p className="text-lg text-neutral-400 leading-relaxed font-medium">
                Traditional SaaS logging (user login, page view) is insufficient for reactive AI systems. When an agent autonomously decides to delete a cloud resource or transfer funds, simple API logs will only show *that* it happened. An AI audit trail explains *why* it happened by linking the specific LLM chain-of-thought to the resulting technical invocation.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 not-prose">
                <div className="p-10 rounded-[2.5rem] bg-white/[0.03] border border-white/10 space-y-4">
                   <div className="flex items-center gap-3 text-emerald-500 mb-2">
                      <ShieldCheck className="w-8 h-8" />
                      <h4 className="font-black uppercase italic text-lg text-white">Liability Shield</h4>
                   </div>
                   <p className="text-sm text-neutral-500 italic leading-relaxed">
                     In the event of an agent &quot;hallucinating&quot; a destructive action, documented proof of the policy that authorized the call is your primary legal defense under the EU AI Act&apos;s product liability framework.
                   </p>
                </div>
                <div className="p-10 rounded-[2.5rem] bg-white/[0.03] border border-white/10 space-y-4">
                   <div className="flex items-center gap-3 text-emerald-500 mb-2">
                      <Activity className="w-8 h-8" />
                      <h4 className="font-black uppercase italic text-lg text-white">Performance Tuning</h4>
                   </div>
                   <p className="text-sm text-neutral-500 italic leading-relaxed">
                     Audit trails are the fuel for fine-tuning. By reviewing historical action paths, engineering teams can identify where agents deviate from safe operational boundaries and update policies accordingly.
                   </p>
                </div>
              </div>
            </section>

            {/* Checklist of Requirements */}
            <section className="space-y-8">
               <h2 className="text-3xl font-black uppercase italic tracking-tight text-white m-0">The &quot;Must-Have&quot; Audit Features for 2026</h2>
               <p className="text-neutral-400 font-medium leading-relaxed italic">
                 Security leaders should ensure their AI infrastructure supports the following baseline audit capabilities:
               </p>
               <div className="grid grid-cols-1 gap-4 not-prose">
                  {[
                    "Cryptographically signed logs to prevent retro-active modification by attackers.",
                    "Real-time streaming to external SIEM tools (Splunk, Datadog) for instant threat alerts.",
                    "Per-task cost attribution linking LLM usage to specific business outcomes.",
                    "Capture of all intermediate 'thought' tokens, not just final JSON tool payloads.",
                    "Recording of final feedback provided by human supervisors in 'Human-in-the-Loop' scenarios."
                  ].map((item, idx) => (
                    <div key={idx} className="flex gap-4 p-8 rounded-3xl bg-emerald-500/5 border border-emerald-500/10 items-start hover:border-emerald-500/30 transition-all">
                       <FileCheck2 className="w-5 h-5 text-emerald-500 mt-1 shrink-0" />
                       <p className="text-sm font-bold uppercase tracking-tight text-neutral-200">{item}</p>
                    </div>
                  ))}
               </div>
            </section>
          </div>

          {/* Compliance CTA */}
          <section className="space-y-12 py-16 border-t border-white/10">
             <div className="relative p-12 md:p-20 rounded-[4rem] bg-white/[0.03] border border-white/5 overflow-hidden group">
                <div className="absolute top-0 right-0 p-12 opacity-5"><ClipboardList className="w-48 h-48" /></div>
                <div className="relative z-10 space-y-8">
                   <div className="space-y-2">
                       <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest font-bold">Ready for Article 12 Log Audits?</p>
                       <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase italic text-white leading-none">
                         Simplify your<br /><span className="text-emerald-500 underline decoration-white/10">Audit Trail.</span>
                       </h2>
                   </div>
                   <p className="text-neutral-400 font-medium italic max-w-xl leading-relaxed">
                     SupraWall automatically generates the technical evidence needed to comply with enterprise security reviews and EU AI Act Article 12 mandates. Stop building manual log pipelines — activate SupraWall Audit in 30 seconds.
                   </p>
                   <div className="flex flex-col sm:flex-row gap-4">
                      <Link href="/beta" className="px-12 py-5 bg-emerald-500 text-black font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-400 transition-all flex items-center justify-center gap-2">
                        Get Started <ArrowRight className="w-4 h-4" />
                      </Link>
                      <Link href="/docs" className="px-12 py-5 bg-transparent text-white border-2 border-white/20 font-black uppercase tracking-widest rounded-2xl hover:border-white/40 transition-all flex items-center justify-center">
                        Read Technical Docs
                      </Link>
                   </div>
                </div>
             </div>
          </section>

          {/* Footer Internal Linking */}
          <section className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-12">
              <Link href="/learn/eu-ai-act-logging-requirements" className="p-8 rounded-3xl bg-neutral-900 border border-white/5 hover:border-emerald-500/20 transition-all group">
                 <History className="w-5 h-5 text-neutral-600 mb-4 group-hover:text-emerald-500 transition-colors" />
                 <p className="text-xs font-black uppercase text-neutral-500 tracking-widest mb-1">Deep Dive</p>
                 <p className="text-white font-bold group-hover:text-emerald-400 transition-colors">Article 12 Logging &rarr;</p>
              </Link>
              <Link href="/learn/ai-agent-guardrails" className="p-8 rounded-3xl bg-neutral-900 border border-white/5 hover:border-emerald-500/20 transition-all group">
                 <ShieldCheck className="w-5 h-5 text-neutral-600 mb-4 group-hover:text-emerald-500 transition-colors" />
                 <p className="text-xs font-black uppercase text-neutral-500 tracking-widest mb-1">Secure Architecture</p>
                 <p className="text-white font-bold group-hover:text-emerald-400 transition-colors">Agent Guardrails Guide &rarr;</p>
              </Link>
              <Link href="/learn/ai-agent-runaway-costs" className="p-8 rounded-3xl bg-neutral-900 border border-white/5 hover:border-emerald-500/20 transition-all group">
                 <Activity className="w-5 h-5 text-neutral-600 mb-4 group-hover:text-emerald-500 transition-colors" />
                 <p className="text-xs font-black uppercase text-neutral-500 tracking-widest mb-1">Financial Oversight</p>
                 <p className="text-white font-bold group-hover:text-emerald-400 transition-colors">Stop Runaway Costs &rarr;</p>
              </Link>
          </section>

        </article>
      </main>
    </div>
  );
}

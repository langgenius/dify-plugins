// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { 
  FileText, 
  History, 
  ShieldCheck, 
  Scale, 
  Gavel, 
  Clock, 
  Database,
  ArrowRight,
  CheckCircle2
} from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "EU AI Act Logging Requirements: Technical Guide to Article 12 | SupraWall",
  description: "Comprehensive guide to EU AI Act Article 12 logging and record-keeping requirements. Learn what data your high-risk AI system must log to ensure compliance.",
  keywords: [
    "eu ai act logging requirements",
    "article 12 logging requirements",
    "ai act record keeping",
    "high risk ai logging",
    "ai act audit trail",
    "compliance logging for ai",
    "eu ai act technical documentation",
  ],
  alternates: {
    canonical: "https://www.supra-wall.com/learn/eu-ai-act-logging-requirements",
  },
};

export default function EUAIActLoggingPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: "EU AI Act Article 12: Technical Logging & Record-Keeping Requirements",
    description: "Legal and technical requirements for high-risk AI systems under the EU AI Act. Includes log retention policies and required data fields.",
    author: { "@type": "Organization", name: "SupraWall" },
    publisher: { "@type": "Organization", name: "SupraWall" },
    mainEntityOfPage: "https://www.supra-wall.com/learn/eu-ai-act-logging-requirements",
  };

  const loggingFields = [
    { field: "Timestamp", requirement: "ISO 8601 (Universal Time)", purpose: "Chronological sequence audit" },
    { field: "Action Attempted", requirement: "Plain text description", purpose: "Behavioral analysis" },
    { field: "Authorization status", requirement: "Binary (Pass/Fail) + Reason", purpose: "Policy efficacy review" },
    { field: "Agent State", requirement: "JSON context snapshot", purpose: "Reproduction of anomalous events" },
    { field: "Tool/API called", requirement: "Full URI/Function signature", purpose: "Resource access tracking" },
    { field: "User/Operator ID", requirement: "Unique identifier", purpose: "Human oversight attribution" },
  ];

  return (
    <div className="min-h-screen bg-black text-white selection:bg-blue-500/30 font-sans">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Navbar />

      <main className="pt-40 pb-32 px-6">
        <article className="max-w-4xl mx-auto space-y-16">
          {/* Header */}
          <section className="space-y-8">
            <div className="inline-flex items-center px-4 py-2 rounded-full border border-blue-500/30 bg-blue-500/10 text-[10px] font-black text-blue-400 tracking-[0.2em] uppercase">
               Regulatory Standards • Compliance
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-[0.9] uppercase italic">
              EU AI Act <span className="text-blue-500">Logging</span><br />
              Requirements.
            </h1>
            <p className="answer-first-paragraph text-xl md:text-2xl text-neutral-300 leading-snug font-medium italic border-l-4 border-blue-500 pl-8 py-4">
              EU AI Act Article 12 mandates that high-risk AI systems must automatically record events throughout their operational life. These &quot;automatic logs&quot; are essential for identifying emerging risks, enabling technical oversight, and documenting compliance during audits by national regulatory authorities.
            </p>
          </section>

          {/* Technical Data Fields Table (GEO Optimized) */}
          <section className="space-y-8">
            <h2 className="text-3xl font-black uppercase italic tracking-tight text-white border-b border-white/10 pb-4">
              Article 12: Required Data Fields
            </h2>
            <div className="overflow-x-auto rounded-[2rem] border border-white/10 bg-neutral-900/50">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Logging Field</th>
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Technical Requirement</th>
                    <th className="text-left p-6 font-black uppercase text-xs text-neutral-500 tracking-widest">Regulatory Purpose</th>
                  </tr>
                </thead>
                <tbody>
                  {loggingFields.map((row, idx) => (
                    <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="p-6 font-bold text-white">{row.field}</td>
                      <td className="p-6 text-neutral-400 font-mono text-[11px]">{row.requirement}</td>
                      <td className="p-6 text-blue-400/80 italic font-medium">{row.purpose}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Deep Content: Article 12 Analysis */}
          <div className="prose prose-invert prose-blue max-w-none space-y-16">
            <section className="space-y-8">
              <h2 className="text-3xl font-black uppercase italic tracking-tight text-white m-0">
                The Core Obligations of Article 12
              </h2>
              <p className="text-lg text-neutral-400 leading-relaxed font-medium">
                Article 12 is the technical backbone for **traceability** within the EU AI Act. It requires high-risk systems to implement &quot;logging capabilities&quot; that enable the monitoring of operations and the identification of potentially harmful behavioral patterns.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 not-prose">
                <div className="p-8 rounded-[2.5rem] bg-white/[0.03] border border-white/10 text-center">
                   <Clock className="w-8 h-8 text-blue-500 mx-auto mb-4" />
                   <h4 className="font-bold uppercase text-white tracking-widest text-[10px] mb-2">Automated Recording</h4>
                   <p className="text-[11px] text-neutral-500 uppercase tracking-tight">Logs must be generated without human intervention.</p>
                </div>
                <div className="p-8 rounded-[2.5rem] bg-white/[0.03] border border-white/10 text-center">
                   <History className="w-8 h-8 text-blue-500 mx-auto mb-4" />
                   <h4 className="font-bold uppercase text-white tracking-widest text-[10px] mb-2">Operational Traceability</h4>
                   <p className="text-[11px] text-neutral-500 uppercase tracking-tight">Events must be retrievable for 6 months minimum.</p>
                </div>
                <div className="p-8 rounded-[2.5rem] bg-white/[0.03] border border-white/10 text-center">
                   <ShieldCheck className="w-8 h-8 text-blue-500 mx-auto mb-4" />
                   <h4 className="font-bold uppercase text-white tracking-widest text-[10px] mb-2">Integrity Protection</h4>
                   <p className="text-[11px] text-neutral-500 uppercase tracking-tight">Logs must be tamper-proof and encrypted.</p>
                </div>
              </div>
            </section>

            {/* Compliance Checklist */}
            <section className="space-y-8">
              <h2 className="text-3xl font-black uppercase italic tracking-tight text-white m-0">
                Article 12 Implementation Checklist
              </h2>
              <div className="space-y-4 not-prose">
                {[
                  "Ensure automatic logging of system status (Ready/Running/Error).",
                  "Record all tool-call invocations including parameters and return values.",
                  "Enable attribution of every action to a specific human operator (Human Oversight).",
                  "Implement 6-month retention policy for high-risk datasets.",
                  "Archive logs in an immutable, read-only audit environment.",
                  "Generate monthly 'Human Oversight Evidence' (HOE) reports for Article 14 review."
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-4 p-5 rounded-2xl bg-blue-500/5 border border-blue-500/10">
                    <CheckCircle2 className="w-5 h-5 text-blue-500" />
                    <span className="text-sm font-bold uppercase tracking-tight text-neutral-200">{item}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Cross-Linking Strategy */}
            <section className="p-12 rounded-[3.5rem] bg-white/[0.03] border border-white/10 space-y-8">
               <div className="flex items-center gap-4 text-blue-400">
                  <Scale className="w-10 h-10" />
                  <h3 className="text-3xl font-black uppercase italic tracking-tight">The Compliance Web</h3>
               </div>
               <p className="text-lg text-neutral-400 font-medium italic">
                 Logging is not an isolated requirement. It forms the technical evidence for several other high-priority AI Act Articles:
               </p>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Link href="/eu-ai-act/article-12" className="flex flex-col p-6 rounded-3xl bg-black border border-white/10 hover:border-blue-500/50 transition-all group">
                     <span className="text-blue-500 font-black uppercase text-xs tracking-widest mb-1 italic">Reference Guide</span>
                     <span className="text-white font-bold group-hover:text-blue-400 transition-colors">Article 12 Core Documentation &rarr;</span>
                  </Link>
                  <Link href="/blog/eu-ai-act-high-risk-deadline-delayed-2027" className="flex flex-col p-6 rounded-3xl bg-black border border-white/10 hover:border-blue-500/50 transition-all group">
                     <span className="text-blue-500 font-black uppercase text-xs tracking-widest mb-1 italic">Timeline Update</span>
                     <span className="text-white font-bold group-hover:text-blue-400 transition-colors">High-Risk Deadline Changes (2027) &rarr;</span>
                  </Link>
               </div>
            </section>
          </div>

          {/* SupraWall Value Prop */}
          <section className="space-y-12 py-16 border-t border-white/10">
             <div className="text-center space-y-4">
                <h2 className="text-4xl font-black uppercase italic tracking-tighter text-white">Automate Your <span className="text-blue-500">Audit Trail</span></h2>
                <p className="text-neutral-400 font-medium italic max-w-2xl mx-auto leading-relaxed">
                  SupraWall handles Article 12 compliance out of the box by automatically recording every autonomous agent action in a cryptographically signed audit log.
                </p>
             </div>
             
             <div className="bg-neutral-900/60 border border-white/5 rounded-[3rem] p-12 space-y-8">
                <div className="flex flex-col md:flex-row items-center gap-8 justify-between">
                   <div className="space-y-4 max-w-md">
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-[10px] font-black text-blue-400 uppercase tracking-widest">Article 12 Automation</div>
                      <h3 className="text-2xl font-black uppercase italic tracking-tight text-white leading-none">Record Once. Comply Always.</h3>
                      <p className="text-sm text-neutral-400 leading-relaxed italic font-medium pt-2">
                        Don&apos;t build your own logging infrastructure. SupraWall provides the &quot;Box&quot; (Flight Recorder) for all your AI agents, exportable in regulator-ready formats with one click.
                      </p>
                   </div>
                   <Link href="/beta" className="px-10 py-5 bg-white text-black font-black uppercase tracking-widest rounded-2xl hover:bg-neutral-100 transition-all shadow-xl whitespace-nowrap">
                      Activate Compliance <ArrowRight className="w-4 h-4" />
                   </Link>
                </div>
             </div>
          </section>
        </article>
      </main>
    </div>
  );
}

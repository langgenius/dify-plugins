// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Shield, CheckCircle2, AlertTriangle, XCircle, Download,
    FileText, Settings, ExternalLink, RefreshCw, Award, Linkedin, Copy, Check, Code2, Globe, Lock
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import Image from "next/image";
import { RiskRegister } from "@/components/RiskRegister";

const API_URL = process.env.NEXT_PUBLIC_SUPRAWALL_API_URL || "http://localhost:3000";

type CheckStatus = "pass" | "partial" | "fail";

interface ComplianceCheck {
    status: CheckStatus;
    detail: string;
}

interface ComplianceStatus {
    overall: "COMPLIANT" | "ATTENTION_NEEDED" | "NOT_CONFIGURED";
    checks: {
        humanOversight: ComplianceCheck;
        auditLogging: ComplianceCheck;
        riskControls: ComplianceCheck;
        recordKeeping: ComplianceCheck;
        dataGovernance: ComplianceCheck;
        incidentLogging: ComplianceCheck;
    };
    lastChecked: string;
}

const CHECKLIST_META = [
    {
        key: "humanOversight" as const,
        article: "Article 14",
        name: "Human Oversight",
        description: "REQUIRE_APPROVAL policies enforce human review before sensitive tool executions.",
        link: "/dashboard/policies",
        linkLabel: "Configure Policies",
    },
    {
        key: "auditLogging" as const,
        article: "Article 12",
        name: "Audit Logging",
        description: "All AI agent tool calls are recorded with timestamps, agent identity, tool name, and decision.",
        link: "/dashboard/audit",
        linkLabel: "View Audit Logs",
    },
    {
        key: "riskControls" as const,
        article: "Article 9",
        name: "Risk Management Controls",
        description: "DENY policies block dangerous or unauthorized tool calls before execution.",
        link: "/dashboard/policies",
        linkLabel: "Configure Policies",
    },
    {
        key: "recordKeeping" as const,
        article: "Article 11",
        name: "Record Keeping",
        description: "Audit logs are retained with sufficient history for regulatory review.",
        link: "/dashboard/audit",
        linkLabel: "View Audit Logs",
    },
    {
        key: "dataGovernance" as const,
        article: "Article 10",
        name: "Data Governance",
        description: "Tool call arguments are logged with full fidelity. Self-hosting ensures data residency compliance.",
        link: "/dashboard/settings",
        linkLabel: "Settings",
    },
    {
        key: "incidentLogging" as const,
        article: "Article 73",
        name: "Incident Logging",
        description: "DENY decisions are logged. Dedicated incident workflow coming soon.",
        link: "/dashboard/audit",
        linkLabel: "View Audit Logs",
    },
];

function StatusBadge({ status }: { status: CheckStatus }) {
    if (status === "pass") {
        return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" /> Active
            </span>
        );
    }
    if (status === "partial") {
        return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <AlertTriangle className="w-3.5 h-3.5" /> Partial
            </span>
        );
    }
    return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle className="w-3.5 h-3.5" /> Not Configured
        </span>
    );
}

function OverallBadge({ overall }: { overall: ComplianceStatus["overall"] }) {
    if (overall === "COMPLIANT") {
        return (
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="w-4 h-4" /> COMPLIANT
            </span>
        );
    }
    if (overall === "ATTENTION_NEEDED") {
        return (
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <AlertTriangle className="w-4 h-4" /> ATTENTION NEEDED
            </span>
        );
    }
    return (
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold bg-red-500/10 text-red-400 border border-red-500/30">
            <XCircle className="w-4 h-4" /> NOT CONFIGURED
        </span>
    );
}

interface CertificateData {
    certId: string;
    orgName: string;
    issueDate: string;
    complianceScore: number;
    articlesCompliant: string[];
    certificateUrl: string;
    verificationUrl: string;
    userId: string;
}

export default function CompliancePage() {
    const [user] = useAuthState(auth);
    const [status, setStatus] = useState<ComplianceStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [certLoading, setCertLoading] = useState(false);
    const [certificate, setCertificate] = useState<CertificateData | null>(null);
    const [copied, setCopied] = useState(false);
    const [certError, setCertError] = useState<string | null>(null);
    const [badgeTab, setBadgeTab] = useState<"image" | "html">("image");
    const [badgeTheme, setBadgeTheme] = useState<"dark" | "light">("dark");
    const [badgeCopied, setBadgeCopied] = useState(false);

    const fetchStatus = async () => {
        if (!user) return;
        setLoading(true);
        setError(null);
        try {
            const idToken = await user.getIdToken();
            const headers = { 'Authorization': `Bearer ${idToken}` };
            const res = await fetch(`/api/v1/compliance/status?tenantId=${user.uid}`, { headers });
            if (!res.ok) throw new Error(`Server returned ${res.status}`);
            const data = await res.json();
            setStatus(data);
        } catch (e) {
            setError(
                e instanceof Error
                    ? e.message
                    : "Failed to fetch compliance status. Ensure NEXT_PUBLIC_SUPRAWALL_API_URL is set and the suprawall server is running."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchStatus();
    }, [user]);

    const generateCertificate = async () => {
        if (!user) return;
        setCertLoading(true);
        setCertError(null);
        try {
            const idToken = await user.getIdToken();
            const res = await fetch("/api/compliance/certificate", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${idToken}`
                },
                body: JSON.stringify({ tenantId: user.uid })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data?.error || "Failed to generate certificate");
            setCertificate(data.certificate);
        } catch (e) {
            console.error(e);
            setCertError(e instanceof Error ? e.message : "Certificate generation failed. Please try again.");
        } finally {
            setCertLoading(false);
        }
    };

    const copyVerificationUrl = async () => {
        if (!certificate) return;
        await navigator.clipboard.writeText(certificate.verificationUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const getBadgeSnippets = (cert: CertificateData) => {
        const certUrl = cert.certificateUrl;
        const themeQuery = badgeTheme === "light" ? "?theme=light" : "";
        const badgeSrc = `https://www.supra-wall.com/api/badge/cert/${cert.certId}${themeQuery}`;
        const articles = cert.articlesCompliant?.map(a => a.replace("Article ", "Art. ")).join(" · ") ?? "Art. 9 · Art. 12 · Art. 14";

        const imageSnippet =
`<!-- Supra-wall EU AI Act Compliance Badge -->
<a href="${certUrl}" target="_blank" rel="noopener noreferrer">
  <img src="${badgeSrc}" alt="EU AI Act Compliant – ${articles}" height="64" />
</a>`;

        const htmlBg = badgeTheme === "dark" ? "#09090b" : "#ffffff";
        const htmlBorder = badgeTheme === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";
        const htmlText = badgeTheme === "dark" ? "#ffffff" : "#09090b";
        const htmlTextSec = badgeTheme === "dark" ? "#71717a" : "#52525b";

        const htmlSnippet =
`<!-- Supra-wall EU AI Act Compliance Badge -->
<a href="${certUrl}" target="_blank" rel="noopener noreferrer"
   style="display:inline-flex;align-items:center;padding:12px 16px;min-width:280px;box-sizing:border-box;
          background:${htmlBg};border:1.5px solid ${htmlBorder};border-radius:16px;
          text-decoration:none;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;color:${htmlText};">
  <div style="width:4px;height:32px;background:#10b981;border-radius:2px;margin-right:16px;"></div>
  <svg width="28" height="32" viewBox="0 0 28 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right:12px;">
    <path d="M14 0L0 5v8c0 7.5 6 12.5 14 14 8-1.5 14-6.5 14-14V5z" fill="#10b981" fill-opacity="0.1"/>
    <path d="M14 0L0 5v8c0 7.5 6 12.5 14 14 8-1.5 14-6.5 14-14V5z"
          stroke="#10b981" stroke-width="2" stroke-linejoin="round"/>
    <path d="M9 13l3 3 6-7" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span style="display:flex;flex-direction:column;gap:2px;flex:1;">
    <span style="font-size:9px;font-weight:800;letter-spacing:0.1em;color:#10b981;text-transform:uppercase;">EU AI ACT SECURED</span>
    <span style="font-size:13px;font-weight:700;">${cert.orgName || 'SupraWall Certified'}</span>
    <span style="font-size:8px;font-weight:500;color:${htmlTextSec};">Art. ${articles}</span>
  </span>
  <div style="margin-left:12px;display:flex;align-items:center;justify-content:center;width:36px;height:36px;
              border:1.5px solid #10b981;border-radius:50%;font-size:11px;font-weight:900;">
    ${cert.complianceScore}
  </div>
</a>`;

        return { imageSnippet, htmlSnippet };
    };

    const copyBadgeSnippet = async () => {
        if (!certificate) return;
        const { imageSnippet, htmlSnippet } = getBadgeSnippets(certificate);
        await navigator.clipboard.writeText(badgeTab === "image" ? imageSnippet : htmlSnippet);
        setBadgeCopied(true);
        setTimeout(() => setBadgeCopied(false), 2000);
    };

    const downloadReport = () => {
        if (!user) return;
        const from = new Date(Date.now() - 30 * 86_400_000).toISOString().split("T")[0];
        const to = new Date().toISOString().split("T")[0];
        const params = new URLSearchParams({ tenantId: user.uid, from, to });
        window.open(`/api/v1/compliance/report?${params}`, "_blank");
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
        >
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                            <Shield className="w-6 h-6 text-emerald-400" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">
                                EU AI Act Compliance
                            </h1>
                            <p className="text-[11px] font-black text-neutral-400 uppercase tracking-[0.2em] mt-1">
                                Real-time compliance readiness across EU AI Act requirements.
                            </p>
                        </div>
                    </div>
                </div>
                <button
                    onClick={fetchStatus}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2.5 bg-black/60 hover:bg-white/[0.05] border border-emerald-500/20 hover:border-emerald-500/40 rounded-xl text-[10px] font-black uppercase tracking-wider text-neutral-400 hover:text-white transition-all disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                </button>
            </div>

            {/* Overall Status Card */}
            <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/10 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent" />
                <CardContent className="p-6">
                    {loading ? (
                        <div className="flex items-center gap-3 text-neutral-400 animate-pulse">
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span className="text-sm">Checking compliance status...</span>
                        </div>
                    ) : error ? (
                        <div className="flex items-start gap-3">
                            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-medium text-amber-400">Could not reach suprawall server</p>
                                <p className="text-xs text-neutral-400 mt-1">{error}</p>
                                <p className="text-xs text-neutral-600 mt-1">
                                    Set <code className="text-emerald-400/80">NEXT_PUBLIC_SUPRAWALL_API_URL</code> in your <code className="text-emerald-400/80">.env.local</code>
                                </p>
                            </div>
                        </div>
                    ) : status ? (
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                            <div className="space-y-1">
                                <p className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-400">Overall Status</p>
                                <OverallBadge overall={status.overall} />
                            </div>
                            <p className="text-xs text-neutral-600">
                                Last checked: {new Date(status.lastChecked).toLocaleString()}
                            </p>
                        </div>
                    ) : null}
                </CardContent>
            </Card>

            {/* Checklist */}
            {status && (
                <div>
                    <h2 className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.25em] mb-4">
                        Requirement Checklist
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {CHECKLIST_META.map((item, i) => {
                            const check = status.checks[item.key];
                            return (
                                <motion.div
                                    key={item.key}
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.06 }}
                                >
                                    <Card className="bg-black/60 backdrop-blur-xl border-white/10 hover:border-emerald-500/20 transition-all duration-300 h-full relative overflow-hidden group">
                                        <CardContent className="p-5 flex flex-col gap-3">
                                            <div className="flex items-start justify-between gap-2">
                                                <div>
                                                    <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-500/60">
                                                        {item.article}
                                                    </span>
                                                    <h3 className="text-sm font-black text-white uppercase italic tracking-tight mt-0.5">
                                                        {item.name}
                                                    </h3>
                                                </div>
                                                <StatusBadge status={check.status} />
                                            </div>
                                            <p className="text-xs text-neutral-400 leading-relaxed">
                                                {item.description}
                                            </p>
                                            <p className="text-xs text-neutral-400 italic">{check.detail}</p>
                                            <Link
                                                href={item.link}
                                                className="inline-flex items-center gap-1 text-xs text-emerald-400/70 hover:text-emerald-400 transition-colors mt-auto"
                                            >
                                                {item.linkLabel}
                                                <ExternalLink className="w-3 h-3" />
                                            </Link>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Risk Register */}
            {status && (
                <div>
                   <RiskRegister />
                </div>
            )}

            {/* Compliance Certificate */}
            <div>

                <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-4">
                    Compliance Certificate
                </h2>
                <Card className="bg-black/60 backdrop-blur-xl border-emerald-500/10 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    <CardContent className="p-6">
                        {!certificate ? (
                            <div className="flex flex-col gap-4">
                                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                    <div>
                                        <h3 className="text-sm font-black text-white uppercase italic tracking-tight mb-1">Generate EU AI Act Certificate</h3>
                                        <p className="text-xs text-neutral-400">
                                            Create a shareable compliance certificate. Share on LinkedIn to drive brand awareness.
                                        </p>
                                    </div>
                                    <button
                                        onClick={generateCertificate}
                                        disabled={certLoading}
                                        className="shrink-0 flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60 text-white rounded-xl text-sm font-semibold transition-colors"
                                    >
                                        <Award className="w-4 h-4" />
                                        {certLoading ? "Generating…" : "Generate Certificate"}
                                    </button>
                                </div>
                                {certError && (
                                    <div className="flex items-start gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                                        <XCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                                        <p className="text-xs text-red-400">{certError}</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                                        <Award className="w-5 h-5 text-emerald-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-white">Certificate Generated</p>
                                        <p className="text-xs text-neutral-400">ID: {certificate.certId} · Score: {certificate.complianceScore}/100</p>
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <a
                                        href={certificate.certificateUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-2 px-4 py-2 bg-white/[0.06] hover:bg-white/[0.1] border border-white/[0.08] rounded-lg text-xs font-medium text-white transition-colors"
                                    >
                                        <Download className="w-3.5 h-3.5" />
                                        View &amp; Print Certificate
                                    </a>
                                    <a
                                        href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(certificate.verificationUrl)}&text=${encodeURIComponent(`Our AI agents are now EU AI Act compliant ✅\n\nArticle 14 human oversight, Article 12 audit logging, and Article 9 risk management — all verified by Supra-wall.\n\nWith August 2026 enforcement approaching, compliance isn't optional.\n\n#EUAIAct #AICompliance #AIAgentSecurity`)}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-2 px-4 py-2 bg-[#0a66c2]/20 hover:bg-[#0a66c2]/30 border border-[#0a66c2]/30 rounded-lg text-xs font-medium text-[#70a9e8] transition-colors"
                                    >
                                        <Linkedin className="w-3.5 h-3.5" />
                                        Share on LinkedIn
                                    </a>
                                    <button
                                        onClick={copyVerificationUrl}
                                        className="flex items-center gap-2 px-4 py-2 bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.06] rounded-lg text-xs font-medium text-neutral-300 transition-colors"
                                    >
                                        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                                        {copied ? "Copied!" : "Copy Verification URL"}
                                    </button>
                                    <button
                                        onClick={() => setCertificate(null)}
                                        className="flex items-center gap-2 px-4 py-2 bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.06] rounded-lg text-xs font-medium text-neutral-400 transition-colors"
                                    >
                                        <RefreshCw className="w-3.5 h-3.5" />
                                        Regenerate
                                    </button>
                                </div>

                                {/* Badge Embed Section */}
                                <div className="mt-4 pt-4 border-t border-white/[0.06]">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Globe className="w-3.5 h-3.5 text-emerald-400" />
                                        <p className="text-xs font-black uppercase tracking-widest text-emerald-400">Embed on Your Website</p>
                                    </div>

                                    <div className="mb-4 flex flex-col sm:flex-row items-start sm:items-center gap-6">
                                        <div className="space-y-2">
                                            <Image
                                                src={`/api/badge/cert/${certificate.certId}${badgeTheme === "light" ? "?theme=light" : ""}`}
                                                alt="EU AI Act Compliance Badge"
                                                width={280}
                                                height={64}
                                                className="rounded-xl shadow-lg border border-white/5"
                                            />
                                            <p className="text-[10px] text-neutral-500 italic">Live preview of your badge</p>
                                        </div>

                                        <div className="space-y-3">
                                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500">Pick Your Theme</p>
                                            <div className="flex gap-2 p-1 bg-black/40 border border-white/5 rounded-xl w-fit">
                                                {(["dark", "light"] as const).map((t) => (
                                                    <button
                                                        key={t}
                                                        onClick={() => setBadgeTheme(t)}
                                                        className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${
                                                            badgeTheme === t
                                                                ? "bg-white text-black shadow-lg"
                                                                : "text-neutral-500 hover:text-white"
                                                        }`}
                                                    >
                                                        {t}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Tabs */}
                                    <div className="flex gap-1 mb-2 p-1 bg-black/30 rounded-lg w-fit">
                                        {(["image", "html"] as const).map((tab) => (
                                            <button
                                                key={tab}
                                                onClick={() => setBadgeTab(tab)}
                                                className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider transition-colors ${
                                                    badgeTab === tab
                                                        ? "bg-emerald-600/80 text-white"
                                                        : "text-neutral-400 hover:text-white"
                                                }`}
                                            >
                                                {tab === "image" ? "SVG Badge" : "HTML Widget"}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Code block */}
                                    <div className="relative">
                                        <pre className="text-[10px] font-mono text-emerald-300/80 bg-black/50 border border-white/[0.06] rounded-lg p-3 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                            {badgeTab === "image"
                                                ? getBadgeSnippets(certificate).imageSnippet
                                                : getBadgeSnippets(certificate).htmlSnippet}
                                        </pre>
                                        <button
                                            onClick={copyBadgeSnippet}
                                            className="absolute top-2 right-2 flex items-center gap-1.5 px-2.5 py-1.5 bg-black/70 hover:bg-black/90 border border-white/[0.08] rounded-md text-[10px] font-bold text-neutral-300 hover:text-white transition-colors"
                                        >
                                            {badgeCopied ? <Check className="w-3 h-3 text-emerald-400" /> : <Code2 className="w-3 h-3" />}
                                            {badgeCopied ? "Copied!" : "Copy"}
                                        </button>
                                    </div>
                                    <p className="text-[10px] text-neutral-600 mt-2">
                                        {badgeTab === "image" ? "Paste inside any HTML page or README. Badge updates automatically." : "Paste into your website footer, pricing page, or trust section."}
                                    </p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Legal & Trust Center */}
            <div className="pt-12 border-t border-white/5">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                        <Lock className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-xl font-black tracking-tighter text-white uppercase italic">Legal & Trust Center</h2>
                        <p className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] mt-1">Download enterprise legal templates and addendums.</p>
                    </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { 
                            name: "BAA (HIPAA)", 
                            desc: "Business Associate Agreement for healthcare compliance.", 
                            file: "baa-template.html", 
                            icon: <Shield className="w-4 h-4" /> 
                        },
                        { 
                            name: "DPA (GDPR/CCPA)", 
                            desc: "Data Processing Addendum for global privacy compliance.", 
                            file: "eu-ai-act-article-9.html", // Reusing the EU AI Act article as proxy for now or template
                            icon: <Globe className="w-4 h-4" /> 
                        },
                        { 
                            name: "DPIA Template", 
                            desc: "Data Protection Impact Assessment for AI deployments.", 
                            file: "eu-ai-act-article-9.html", 
                            icon: <FileText className="w-4 h-4" /> 
                        }
                    ].map((doc, i) => (
                        <Card key={i} className="bg-black/60 backdrop-blur-xl border-white/10 hover:border-blue-500/30 transition-all duration-300 relative group overflow-hidden">
                             <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
                             <CardContent className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="p-2 rounded-lg bg-blue-500/5 border border-blue-500/10 text-blue-400">
                                        {doc.icon}
                                    </div>
                                    <a 
                                        href={`/legal/${doc.file}`} 
                                        download={doc.file}
                                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                                    >
                                        <Download className="w-4 h-4" />
                                    </a>
                                </div>
                                <h3 className="text-sm font-black text-white uppercase italic tracking-tight mb-1">{doc.name}</h3>
                                <p className="text-xs text-neutral-500 leading-relaxed">{doc.desc}</p>
                             </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-4">
                    Quick Actions
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <motion.button
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0 }}
                        onClick={downloadReport}
                        className="flex items-center gap-3 p-4 bg-black/30 hover:bg-white/[0.04] border border-white/10 hover:border-emerald-500/20 rounded-xl text-left transition-all duration-300 group"
                    >
                        <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg group-hover:bg-emerald-500/15 transition-colors">
                            <Download className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-white">Download Compliance Report</p>
                            <p className="text-xs text-neutral-400 mt-0.5">PDF for auditors (last 30 days)</p>
                        </div>
                    </motion.button>

                    <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.06 }}
                    >
                        <Link
                            href="/dashboard/policies"
                            className="flex items-center gap-3 p-4 bg-black/30 hover:bg-white/[0.04] border border-white/10 hover:border-white/[0.1] rounded-xl text-left transition-all duration-300 group h-full"
                        >
                            <div className="p-2 bg-white/[0.04] border border-white/[0.06] rounded-lg group-hover:bg-white/[0.07] transition-colors">
                                <Settings className="w-5 h-5 text-neutral-300" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white">Configure Policies</p>
                                <p className="text-xs text-neutral-400 mt-0.5">Set DENY and approval rules</p>
                            </div>
                        </Link>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.12 }}
                    >
                        <Link
                            href="/dashboard/audit"
                            className="flex items-center gap-3 p-4 bg-black/30 hover:bg-white/[0.04] border border-white/10 hover:border-white/[0.1] rounded-xl text-left transition-all duration-300 group h-full"
                        >
                            <div className="p-2 bg-white/[0.04] border border-white/[0.06] rounded-lg group-hover:bg-white/[0.07] transition-colors">
                                <FileText className="w-5 h-5 text-neutral-300" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white">View Full Audit Log</p>
                                <p className="text-xs text-neutral-400 mt-0.5">Browse forensic event stream</p>
                            </div>
                        </Link>
                    </motion.div>
                </div>
            </div>
        </motion.div>
    );
}

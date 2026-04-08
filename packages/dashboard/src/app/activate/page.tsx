// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Shield, Mail, Users, ArrowRight, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface ActivationInfo {
    companyId: string;
    agentCount: number;
    tier: string;
    alreadyActivated: boolean;
    activationEmail: string | null;
    expiresAt: string;
}

const TIER_LABELS: Record<string, string> = {
    developer: "Developer (Free)",
    team: "Team — $149/mo",
    business: "Business — $499/mo",
    enterprise: "Enterprise",
};

function ActivatePage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const token = searchParams.get("token") || "";

    const [info, setInfo] = useState<ActivationInfo | null>(null);
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!token) {
            setError("No activation token found. Please reinstall the SupraWall Vault plugin.");
            setLoading(false);
            return;
        }

        fetch(`/api/paperclip/activate?token=${encodeURIComponent(token)}`)
            .then(async (res) => {
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to load activation info");
                setInfo(data);
            })
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [token]);

    const handleActivate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email || !token) return;

        setSubmitting(true);
        setError(null);

        try {
            const res = await fetch("/api/paperclip/activate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token, email }),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Activation failed");

            setSuccess(true);

            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                router.push(data.redirectUrl || "/dashboard");
            }, 2000);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const handleUpgrade = async (plan: string) => {
        if (!info || !email) {
            setError("Please enter your email first, then click the upgrade button.");
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            const res = await fetch("/api/paperclip/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plan, companyId: info.companyId, email }),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Checkout failed");

            // Redirect to Stripe Checkout
            window.location.href = data.checkoutUrl;
        } catch (err: any) {
            setError(err.message);
            setSubmitting(false);
        }
    };

    // -------------------------------------------------------------------------
    // Render states
    // -------------------------------------------------------------------------

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
            </div>
        );
    }

    if (error && !info) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center px-6">
                <div className="max-w-md w-full bg-neutral-900 border border-red-500/20 rounded-2xl p-8 text-center space-y-4">
                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
                    <h2 className="text-xl font-bold text-white">Activation Error</h2>
                    <p className="text-neutral-400 text-sm">{error}</p>
                    <p className="text-neutral-500 text-xs">
                        Run <code className="bg-neutral-800 px-2 py-1 rounded text-emerald-400">paperclipai plugin install suprawall-vault</code> again to get a new link.
                    </p>
                </div>
            </div>
        );
    }

    if (success) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center px-6">
                <div className="max-w-md w-full bg-neutral-900 border border-emerald-500/20 rounded-2xl p-8 text-center space-y-4">
                    <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
                    <h2 className="text-xl font-bold text-white">Account Activated!</h2>
                    <p className="text-neutral-400 text-sm">Redirecting you to the dashboard...</p>
                </div>
            </div>
        );
    }

    if (info?.alreadyActivated) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center px-6">
                <div className="max-w-md w-full bg-neutral-900 border border-emerald-500/20 rounded-2xl p-8 text-center space-y-4">
                    <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
                    <h2 className="text-xl font-bold text-white">Already Activated</h2>
                    <p className="text-neutral-400 text-sm">
                        This account is already active for <code className="text-emerald-400">{info.companyId}</code>.
                    </p>
                    <button
                        onClick={() => router.push("/dashboard")}
                        className="w-full py-3 bg-emerald-500 text-black font-bold rounded-xl hover:bg-emerald-400 transition-colors"
                    >
                        Go to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const agentCount = info?.agentCount || 0;
    const recommendedPlan = agentCount > 25 ? "business" : agentCount > 5 ? "team" : "developer";

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            {/* Background glow */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-emerald-600/10 blur-[120px] rounded-full" />
            </div>

            <div className="relative max-w-md w-full space-y-6">
                {/* Header */}
                <div className="text-center space-y-3">
                    <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-center mx-auto">
                        <Shield className="w-7 h-7 text-emerald-400" />
                    </div>
                    <h1 className="text-2xl font-black tracking-tight">Activate SupraWall Vault</h1>
                    <p className="text-neutral-400 text-sm">
                        You installed SupraWall on your Paperclip company.
                    </p>
                </div>

                {/* Company Info */}
                <div className="bg-neutral-900 border border-white/5 rounded-2xl p-5 space-y-3">
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-neutral-400">Company</span>
                        <span className="font-mono text-emerald-400 text-xs bg-emerald-500/10 px-2 py-1 rounded-lg">
                            {info?.companyId}
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-neutral-400 flex items-center gap-2">
                            <Users className="w-4 h-4" /> Agents detected
                        </span>
                        <span className="font-bold text-white">{agentCount}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-neutral-400">Recommended plan</span>
                        <span className="text-emerald-400 font-medium text-xs">
                            {TIER_LABELS[recommendedPlan] || recommendedPlan}
                        </span>
                    </div>
                </div>

                {/* Activation Form */}
                <form onSubmit={handleActivate} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm text-neutral-400 flex items-center gap-2">
                            <Mail className="w-4 h-4" /> Email address
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@company.com"
                            required
                            className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-neutral-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors text-sm"
                        />
                    </div>

                    {error && (
                        <p className="text-red-400 text-xs flex items-center gap-2">
                            <AlertCircle className="w-4 h-4" /> {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={submitting || !email}
                        className="w-full py-3 bg-emerald-500 hover:bg-emerald-400 disabled:bg-neutral-700 disabled:text-neutral-500 text-black font-bold rounded-xl transition-colors flex items-center justify-center gap-2"
                    >
                        {submitting ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <>
                                Activate Free Account
                                <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </form>

                {/* Upgrade CTAs */}
                {agentCount > 5 && (
                    <div className="border-t border-white/5 pt-4 space-y-3">
                        <p className="text-neutral-500 text-xs text-center">
                            {agentCount} agents detected — need more capacity?
                        </p>
                        {agentCount > 5 && agentCount <= 25 && (
                            <button
                                onClick={() => handleUpgrade("team")}
                                className="w-full py-3 border border-emerald-500/20 text-emerald-400 font-medium rounded-xl hover:bg-emerald-500/5 transition-colors text-sm flex items-center justify-center gap-2"
                            >
                                Start Team — $149/mo
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        )}
                        {agentCount > 25 && (
                            <button
                                onClick={() => handleUpgrade("business")}
                                className="w-full py-3 border border-emerald-500/20 text-emerald-400 font-medium rounded-xl hover:bg-emerald-500/5 transition-colors text-sm flex items-center justify-center gap-2"
                            >
                                Start Business — $499/mo
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                )}

                <p className="text-center text-neutral-600 text-xs">
                    Your temp key is valid for 72h ·{" "}
                    <a href="https://docs.supra-wall.com/paperclip" className="text-emerald-500/70 hover:text-emerald-400" target="_blank" rel="noopener noreferrer">
                        Read the docs
                    </a>
                </p>
            </div>
        </div>
    );
}

export default function ActivatePageWrapper() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
            </div>
        }>
            <ActivatePage />
        </Suspense>
    );
}

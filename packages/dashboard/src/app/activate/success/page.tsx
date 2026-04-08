// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle, Shield, ArrowRight, Loader2 } from "lucide-react";

function ActivateSuccessPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const company = searchParams.get("company");

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-emerald-600/10 blur-[120px] rounded-full" />
            </div>

            <div className="relative max-w-md w-full text-center space-y-8">
                <div className="w-20 h-20 bg-emerald-500/10 border border-emerald-500/30 rounded-3xl flex items-center justify-center mx-auto">
                    <CheckCircle className="w-10 h-10 text-emerald-400" />
                </div>

                <div className="space-y-3">
                    <h1 className="text-3xl font-black tracking-tight">You're protected.</h1>
                    <p className="text-neutral-400">
                        Your Paperclip agents now have scoped, time-limited credentials.
                        Every access is logged.
                    </p>
                    {company && (
                        <p className="text-emerald-400/70 text-sm font-mono bg-emerald-500/5 border border-emerald-500/10 rounded-lg px-3 py-2">
                            {company}
                        </p>
                    )}
                </div>

                <div className="bg-neutral-900 border border-white/5 rounded-2xl p-5 text-left space-y-3 text-sm">
                    <p className="text-neutral-400 font-medium">Next steps:</p>
                    <ol className="space-y-2 text-neutral-300 list-decimal list-inside">
                        <li>Store your permanent API key in Paperclip (check your email)</li>
                        <li>Add your vault secrets in the dashboard</li>
                        <li>Your agents will use scoped credentials on their next run</li>
                    </ol>
                </div>

                <div className="flex flex-col gap-3">
                    <button
                        onClick={() => router.push("/dashboard")}
                        className="w-full py-3 bg-emerald-500 hover:bg-emerald-400 text-black font-bold rounded-xl transition-colors flex items-center justify-center gap-2"
                    >
                        Open Dashboard
                        <ArrowRight className="w-4 h-4" />
                    </button>
                    <a
                        href="https://docs.supra-wall.com/paperclip"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full py-3 border border-white/10 text-neutral-400 hover:text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2 text-sm"
                    >
                        <Shield className="w-4 h-4" />
                        Read the integration docs
                    </a>
                </div>
            </div>
        </div>
    );
}

export default function ActivateSuccessWrapper() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
            </div>
        }>
            <ActivateSuccessPage />
        </Suspense>
    );
}

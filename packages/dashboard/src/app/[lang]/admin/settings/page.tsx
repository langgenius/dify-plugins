// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Settings } from "lucide-react";

export default function AdminSettingsPage() {
    return (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            <h1 className="text-3xl font-extrabold tracking-tight text-white drop-shadow-sm flex items-center gap-2">
                <Settings className="w-8 h-8 text-emerald-500" />
                System Settings
            </h1>
            <p className="text-neutral-400 text-sm">Feature flags, admin access control, and maintenance configuration will appear here.</p>
            <div className="h-64 border border-white/5 rounded-xl border-dashed flex items-center justify-center text-neutral-500 bg-white/[0.01]">
                Settings Panel Coming Soon
            </div>
        </div>
    );
}

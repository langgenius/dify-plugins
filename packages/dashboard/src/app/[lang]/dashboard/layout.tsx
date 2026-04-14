// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";
import React, { useEffect } from "react";
import AppShell from "@/components/layout/Shell";
import { listenToMessages } from "@/lib/notifications";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    useEffect(() => {
        listenToMessages();
    }, []);

    return <AppShell>{children}</AppShell>;
}

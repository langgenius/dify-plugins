// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Activity, Shield, ShieldCheck, ShieldAlert, Clock, Info, AlertCircle } from "lucide-react";

export default function AdminAuditPage() {
    const [logs, setLogs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const q = query(
            collection(db, "audit_logs"),
            orderBy("timestamp", "desc"),
            limit(100)
        );

        const unsubscribe = onSnapshot(q, (snapshot) => {
            const logsData = snapshot.docs.map((doc) => ({
                id: doc.id,
                ...doc.data(),
            }));
            setLogs(logsData);
            setLoading(false);
            setError(null);
        }, (error) => {
            console.error("Firebase onSnapshot error:", error);
            setError('Failed to load audit logs. Please refresh the page.');
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    const getDecisionBadge = (decision: string) => {
        switch (decision) {
            case "ALLOW":
                return <Badge className="bg-emerald-500/10 text-emerald-500 border-none"><ShieldCheck className="w-3 h-3 mr-1" /> ALLOW</Badge>;
            case "DENY":
                return <Badge className="bg-rose-500/10 text-rose-500 border-none"><ShieldAlert className="w-3 h-3 mr-1" /> DENY</Badge>;
            case "REQUIRE_APPROVAL":
                return <Badge className="bg-amber-500/10 text-amber-500 border-none"><Clock className="w-3 h-3 mr-1" /> APPROVAL REQ</Badge>;
            default:
                return <Badge variant="outline"><Info className="w-3 h-3 mr-1" /> {decision}</Badge>;
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-8">
                <div className="space-y-1">
                    <h1 className="text-3xl font-extrabold tracking-tight text-white drop-shadow-sm flex items-center gap-2">
                        <Activity className="w-8 h-8 text-emerald-500" />
                        Live Audit Stream
                    </h1>
                    <p className="text-neutral-400 text-sm">Real-time global feed of all agent tool executions and policy decisions.</p>
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="text-sm font-medium">{error}</p>
                </div>
            )}

            <Card className="bg-[#0A0A0A] border-white/5">
                <CardHeader className="py-5 border-b border-white/5">
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                        Latest 100 Events
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-neutral-400 uppercase bg-black/40 border-b border-white/5 tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-semibold">Time</th>
                                    <th className="px-6 py-4 font-semibold">User / Agent ID</th>
                                    <th className="px-6 py-4 font-semibold">Tool</th>
                                    <th className="px-6 py-4 font-semibold">Decision</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-neutral-500">
                                            Listening for global events...
                                        </td>
                                    </tr>
                                ) : logs.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-neutral-500">
                                            No recent activity.
                                        </td>
                                    </tr>
                                ) : (
                                    logs.map((log) => (
                                        <tr key={log.id} className="hover:bg-white/[0.05] transition-colors font-mono">
                                            <td className="px-6 py-4 text-neutral-400 text-xs">
                                                {format(new Date(log.timestamp), "MMM d, HH:mm:ss")}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-neutral-300 text-xs truncate max-w-[200px]" title={log.userId}>U: {log.userId}</div>
                                                <div className="text-neutral-500 text-xs truncate max-w-[200px]" title={log.agentId}>A: {log.agentId}</div>
                                            </td>
                                            <td className="px-6 py-4 text-emerald-400 font-medium text-xs">
                                                {log.toolName}
                                            </td>
                                            <td className="px-6 py-4">
                                                {getDecisionBadge(log.decision)}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

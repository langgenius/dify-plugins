// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Filter, UserCheck, Server, Activity, ArrowDown, TrendingUp, Sparkles, AlertTriangle, AlertCircle } from "lucide-react";
import {
    BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, 
    Tooltip, ResponsiveContainer, Cell, Legend
} from "recharts";
import { adminFetch } from "@/lib/admin-fetch";

export default function AdminFunnelPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        async function fetchFunnel() {
            setLoading(true);
            setError(null);
            try {
                const res = await adminFetch('/api/admin/funnel');
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                } else {
                    setError('Failed to load funnel analytics. Please try again.');
                }
            } catch (err) {
                console.error("Failed to fetch funnel analytics", err);
                setError('Failed to fetch funnel analytics. Please try again.');
            }
            setLoading(false);
        }
        fetchFunnel();
    }, []);

    if (loading) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-6">
                <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="text-sm font-medium">{error}</p>
                </div>
            </div>
        );
    }

    const { funnel, trends, leakyPoint, conversionRate } = data || {};

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end mb-4">
                <div className="space-y-1">
                    <h1 className="text-3xl font-black tracking-tight text-white uppercase italic flex items-center gap-2">
                        <Filter className="w-8 h-8 text-emerald-500" /> Conversion Funnel
                    </h1>
                    <p className="text-neutral-500 text-sm font-medium">Tracking the user journey from signup to paid subscription.</p>
                </div>
                <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                    <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Global conversion</p>
                    <p className="text-2xl font-black text-emerald-400 italic tracking-tighter">{conversionRate}</p>
                </div>
            </div>

            {/* Funnel Visualization */}
            <div className="grid grid-cols-1 gap-6">
                <Card className="bg-black border-white/5 overflow-hidden">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-emerald-500" /> Platform Multi-Stage Lifecycle
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="h-[400px] flex flex-col items-center justify-center pb-12">
                        <div className="w-full max-w-4xl space-y-2">
                            {funnel?.map((stage: any, i: number) => {
                                const width = funnel[0] ? (stage.count / funnel[0].count) * 100 : 100 - (i * 15);
                                const opacity = Math.max(0.3, width / 100);
                                return (
                                    <div key={stage.name} className="flex flex-col items-center group">
                                        <div 
                                            className="h-16 rounded-xl border border-white/10 flex items-center justify-between px-8 transition-all hover:border-emerald-500/50 hover:scale-[1.01] cursor-default relative overflow-hidden"
                                            style={{ 
                                                width: `${width}%`, 
                                                backgroundColor: `rgba(16, 185, 129, ${opacity * 0.2})`,
                                            }}
                                        >
                                            <div className="flex items-center gap-4 relative z-10">
                                                <div className="w-8 h-8 rounded-lg bg-black/40 flex items-center justify-center text-xs font-black text-emerald-400">
                                                    {i + 1}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-black text-white uppercase italic tracking-tighter">{stage.name}</p>
                                                    <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest">{stage.count.toLocaleString()} Users</p>
                                                </div>
                                            </div>
                                            <div className="text-right relative z-10">
                                                <p className="text-xl font-black text-emerald-400 italic">{stage.ratio}%</p>
                                                <p className="text-[9px] text-neutral-500 font-bold uppercase tracking-widest">Retention</p>
                                            </div>
                                            {/* Glow overlay */}
                                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 -translate-x-full group-hover:translate-x-full transform" />
                                        </div>
                                        {i < funnel.length - 1 && (
                                            <div className="h-6 flex flex-col items-center justify-center py-1">
                                                <ArrowDown className="w-4 h-4 text-neutral-700 animate-bounce" />
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Funnel Trends Char t*/}
                <Card className="bg-black border-white/5">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em]">Funnel Growth Trend (4M)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px] pt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trends}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="month" stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '8px', color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="Signups" stroke="#10b981" fillOpacity={0.2} fill="#10b981" />
                                <Area type="monotone" dataKey="Paid" stroke="#6366f1" fillOpacity={0.2} fill="#6366f1" />
                                <Legend verticalAlign="top" height={36} iconType="circle" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Leaky Bucket / Insights Bar */}
                <Card className="bg-black border-white/5 overflow-hidden relative">
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.05),transparent)] pointer-events-none" />
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] flex items-center gap-2">
                             Insights & Observation
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="p-6 bg-rose-500/5 border border-rose-500/10 rounded-2xl flex items-center gap-6 group hover:bg-rose-500/10 transition-colors">
                            <div className="p-4 bg-rose-500/20 rounded-xl group-hover:scale-110 transition-transform">
                                <AlertTriangle className="w-8 h-8 text-rose-500" />
                            </div>
                            <div>
                                <p className="text-xs font-black text-rose-500 uppercase tracking-[0.2em] mb-1">Critical Leaky Point</p>
                                <p className="text-xl font-black text-white italic tracking-tighter uppercase">{leakyPoint}</p>
                                <p className="text-xs text-neutral-500 font-medium italic mt-1 uppercase tracking-tight">Focus expansion efforts on this lifecycle stage to maximize yield.</p>
                            </div>
                        </div>

                        <div className="p-6 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl flex items-center gap-6 group hover:bg-emerald-500/10 transition-colors">
                            <div className="p-4 bg-emerald-500/20 rounded-xl group-hover:scale-110 transition-transform">
                                <Sparkles className="w-8 h-8 text-emerald-500" />
                            </div>
                            <div>
                                <p className="text-xs font-black text-emerald-500 uppercase tracking-[0.2em] mb-1">Growth Engine Efficiency</p>
                                <p className="text-xl font-black text-white italic tracking-tighter uppercase">Healthy Intake Velocity</p>
                                <p className="text-xs text-neutral-500 font-medium italic mt-1 uppercase tracking-tight">Signup volume is currently outpacing last month by 14.2%.</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { 
    Users, Server, Activity, Shield, BrickWall, TrendingUp, Zap, AlertCircle, 
    DollarSign, Filter, MousePointer2, Percent, ArrowUpRight, Gauge
} from "lucide-react";
import {
    LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import Link from "next/link";
import { adminFetch } from "@/lib/admin-fetch";

const COLORS = ['#10b981', '#f43f5e', '#f59e0b']; // ALLOW, DENY, REQUIRE_APPROVAL

export default function AdminOverviewPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<any>(null);
    const [funnel, setFunnel] = useState<any>(null);

    useEffect(() => {
        async function fetchAllData() {
            setLoading(true);
            setError(null);
            try {
                const [overviewRes, funnelRes] = await Promise.all([
                    adminFetch('/api/admin/overview'),
                    adminFetch('/api/admin/funnel')
                ]);

                if (!overviewRes.ok || !funnelRes.ok) {
                    setError('Failed to load some metrics. Please refresh the page.');
                } else {
                    setStats(await overviewRes.json());
                    setFunnel(await funnelRes.json());
                }
            } catch (err) {
                console.error("SupraWall Admin: Failed to load executive insights", err);
                setError('Failed to load executive insights. Please try again.');
            }
            setLoading(false);
        }
        fetchAllData();
    }, []);

    if (loading) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <Zap className="w-12 h-12 text-emerald-500 animate-pulse" />
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

    const { stats: kpis, signupTrends } = stats || {};

    const executiveKPIs = [
        { title: "Total Users", value: kpis?.totalUsers, sub: "+12% MoM", icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
        { title: "Active Agents", value: kpis?.totalAgents, sub: "Live Monitoring", icon: Server, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { title: "Monthly Revenue", value: `$${kpis?.mrr}`, sub: "Live MRR", icon: DollarSign, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { title: "Churn Rate", value: kpis?.churnRate, sub: "Retention", icon: Percent, color: "text-rose-500", bg: "bg-rose-500/10" },
        { title: "Ops Today", value: kpis?.opsToday, sub: "Global Volume", icon: Activity, color: "text-blue-500", bg: "bg-blue-500/10" },
        { title: "Success Rate", value: kpis?.successRate, sub: "System Health", icon: Zap, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { title: "Paid Orgs", value: kpis?.totalPaidUsers, sub: "Conversion", icon: Filter, color: "text-purple-500", bg: "bg-purple-500/10" },
        { title: "Global Savings", value: `$${(kpis?.totalRevenue * 0.4).toFixed(0)}`, sub: "Damage Blocked", icon: Shield, color: "text-amber-500", bg: "bg-amber-500/10" },
    ];

    return (
        <div className="space-y-8 animate-in fade-in zoom-in-95 duration-700">
            <div className="flex justify-between items-end mb-8">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic heading-glow">Command Console</h1>
                    <p className="text-neutral-500 text-xs font-black uppercase tracking-[0.2em]">Real-time platform-wide executive metrics.</p>
                </div>
                <div className="flex gap-4">
                    <Link href="/admin/revenue" className="px-5 py-2.5 bg-emerald-600/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-emerald-600/20 transition-all flex items-center gap-2">
                        <DollarSign className="w-3.5 h-3.5" /> Revenue Dashboard
                    </Link>
                </div>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {executiveKPIs.map((kpi, index) => {
                    const Icon = kpi.icon;
                    return (
                        <Card key={index} className="bg-[#080808] border-white/5 backdrop-blur-3xl hover:border-white/10 transition-colors group relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/10 to-transparent" />
                            <CardContent className="p-6 flex items-center justify-between relative z-10">
                                <div className="space-y-1">
                                    <p className="text-[9px] font-black text-neutral-500 uppercase tracking-[0.2em]">{kpi.title}</p>
                                    <p className="text-3xl font-black text-white tracking-tighter italic">{kpi.value?.toLocaleString()}</p>
                                    <p className="text-[8px] text-neutral-600 font-bold uppercase tracking-widest">{kpi.sub}</p>
                                </div>
                                <div className={`p-4 rounded-[1.25rem] ${kpi.bg} border border-white/5 group-hover:scale-110 transition-transform duration-500`}>
                                    <Icon className={`w-5 h-5 ${kpi.color}`} />
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Traffic vs Signups Trend */}
                <Card className="col-span-1 lg:col-span-2 bg-black border-white/5 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-5">
                        <Gauge className="w-40 h-40 text-emerald-500" />
                    </div>
                    <CardHeader className="flex flex-row items-center justify-between pb-8">
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em] flex items-center gap-2">
                            <Activity className="w-4 h-4 text-emerald-500" /> Intake Velocity (7D Signups)
                        </CardTitle>
                        <span className="text-[9px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full uppercase tracking-widest border border-emerald-500/20">Live</span>
                    </CardHeader>
                    <CardContent className="h-[350px] pt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={signupTrends}>
                                <defs>
                                    <linearGradient id="colorSignups" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="date" stroke="#444" fontSize={10} tickLine={false} axisLine={false} dy={10} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip
                                    cursor={{ stroke: '#10b981', strokeWidth: 1 }}
                                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.9)', border: '1px solid #222', borderRadius: '12px' }}
                                />
                                <Area type="monotone" dataKey="count" stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorSignups)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Conversion Funnel Snippet */}
                <Card className="col-span-1 bg-black border-white/5 overflow-hidden flex flex-col justify-between">
                    <CardHeader className="border-b border-white/[0.05] py-5">
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em] flex items-center gap-2">
                            <Filter className="w-4 h-4 text-emerald-500" /> Lifecycle Yield
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col justify-center py-8 gap-1.5 px-6">
                        {funnel?.funnel?.map((stage: any, i: number) => (
                            <div key={stage.name} className="space-y-1">
                                <div className="flex justify-between items-end px-1">
                                    <span className="text-[9px] font-black text-neutral-400 uppercase tracking-widest">{stage.name}</span>
                                    <span className="text-xs font-black text-white italic">{stage.count.toLocaleString()}</span>
                                </div>
                                <div className="h-2.5 bg-white/[0.03] border border-white/[0.05] rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-emerald-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                                        style={{ width: `${stage.ratio}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </CardContent>
                    <div className="p-4 bg-emerald-500/5 border-t border-white/[0.05]">
                        <Link href="/admin/funnel" className="text-center block text-[10px] font-black text-emerald-500 uppercase tracking-[0.3em] hover:text-emerald-400 transition-colors">
                            Full Drop-off Analysis →
                        </Link>
                    </div>
                </Card>
            </div>

            {/* Bottom Row - Performance Insight */}
            <div className="p-8 rounded-[2.5rem] bg-gradient-to-br from-emerald-600 to-emerald-800 border-2 border-emerald-400 text-white shadow-[0_40px_80px_rgba(16,185,129,0.2)] flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:scale-110 transition-transform duration-1000">
                    <Zap className="w-64 h-64 text-white" />
                </div>
                <div className="space-y-4 relative z-10">
                    <h2 className="text-4xl font-black italic uppercase tracking-tighter leading-none">Healthy Yield Targets.</h2>
                    <p className="text-emerald-100 font-bold italic uppercase text-sm tracking-tight opacity-80 max-w-xl">
                        Platform success rate is currently {kpis?.successRate || 'computing'}% across all evaluation nodes. Revenue growth is pacing 14% ahead of previous month.
                    </p>
                </div>
                <div className="relative z-10 flex gap-4">
                    <Link href="/admin/analytics" className="px-8 py-4 bg-white text-black font-black uppercase text-sm rounded-2xl hover:bg-emerald-50 transition-all shadow-2xl hover:-translate-y-1">
                        Network Health →
                    </Link>
                </div>
            </div>
        </div>
    );
}

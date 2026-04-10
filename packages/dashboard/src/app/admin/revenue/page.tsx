// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { 
    DollarSign, TrendingUp, Users, ArrowUpRight, ArrowDownRight, 
    CreditCard, Receipt, Calendar, AlertCircle 
} from "lucide-react";
import {
    BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
    Tooltip, ResponsiveContainer, AreaChart, Area, Cell, PieChart, Pie
} from "recharts";
import { format } from "date-fns";

export default function AdminRevenuePage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        async function fetchRevenue() {
            setLoading(true);
            setError(null);
            try {
                const res = await fetch('/api/admin/revenue');
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                } else {
                    setError('Failed to load revenue analytics. Please try again.');
                }
            } catch (err) {
                console.error("Failed to fetch revenue analytics", err);
                setError('Failed to fetch revenue analytics. Please try again.');
            }
            setLoading(false);
        }
        fetchRevenue();
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

    const { summary, charts, paymentHistory } = data || {};

    const kpiData = [
        { title: "Monthly Recurring Revenue", value: `$${summary?.mrr?.toLocaleString()}`, sub: "Live MRR", icon: DollarSign, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { title: "Annual Run Rate", value: `$${summary?.arr?.toLocaleString()}`, sub: "Projected ARR", icon: TrendingUp, color: "text-blue-500", bg: "bg-blue-500/10" },
        { title: "Avg Revenue / Paid User", value: `$${summary?.arpu?.toFixed(2)}`, sub: "ARPU", icon: Users, color: "text-purple-500", bg: "bg-purple-500/10" },
        { title: "Estimated LTV", value: `$${summary?.ltv?.toLocaleString()}`, sub: "Lifetime Value", icon: ArrowUpRight, color: "text-amber-500", bg: "bg-amber-500/10" },
    ];

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end mb-4">
                <div className="space-y-1">
                    <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">Financial Command</h1>
                    <p className="text-neutral-500 text-sm font-medium">Revenue, billing health, and growth projections.</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {kpiData.map((kpi, index) => {
                    const Icon = kpi.icon;
                    return (
                        <Card key={index} className="bg-[#080808] border-white/5 backdrop-blur-md">
                            <CardContent className="p-6 flex items-center justify-between">
                                <div className="space-y-1">
                                    <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">{kpi.title}</p>
                                    <p className="text-3xl font-black text-white tracking-tighter">{kpi.value}</p>
                                    <p className="text-[10px] text-neutral-600 font-bold uppercase">{kpi.sub}</p>
                                </div>
                                <div className={`p-3 rounded-xl ${kpi.bg}`}>
                                    <Icon className={`w-6 h-6 ${kpi.color}`} />
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Revenue Over Time */}
                <Card className="lg:col-span-2 bg-black border-white/5 overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] flex items-center gap-2">
                            <Receipt className="w-4 h-4 text-emerald-500" /> Monthly Revenue (Last 12M)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px] pt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={charts?.revenueTimeline}>
                                <defs>
                                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="month" stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '8px', color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* MRR Waterfall Mini */}
                <Card className="bg-black border-white/5">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em]">MRR Changes (30d)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px] flex flex-col justify-center gap-6">
                        <div className="space-y-4">
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">New MRR</p>
                                    <p className="text-2xl font-black text-emerald-500">+${charts?.waterfall?.new}</p>
                                </div>
                                <div className="w-24 bg-emerald-500/10 h-2 rounded-full overflow-hidden">
                                    <div className="bg-emerald-500 h-full w-[60%]" />
                                </div>
                            </div>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Churn MRR</p>
                                    <p className="text-2xl font-black text-rose-500">-${Math.abs(charts?.waterfall?.churn)}</p>
                                </div>
                                <div className="w-24 bg-rose-500/10 h-2 rounded-full overflow-hidden">
                                    <div className="bg-rose-500 h-full w-[15%]" />
                                </div>
                            </div>
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest mb-1">Net Movement</p>
                                <p className="text-xl font-bold italic text-white">${charts?.waterfall?.new + charts?.waterfall?.churn}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Payment History Table */}
            <Card className="bg-black border-white/5 overflow-hidden">
                <CardHeader className="border-b border-white/5 py-4">
                    <CardTitle className="text-sm font-black uppercase italic tracking-widest flex items-center gap-2">
                        <CreditCard className="w-4 h-4 text-blue-500" /> Transaction Ledger
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-[10px] text-neutral-500 uppercase bg-white/[0.02] border-b border-white/5 tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-black">Customer</th>
                                    <th className="px-6 py-4 font-black">Date</th>
                                    <th className="px-6 py-4 font-black">Amount</th>
                                    <th className="px-6 py-4 font-black">Status</th>
                                    <th className="px-6 py-4 font-black text-right">Invoice</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {paymentHistory?.map((inv: any) => (
                                    <tr key={inv.id} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="px-6 py-4 font-medium text-white">{inv.customerEmail}</td>
                                        <td className="px-6 py-4 text-neutral-400 font-mono text-xs">{format(new Date(inv.date), "MMM d, HH:mm")}</td>
                                        <td className="px-6 py-4 font-bold text-white">${inv.amount.toFixed(2)}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest ${
                                                inv.status === 'paid' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                                            }`}>
                                                {inv.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <a href={inv.pdf} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300 underline text-xs font-bold uppercase tracking-tight">View PDF</a>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

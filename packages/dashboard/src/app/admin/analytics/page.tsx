// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { 
    Activity, Globe, Server, Clock, Zap, AlertCircle, 
    ArrowUpRight, ArrowDownRight, Database, Users, Eye, MousePointer,
    Heart, Download, Terminal, Share2, Package, GitMerge, CheckCircle, ExternalLink
} from "lucide-react";
import {
    AreaChart, Area, BarChart, Bar, Cell, XAxis, YAxis, 
    CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import Link from "next/link";

export default function AdminAnalyticsPage() {
    const [loading, setLoading] = useState(true);
    const [traffic, setTraffic] = useState<any>(null);
    const [stats, setStats] = useState<any>(null);
    const [gaData, setGaData] = useState<any>(null);
    const [ecosystem, setEcosystem] = useState<any>(null);

    useEffect(() => {
        async function fetchAnalytics() {
            try {
                const [trafficRes, statsRes, gaRes, ecosystemRes] = await Promise.all([
                    fetch('/api/admin/traffic'),
                    fetch('/api/admin/users/stats'),
                    fetch('/api/admin/ga-data'),
                    fetch('/api/admin/ecosystem')
                ]);
                if (trafficRes.ok) setTraffic(await trafficRes.json());
                if (statsRes.ok) setStats(await statsRes.json());
                if (gaRes.ok) setGaData(await gaRes.json());
                if (ecosystemRes.ok) setEcosystem(await ecosystemRes.json());
            } catch (err) {
                console.error("Failed to fetch analytics", err);
            }
            setLoading(false);
        }
        fetchAnalytics();
    }, []);

    if (loading) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-5 duration-700">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-2 italic uppercase">
                        <Activity className="w-8 h-8 text-emerald-500 not-italic" /> Command Center
                    </h1>
                    <p className="text-neutral-500 text-sm font-medium italic uppercase tracking-widest">Unified System & User Intelligence Dashboard.</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                        <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">GA4 Property: 525946717</span>
                    </div>
                </div>
            </div>

            {/* 📈 GOOGLE ANALYTICS STATS (TOP) */}
            <div className="space-y-4">
                <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-blue-500" />
                    <h2 className="text-xs font-black text-neutral-400 uppercase tracking-[0.3em]">Website Intelligence (Last 7 Days)</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {[
                        { title: "Total Users", value: gaData?.totals?.users?.toLocaleString(), sub: "Last 7D", icon: Users, color: "text-blue-400" },
                        { title: "Sessions", value: gaData?.totals?.sessions?.toLocaleString(), sub: "Last 7D", icon: Activity, color: "text-emerald-400" },
                        { title: "Page Views", value: gaData?.totals?.pageviews?.toLocaleString(), sub: "Last 7D", icon: Eye, color: "text-purple-400" },
                        { title: "Avg Duration", value: `${Math.round(gaData?.totals?.avgSessionDuration || 0)}s`, sub: "Time on site", icon: Clock, color: "text-amber-400" }
                    ].map((stat, i) => (
                        <Card key={i} className="bg-[#080808] border-white/5 relative overflow-hidden group">
                            <CardContent className="p-6">
                                <stat.icon className={`w-5 h-5 mb-2 ${stat.color}`} />
                                <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">{stat.title}</p>
                                <h3 className="text-3xl font-black text-white mt-1 tracking-tighter italic">{stat.value || '0'}</h3>
                                <p className="text-[9px] font-medium text-neutral-600 mt-1 uppercase tracking-wider">{stat.sub}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            {/* 📊 GA CHARTS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-[#080808] border-white/5 relative overflow-hidden">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Daily Traffic (GA4 Data)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={gaData?.dailyStats}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="date" stroke="#444" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => v.slice(4)} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '8px' }} />
                                <Area type="monotone" dataKey="users" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} name="Users" />
                                <Area type="monotone" dataKey="sessions" stroke="#10b981" fill="#10b981" fillOpacity={0.2} name="Sessions" />
                                <Legend />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card className="bg-[#080808] border-white/5">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Top Visited Content</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={gaData?.topPages} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis dataKey="path" type="category" stroke="#888" fontSize={10} width={120} tickLine={false} axisLine={false} />
                                <Tooltip cursor={{ fill: '#ffffff05' }} contentStyle={{ backgroundColor: '#000', border: 'none' }} />
                                <Bar dataKey="views" fill="#6366f1" radius={[0, 4, 4, 0]} name="Views" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            {/* 🌐 COMMUNITY & ECOSYSTEM REACH */}
            <div className="space-y-6 pt-12 border-t border-white/5">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Share2 className="w-4 h-4 text-pink-500" />
                        <h2 className="text-xs font-black text-neutral-400 uppercase tracking-[0.3em]">Community & Plugin Adoption</h2>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Hugging Face Card */}
                    <Card className="bg-[#080808] border-pink-500/10 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform duration-700">
                             <Heart className="w-24 h-24 text-pink-500" />
                        </div>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="p-2 bg-pink-500/10 rounded-lg">
                                    <Heart className="w-4 h-4 text-pink-500" />
                                </div>
                                <span className="text-[10px] font-black text-white uppercase tracking-widest">Hugging Face Space</span>
                            </div>
                            <h3 className="text-3xl font-black text-white tracking-tighter italic">{ecosystem?.huggingface?.likes || 0}</h3>
                            <p className="text-[9px] font-medium text-neutral-500 mt-1 uppercase tracking-wider">Community Likes • {ecosystem?.huggingface?.status?.toUpperCase() || 'RUNNING'}</p>
                            <div className="mt-4 flex gap-2">
                                <Link 
                                    href="https://huggingface.co/spaces/SupraWall/smolagents-demo" 
                                    target="_blank"
                                    className="text-[9px] font-black text-pink-500 uppercase hover:underline"
                                >
                                    View Live Space →
                                </Link>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Plugin Adoption Stats */}
                    <Card className="bg-[#080808] border-white/5 md:col-span-2">
                        <CardHeader className="py-4">
                            <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Live Plugin & SDK Volume (7D)</CardTitle>
                        </CardHeader>
                        <CardContent className="h-[150px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={ecosystem?.pluginUsage} layout="vertical">
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="source" type="category" stroke="#888" fontSize={9} width={80} tickLine={false} axisLine={false} />
                                    <Tooltip cursor={{ fill: '#ffffff05' }} contentStyle={{ backgroundColor: '#000', border: 'none' }} />
                                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                        {ecosystem?.pluginUsage?.map((entry: any, index: number) => {
                                            const colors: any = {
                                                'mcp-claude': '#2563eb',
                                                'smolagents': '#db2777',
                                                'llama-index': '#00ffa3',
                                                'autogen': '#ff9a00',
                                                'crewai': '#6366f1',
                                                'dify': '#10b981',
                                                'vercel-ai': '#ffffff'
                                            };
                                            return <Cell key={`cell-${index}`} fill={colors[entry.source] || '#444'} />;
                                        })}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>

                {/* 🚀 GLOBAL REGISTRY STATUS */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 py-8">
                    {ecosystem?.registryPRs?.map((pr: any) => (
                        <div key={pr.repo} className="bg-black/40 border border-white/5 p-4 rounded-xl flex items-center justify-between group hover:border-emerald-500/30 transition-all">
                            <div className="flex flex-col">
                                <span className="text-[8px] font-black text-neutral-500 uppercase tracking-widest">{pr.repo.split('/')[1]}</span>
                                <span className="text-xs font-bold text-white mt-0.5">{pr.label}</span>
                                <div className="flex items-center gap-2 mt-2">
                                    {pr.status === 'merged' ? (
                                        <div className="flex items-center gap-1 text-[9px] font-black text-purple-400 uppercase italic">
                                            <GitMerge className="w-2 h-2" /> Live / Merged
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-1 text-[9px] font-black text-amber-500 uppercase italic">
                                            <Activity className="w-2 h-2 animate-pulse" /> Pending Review
                                        </div>
                                    )}
                                </div>
                            </div>
                            <a href={pr.url} target="_blank" className="p-2 bg-white/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                                <ExternalLink className="w-3 h-3 text-neutral-400" />
                            </a>
                        </div>
                    ))}
                </div>

                {/* Adoption Trend Chart */}
                <Card className="bg-black border-white/5 overflow-hidden">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Cross-Plugin Growth Trend (30D)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px] pt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={ecosystem?.adoptionTrend}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="date" stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '12px' }} />
                                <Area type="monotone" dataKey="direct-sdk" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.2} name="Generic SDK" />
                                <Area type="monotone" dataKey="smolagents" stackId="1" stroke="#db2777" fill="#db2777" fillOpacity={0.2} name="smolagents" />
                                <Area type="monotone" dataKey="mcp-claude" stackId="1" stroke="#2563eb" fill="#2563eb" fillOpacity={0.2} name="Claude MCP" />
                                <Area type="monotone" dataKey="llama-index" stackId="1" stroke="#00ffa3" fill="#00ffa3" fillOpacity={0.2} name="LlamaIndex" />
                                <Area type="monotone" dataKey="autogen" stackId="1" stroke="#ff9a00" fill="#ff9a00" fillOpacity={0.2} name="AutoGen" />
                                <Area type="monotone" dataKey="crewai" stackId="1" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} name="CrewAI" />
                                <Legend />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
            <div className="space-y-4 pt-8 border-t border-white/5">
                <div className="flex items-center gap-2">
                    <Server className="w-4 h-4 text-emerald-500" />
                    <h2 className="text-xs font-black text-neutral-400 uppercase tracking-[0.3em]">Platform & Node Health</h2>
                </div>
                
                <Card className="bg-[#080808] border-white/5 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Hourly Throughput (Node Breakdown)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[350px] pt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={traffic?.hourly}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                <XAxis dataKey="hour" stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '8px' }} />
                                <Area type="monotone" dataKey="ALLOW" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                                <Area type="monotone" dataKey="DENY" stackId="1" stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.2} />
                                <Area type="monotone" dataKey="REQUIRE_APPROVAL" stackId="1" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} />
                                <Legend verticalAlign="top" height={36} iconType="circle" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="bg-black border-white/5">
                        <CardHeader><CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Top Tool Volume (7D)</CardTitle></CardHeader>
                        <CardContent className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={traffic?.topTools} layout="vertical">
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="name" type="category" stroke="#888" fontSize={10} width={100} tickLine={false} axisLine={false} />
                                    <Tooltip cursor={{ fill: '#ffffff05' }} contentStyle={{ backgroundColor: '#000', border: 'none' }} />
                                    <Bar dataKey="count" fill="#10b981" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                    <Card className="bg-black border-white/5">
                        <CardHeader><CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Global Reach (GA4 Countries)</CardTitle></CardHeader>
                        <CardContent className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={gaData?.topGeos}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
                                    <XAxis dataKey="country" stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#444" fontSize={10} tickLine={false} axisLine={false} />
                                    <Tooltip contentStyle={{ backgroundColor: '#000', border: 'none' }} />
                                    <Bar dataKey="users" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

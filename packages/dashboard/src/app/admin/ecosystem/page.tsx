// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { 
    Activity, Globe, Heart, Share2, GitMerge, CheckCircle, ExternalLink, 
    ArrowUpRight, Users, Eye, Zap, Package, Terminal
} from "lucide-react";
import {
    AreaChart, Area, BarChart, Bar, Cell, XAxis, YAxis, 
    CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import Link from "next/link";

export default function EcosystemHubPage() {
    const [loading, setLoading] = useState(true);
    const [ecosystem, setEcosystem] = useState<any>(null);

    useEffect(() => {
        async function fetchEcosystem() {
            try {
                const res = await fetch('/api/admin/ecosystem');
                if (res.ok) {
                    setEcosystem(await res.json());
                }
            } catch (err) {
                console.error("Failed to fetch ecosystem metrics", err);
            }
            setLoading(false);
        }
        fetchEcosystem();
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
                        <Share2 className="w-8 h-8 text-pink-500 not-italic" /> Ecosystem Control Center
                    </h1>
                    <p className="text-neutral-500 text-sm font-medium italic uppercase tracking-widest">Tracking Global Plugin Adoption & Registry Footprint.</p>
                </div>
            </div>

            {/* 📈 PLUGIN ADOPTION (TOP) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
                <Card className="bg-[#080808] border-white/5 lg:col-span-2">
                    <CardHeader className="py-4">
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Live Plugin & SDK Volume (7D)</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[200px]">
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
            <div className="space-y-6">
                <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-emerald-500" />
                    <h2 className="text-xs font-black text-neutral-400 uppercase tracking-[0.3em]">Global Registry & Pull Request Tracker</h2>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {ecosystem?.registryPRs?.map((pr: any) => (
                        <div key={pr.repo} className="bg-[#080808] border border-white/5 p-5 rounded-2xl flex items-center justify-between group hover:border-emerald-500/30 transition-all shadow-xl">
                            <div className="flex flex-col">
                                <span className="text-[8px] font-black text-neutral-500 uppercase tracking-widest">{pr.repo.split('/')[1]}</span>
                                <span className="text-sm font-bold text-white mt-1">{pr.label}</span>
                                <div className="flex items-center gap-2 mt-3">
                                    {pr.status === 'merged' ? (
                                        <div className="flex items-center gap-1.5 text-[10px] font-black text-purple-400 uppercase italic">
                                            <GitMerge className="w-3 h-3" /> Live / Merged
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-1.5 text-[10px] font-black text-amber-500 uppercase italic">
                                            <Activity className="w-3 h-3 animate-pulse" /> Pending Review
                                        </div>
                                    )}
                                </div>
                            </div>
                            <a 
                                href={pr.url} 
                                target="_blank" 
                                className="p-3 bg-white/5 rounded-xl opacity-0 group-hover:opacity-100 transition-all hover:bg-emerald-500/10 hover:text-emerald-400"
                            >
                                <ExternalLink className="w-4 h-4" />
                            </a>
                        </div>
                    ))}
                </div>
            </div>

            {/* Adoption Trend Chart */}
            <div className="space-y-6">
                <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-amber-500" />
                    <h2 className="text-xs font-black text-neutral-400 uppercase tracking-[0.3em]">Cross-Plugin Growth Trend (30D)</h2>
                </div>
                
                <Card className="bg-black border-white/5 overflow-hidden">
                    <CardHeader>
                        <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Standard vs Framework Traffic Split</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[400px] pt-4">
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
        </div>
    );
}

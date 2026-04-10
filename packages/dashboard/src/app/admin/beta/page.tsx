// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { 
    Users, 
    Zap, 
    Activity, 
    Shield, 
    Cpu, 
    Search,
    Filter,
    ArrowUpRight,
    CheckCircle2,
    Clock,
    UserCheck,
    AlertCircle
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { adminFetch } from "@/lib/admin-fetch";

export default function AdminBetaListPage() {
    const [leads, setLeads] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        async function fetchLeads() {
            setLoading(true);
            try {
                const res = await adminFetch('/api/admin/beta');
                if (res.ok) {
                    const data = await res.json();
                    setLeads(data.leads || []);
                }
            } catch (err) {
                console.error("Failed to load leads", err);
            }
            setLoading(false);
        }
        fetchLeads();
    }, []);

    const filteredLeads = leads.filter(lead => 
        lead.name.toLowerCase().includes(search.toLowerCase()) || 
        lead.surname.toLowerCase().includes(search.toLowerCase()) ||
        lead.email.toLowerCase().includes(search.toLowerCase()) ||
        lead.mainRisk.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <Zap className="w-12 h-12 text-emerald-500 animate-pulse" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in zoom-in-95 duration-700">
            <div className="flex justify-between items-end mb-8">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic heading-glow">Beta Waitlist Leads</h1>
                    <p className="text-neutral-500 text-xs font-black uppercase tracking-[0.2em]">Manage and qualify onboarding requests.</p>
                </div>
                <div className="flex gap-4">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 group-focus-within:text-emerald-500 transition-colors" />
                        <Input 
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Filter leads..."
                            className="bg-black border-white/10 h-10 pl-10 w-64 rounded-xl text-neutral-400 focus:border-emerald-500/50"
                        />
                    </div>
                </div>
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { label: "Total Leads", value: leads.length, icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
                    { label: "Qualified", value: leads.filter(l => l.isQualified).length, icon: UserCheck, color: "text-emerald-500", bg: "bg-emerald-500/10" },
                    { label: "High Risk Needs", value: leads.filter(l => l.isQualified && l.agentsCount !== "10+").length, icon: Shield, color: "text-amber-500", bg: "bg-amber-500/10" },
                    { label: "New Tech (Vercel/Llama)", value: leads.filter(l => ["Vercel AI", "LlamaIndex", "vercel-ai", "llamaindex"].includes(l.framework)).length, icon: Cpu, color: "text-purple-500", bg: "bg-purple-500/10" }
                ].map((stat, i) => (
                    <Card key={i} className="bg-[#080808] border-white/5 backdrop-blur-3xl p-6">
                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <p className="text-[9px] font-black text-neutral-500 uppercase tracking-[0.2em]">{stat.label}</p>
                                <p className="text-3xl font-black text-white italic tracking-tighter">{stat.value}</p>
                            </div>
                            <div className={`p-4 rounded-2xl ${stat.bg} border border-white/5`}>
                                <stat.icon className={`w-5 h-5 ${stat.color}`} />
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Leads Table */}
            <Card className="bg-black border-white/5 overflow-hidden">
                <CardHeader className="border-b border-white/[0.05] py-5 px-8">
                    <CardTitle className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em] flex items-center gap-2">
                        <Filter className="w-4 h-4 text-emerald-500" /> Active Intake Queue
                    </CardTitle>
                </CardHeader>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/[0.02]">
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5">Applicant</th>
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5">Tech Stack</th>
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5 text-center">Agents</th>
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5">Primary Concern</th>
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5">Qualification</th>
                                <th className="p-4 px-8 text-[10px] font-black uppercase tracking-widest text-neutral-500 border-b border-white/5 text-right">Applied</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {filteredLeads.map((lead) => (
                                <tr key={lead.id} className="group hover:bg-white/[0.01] transition-colors">
                                    <td className="p-6 px-8">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-black text-white italic uppercase tracking-tight">{lead.name} {lead.surname}</span>
                                            <span className="text-xs text-neutral-500 font-medium">{lead.email}</span>
                                        </div>
                                    </td>
                                    <td className="p-6 px-8">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                                            {lead.framework}
                                        </span>
                                    </td>
                                    <td className="p-6 px-8 text-center">
                                        <span className="text-lg font-black text-white italic">{lead.agentsCount}</span>
                                    </td>
                                    <td className="p-6 px-8">
                                        <p className="text-xs text-neutral-400 max-w-xs truncate" title={lead.mainRisk}>
                                            {lead.mainRisk}
                                        </p>
                                    </td>
                                    <td className="p-6 px-8">
                                        {lead.isQualified ? (
                                            <div className="flex items-center gap-2 text-emerald-400">
                                                <CheckCircle2 className="w-4 h-4" />
                                                <span className="text-[10px] font-black uppercase tracking-widest">Qualified</span>
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 text-neutral-600">
                                                <AlertCircle className="w-4 h-4" />
                                                <span className="text-[10px] font-black uppercase tracking-widest">Low Priority</span>
                                            </div>
                                        )}
                                    </td>
                                    <td className="p-6 px-8 text-right">
                                        <div className="flex flex-col items-end">
                                            <span className="text-xs text-neutral-400 font-bold uppercase tracking-widest">{new Date(lead.appliedAt).toLocaleDateString()}</span>
                                            <span className="text-[10px] text-neutral-600 font-black uppercase tracking-tighter italic flex items-center gap-1 group-hover:text-emerald-500 transition-colors cursor-pointer">
                                                Review <ArrowUpRight className="w-3 h-3" />
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {filteredLeads.length === 0 && (
                    <div className="p-20 text-center flex flex-col items-center gap-4">
                        <Clock className="w-12 h-12 text-neutral-800" />
                        <p className="text-neutral-500 font-black uppercase tracking-widest text-xs">Intake volume is currently zero.</p>
                    </div>
                )}
            </Card>
        </div>
    );
}

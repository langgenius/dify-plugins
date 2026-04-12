// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { collection, query, onSnapshot, doc, deleteDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Server, Search, Trash2, KeyRound } from "lucide-react";

export default function AdminAgentsPage() {
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const q = query(collection(db, "agents"));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            const rawAgents = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

            const enhancedAgents = rawAgents.map((a: any) => ({
                ...a,
                policyCount: a.policyCount ?? 0,
                logCount: a.logCount ?? 0,
                isActive: a.lastEvaluatedAt ? Date.now() - new Date(a.lastEvaluatedAt).getTime() < 86400000 : false,
                createdAt: a.createdAt || new Date().toISOString(),
            }));

            setAgents(enhancedAgents.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()));
            setLoading(false);
        }, (error) => {
            console.error("Firebase onSnapshot error:", error);
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    const deleteAgent = async (id: string, name: string) => {
        if (!window.confirm(`Are you sure you want to delete the agent "${name}"? This action cannot be undone.`)) return;
        try {
            await deleteDoc(doc(db, "agents", id));
        } catch (e) {
            console.error(e);
            alert("Failed to delete agent.");
        }
    };

    const filteredAgents = agents.filter((a) => {
        const nameMatch = a.name?.toLowerCase().includes(searchTerm.toLowerCase());
        const idMatch = a.id?.toLowerCase().includes(searchTerm.toLowerCase());
        const ownerMatch = a.userId?.toLowerCase().includes(searchTerm.toLowerCase());
        return nameMatch || idMatch || ownerMatch;
    });

    const formatKey = (key: string) => {
        if (!key) return "N/A";
        if (key.length <= 8) return key;
        return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`;
    };

    return (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-8">
                <div className="space-y-1">
                    <h1 className="text-3xl font-extrabold tracking-tight text-white drop-shadow-sm flex items-center gap-2">
                        <Server className="w-8 h-8 text-emerald-500" />
                        Agent Directory
                    </h1>
                    <p className="text-neutral-400 text-sm">Monitor and manage all AI agents connected to the platform.</p>
                </div>
            </div>

            <Card className="bg-[#0A0A0A] border-white/5">
                <CardHeader className="py-5 border-b border-white/5 flex flex-col sm:flex-row justify-between sm:items-center space-y-4 sm:space-y-0">
                    <CardTitle className="text-lg font-bold">Total Agents ({agents.length})</CardTitle>
                    <div className="relative w-full sm:w-72">
                        <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-500" />
                        <Input
                            placeholder="Search agents..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-black border-white/10 pl-9 text-sm focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-white placeholder:text-neutral-600"
                        />
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-neutral-400 uppercase bg-black/40 border-b border-white/5 tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-semibold">Agent Name</th>
                                    <th className="px-6 py-4 font-semibold">API Key</th>
                                    <th className="px-6 py-4 font-semibold">Owner UID</th>
                                    <th className="px-6 py-4 font-semibold">Status / Stats</th>
                                    <th className="px-6 py-4 font-semibold text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-neutral-500">
                                            Loading agents...
                                        </td>
                                    </tr>
                                ) : filteredAgents.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-12 text-center text-neutral-500">
                                            No agents found.
                                        </td>
                                    </tr>
                                ) : (
                                    filteredAgents.map((agent) => (
                                        <tr key={agent.id} className="hover:bg-white/[0.05] transition-colors group">
                                            <td className="px-6 py-4">
                                                <div className="font-medium text-white flex items-center gap-2">
                                                    {agent.name}
                                                    {Date.now() - agent.createdAt < 86400000 && (
                                                        <Badge className="bg-emerald-500/20 text-emerald-400 border-none text-[10px] px-1.5 py-0">NEW</Badge>
                                                    )}
                                                </div>
                                                <div className="text-xs text-neutral-500 mt-1">ID: {agent.id}</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center text-neutral-300 font-mono text-xs gap-2">
                                                    <KeyRound className="w-3 h-3 text-neutral-500" />
                                                    {formatKey(agent.apiKey)}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-neutral-300 font-mono text-xs">
                                                {agent.userId}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-4">
                                                    <div className="flex items-center gap-1.5">
                                                        <span className={`w-2 h-2 rounded-full ${agent.isActive ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                                                        <span className="text-xs text-neutral-400">{agent.isActive ? 'Active' : 'Inactive'}</span>
                                                    </div>
                                                    <div className="text-xs text-neutral-500 flex flex-col">
                                                        <span>{agent.policyCount} Policies</span>
                                                        <span>{agent.logCount} Logs (7d)</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="border border-white/10 hover:bg-rose-500/20 hover:text-rose-400 hover:border-rose-500/50 transition-all text-neutral-400"
                                                    onClick={() => deleteAgent(agent.id, agent.name)}
                                                >
                                                    <Trash2 className="w-4 h-4 mr-2" />
                                                    Delete
                                                </Button>
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

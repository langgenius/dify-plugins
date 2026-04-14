// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useEffect, useState } from "react";
import { collection, onSnapshot, doc, updateDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Users, Server, Search, Calendar, Activity, Ban, PlayCircle, Clock, ShieldCheck, AlertCircle } from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";

export default function AdminUsersPage() {
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedUser, setSelectedUser] = useState<any | null>(null);

    useEffect(() => {
        const unsubscribe = onSnapshot(
            collection(db, "users"),
            (snap) => {
                const raw = snap.docs.map(d => ({ id: d.id, ...d.data() }));
                setUsers(raw.sort((a: any, b: any) => (b.lastLogin || 0) - (a.lastLogin || 0)));
                setLoading(false);
                setError(null);
            },
            (err) => {
                console.error("Failed to load users:", err);
                setError('Failed to load users. Please refresh the page.');
                setLoading(false);
            }
        );
        return () => unsubscribe();
    }, []);

    const toggleBan = async (user: any) => {
        try {
            await updateDoc(doc(db, "users", user.id), { isBanned: !user.isBanned });
            setSelectedUser({ ...user, isBanned: !user.isBanned });
        } catch (e) {
            console.error(e);
        }
    };

    const filtered = users.filter(u => 
        u.email?.toLowerCase().includes(searchTerm.toLowerCase()) || 
        u.id?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-4">
                <div className="space-y-1">
                    <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-2 italic uppercase">
                        <Users className="w-8 h-8 text-emerald-500" /> User Directory
                    </h1>
                    <p className="text-neutral-500 text-sm font-medium italic uppercase tracking-widest">Platform identities and account management.</p>
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="text-sm font-medium">{error}</p>
                </div>
            )}

            <Card className="bg-[#080808] border-white/5 overflow-hidden">
                <CardHeader className="py-6 border-b border-white/5 flex flex-col sm:flex-row justify-between sm:items-center gap-4 bg-white/[0.01]">
                    <CardTitle className="text-sm font-black uppercase tracking-widest text-neutral-400">Registry — {users.length} Identities</CardTitle>
                    <div className="relative w-full sm:w-80">
                        <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-600" />
                        <Input
                            placeholder="SEARCH BY EMAIL OR UID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-black border-white/10 pl-10 text-xs font-black uppercase tracking-wider focus:border-emerald-500 transition-all text-white"
                        />
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-[10px] text-neutral-500 uppercase bg-white/[0.02] border-b border-white/5 tracking-[0.2em] font-black italic">
                                <tr>
                                    <th className="px-6 py-4">Identity</th>
                                    <th className="px-6 py-4 text-center">Status</th>
                                    <th className="px-6 py-4 text-center">Subscription</th>
                                    <th className="px-6 py-4 text-center">Last Pulse</th>
                                    <th className="px-6 py-4 text-right">Control</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {loading ? (
                                    <tr><td colSpan={5} className="py-20 text-center"><div className="animate-pulse text-emerald-500 font-black italic uppercase">Synchronizing...</div></td></tr>
                                ) : filtered.map((u) => (
                                    <tr key={u.id} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="font-black text-white italic text-base tracking-tight">{u.email}</span>
                                                <span className="text-[9px] text-neutral-600 font-mono tracking-tighter">ID: {u.id?.substring(0, 12)}...</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest ${
                                                u.isBanned ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                                            }`}>
                                                {u.isBanned ? 'Banned' : 'Authorized'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <span className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${
                                                u.isAdmin ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'bg-white/5 text-neutral-500'
                                            }`}>
                                                {u.isAdmin ? 'Enterprise Admin' : 'Standard Node'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5 text-center">
                                            <div className="flex flex-col items-center">
                                                <span className="text-[11px] font-black text-white italic uppercase">{u.lastLogin ? formatDistanceToNow(new Date(u.lastLogin), { addSuffix: true }) : "N/A"}</span>
                                                <span className="text-[9px] text-neutral-600 font-bold uppercase tracking-widest">Global Activity</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <button 
                                                onClick={() => setSelectedUser(u)}
                                                className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 text-[10px] font-black text-white uppercase tracking-[0.2em] rounded-xl transition-all"
                                            >
                                                Details
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
                <DialogContent className="sm:max-w-xl bg-[#0a0a0a] border-white/5 text-white shadow-3xl">
                    <DialogHeader>
                        <DialogTitle className="text-2xl font-black italic uppercase tracking-tight flex items-center gap-3">
                            {selectedUser?.email}
                        </DialogTitle>
                        <DialogDescription className="text-neutral-500 font-mono text-[10px] break-all">UID: {selectedUser?.id}</DialogDescription>
                    </DialogHeader>

                    <div className="grid grid-cols-2 gap-4 mt-6">
                        {[
                            { label: "Onboard Date", val: selectedUser?.createdAt ? format(new Date(selectedUser.createdAt), "MMM d, yyyy") : "N/A", icon: Calendar },
                            { label: "Last Pulse", val: selectedUser?.lastLogin ? format(new Date(selectedUser.lastLogin), "MMM d, h:mm a") : "N/A", icon: Clock },
                            { label: "Compliance Status", val: selectedUser?.isBanned ? "Flagged/Banned" : "Compliant", icon: ShieldCheck, color: selectedUser?.isBanned ? "text-rose-500" : "text-emerald-500" }
                        ].map((item, i) => (
                            <div key={i} className="bg-white/[0.02] border border-white/5 p-4 rounded-2xl flex items-center gap-4">
                                <div className="p-3 bg-white/5 rounded-xl"><item.icon className={`w-5 h-5 ${item.color || 'text-neutral-400'}`} /></div>
                                <div>
                                    <p className="text-[9px] font-black text-neutral-500 uppercase tracking-widest">{item.label}</p>
                                    <p className="font-bold text-white text-sm italic">{item.val}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex justify-end gap-3 pt-6 border-t border-white/5">
                        <Button
                            variant={selectedUser?.isBanned ? "default" : "destructive"}
                            className={`font-black uppercase tracking-widest text-[10px] px-8 py-6 rounded-2xl transition-all ${selectedUser?.isBanned ? 'bg-emerald-600 hover:bg-emerald-500' : ''}`}
                            onClick={() => toggleBan(selectedUser)}
                        >
                            {selectedUser?.isBanned ? "Authorized Node" : "Suspend Account"}
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}

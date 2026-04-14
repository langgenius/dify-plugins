// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";
import {
    Users,
    Mail,
    Trash2,
    Shield,
    ShieldCheck,
    UserPlus,
    Search,
    ExternalLink,
    Filter,
} from "lucide-react";
import { TierBanner } from "@/components/TierBanner";

interface TeamMember {
    id: string;
    user_email: string;
    role: "admin" | "auditor" | "viewer" | "member";
    status: "active" | "pending" | "removed";
    invited_at: string;
    accepted_at?: string;
}

export default function TeamPage() {
    const [user] = useAuthState(auth);
    const [members, setMembers] = useState<TeamMember[]>([]);
    const [loading, setLoading] = useState(true);
    const [isInviting, setIsInviting] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [inviteStatus, setInviteStatus] = useState<"idle" | "success" | "error">("idle");
    const [inviteEmail, setInviteEmail] = useState("");
    const [inviteRole, setInviteRole] = useState<string>("member");
    const [searchTerm, setSearchTerm] = useState("");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const fetchMembers = useCallback(async () => {
        if (!user) return;
        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/v1/members?tenantId=${user.uid}`, {
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (!res.ok) throw new Error("Failed to fetch members");
            const data = await res.json();
            setMembers(data);
        } catch (e) {
            console.error("Fetch members error:", e);
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        fetchMembers();
    }, [fetchMembers]);

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user || !inviteEmail || isSubmitting) return;

        setIsSubmitting(true);
        setInviteStatus("idle");
        setErrorMsg(null);

        try {
            const idToken = await user.getIdToken();
            const res = await fetch("/v1/members/invite", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    tenantId: user.uid,
                    email: inviteEmail,
                    role: inviteRole
                })
            });

            const data = await res.json();

            if (!res.ok) {
                setErrorMsg(data.message || data.error || "Invite failed");
                throw new Error("Invite failed");
            }

            setInviteStatus("success");
            setInviteEmail("");
            await fetchMembers();
            
            setTimeout(() => {
                setIsInviting(false);
                setInviteStatus("idle");
                setIsSubmitting(false);
            }, 1800);

        } catch (error) {
            setInviteStatus("error");
            setIsSubmitting(false);
        }
    };

    const removeMember = async (memberId: string) => {
        if (!user) return;
        if (!confirm("Are you sure you want to remove this team member? This will immediately revoke their access.")) return;

        try {
            const idToken = await user.getIdToken();
            const res = await fetch(`/v1/members/${memberId}?tenantId=${user.uid}`, {
                method: "DELETE",
                headers: { 'Authorization': `Bearer ${idToken}` }
            });
            if (res.ok) {
                await fetchMembers();
            }
        } catch (error) {
            console.error("Error removing member:", error);
        }
    };

    const filteredMembers = members.filter(m =>
        m.user_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.role.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return <div className="p-10 animate-pulse bg-neutral-900/20 rounded-3xl h-[600px]" />;
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-2">
                    <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase tracking-widest mb-2 italic">
                        <Users className="w-3.5 h-3.5" />
                        <span>Workforce Governance</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white italic uppercase">
                        Team <span className="text-neutral-500 not-italic font-black">Management</span>
                    </h1>
                </div>
                <button
                    onClick={() => {
                        setInviteStatus("idle");
                        setIsInviting(true);
                    }}
                    className="group bg-white text-black hover:bg-emerald-400 px-8 py-4 rounded-xl font-black uppercase tracking-tighter transition-all duration-300 flex items-center shadow-2xl"
                >
                    <UserPlus className="w-5 h-5 mr-3" />
                    Invite Member
                </button>
            </div>

            {/* Tier Governance Banner */}
            <TierBanner 
                tier="open_source" 
                usages={[{ current: members.length, max: 1, label: "Seats", upgradeFeature: "Add up to 5 seats on Developer" }]} 
            />

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: "Total Members", value: members.length, icon: Users, color: "emerald" },
                    { label: "Pending Invites", value: members.filter(m => m.status === "pending").length, icon: Mail, color: "violet" },
                    { label: "Admins", value: members.filter(m => m.role === "admin").length, icon: ShieldCheck, color: "blue" },
                ].map((stat, i) => (
                    <div key={i} className="bg-neutral-900/40 border border-white/10 p-6 rounded-3xl">
                        <div className="flex items-center justify-between mb-4">
                            <div className={`p-3 rounded-2xl bg-${stat.color}-500/10 text-${stat.color}-400`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                            <span className="text-3xl font-bold text-white tracking-tighter tabular-nums">{stat.value}</span>
                        </div>
                        <p className="text-neutral-400 font-medium text-xs uppercase tracking-widest">{stat.label}</p>
                    </div>
                ))}
            </div>

            {/* Main Content Area */}
            <div className="bg-neutral-950 border border-white/10 rounded-3xl overflow-hidden shadow-2xl relative">
                <div className="p-6 border-b border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-neutral-900/20">
                    <div className="relative flex-1 max-w-md group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within:text-emerald-400 transition-colors" />
                        <input
                            type="text"
                            placeholder="Search by email..."
                            className="w-full bg-black border border-white/[0.1] rounded-xl py-3 pl-12 pr-4 text-sm text-white focus:outline-none"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-neutral-900/40 text-neutral-400 text-[10px] font-black uppercase tracking-widest">
                                <th className="px-8 py-5 italic">Operator</th>
                                <th className="px-8 py-5 italic">Role</th>
                                <th className="px-8 py-5 italic">Status</th>
                                <th className="px-8 py-5 text-right italic">Decommission</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {filteredMembers.map((member) => (
                                <tr key={member.id} className="group hover:bg-white/[0.01] transition-colors">
                                    <td className="px-8 py-6">
                                        <div className="flex items-center">
                                            <div className="w-10 h-10 rounded-full bg-neutral-800 border border-white/[0.1] flex items-center justify-center text-emerald-400 font-bold text-sm mr-4 shadow-inner">
                                                {member.user_email[0].toUpperCase()}
                                            </div>
                                            <div>
                                                <p className="text-sm font-semibold text-white tracking-tight">{member.user_email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex items-center">
                                            {member.role === "admin" ? (
                                                <ShieldCheck className="w-4 h-4 text-emerald-400 mr-2" />
                                            ) : (
                                                <Shield className="w-4 h-4 text-neutral-400 mr-2" />
                                            )}
                                            <span className={`text-[10px] font-black uppercase tracking-widest ${member.role === 'admin' ? 'text-white' : 'text-neutral-500'}`}>
                                                {member.role}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${member.status === 'active'
                                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                                : 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                                            }`}>
                                            {member.status}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <button
                                            onClick={() => removeMember(member.id)}
                                            className="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Invite Modal */}
            {isInviting && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-3xl bg-black/80 animate-in fade-in duration-300">
                    <div className="bg-neutral-950 border border-white/[0.1] w-full max-w-md rounded-[40px] overflow-hidden shadow-2xl slide-in-from-bottom-12 animate-in duration-500">
                        <div className="p-10 border-b border-white/5 bg-gradient-to-br from-neutral-900 to-black relative">
                            {inviteStatus === "success" && (
                                <div className="absolute inset-0 bg-emerald-500/95 flex flex-col items-center justify-center z-20 animate-in fade-in zoom-in duration-300">
                                    <ShieldCheck className="w-16 h-16 text-black mb-4" />
                                    <h4 className="text-2xl font-black text-black uppercase tracking-tighter italic">Invite Sent</h4>
                                </div>
                            )}
                            
                            {inviteStatus === "error" && (
                                <div className="absolute inset-0 bg-red-500/95 flex flex-col items-center justify-center z-20 animate-in fade-in zoom-in duration-300">
                                    <Trash2 className="w-16 h-16 text-black mb-4" />
                                    <h4 className="text-2xl font-black text-black uppercase tracking-tighter italic">Process Terminated</h4>
                                    <p className="text-black/80 font-bold uppercase tracking-widest text-[9px] mt-2 italic px-8 text-center">{errorMsg}</p>
                                    <button onClick={() => setInviteStatus("idle")} className="mt-6 px-4 py-2 bg-black text-white rounded-lg text-[10px] font-black uppercase italic">Retry</button>
                                </div>
                            )}

                            <h3 className="text-3xl font-black text-white mb-2 italic tracking-tighter uppercase text-center">Identity <span className="text-emerald-500 not-italic">Enrollment</span></h3>
                        </div>
                        <form onSubmit={handleInvite} className="p-10 space-y-8">
                            <div className="space-y-3">
                                <label className="text-[9px] font-black text-neutral-500 uppercase tracking-[0.2em] italic">Operator Email</label>
                                <input
                                    type="email"
                                    required
                                    disabled={isSubmitting}
                                    className="w-full bg-black border border-white/[0.1] rounded-2xl py-5 px-6 text-white font-medium placeholder:text-neutral-800 focus:outline-none focus:border-emerald-500/30 transition-all"
                                    placeholder="operator@system.io"
                                    value={inviteEmail}
                                    onChange={(e) => setInviteEmail(e.target.value)}
                                />
                            </div>

                            <div className="space-y-3">
                                <label className="text-[9px] font-black text-neutral-500 uppercase tracking-[0.2em] italic">Access Role</label>
                                <select 
                                    value={inviteRole}
                                    onChange={(e) => setInviteRole(e.target.value)}
                                    className="w-full bg-black border border-white/[0.1] rounded-2xl py-5 px-6 text-white text-[10px] font-black uppercase tracking-widest italic"
                                >
                                    <option value="member">Network Member</option>
                                    <option value="auditor">Security Auditor</option>
                                    <option value="admin">System Admin</option>
                                </select>
                            </div>

                            <div className="flex gap-4 pt-6">
                                <button type="button" onClick={() => setIsInviting(false)} className="flex-1 py-5 text-[10px] font-black text-neutral-600 uppercase tracking-widest transition-colors italic">Cancel</button>
                                <button type="submit" disabled={isSubmitting} className="flex-2 bg-emerald-500 text-black py-5 px-10 rounded-2xl font-black uppercase tracking-widest italic text-[10px] shadow-2xl active:scale-95 disabled:opacity-50 min-w-[160px]">
                                    {isSubmitting ? "Processing..." : "Dispatch Invite"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

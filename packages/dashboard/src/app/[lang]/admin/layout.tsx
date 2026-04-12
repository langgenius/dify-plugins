// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useAuthState } from "react-firebase-hooks/auth";
import { auth, db } from "@/lib/firebase";
import { doc, setDoc } from "firebase/firestore";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import {
    Shield,
    BrickWall,
    Users,
    Activity,
    Settings,
    Database,
    Server,
    BarChart2,
    CheckSquare,
    Brain,
    Layout,
    ListOrdered,
    DollarSign,
    Filter,
    Share2
} from "lucide-react";
import { isAdminEmail } from "@/lib/auth-config";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const [user, loading] = useAuthState(auth);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!loading) {
            if (!user) {
                router.push("/login");
            } else if (!isAdminEmail(user.email)) {
                // Not an admin, redirect to normal dashboard
                router.push("/dashboard");
            } else {
                // Register admin in Firestore so they appear in standard tables
                setDoc(doc(db, "users", user.uid), {
                    email: user.email,
                    createdAt: user.metadata?.creationTime || new Date().toISOString(),
                    lastLogin: new Date().toISOString(),
                    isAdmin: true
                }, { merge: true }).catch(console.error);
            }
        }
    }, [user, loading, router]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-white">
                <div className="flex flex-col items-center gap-4">
                    <BrickWall className="w-12 h-12 text-emerald-500 animate-pulse" />
                    <p className="text-xl font-semibold italic text-neutral-400">Initializing Admin Session...</p>
                </div>
            </div>
        );
    }

    if (!user || !isAdminEmail(user.email)) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-white p-6">
                <div className="max-w-md w-full bg-neutral-950 border border-white/10 rounded-2xl p-8 text-center shadow-2xl">
                    <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Shield className="w-8 h-8 text-red-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
                    <p className="text-neutral-400 mb-8">
                        This area is restricted to SupraWall administrators. 
                        Your activity has been logged for security purposes.
                    </p>
                    <Link 
                        href="/dashboard" 
                        className="inline-flex items-center px-6 py-3 bg-white text-black font-semibold rounded-lg hover:bg-neutral-200 transition-colors"
                    >
                        Return to Personal Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    const navItems = [
        { name: "Overview", href: "/admin", icon: BarChart2 },
        { name: "Revenue", href: "/admin/revenue", icon: DollarSign },
        { name: "Funnel", href: "/admin/funnel", icon: Filter },
        { name: "Traffic", href: "/admin/analytics", icon: Activity },
        { name: "Ecosystem Hub", href: "/admin/ecosystem", icon: Share2 },
        { name: "Users", href: "/admin/users", icon: Users },
        { name: "Agents", href: "/admin/agents", icon: Server },
        { name: "Audit Logs", href: "/admin/audit", icon: Database },
        { name: "Task Review", href: "/admin/tasks", icon: CheckSquare },
        { name: "Intelligence", href: "/admin/intelligence", icon: Brain },
        { name: "Published", href: "/admin/published", icon: Layout },
        { name: "Queue", href: "/admin/queue", icon: ListOrdered },
        { name: "Settings", href: "/admin/settings", icon: Settings },
        { name: "Beta List", href: "/admin/beta", icon: ListOrdered },
    ];

    return (
        <div className="flex h-screen bg-[#050505] text-white overflow-hidden relative font-sans">
            {/* Admin Header / Sidebar */}
            <aside className="w-64 border-r border-white/5 bg-neutral-950 flex flex-col z-20">
                <div className="h-16 flex items-center px-6 border-b border-white/5 bg-black/40">
                    <BrickWall className="w-6 h-6 text-red-500 mr-3" />
                    <span className="font-bold text-lg tracking-tight text-white drop-shadow-sm flex items-center gap-2">
                        SupraWall <span className="bg-red-500/20 text-red-400 text-[10px] px-2 py-0.5 rounded-full uppercase font-bold tracking-wider">Admin</span>
                    </span>
                </div>

                <nav className="flex-1 py-4 flex flex-col gap-1 overflow-y-auto">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`group flex items-center px-6 py-3 mx-2 rounded-lg transition-all duration-300 ${isActive ? "bg-white/[0.08] text-white shadow-sm ring-1 ring-white/10" : "text-neutral-400 hover:text-white hover:bg-white/[0.04]"
                                    }`}
                            >
                                <Icon className={`w-4 h-4 mr-3 transition-transform duration-300 ${isActive ? "scale-110 text-emerald-400" : "group-hover:scale-110 group-hover:text-neutral-200"}`} />
                                <span className={`text-sm font-medium transition-colors ${isActive ? "text-white" : "group-hover:text-white"}`}>{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-white/5 bg-black/40">
                    <Link href="/dashboard" className="w-full text-center text-sm text-neutral-400 hover:text-white transition-colors block py-2 border border-white/10 rounded-md hover:bg-white/5">
                        Exit Admin Panel
                    </Link>
                </div>
            </aside>

            <main className="flex-1 overflow-y-auto relative z-10 scroll-smooth">
                <div className="p-8 max-w-7xl mx-auto min-h-full">
                    {children}
                </div>
            </main>
        </div>
    );
}

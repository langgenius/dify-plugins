// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import {
    Shield,
    ArrowRight,
    Zap,
    CheckCircle2,
    ChevronRight,
    Loader2,
    Users,
    Activity,
    Lock,
    Cpu,
    Network,
    Github,
    BookOpen,
    MessageCircle
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function BetaLandingPage() {
    const params = useParams();
    const lang = (params?.lang as string) || 'en';

    const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState<string>("");
    const [formData, setFormData] = useState({
        name: "",
        surname: "",
        email: "",
        framework: "langchain",
        agentsCount: "",
        mainRisk: ""
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("submitting");
        setErrorMessage("");

        // QA-007: trim email before sending
        const payload = { ...formData, email: formData.email.trim() };

        try {
            const res = await fetch("/api/waitlist", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setStatus("success");
            } else {
                // QA-006: surface the actual error from the server
                let msg = "Submission failed. Please try again.";
                try {
                    const data = await res.json();
                    if (data?.error) msg = data.error;
                } catch {}
                setErrorMessage(msg);
                setStatus("error");
            }
        } catch (err) {
            setErrorMessage("Connection failed. Please check your network and try again.");
            setStatus("error");
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen bg-[#000000] text-neutral-200 font-sans selection:bg-emerald-500/30">
            <Navbar />

            <main className="relative pt-32 pb-32 px-6 overflow-hidden">
                {/* Background Decor — orbs capped to viewport width so they don't overflow on mobile */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[min(1200px,80vw)] h-[800px] bg-emerald-600/10 blur-[180px] rounded-full -translate-y-1/2" />
                    <div className="absolute bottom-0 right-0 w-[min(600px,60vw)] h-[min(600px,60vw)] bg-blue-600/5 blur-[150px] rounded-full translate-x-1/3 translate-y-1/3" />
                </div>

                <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center relative z-10">
                    {/* Content Column */}
                    <div className="space-y-12">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="inline-flex items-center px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-[10px] font-black tracking-[0.2em] text-emerald-400 uppercase"
                        >
                            <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 mr-3 animate-pulse"></span>
                            Private Beta Access
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="space-y-6"
                        >
                            <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white leading-[0.85] uppercase italic text-glow">
                                The <span className="text-emerald-500">Waitlist</span> <br />
                                Is Open.
                            </h1>
                            <p className="text-2xl text-neutral-400 font-medium leading-relaxed italic max-w-xl">
                                We are onboarding design partners in small batches to ensure each team has direct support from our founding engineers.
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6"
                        >
                            {[
                                { title: "Free Team Tier", desc: "$79/mo value during beta", icon: Zap },
                                { title: "Roadmap Input", desc: "Influence core features", icon: Activity },
                                { title: "Direct Support", desc: "Line to founders", icon: Users },
                                { title: "Priority Onboarding", desc: "Skip the public line", icon: ArrowRight }
                            ].map((item, i) => (
                                <div key={i} className="flex gap-4 p-6 rounded-3xl bg-white/[0.03] border border-white/5 hover:border-emerald-500/20 transition-all group">
                                    <div className="p-3 rounded-2xl bg-white/5 text-emerald-500 group-hover:scale-110 transition-transform">
                                        <item.icon className="w-5 h-5" />
                                    </div>
                                    <div className="space-y-1">
                                        <h3 className="font-black text-white text-xs uppercase tracking-widest leading-none">{item.title}</h3>
                                        <p className="text-[10px] text-neutral-500 font-bold uppercase tracking-wider">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </motion.div>
                    </div>

                    {/* Form Column */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="relative"
                    >
                        <div className="absolute inset-0 bg-emerald-500/10 blur-[100px] rounded-full opacity-50" />

                        <div className="bg-[#080808] border border-white/10 rounded-[3.5rem] p-10 md:p-14 shadow-2xl backdrop-blur-3xl relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent" />

                            <AnimatePresence mode="wait">
                                {status === "success" ? (
                                    // QA-020: Post-submit "What's next" card — no more dead end
                                    <motion.div
                                        key="success"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="h-full flex flex-col items-center text-center space-y-8 py-10"
                                    >
                                        <div className="w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                                            <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                                        </div>
                                        <div className="space-y-3">
                                            <h2 className="text-3xl font-black italic uppercase text-white tracking-tighter">You&apos;re on the list.</h2>
                                            <p className="text-neutral-400 font-medium text-sm max-w-xs mx-auto">An engineer will reach out to schedule your onboarding. While you wait:</p>
                                        </div>

                                        <div className="w-full space-y-3 text-left">
                                            <Link
                                                href={`/${lang}/docs`}
                                                className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-all group"
                                            >
                                                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition-transform">
                                                    <BookOpen className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="text-white font-black text-xs uppercase tracking-widest">Read the Docs</p>
                                                    <p className="text-neutral-500 text-[10px] mt-0.5">SDK guides, API reference, quickstart</p>
                                                </div>
                                                <ArrowRight className="w-4 h-4 text-neutral-600 ml-auto group-hover:text-emerald-400 transition-colors" />
                                            </Link>

                                            <a
                                                href="https://github.com/wiserautomation/SupraWall"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition-all group"
                                            >
                                                <div className="p-2.5 rounded-xl bg-white/5 text-neutral-300 group-hover:scale-110 transition-transform">
                                                    <Github className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="text-white font-black text-xs uppercase tracking-widest">Self-Host Now</p>
                                                    <p className="text-neutral-500 text-[10px] mt-0.5">docker compose up — runs in 30 seconds</p>
                                                </div>
                                                <ArrowRight className="w-4 h-4 text-neutral-600 ml-auto group-hover:text-white transition-colors" />
                                            </a>

                                            <a
                                                href="https://discord.gg/suprawall"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-indigo-500/30 transition-all group"
                                            >
                                                <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform">
                                                    <MessageCircle className="w-4 h-4" />
                                                </div>
                                                <div>
                                                    <p className="text-white font-black text-xs uppercase tracking-widest">Join Discord</p>
                                                    <p className="text-neutral-500 text-[10px] mt-0.5">Chat with the team and other beta testers</p>
                                                </div>
                                                <ArrowRight className="w-4 h-4 text-neutral-600 ml-auto group-hover:text-indigo-400 transition-colors" />
                                            </a>
                                        </div>

                                        <Button
                                            onClick={() => { setStatus("idle"); setErrorMessage(""); }}
                                            className="bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest text-xs px-8 py-4 rounded-xl border border-white/10"
                                        >
                                            Submit Another Request
                                        </Button>
                                    </motion.div>
                                ) : (
                                    <motion.form
                                        key="form"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        onSubmit={handleSubmit}
                                        className="space-y-8"
                                    >
                                        <div className="space-y-2">
                                            <h2 className="text-3xl font-black italic uppercase text-white tracking-tighter">Onboarding Request</h2>
                                            <p className="text-neutral-500 text-[10px] font-black uppercase tracking-[0.2em]">All fields are mandatory for qualification.</p>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">First Name</label>
                                                <Input
                                                    name="name"
                                                    value={formData.name}
                                                    onChange={handleChange}
                                                    required
                                                    className="h-14 bg-black border-white/10 focus:border-emerald-500/50 text-white rounded-xl font-bold"
                                                    placeholder="Alex"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Surname</label>
                                                <Input
                                                    name="surname"
                                                    value={formData.surname}
                                                    onChange={handleChange}
                                                    required
                                                    className="h-14 bg-black border-white/10 focus:border-emerald-500/50 text-white rounded-xl font-bold"
                                                    placeholder="Operator"
                                                />
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">Professional Email</label>
                                            <Input
                                                name="email"
                                                type="email"
                                                value={formData.email}
                                                onChange={handleChange}
                                                required
                                                className="h-14 bg-black border-white/10 focus:border-emerald-500/50 text-white rounded-xl font-bold"
                                                placeholder="alex@company.com"
                                            />
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">What framework are you using?</label>
                                                <select
                                                    name="framework"
                                                    value={formData.framework}
                                                    onChange={handleChange}
                                                    className="flex h-14 w-full rounded-xl border border-white/10 bg-black px-3 py-2 text-sm font-bold text-white focus:outline-none focus:ring-1 focus:ring-emerald-500/50 appearance-none"
                                                >
                                                    <option value="LangChain">LangChain</option>
                                                    <option value="CrewAI">CrewAI</option>
                                                    <option value="AutoGen">AutoGen</option>
                                                    <option value="Vercel AI">Vercel AI SDK</option>
                                                    <option value="Other">Other / Custom</option>
                                                </select>
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">AI agents in production?</label>
                                                <select
                                                    name="agentsCount"
                                                    value={formData.agentsCount}
                                                    onChange={handleChange}
                                                    className="flex h-14 w-full rounded-xl border border-white/10 bg-black px-3 py-2 text-sm font-bold text-white focus:outline-none focus:ring-1 focus:ring-emerald-500/50 appearance-none"
                                                >
                                                    <option value="">Select count...</option>
                                                    <option value="1–3">1–3</option>
                                                    <option value="4–10">4–10</option>
                                                    <option value="10+">10+</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 ml-1">One sentence: what&apos;s the main risk you&apos;re trying to control?</label>
                                            <textarea
                                                name="mainRisk"
                                                value={formData.mainRisk}
                                                onChange={handleChange}
                                                required
                                                className="w-full min-h-[120px] bg-black border border-white/10 focus:border-emerald-500/50 text-white rounded-xl font-bold p-4 focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
                                                placeholder="e.g. Preventing unauthorized database access or cost runs..."
                                            />
                                        </div>

                                        {status === "error" && (
                                            <p className="text-rose-500 text-xs font-black uppercase tracking-widest text-center">
                                                {errorMessage || "Connection failed. Please try again."}
                                            </p>
                                        )}

                                        <Button
                                            disabled={status === "submitting"}
                                            className="w-full h-16 bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-[0.1em] text-lg rounded-2xl transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-3 active:scale-[0.98]"
                                        >
                                            {status === "submitting" ? (
                                                <Loader2 className="w-6 h-6 animate-spin text-white" />
                                            ) : (
                                                <>Request Access <ArrowRight className="w-5 h-5" /></>
                                            )}
                                        </Button>
                                    </motion.form>
                                )}
                            </AnimatePresence>
                        </div>
                    </motion.div>
                </div>
            </main>

            <Footer />
        </div>
    );
}

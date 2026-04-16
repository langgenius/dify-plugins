// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
    DollarSign,
    AlertTriangle,
    CheckCircle2,
    ChevronDown,
    ArrowRight,
    Zap,
    RefreshCw,
    TrendingDown,
    Shield,
    Clock,
    Copy,
    Check,
    Activity,
} from "lucide-react";

// ── Count-up hook ──
function useCountUp(target: number, duration = 2000, startOnMount = false) {
    const [count, setCount] = useState(0);
    const [started, setStarted] = useState(startOnMount);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!started) return;
        const startTime = performance.now();
        const step = (now: number) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3);
            setCount(Math.floor(ease * target));
            if (progress < 1) requestAnimationFrame(step);
            else setCount(target);
        };
        requestAnimationFrame(step);
    }, [started, target, duration]);

    useEffect(() => {
        if (startOnMount) return;
        const observer = new IntersectionObserver(
            ([entry]) => { if (entry.isIntersecting) setStarted(true); },
            { threshold: 0.3 }
        );
        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [startOnMount]);

    return { count, ref };
}

// ── Runaway cost ticker ──
function CostTicker() {
    const [amount, setAmount] = useState(0.02);
    const [blocked, setBlocked] = useState(false);
    const [phase, setPhase] = useState<"running" | "blocked">("running");

    useEffect(() => {
        if (phase === "blocked") return;
        const values = [0.02, 0.34, 2.10, 18.50, 147.20, 892.40, 2341.80, 4127.60];
        let idx = 0;
        const interval = setInterval(() => {
            idx++;
            if (idx < values.length) {
                setAmount(values[idx]);
            } else {
                clearInterval(interval);
                setTimeout(() => {
                    setPhase("blocked");
                    setBlocked(true);
                    setTimeout(() => {
                        setPhase("running");
                        setBlocked(false);
                        setAmount(0.02);
                        idx = 0;
                    }, 3000);
                }, 600);
            }
        }, 500);
        return () => clearInterval(interval);
    }, [phase]);

    return (
        <div className="relative bg-neutral-900 border border-white/10 rounded-[2rem] p-8 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-rose-500/5 to-transparent pointer-events-none" />
            <div className="flex items-center gap-2 mb-6">
                <div className="w-3 h-3 rounded-full bg-rose-500 animate-pulse" />
                <div className="w-3 h-3 rounded-full bg-amber-500/40" />
                <div className="w-3 h-3 rounded-full bg-neutral-700" />
                <span className="ml-2 text-[10px] font-mono text-neutral-500 uppercase tracking-widest">Agent Spend Monitor</span>
            </div>

            <div className="space-y-3">
                <div className="flex items-baseline gap-3">
                    <span className={`text-6xl font-black font-mono transition-all duration-300 ${blocked ? "text-emerald-500" : amount > 100 ? "text-rose-400" : amount > 10 ? "text-amber-400" : "text-white"}`}>
                        ${amount.toFixed(2)}
                    </span>
                    {!blocked && <span className="text-neutral-500 text-sm font-mono">accrued</span>}
                </div>

                {!blocked ? (
                    <div className="space-y-2">
                        <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{
                                    width: `${Math.min((amount / 4127.60) * 100, 100)}%`,
                                    background: amount > 1000 ? "#ef4444" : amount > 100 ? "#f59e0b" : "#10b981",
                                }}
                            />
                        </div>
                        <p className="text-xs font-mono text-neutral-600">
                            {amount < 10 ? "🟢 Within budget" : amount < 100 ? "🟡 Warning: spending accelerating" : "🔴 Runaway loop detected..."}
                        </p>
                    </div>
                ) : (
                    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-4 py-3 space-y-1">
                        <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4 text-emerald-500" />
                            <span className="text-emerald-400 font-black text-sm uppercase tracking-wider">SupraWall: Blocked at $10.00</span>
                        </div>
                        <p className="text-emerald-300/60 font-mono text-xs">Saved: $4,117.60 · Audit log written · Team notified</p>
                    </div>
                )}
            </div>
        </div>
    );
}

// ── Cost Calculator ──
function CostCalculator() {
    const [agents, setAgents] = useState(5);
    const [callsPerDay, setCallsPerDay] = useState(500);
    const [tokensPerCall, setTokensPerCall] = useState(5000);
    const [model, setModel] = useState("gpt-4o");

    const RATES: Record<string, number> = {
        "gpt-4o": 0.005,
        "claude-sonnet": 0.003,
        "claude-opus": 0.015,
        "gpt-4o-mini": 0.00015,
        "llama-3": 0.0001,
    };

    const rate = RATES[model] ?? 0.005;
    const dailyCostPerAgent = (callsPerDay * tokensPerCall / 1000) * rate;
    const monthlyUnlimited = dailyCostPerAgent * agents * 30;
    const monthlyWithCap = Math.min(dailyCostPerAgent, 10) * agents * 30;
    const savings = monthlyUnlimited - monthlyWithCap;
    const worstCase = callsPerDay * 10 * tokensPerCall * 10 / 1000 * rate; // 10x loop for 10 min

    const fmt = (n: number) => n >= 1000 ? `$${(n / 1000).toFixed(1)}K` : `$${n.toFixed(0)}`;

    return (
        <div id="cost-calculator" className="bg-neutral-900 border border-white/5 rounded-[2.5rem] p-10 space-y-8">
            <div className="text-center space-y-2">
                <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Interactive Calculator</p>
                <h3 className="text-3xl font-black tracking-tight text-white italic">What Does an Uncontrolled Agent Really Cost?</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <label className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Number of Agents</label>
                            <span className="text-emerald-400 font-black text-sm">{agents}</span>
                        </div>
                        <input type="range" min={1} max={100} value={agents} onChange={e => setAgents(+e.target.value)}
                            className="w-full accent-emerald-500 h-2" />
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <label className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Tool Calls / Agent / Day</label>
                            <span className="text-emerald-400 font-black text-sm">{callsPerDay.toLocaleString()}</span>
                        </div>
                        <input type="range" min={10} max={10000} step={10} value={callsPerDay} onChange={e => setCallsPerDay(+e.target.value)}
                            className="w-full accent-emerald-500 h-2" />
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <label className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Avg Tokens / Call</label>
                            <span className="text-emerald-400 font-black text-sm">{tokensPerCall.toLocaleString()}</span>
                        </div>
                        <input type="range" min={500} max={50000} step={500} value={tokensPerCall} onChange={e => setTokensPerCall(+e.target.value)}
                            className="w-full accent-emerald-500 h-2" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-neutral-500 uppercase tracking-widest block">Model</label>
                        <select value={model} onChange={e => setModel(e.target.value)}
                            className="w-full bg-neutral-800 border border-white/10 text-white rounded-xl px-4 py-3 text-sm">
                            <option value="gpt-4o">GPT-4o</option>
                            <option value="claude-sonnet">Claude Sonnet</option>
                            <option value="claude-opus">Claude Opus</option>
                            <option value="gpt-4o-mini">GPT-4o Mini</option>
                            <option value="llama-3">Llama 3</option>
                        </select>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-6 space-y-2">
                        <p className="text-[10px] font-black text-rose-400 uppercase tracking-widest">Monthly Cost WITHOUT Limits</p>
                        <p className="text-4xl font-black text-rose-400">{fmt(monthlyUnlimited)}</p>
                        <p className="text-xs text-rose-300/60">Assuming agents run uncapped</p>
                    </div>
                    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 space-y-2">
                        <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Monthly Cost WITH $10/day Cap</p>
                        <p className="text-4xl font-black text-emerald-400">{fmt(monthlyWithCap)}</p>
                        <p className="text-xs text-emerald-300/60">Savings: {fmt(savings)}/month</p>
                    </div>
                    <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-6 space-y-2">
                        <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest">Worst-Case Incident (1 Loop)</p>
                        <p className="text-4xl font-black text-amber-400">{fmt(worstCase)}</p>
                        <p className="text-xs text-amber-300/60">Infinite loop for 10 minutes</p>
                    </div>
                </div>
            </div>

            <div className="text-center pt-4">
                <Link href={`/${lang}/beta`} className="inline-flex items-center gap-2 px-10 py-5 bg-emerald-600 text-white font-black uppercase tracking-widest rounded-2xl hover:bg-emerald-500 transition-all">
                    Protect This Budget Now <ArrowRight className="w-4 h-4" />
                </Link>
            </div>
        </div>
    );
}

const INCIDENTS = [
    {
        title: "Recursive Research Agent",
        framework: "LangChain",
        color: "rose",
        cost: "$3,800",
        time: "4 hours to detect",
        desc: "A LangChain agent tasked with market research entered an infinite search-summarize-search loop at 3AM. By 7AM it had consumed 47 million tokens across 12,000 API calls.",
        calls: "12,000 API calls",
    },
    {
        title: "The Helpful Emailer",
        framework: "CrewAI",
        color: "amber",
        cost: "$450",
        time: "20 minutes",
        desc: "A CrewAI agent hallucinated that it needed to send follow-up emails to every contact in the database. It called the email API 2,400 times before the team noticed.",
        calls: "2,400 email calls",
    },
    {
        title: "Parallel Database Drain",
        framework: "AutoGen",
        color: "rose",
        cost: "$1,800",
        time: "45 minutes",
        desc: "An AutoGen multi-agent swarm spawned 8 sub-agents that each ran the same expensive aggregation query in parallel, repeatedly.",
        calls: "8 agents × repeated queries",
    },
];

const COMPARISON_ROWS = [
    { cap: "Hard dollar cap per agent", sw: true, api: false, diy: "partial", port: true },
    { cap: "Infinite loop circuit breaker", sw: true, api: false, diy: false, port: false },
    { cap: "Per-session token limits", sw: true, api: false, diy: "partial", port: true },
    { cap: "Works at SDK level (not gateway)", sw: true, api: false, diy: true, port: false },
    { cap: "Agent self-correction on budget hit", sw: true, api: false, diy: false, port: "partial" },
    { cap: "EU AI Act compliant logging", sw: true, api: false, diy: false, port: false },
    { cap: "Combined with vault + tool interception", sw: true, api: false, diy: false, port: false },
    { cap: "Latency overhead", sw: "1.2ms", api: "N/A", diy: "5-20ms", port: "10-50ms" },
];

const FAQS = [
    { q: "How do SupraWall budget limits work?", a: "You set a dollar or token cap (e.g., $10/day per agent). SupraWall tracks every tool call's token consumption in real time. When the cap is reached, all further API executions are deterministically blocked — no exceptions, no overrides." },
    { q: "Can I set different budgets for different agents?", a: "Yes. Each agent gets its own budget scope. Your billing-bot might get $50/day while your research-agent gets $5/day. Team-level and organization-level caps are also supported." },
    { q: "What happens when an agent hits its budget?", a: "SupraWall returns a structured BudgetExceeded error to the agent, which forces it to self-correct or halt gracefully. You receive a webhook notification. The agent cannot circumvent the cap." },
    { q: "How does infinite loop detection work?", a: "SupraWall analyzes tool call patterns in real time. If it detects N identical or near-identical calls within a time window (configurable), it triggers the circuit breaker and halts the agent. Default: 10 identical calls in 60 seconds." },
    { q: "Does this work with streaming APIs and extended thinking?", a: "Yes. Token counting works with streaming responses, extended thinking windows (Claude), and multi-turn conversations. Both input and output tokens are tracked." },
    { q: "Can budget limits help with EU AI Act compliance?", a: "Yes. Budget enforcement is part of your risk management system (Article 9). SupraWall logs every budget decision for audit export, demonstrating you have systematic controls over AI agent resource consumption." },
];

const CODE = `import { secure_agent } from "suprawall";

const secured = secure_agent(myAgent, {
  budget: {
    daily_limit_usd: 10,        // Hard stop at $10/day
    session_tokens:  500_000,   // Max 500K tokens per session
    circuit_breaker: {
      max_identical_calls: 10,  // Kill after 10 repeated calls
      window_seconds: 60,       // Within 60-second window
    },
  },
  on_budget_exceeded: "halt",   // "halt" | "notify" | "degrade"
  on_loop_detected:   "halt",
});

// That's it. No agent can spend beyond $10/day.
// Infinite loops are caught in < 60 seconds.`;

function CmpCell({ v }: { v: boolean | "partial" | string }) {
    if (v === true) return <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" />;
    if (v === false) return <span className="text-neutral-700 text-lg mx-auto block text-center">—</span>;
    if (v === "partial") return <span className="text-amber-400 font-bold text-xs mx-auto block text-center">PARTIAL</span>;
    return <span className="text-neutral-400 font-mono text-xs mx-auto block text-center">{v}</span>;
}

export default function BudgetClient() {
    const params = useParams();
    const lang = (params?.lang as string) || 'en';
    const [openFaq, setOpenFaq] = useState<number | null>(null);
    const [copied, setCopied] = useState(false);
    const { count: countCapital, ref: refCapital } = useCountUp(124000, 2200);
    const { count: countLoops, ref: refLoops } = useCountUp(847, 1800);

    const handleCopy = () => {
        navigator.clipboard.writeText(CODE);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <main className="overflow-x-hidden">

            {/* ── HERO ── */}
            <section className="relative min-h-screen flex flex-col lg:flex-row items-center justify-center px-6 pt-32 pb-24 gap-16 overflow-hidden">
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-rose-500/5 rounded-full blur-[120px]" />
                    <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-emerald-500/5 rounded-full blur-[80px]" />
                </div>

                <div className="relative z-10 max-w-2xl space-y-8">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-amber-500/30 bg-amber-500/10 text-[10px] font-black text-amber-400 tracking-[0.25em] uppercase">
                        <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                        Agent Cost Control
                    </div>

                    <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.82] uppercase italic">
                        Your Agent<br />
                        Burned <span className="text-rose-500">$4,000</span><br />
                        Overnight.<br />
                        <span className="text-emerald-500">Budget Limits</span><br />
                        Stop It at <span className="text-white">$10.</span>
                    </h1>

                    <p className="text-xl text-neutral-400 leading-relaxed font-medium">
                        One infinite loop. One recursive tool chain. One hallucinated API call repeated 10,000 times. That&apos;s all it takes to turn a $0.002 agent call into a $4,000 overnight disaster. SupraWall Budget Limits set hard, deterministic caps that no LLM can talk its way around.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <Link href={`/${lang}/beta`} className="inline-flex items-center gap-2 px-10 py-5 bg-white text-black font-black uppercase tracking-widest rounded-2xl hover:bg-neutral-100 transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)] text-sm">
                            Set Your First Budget <ArrowRight className="w-4 h-4" />
                        </Link>
                        <a href="#cost-calculator" className="inline-flex items-center gap-2 px-10 py-5 bg-transparent text-white border-2 border-amber-500/40 font-black uppercase tracking-widest rounded-2xl hover:border-amber-500 hover:bg-amber-500/5 transition-all text-sm">
                            Calculate Your Risk
                        </a>
                    </div>
                </div>

                <div className="relative z-10 w-full max-w-md">
                    <CostTicker />
                </div>
            </section>

            {/* ── INCIDENTS ── */}
            <section className="py-32 px-6 bg-neutral-950/50">
                <div className="max-w-6xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-rose-500/30 bg-rose-500/10 text-[10px] font-black text-rose-400 tracking-[0.25em] uppercase">
                            <AlertTriangle className="w-3 h-3" /> Real-World Incidents
                        </div>
                        <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase italic text-white">
                            These Happened.<br />To Real Teams. <span className="text-rose-500">Last Month.</span>
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {INCIDENTS.map((inc) => (
                            <div key={inc.title} className="bg-neutral-900 border border-rose-500/20 rounded-[2rem] p-8 space-y-6 relative overflow-hidden hover:border-rose-500/40 transition-all">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/5 rounded-full blur-2xl" />
                                <div className="flex items-start justify-between">
                                    <div className="space-y-1">
                                        <span className="text-[9px] font-black text-neutral-600 uppercase tracking-widest">{inc.framework}</span>
                                        <h3 className="text-lg font-black text-white">{inc.title}</h3>
                                    </div>
                                    <span className="text-rose-400 font-black text-xl">{inc.cost}</span>
                                </div>
                                <p className="text-neutral-400 text-sm leading-relaxed">{inc.desc}</p>
                                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest">
                                    <span className="text-neutral-600">{inc.calls}</span>
                                    <span className="text-rose-400/60">{inc.time}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <p className="text-center text-emerald-400 font-black italic text-lg">
                        With SupraWall Budget Limits, every one of these incidents would have been stopped at the cap you set.
                    </p>
                </div>
            </section>

            {/* ── THREE LAYERS ── */}
            <section className="py-32 px-6">
                <div className="max-w-4xl mx-auto space-y-16">
                    <div className="text-center space-y-4">
                        <p className="text-[10px] font-black text-emerald-400 uppercase tracking-[0.3em]">Architecture</p>
                        <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase italic text-white">
                            Three Layers.<br /><span className="text-emerald-500">Zero Overruns.</span>
                        </h2>
                    </div>

                    <div className="relative space-y-4">
                        {[
                            {
                                num: "01",
                                label: "Hard Budget Cap",
                                icon: <DollarSign className="w-7 h-7 text-emerald-500" />,
                                color: "emerald",
                                title: "Dollar Limit Per Agent Per Day",
                                desc: "Set a dollar limit per agent, per day ($10/day, $50/day, $500/day). SupraWall tracks accumulated cost in real time by multiplying token consumption by the model's per-token price. When the cap is reached: hard stop. No exceptions, no overrides, no matter what the LLM requests.",
                                badge: "Enforced at Evaluate API"
                            },
                            {
                                num: "02",
                                label: "Circuit Breaker",
                                icon: <Zap className="w-7 h-7 text-amber-500" />,
                                color: "amber",
                                title: "Loop Detection Before Budget Impact",
                                desc: "SupraWall analyzes tool call patterns in real time. If it detects repetitive identical calls (configurable threshold), it triggers the circuit breaker immediately — before the budget cap is even reached. Catches infinite loops in seconds, not hours.",
                                badge: "Default: 10 calls / 60 seconds"
                            },
                            {
                                num: "03",
                                label: "Session Token Limit",
                                icon: <Activity className="w-7 h-7 text-purple-400" />,
                                color: "purple",
                                title: "Max Token Count Per Session",
                                desc: "Independent of dollar cost, set a maximum token count per session. Prevents long-running agents from accumulating excessive context windows that degrade performance and inflate costs. Works with streaming, extended thinking, and multi-agent conversations.",
                                badge: "Input + Output tokens tracked"
                            },
                        ].map((layer, i) => (
                            <div key={layer.num} className={`bg-neutral-900 border rounded-[2rem] p-8 md:p-10 space-y-4 transition-all hover:border-${layer.color}-500/30 border-white/5`}>
                                <div className="flex items-start gap-6">
                                    <span className="text-5xl font-black text-neutral-800 shrink-0">{layer.num}</span>
                                    <div className="space-y-4 flex-1">
                                        <div className="flex items-center gap-3 flex-wrap">
                                            <div className="p-2 bg-white/5 rounded-xl">{layer.icon}</div>
                                            <div>
                                                <p className={`text-[9px] font-black text-${layer.color}-400 uppercase tracking-widest`}>{layer.label}</p>
                                                <h3 className="text-xl font-black text-white">{layer.title}</h3>
                                            </div>
                                            <span className={`ml-auto px-3 py-1 text-[9px] font-black uppercase tracking-widest rounded-full bg-${layer.color}-500/10 text-${layer.color}-400 border border-${layer.color}-500/20`}>
                                                {layer.badge}
                                            </span>
                                        </div>
                                        <p className="text-neutral-400 text-base leading-relaxed">{layer.desc}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── CALCULATOR ── */}
            <section className="py-32 px-6 bg-neutral-950/50">
                <div className="max-w-4xl mx-auto">
                    <CostCalculator />
                </div>
            </section>

            {/* ── COMPARISON TABLE ── */}
            <section className="py-32 px-6">
                <div className="max-w-6xl mx-auto space-y-12">
                    <div className="text-center space-y-4">
                        <p className="text-[10px] font-black text-emerald-400 uppercase tracking-[0.3em]">Why Not Just...</p>
                        <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase italic text-white">
                            Deterministic Limits.<br /><span className="text-emerald-500">Not Rate-Limit Hacks.</span>
                        </h2>
                    </div>

                    <div className="bg-neutral-900/60 border border-white/5 rounded-[2.5rem] overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-neutral-900 border-b border-white/10">
                                    <tr>
                                        <th className="text-left px-8 py-6 text-[10px] font-black text-neutral-500 uppercase tracking-widest w-[36%]">Capability</th>
                                        <th className="px-5 py-6 text-center">
                                            <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest block">SupraWall</span>
                                            <span className="text-[9px] text-neutral-600 block mt-1">Budget Limits</span>
                                        </th>
                                        <th className="px-5 py-6 text-center">
                                            <span className="text-[10px] font-black text-neutral-400 uppercase tracking-widest block">API Provider</span>
                                            <span className="text-[9px] text-neutral-600 block mt-1">Rate Limits</span>
                                        </th>
                                        <th className="px-5 py-6 text-center">
                                            <span className="text-[10px] font-black text-neutral-400 uppercase tracking-widest block">DIY Token</span>
                                            <span className="text-[9px] text-neutral-600 block mt-1">Counting</span>
                                        </th>
                                        <th className="px-5 py-6 text-center">
                                            <span className="text-[10px] font-black text-neutral-400 uppercase tracking-widest block">Portkey /</span>
                                            <span className="text-[9px] text-neutral-600 block mt-1">LLM Gateway</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.04]">
                                    {COMPARISON_ROWS.map((row) => (
                                        <tr key={row.cap} className="hover:bg-white/[0.05] transition-colors">
                                            <td className="px-8 py-5 text-neutral-300 font-medium text-sm">{row.cap}</td>
                                            <td className="px-5 py-5"><CmpCell v={row.sw} /></td>
                                            <td className="px-5 py-5"><CmpCell v={row.api} /></td>
                                            <td className="px-5 py-5"><CmpCell v={row.diy} /></td>
                                            <td className="px-5 py-5"><CmpCell v={row.port} /></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── CODE ── */}
            <section className="py-32 px-6 bg-neutral-950/50">
                <div className="max-w-4xl mx-auto space-y-12">
                    <div className="text-center space-y-4">
                        <p className="text-[10px] font-black text-emerald-400 uppercase tracking-[0.3em]">Integration</p>
                        <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase italic text-white">
                            Three Lines.<br /><span className="text-emerald-500">Total Cost Control.</span>
                        </h2>
                    </div>

                    <div className="bg-neutral-900 border border-white/5 rounded-[2.5rem] overflow-hidden">
                        <div className="flex items-center justify-between px-8 py-5 border-b border-white/5">
                            <div className="flex items-center gap-3">
                                <div className="w-3 h-3 rounded-full bg-rose-500/60" />
                                <div className="w-3 h-3 rounded-full bg-amber-500/60" />
                                <div className="w-3 h-3 rounded-full bg-emerald-500/60" />
                                <span className="ml-2 text-[10px] text-neutral-500 font-mono uppercase tracking-widest">TypeScript / Python</span>
                            </div>
                            <button onClick={handleCopy} className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl text-neutral-400 hover:text-white transition-all text-[11px] font-bold uppercase tracking-wider">
                                {copied ? <><Check className="w-3.5 h-3.5 text-emerald-500" /> Copied</> : <><Copy className="w-3.5 h-3.5" /> Copy</>}
                            </button>
                        </div>
                        <div className="p-8 overflow-x-auto">
                            <pre className="font-mono text-sm text-emerald-100/80 leading-relaxed">{CODE}</pre>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── STATS ── */}
            <section className="py-32 px-6">
                <div className="max-w-5xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                        <div ref={refCapital} className="space-y-2">
                            <p className="text-6xl font-black text-emerald-500">
                                ${countCapital >= 1000 ? `${(countCapital / 1000).toFixed(0)}K` : countCapital}+
                            </p>
                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Capital Protected from Runaway Agents</p>
                        </div>
                        <div ref={refLoops} className="space-y-2">
                            <p className="text-6xl font-black text-white">{countLoops}</p>
                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Infinite Loops Caught This Month</p>
                        </div>
                        <div className="space-y-2">
                            <p className="text-6xl font-black text-white">1.2ms</p>
                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Average Enforcement Latency</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── FAQ ── */}
            <section className="py-32 px-6 bg-neutral-950/50">
                <div className="max-w-3xl mx-auto space-y-12">
                    <div className="text-center">
                        <h2 className="text-4xl font-black tracking-tighter uppercase italic text-white">
                            Frequently Asked <span className="text-emerald-500">Questions</span>
                        </h2>
                    </div>
                    <div className="space-y-3">
                        {FAQS.map((faq, i) => (
                            <div key={i} className="bg-neutral-900 border border-white/5 rounded-2xl overflow-hidden hover:border-emerald-500/20 transition-all">
                                <button onClick={() => setOpenFaq(openFaq === i ? null : i)}
                                    className="w-full flex items-center justify-between px-8 py-6 text-left">
                                    <span className="text-white font-bold pr-4">{faq.q}</span>
                                    <ChevronDown className={`w-5 h-5 text-emerald-500 shrink-0 transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                                </button>
                                {openFaq === i && (
                                    <div className="px-8 pb-6 text-neutral-400 text-sm leading-relaxed border-t border-white/5 pt-4">{faq.a}</div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── FINAL CTA ── */}
            <section className="py-32 px-6">
                <div className="max-w-5xl mx-auto">
                    <div className="relative bg-emerald-600 rounded-[3rem] p-16 md:p-24 text-center overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-emerald-800 opacity-0 hover:opacity-100 transition-opacity duration-1000" />
                        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 blur-3xl rounded-full translate-x-1/2 -translate-y-1/2" />
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/20 blur-3xl rounded-full -translate-x-1/2 translate-y-1/2" />
                        <div className="relative z-10 space-y-8">
                            <p className="text-[10px] font-black text-emerald-200 uppercase tracking-[0.4em]">How Much Did Your Agents Spend Last Night?</p>
                            <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic text-white leading-none">
                                Set your first<br />budget in<br />3 minutes.
                            </h2>
                            <p className="text-emerald-100/80 text-lg font-medium italic max-w-md mx-auto">
                                Free tier includes 10,000 operations. No credit card required.
                            </p>
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <Link href={`/${lang}/beta`} className="inline-flex items-center gap-2 px-12 py-5 bg-white text-black font-black uppercase tracking-widest rounded-2xl hover:bg-neutral-100 transition-all shadow-2xl">
                                    Set Budget Limits <ArrowRight className="w-4 h-4" />
                                </Link>
                                <Link href={`/${lang}/docs`} className="inline-flex items-center gap-2 px-12 py-5 bg-black/20 text-white border-2 border-white/20 font-black uppercase tracking-widest rounded-2xl hover:bg-black/40 transition-all">
                                    Read the Budget Docs
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── LEARN MORE ── */}
            <section className="py-20 px-6 border-t border-white/5">
                <div className="max-w-5xl mx-auto">
                    <p className="text-[10px] font-black text-neutral-600 uppercase tracking-widest mb-4 text-center">Deep Dives</p>
                    <h2 className="text-2xl font-black uppercase italic text-white text-center mb-12">Learn More About Budget Control</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[
                            { href: "/learn/ai-agent-runaway-costs", label: "AI Agent Runaway Costs", desc: "How agents burn $4,000 overnight — and the 4 root causes you must understand." },
                            { href: "/learn/how-to-set-token-limits-ai-agents", label: "How to Set Token Limits", desc: "Step-by-step implementation for LangChain, CrewAI, AutoGen, and SupraWall." },
                            { href: "/learn/ai-agent-infinite-loop-detection", label: "Infinite Loop Detection", desc: "3 detection strategies and circuit breaker patterns to kill runaway agents." },
                            { href: "/tools/llm-cost-calculator", label: "LLM Cost Calculator", desc: "Calculate your real AI agent costs — daily, monthly, and worst-case loop scenario." },
                        ].map((l) => (
                            <Link key={l.href} href={l.href} className="p-6 bg-neutral-900/40 border border-white/5 rounded-2xl hover:border-emerald-500/30 transition-all group">
                                <p className="text-white font-black group-hover:text-emerald-400 transition-colors text-sm mb-2">{l.label}</p>
                                <p className="text-neutral-500 text-xs leading-relaxed">{l.desc}</p>
                            </Link>
                        ))}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                        {[
                            { href: "/features/vault", label: "Credential Vault", desc: "Protect secrets from your LLM" },
                            { href: "/learn/ai-agent-infinite-loop-detection", label: "Loop Detection Guide", desc: "How circuit breakers work" },
                            { href: "/learn/ai-agent-security-best-practices", label: "Security Best Practices", desc: "The full production checklist" },
                        ].map((l) => (
                            <Link key={l.href} href={l.href} className="p-6 bg-neutral-900/40 border border-white/5 rounded-2xl hover:border-emerald-500/30 transition-all group">
                                <p className="text-white font-black group-hover:text-emerald-400 transition-colors">{l.label}</p>
                                <p className="text-neutral-500 text-xs mt-1 italic">{l.desc}</p>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            <footer className="py-16 border-t border-white/5 text-center">
                <p className="text-neutral-700 text-[10px] font-black uppercase tracking-[0.5em]">
                    SupraWall © 2026 • Real-time Agent Governance
                </p>
            </footer>
             {/* ⚡ TRY IN 30 SECONDS */}
             <section className="py-24 px-6 bg-[#030303] border-t border-white/5 relative z-10 text-center">
                <div className="max-w-4xl mx-auto space-y-12">
                    <h2 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter text-glow">
                        Try It In <span className="text-emerald-500 underline decoration-white/10">30 Seconds.</span>
                    </h2>
                    <p className="text-xl md:text-2xl text-neutral-400 font-medium italic max-w-2xl mx-auto">
                        No account required. Auto-detect your framework and wrap your agent with security in one command.
                    </p>
                    <div className="p-6 md:p-8 bg-[#0a0a0a] rounded-[2rem] border border-emerald-500/20 font-mono text-[13px] relative overflow-hidden group shadow-[0_0_80px_rgba(16,185,129,0.15)] text-left cursor-copy mx-auto max-w-2xl hover:border-emerald-500/50 transition-all" onClick={() => navigator.clipboard && navigator.clipboard.writeText('npx suprawall init')} title="Copy command">
                        <div className="absolute top-4 right-6 text-emerald-500/30 text-[10px] font-black uppercase tracking-widest italic group-hover:text-emerald-500 transition-colors">
                            CLICK TO COPY
                        </div>
                        <pre className="text-emerald-100/80 leading-loose">
$ npx suprawall init

? Detected: my-agent.ts — secure it? (Y/n) y

[✓] .env updated with SUPRAWALL_API_KEY
[✓] my-agent.ts wrapped with protect()

🛡️  Your agent is now armored.
                        </pre>
                    </div>
                </div>
            </section>
        </main>

    );
}

// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

const DEFAULT_CLOUD_FUNCTION_URL =
    "https://www.supra-wall.com/api/v1/evaluate";
const SDK_VERSION = "1.1.0";

let _tenantIdWarned = false;
function getDefaultTenantId(): string {
    if (!_tenantIdWarned && typeof console !== "undefined") {
        console.warn("[SupraWall SDK] No tenantId provided. Set options.tenantId to your organization ID.");
        _tenantIdWarned = true;
    }
    return "unspecified";
}

/**
 * Enhanced fetch with exponential backoff and jitter.
 */
async function fetchWithRetry(url: string, options: RequestInit, maxRetries = 3): Promise<Response> {
    let retries = 0;
    while (retries < maxRetries) {
        try {
            const response = await fetch(url, options);
            // Retry on server errors or rate limits (5xx, 429)
            if (response.status >= 500 || response.status === 429) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response;
        } catch (err) {
            retries++;
            if (retries >= maxRetries) throw err;
            // Exponential backoff: 200ms, 400ms, 800ms... with jitter
            const backoff = Math.pow(2, retries) * 100 + Math.random() * 50;
            await new Promise(res => setTimeout(res, backoff));
        }
    }
    throw new Error("Max retries exceeded");
}

// ---------------------------------------------------------------------------
// Cost estimation — model token costs (USD per 1k tokens)
// ---------------------------------------------------------------------------

const MODEL_COSTS_PER_1K: Record<string, { input: number; output: number }> = {
    "gpt-4o": { input: 0.005, output: 0.015 },
    "gpt-4o-mini": { input: 0.00015, output: 0.0006 },
    "gpt-4-turbo": { input: 0.01, output: 0.03 },
    "claude-3-5-sonnet": { input: 0.003, output: 0.015 },
    "claude-3-5-haiku": { input: 0.0008, output: 0.004 },
    "gemini-1.5-pro": { input: 0.00125, output: 0.005 },
    "gemini-1.5-flash": { input: 0.000075, output: 0.0003 },
};

function estimateCost(model: string, inputTokens: number, outputTokens: number): number {
    const key = Object.keys(MODEL_COSTS_PER_1K).find(k => model.toLowerCase().startsWith(k));
    const rates = key ? MODEL_COSTS_PER_1K[key] : { input: 0.001, output: 0.002 };
    return (inputTokens / 1000 * rates.input) + (outputTokens / 1000 * rates.output);
}

function formatCost(usd: number): string {
    if (usd < 0.0001) return `$${usd.toFixed(6)}`;
    if (usd < 0.01) return `$${usd.toFixed(4)}`;
    return `$${usd.toFixed(2)}`;
}

// ---------------------------------------------------------------------------
// Budget control
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// In-memory trackers (Budget & Loops) — shared across instances
// ---------------------------------------------------------------------------

const _sessionCosts = new Map<string, number>();        // session_id -> cumulative USD
const _sessionIterations = new Map<string, number>();   // session_id -> total tool calls
const _sessionCallHistory = new Map<string, string[]>(); // session_id -> list of call sigs


export class BudgetExceededError extends Error {
    public readonly limitUsd: number;
    public readonly actualUsd: number;

    constructor(limitUsd: number, actualUsd: number) {
        super(
            `[SupraWall] Budget cap of ${formatCost(limitUsd)} exceeded ` +
            `(session spend: ${formatCost(actualUsd)}). Agent halted.`
        );
        this.name = "BudgetExceededError";
        this.limitUsd = limitUsd;
        this.actualUsd = actualUsd;
    }
}

export class SupraWallConnectionError extends Error {
    constructor(message: string) {
        super(`\n[SupraWallConnectionError] ${message}\n  → Docs: https://docs.supra-wall.com/troubleshooting/connection\n`);
        this.name = "SupraWallConnectionError";
    }
}

export class BudgetTracker {
    private sessionCost = 0;
    private alertFired = false;

    constructor(
        private readonly maxCostUsd?: number,
        private readonly alertUsd?: number,
        private readonly logger: Pick<Console, "warn"> = console,
    ) { }

    /**
     * Record a call and enforce the budget cap.
     * Pass costUsd directly, or model+tokens for auto-estimation.
     * Throws BudgetExceededError if the hard cap is breached.
     */
    record(opts: { model?: string; inputTokens?: number; outputTokens?: number; costUsd?: number } = {}): number {
        const cost = opts.costUsd ?? estimateCost(
            opts.model ?? "gpt-4o-mini",
            opts.inputTokens ?? 0,
            opts.outputTokens ?? 0,
        );
        this.sessionCost += cost;

        if (this.alertUsd && !this.alertFired && this.sessionCost >= this.alertUsd) {
            this.alertFired = true;
            this.logger.warn(
                `[SupraWall] Budget alert: session spend ${formatCost(this.sessionCost)} ` +
                `>= alert threshold ${formatCost(this.alertUsd)}.`
            );
        }

        if (this.maxCostUsd !== undefined && this.sessionCost >= this.maxCostUsd) {
            throw new BudgetExceededError(this.maxCostUsd, this.sessionCost);
        }

        return cost;
    }

    reset(): void {
        this.sessionCost = 0;
        this.alertFired = false;
    }

    get summary(): string {
        const limit = this.maxCostUsd !== undefined ? formatCost(this.maxCostUsd) : "unlimited";
        return `Session spend: ${formatCost(this.sessionCost)} / ${limit}`;
    }
}

export interface OpenRouterAttribution {
    /** Your app's URL for OpenRouter rankings */
    appUrl?: string;
    /** Your app's display name */
    appTitle?: string;
    /** Comma-separated list of categories (e.g. cli-agent, personal-agent) */
    categories?: string;
}

export interface SupraWallResponse {
    decision: "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
    reason?: string;
    estimated_cost_usd?: number;
    is_loop?: boolean;
    vaultInjected?: boolean;
    resolvedArguments?: Record<string, unknown>;
    injectedSecrets?: string[];
    branding?: {
        enabled: boolean;
        text: string;
        url: string;
        format: "text" | "markdown" | "html";
    };
    /** Layer 2 semantic threat score (0.0–1.0). Present on Team tier and above. */
    semanticScore?: number;
    /** True when Layer 2 flagged the call but still allowed it. */
    semanticFlag?: boolean;
    /** LLM-generated explanation of the semantic assessment. */
    semanticReasoning?: string;
    /** Behavioral anomaly score (0.0–1.0). Present on Business tier and above. */
    anomalyScore?: number;
}

export interface SupraWallOptions {
    /**
     * Your SupraWall API key.
     * Get one free at https://www.supra-wall.com/
     * Format: sw_xxxxxxxxxxxxxxxx
     */
    apiKey: string;
    /**
     * Override the SupraWall evaluation endpoint.
     * Defaults to the hosted SupraWall cloud function.
     * Set this for self-hosted deployments.
     */
    cloudFunctionUrl?: string;
    /**
     * What to do when SupraWall is unreachable.
     * "fail-open"   → allow the action and log a warning (default, good for dev)
     * "fail-closed" → block the action (recommended for production)
     */
    onNetworkError?: "fail-open" | "fail-closed";
    /**
     * Custom logger. Defaults to console.
     * Pass `{ warn: () => {}, error: () => {}, log: () => {} }` to silence.
     */
    logger?: Pick<Console, "warn" | "error" | "log">;
    /**
     * Hard cost cap per agent session in USD.
     * When the accumulated LLM spend reaches this limit, BudgetExceededError is thrown.
     * Example: maxCostUsd: 5.00  →  agent auto-stops at $5
     */
    maxCostUsd?: number;
    /**
     * Soft alert threshold in USD. Logs a warning when spend reaches this amount.
     */
    budgetAlertUsd?: number;
    /**
     * Optional session ID to group calls for cost/loop tracking.
     */
    sessionId?: string;
    /**
     * Optional agent role descriptor (e.g. "researcher", "executor").
     */
    agentRole?: string;
    /**
     * Hard stop after N tool calls in this session.
     * Prevents runaway agents regardless of loop patterns.
     */
    maxIterations?: number;
    /**
     * Enable circuit breaker for infinite loops.
     * Detects when the same tool is called repeatedly with identical arguments.
     */
    loopDetection?: boolean;
    /**
     * Number of consecutive identical calls needed to trigger a block.
     * Defaults to 3.
     */
    loopThreshold?: number;
    /**
     * Override the vault scrub endpoint URL.
     * Defaults to the evaluate URL with /v1/evaluate replaced by /v1/scrub.
     * Only relevant for self-hosted deployments using the Vault feature.
     */
    vaultScrubUrl?: string;
    /**
     * Tenant ID to include with vault requests.
     */
    tenantId?: string;
    /**
     * Optional delegation chain of agent IDs.
     * Used for verifying identity in multi-agent workflows.
     */
    delegationChain?: string[];
    /**
     * Optional OpenRouter app attribution headers.
     * When set, SupraWall automatically injects these into outbound OpenRouter calls.
     */
    openrouterAttribution?: OpenRouterAttribution;
}

export interface AgentInstance {
    executeTool: (toolName: string, args: Record<string, unknown>) => Promise<unknown> | unknown;
    [key: string]: unknown;
}

/**
 * Wraps any AI agent with SupraWall security enforcement.
 *
 * Every tool call is intercepted and evaluated against your policies
 * before execution. Zero infrastructure required — just an API key.
 *
 * @example
 * // Works with LangChain, OpenAI Agents SDK, CrewAI, AutoGen, raw MCP
 * import { withSupraWall } from "suprawall";
 *
 * const secured = withSupraWall(myAgent, { apiKey: "sw_your_key" });
 * await secured.executeTool("send_email", { to: "ceo@company.com" }); // checked
 *
 * @param agentInstance - Any agent object with an `executeTool` method
 * @param options - SupraWall configuration (only `apiKey` is required)
 * @returns The same agent instance, now protected by SupraWall
 */
/**
 * Appends the Supra-wall branding footer to the content.
 */
function appendBranding(content: string, branding: SupraWallResponse["branding"]): string {
    if (!branding || !branding.enabled) return content;
    const { text, url } = branding;
    // For now, we only support simple text appending. 
    // In future, we could support markdown/html formats more natively.
    return `${content}\n\n---\n${text}\n${url}`;
}

/**
 * Core internal evaluator that handles budget, loops, and network policy checks.
 */
let _hasVerifiedConnection = false;
async function internalEvaluate(
    toolName: string,
    args: Record<string, unknown>,
    options: SupraWallOptions,
    metadata: { model?: string; inputTokens?: number; outputTokens?: number } = {}
): Promise<{ decision: "ALLOW" | "DENY" | "REQUIRE_APPROVAL"; reason?: string; error?: string; resolvedArguments?: Record<string, unknown>; injectedSecrets?: string[]; vaultInjected?: boolean; branding?: SupraWallResponse["branding"] }> {
    const {
        apiKey,
        cloudFunctionUrl = DEFAULT_CLOUD_FUNCTION_URL,
        onNetworkError = "fail-open",
        logger = console,
        maxCostUsd,
        budgetAlertUsd,
        sessionId: optSessionId,
        maxIterations,
        loopDetection = false,
        loopThreshold = 3,
    } = options;

    const sessionId = optSessionId ?? apiKey;

    // --- 1. Budget Check (Fast-Reject) ---
    if (maxCostUsd !== undefined) {
        const current = _sessionCosts.get(sessionId) ?? 0;
        if (budgetAlertUsd && current >= budgetAlertUsd) {
            logger.warn(`[SupraWall] 💰 Budget alert: ${formatCost(current)} used for session ${sessionId}`);
        }
        if (current >= maxCostUsd) {
            return {
                decision: "DENY",
                reason: `Budget cap reached: ${formatCost(current)} >= ${formatCost(maxCostUsd)}. Agent stopped.`,
                error: "BudgetExceededError"
            };
        }
    }

    // --- 2. Iteration Limit ---
    if (maxIterations !== undefined) {
        const iterations = (_sessionIterations.get(sessionId) ?? 0) + 1;
        _sessionIterations.set(sessionId, iterations);
        if (iterations > maxIterations) {
            return {
                decision: "DENY",
                reason: `Circuit breaker: Exceeded maximum tool iterations (${maxIterations}).`,
                error: "IterationLimitError"
            };
        }
    }

    // --- 3. Loop Detection ---
    let isLoopDetected = false;
    if (loopDetection) {
        const callSig = `${toolName}:${JSON.stringify(args, Object.keys(args || {}).sort())}`;
        let history = _sessionCallHistory.get(sessionId) ?? [];
        history.push(callSig);
        
        // Prevent memory leak by keeping only what's needed for threshold checking
        if (history.length > loopThreshold) {
            history = history.slice(-loopThreshold);
        }
        _sessionCallHistory.set(sessionId, history);

        const recent = history;
        if (recent.length === loopThreshold && new Set(recent).size === 1) {
            isLoopDetected = true;
            // Don't stop yet, let's report it to the server in the next step
        }
    }

    try {
        const payload = {
            apiKey,
            toolName,
            arguments: args,
            agentId: sessionId,
            tenantId: options.tenantId || getDefaultTenantId(),
            sessionId,
            agentRole: options.agentRole,
            model: metadata.model,
            inputTokens: metadata.inputTokens,
            outputTokens: metadata.outputTokens,
            isLoop: isLoopDetected,
            delegationChain: options.delegationChain
        };

        const headers: Record<string, string> = {
            "Content-Type": "application/json",
            "X-SupraWall-SDK": `js-${SDK_VERSION}`,
        };

        if (options.openrouterAttribution) {
            if (options.openrouterAttribution.appUrl) {
                headers["HTTP-Referer"] = options.openrouterAttribution.appUrl;
            }
            if (options.openrouterAttribution.appTitle) {
                headers["X-Title"] = options.openrouterAttribution.appTitle;
            }
            if (options.openrouterAttribution.categories) {
                headers["X-OpenRouter-Categories"] = options.openrouterAttribution.categories;
            }
        }

        const response = await fetchWithRetry(cloudFunctionUrl, {
            method: "POST",
            headers,
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            if (response.status === 401 && !_hasVerifiedConnection) {
                throw new SupraWallConnectionError(`Invalid API key. Check your SUPRAWALL_API_KEY.`);
            }
            if (response.status === 403) {
                return { decision: "DENY", reason: "Action blocked by SupraWall security policy." };
            }
            throw new Error(`SupraWall server error: ${response.status}`);
        }
        _hasVerifiedConnection = true;

        let data: SupraWallResponse & { approvalId?: string };
        try {
            data = await response.json();
        } catch (err) {
            throw new Error("Failed to parse SupraWall response: Malformed JSON");
        }

        // Record cost tracking
        const current = _sessionCosts.get(sessionId) ?? 0;
        const total = current + (data.estimated_cost_usd || 0);
        _sessionCosts.set(sessionId, total);

        if (isLoopDetected) {
            return {
                decision: "DENY",
                reason: `Loop detected: Tool '${toolName}' called ${loopThreshold}x consecutively with identical args.`
            };
        }

        // --- 4. Handle Human-in-the-loop (Polling) ---
        if (data.decision === "REQUIRE_APPROVAL" && data.approvalId) {
            logger.log(`[SupraWall] ⏳ Action '${toolName}' requires manual approval. Polling for decision...`);
            
            const pollUrl = `${cloudFunctionUrl.replace("/v1/evaluate", "/v1/approvals/status")}/${data.approvalId}`;
            const maxPolls = 150; // 5 minutes (2s * 150)
            let polls = 0;

            while (polls < maxPolls) {
                await new Promise(resolve => setTimeout(resolve, 2000));
                polls++;

                try {
                    const pollRes = await fetch(pollUrl);
                    if (pollRes.ok) {
                        const statusData = (await pollRes.json()) as { status: string; decision_comment?: string };
                        const status = statusData.status.toUpperCase();
                        if (status === "APPROVED") {
                            logger.log(`[SupraWall] ✅ Action '${toolName}' approved by human.`);
                            return {
                                decision: "ALLOW",
                                reason: statusData.decision_comment || "Approved by human",
                                resolvedArguments: data.resolvedArguments,
                                injectedSecrets: data.injectedSecrets,
                                vaultInjected: data.vaultInjected,
                                branding: data.branding,
                            };
                        } else if (status === "DENIED" || status === "REJECTED") {
                            logger.warn(`[SupraWall] ❌ Action '${toolName}' denied by human.`);
                            return {
                                decision: "DENY",
                                reason: statusData.decision_comment || "Denied by human",
                            };
                        }
                    }
                } catch (pollErr) {
                    logger.error("[SupraWall] Polling error", pollErr);
                }
            }

            return {
                decision: "DENY",
                reason: "Approval request timed out after 5 minutes."
            };
        }

        return {
            decision: data.decision,
            reason: data.reason,
            resolvedArguments: data.resolvedArguments,
            injectedSecrets: data.injectedSecrets,
            vaultInjected: data.vaultInjected,
            branding: data.branding,
        };
    } catch (e: any) {
        if (e instanceof Error && e.message.includes("[SupraWall]")) throw e;
        if (e instanceof SupraWallConnectionError) throw e;

        if (!_hasVerifiedConnection && (e.message.includes("fetch") || e.message.includes("network"))) {
            throw new SupraWallConnectionError(`Cannot reach SupraWall server at ${cloudFunctionUrl}.`);
        }

        logger.error("[SupraWall] Network error reaching control plane.", e);
        if (onNetworkError === "fail-closed") {
            return { decision: "DENY", reason: "SupraWall unreachable. Action blocked (fail-closed mode)." };
        }
        return { decision: "ALLOW" };
    }
}

// ---------------------------------------------------------------------------
// Vault helpers
// ---------------------------------------------------------------------------

function deriveScrubUrl(cloudFunctionUrl: string, vaultScrubUrl?: string): string {
    if (vaultScrubUrl) return vaultScrubUrl;
    return cloudFunctionUrl.replace("/v1/evaluate", "/v1/scrub");
}

async function scrubAfterExecution(
    toolResult: any,
    injectedSecrets: string[],
    options: SupraWallOptions
): Promise<any> {
    const scrubUrl = deriveScrubUrl(
        options.cloudFunctionUrl || DEFAULT_CLOUD_FUNCTION_URL,
        options.vaultScrubUrl
    );
    try {
        const res = await fetch(scrubUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tenantId: options.tenantId || getDefaultTenantId(),
                secretNames: injectedSecrets,
                toolResponse: toolResult,
            }),
        });
        if (!res.ok) throw new Error(`Scrub endpoint returned ${res.status}`);
        const data = await res.json() as { scrubbedResponse: any };
        return data.scrubbedResponse;
    } catch {
        // Fail safe: return fully redacted response if scrub fails
        return "[Response redacted — vault scrub unavailable]";
    }
}

export function withSupraWall<T extends AgentInstance>(
    agentInstance: T,
    options: SupraWallOptions
): T {
    const { apiKey, logger = console } = options;

    if (!apiKey || !/^(sw_|swc_|ag_)/.test(apiKey)) {
        throw new Error(
            `[SupraWall] Invalid API key: "${apiKey}".\n` +
            `  Get your free key at https://www.supra-wall.com/\n` +
            `  Expected format: sw_xxxx, swc_xxxx, or ag_xxxx`
        );
    }

    const originalExecuteTool = agentInstance.executeTool.bind(agentInstance);

    agentInstance.executeTool = async (toolName: string, args: any) => {
        const result = await internalEvaluate(toolName, args, options);

        if (result.decision === "ALLOW") {
            const executionArgs = result.vaultInjected ? result.resolvedArguments : args;
            let toolResult = await originalExecuteTool(toolName, executionArgs);
            
            // Branding injection for strings
            if (typeof toolResult === "string" && result.branding?.enabled) {
                toolResult = appendBranding(toolResult, result.branding);
            }

            if (result.vaultInjected && result.injectedSecrets?.length) {
                return await scrubAfterExecution(toolResult, result.injectedSecrets, options);
            }
            return toolResult;
        }

        logger.warn(`[SupraWall] ${result.decision}: ${result.reason ?? ""}`);
        return `ERROR: ${result.reason ?? "Action blocked by SupraWall."}`;
    };

    return agentInstance;
}

/**
 * MCP-native middleware for Model Context Protocol servers.
 */
export function createSupraWallMiddleware(options: SupraWallOptions) {
    const {
        apiKey,
        logger = console,
    } = options;

    return async function supraWallMiddleware(
        toolName: string,
        args: any,
        next: (executionArgs?: any) => Promise<any>
    ): Promise<any> {
        const result = await internalEvaluate(toolName, args, options);

        if (result.decision === "ALLOW") {
            const executionArgs = result.vaultInjected ? result.resolvedArguments : args;
            let toolResult = await next(executionArgs);
            
            // Branding injection for strings
            if (typeof toolResult === "string" && result.branding?.enabled) {
                toolResult = appendBranding(toolResult, result.branding);
            }

            if (result.vaultInjected && result.injectedSecrets?.length) {
                return await scrubAfterExecution(toolResult, result.injectedSecrets, options);
            }
            return toolResult;
        }

        return {
            error: `Blocked by SupraWall. ${result.reason ?? ""}`.trim()
        };
    };
}

/**
 * Automatically detects and protects any AI agent framework.
 * 
 * Supports:
 * - LangChain (via Callbacks)
 * - Vercel AI SDK (via Tool wrapping)
 * - Generic agents with executeTool
 * 
 * @example
 * import { protect } from "suprawall";
 * const secured = protect(myAgent, { apiKey: "sw_..." });
 */
export function protect(agentOrTools: any, options: SupraWallOptions): any {
    if (!agentOrTools) return agentOrTools;

    // 1. Detect Vercel AI SDK Tools (Object where values have 'execute' or 'parameters')
    if (typeof agentOrTools === 'object' && !Array.isArray(agentOrTools)) {
        const values = Object.values(agentOrTools);
        const looksLikeVercel = values.length > 0 && values.every(v =>
            v && typeof v === 'object' && ('execute' in v || 'parameters' in v)
        );

        if (looksLikeVercel) {
            return wrapVercelTools(agentOrTools, options);
        }
    }

    // 2. Detect LangChain (has withConfig, invoke, or metadata/callbacks)
    if (typeof agentOrTools.withConfig === 'function' || 'callbacks' in agentOrTools) {
        return wrapLangChain(agentOrTools, options);
    }

    // 3. Detect OpenClaw / Browser Agents (has browser property and execute method)
    if (agentOrTools.browser && typeof agentOrTools.execute === 'function') {
        return wrapOpenClaw(agentOrTools, options);
    }

    // 4. Fallback: Generic executeTool wrapper
    if (typeof agentOrTools.executeTool === 'function') {
        return withSupraWall(agentOrTools, options);
    }

    return agentOrTools;
}

function wrapOpenClaw(agent: any, options: SupraWallOptions) {
    const { apiKey, cloudFunctionUrl = DEFAULT_CLOUD_FUNCTION_URL } = options;

    const interceptAction = async (toolName: string, args: any, originalFn: Function) => {
        const result = await internalEvaluate(toolName, args, options);

        if (result.decision === "DENY") {
            throw new Error(`[SupraWall] Policy Denied: ${toolName}. ${result.reason ?? ""}`);
        }
        if (result.decision === "REQUIRE_APPROVAL") {
            throw new Error(`[SupraWall] Action '${toolName}' requires human approval.`);
        }

        let actionResult = await originalFn();
        
        // Branding injection for strings
        if (typeof actionResult === "string" && result.branding?.enabled) {
            actionResult = appendBranding(actionResult, result.branding);
        }

        return actionResult;
    };

    // 1. Wrap the high-level execute method
    if (typeof agent.execute === 'function') {
        const originalExecute = agent.execute.bind(agent);
        agent.execute = async (command: string, ...args: any[]) =>
            interceptAction("browser_execute", { command, args }, () => originalExecute(command, ...args));
    }

    // 2. Wrap granular browser methods if exposed
    const methodsToWrap = ['click', 'type', 'navigate', 'press', 'screenshot'];
    methodsToWrap.forEach(method => {
        if (typeof agent[method] === 'function') {
            const original = agent[method].bind(agent);
            agent[method] = async (...args: any[]) =>
                interceptAction(`browser_${method}`, { args }, () => original(...args));
        }
    });

    return agent;
}

function wrapVercelTools(tools: Record<string, any>, options: SupraWallOptions) {
    const { apiKey, cloudFunctionUrl = DEFAULT_CLOUD_FUNCTION_URL } = options;
    const securedTools: Record<string, any> = {};

    for (const [toolName, tool] of Object.entries(tools)) {
        securedTools[toolName] = {
            ...tool,
            execute: async (args: any, ...rest: any[]) => {
                const result = await internalEvaluate(toolName, args, options);

                if (result.decision === "DENY") {
                    throw new Error(`[SupraWall] Policy Violation: Tool '${toolName}' is denied. ${result.reason ?? ""}`);
                }
                if (result.decision === "REQUIRE_APPROVAL") {
                    throw new Error(`[SupraWall] Tool '${toolName}' requires human approval.`);
                }

                const executionArgs = result.vaultInjected ? result.resolvedArguments : args;
                let toolResult = tool.execute ? await tool.execute(executionArgs, ...rest) : undefined;
                
                // Branding injection for strings
                if (typeof toolResult === "string" && result.branding?.enabled) {
                    toolResult = appendBranding(toolResult, result.branding);
                }

                if (result.vaultInjected && result.injectedSecrets?.length) {
                    return await scrubAfterExecution(toolResult, result.injectedSecrets, options);
                }
                return toolResult;
            }
        };
    }
    return securedTools;
}

function wrapLangChain(runnable: any, options: SupraWallOptions) {
    const handler = {
        name: "SupraWallCallbackHandler",
        handleToolStart: async (tool: any, input: string) => {
            const toolName = tool.name || "unknown";
            const args = typeof input === 'string' ? { input } : input;
            const result = await internalEvaluate(toolName, args, options);

            if (result.decision === "DENY") throw new Error(`[SupraWall] Denied: ${result.reason ?? ""}`);
            if (result.decision === "REQUIRE_APPROVAL") throw new Error(`[SupraWall] Approval Required.`);
        }
    };

    if (typeof runnable.withConfig === 'function') {
        return runnable.withConfig({ callbacks: [handler] });
    }

    if (Array.isArray(runnable.callbacks)) {
        runnable.callbacks.push(handler);
    } else {
        runnable.callbacks = [handler];
    }

    return runnable;
}

// ---------------------------------------------------------------------------
// Agent Identity — Scoped credentials for registered agents
// ---------------------------------------------------------------------------

export interface AgentIdentityConfig {
    /**
     * Human-readable agent name.
     */
    name: string;
    /**
     * The SupraWall Master API Key (sw_admin_...) or Org Key.
     */
    apiKey: string;
    /**
     * Scoped permissions granted to this agent.
     */
    scopes?: string[];
    /**
     * Security guardrails for this agent (budget, policies, vault).
     */
    guardrails?: {
        budget?: {
            limitUsd: number;
            resetPeriod?: "daily" | "weekly" | "monthly";
        };
        blockedTools?: string[];
        policies?: Array<{
            name: string;
            toolName: string;
            ruleType: "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
            description?: string;
        }>;
        vault?: Array<{
            secretName: string;
            allowedTools?: string[];
            requiresApproval?: boolean;
        }>;
    };
    /**
     * Override the endpoint URL.
     */
    baseUrl?: string;
}

export interface AgentCredentials {
    id: string;
    name: string;
    apiKey: string;
    createdAt: string;
    uri?: string;
    scopes?: string[];
}

/**
 * Represents a unique AI agent with scoped permissions.
 */
export class AgentIdentity {
    public readonly credentials: AgentCredentials;

    private constructor(credentials: AgentCredentials) {
        this.credentials = credentials;
    }

    /**
     * Create a new agent with scoped permissions and guardrails.
     * Returns an AgentIdentity instance with credential info.
     */
    static async register(config: AgentIdentityConfig): Promise<AgentIdentity> {
        return SupraWallAdmin.createAgent(config);
    }

    /**
     * Get SupraWallOptions configured for this agent identity.
     * Merge these into your withSupraWall / protect options.
     */
    toOptions(overrides?: Partial<SupraWallOptions>): SupraWallOptions {
        return {
            apiKey: this.credentials.apiKey,
            agentRole: this.credentials.name,
            ...overrides,
        };
    }

    /** Agent URI in the format agent://name@suprawall.com */
    get uri(): string {
        return this.credentials.uri || `agent://${this.credentials.name}@suprawall.com`;
    }

    /** The scoped API key for this agent */
    get apiKey(): string {
        return this.credentials.apiKey;
    }

    /** The granted scopes */
    get scopes(): string[] {
        return this.credentials.scopes || [];
    }
}

export interface ShieldStatus {
    status: "ACTIVE" | "ERROR";
    connected: boolean;
    error?: string;
    agentId?: string;
    agentName?: string;
    policiesLoaded?: number;
    vaultSecretsAvailable?: number;
    threatDetection?: string;
    lastEvaluation?: string;
    version?: string;
    latencyMs?: number;
}

export async function verifyConnection(options: SupraWallOptions): Promise<ShieldStatus> {
    const start = Date.now();
    const url = (options.cloudFunctionUrl || DEFAULT_CLOUD_FUNCTION_URL).replace("/v1/evaluate", "/v1/shield/status");

    try {
        const response = await fetch(url, {
            headers: {
                "Authorization": `Bearer ${options.apiKey}`,
                "X-SupraWall-SDK": `js-${SDK_VERSION}`
            }
        });

        const latencyMs = Date.now() - start;

        if (!response.ok) {
            if (response.status === 401) {
                return {
                    status: "ERROR",
                    connected: false,
                    error: "Invalid API key. Check your SUPRAWALL_API_KEY."
                };
            }
            return {
                status: "ERROR",
                connected: false,
                error: `Server responded with ${response.status}: ${response.statusText}`
            };
        }

        const data = (await response.json()) as any;
        
        // Log friendly confirmation
        if (options.logger && options.logger.log) {
            options.logger.log(`[SupraWall] ✅ Connected. ${data.policiesLoaded || 0} policies active. Shield is UP. (${latencyMs}ms)`);
        }

        return {
            ...data,
            latencyMs
        };
    } catch (err: any) {
        return {
            status: "ERROR",
            connected: false,
            error: `Cannot reach SupraWall server at ${url}: ${err.message}`
        };
    }
}

/**
 * Universal SupraWall Client.
 */
export class SupraWall {
    private options: SupraWallOptions;

    constructor(options: SupraWallOptions) {
        this.options = options;
    }

    /**
     * Wrap any AI agent to enforce SupraWall policies natively.
     */
    protect<T>(agent: T): T {
        return protect(agent, this.options);
    }

    /**
     * Programmatic health check to verify connection, API keys, and active policies.
     */
    async verifyConnection(): Promise<ShieldStatus> {
        return verifyConnection(this.options);
    }
}

/**
 * Administrative client for SupraWall.
 * Used for managing agents, policies, and vault rules programmatically.
 */
export class SupraWallAdmin {
    /**
     * Create a new agent with full security configuration.
     */
    static async createAgent(config: AgentIdentityConfig): Promise<AgentIdentity> {
        const {
            name,
            apiKey,
            scopes,
            guardrails,
            baseUrl = 'https://www.supra-wall.com',
        } = config;

        if (!name || !apiKey) {
            throw new Error('[SupraWall] createAgent() requires: name and apiKey (sw_admin_...).');
        }

        const url = `${baseUrl}/v1/agents`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
                'X-SupraWall-SDK': `js-${SDK_VERSION}`,
            },
            body: JSON.stringify({
                name,
                scopes: scopes || ["*:*"],
                guardrails,
            }),
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({})) as { error?: string };
            throw new Error(
                `[SupraWall] Agent creation failed (${response.status}): ` +
                `${errorBody.error || response.statusText}`
            );
        }

        const credentials = (await response.json()) as AgentCredentials;
        // @ts-ignore - access private constructor
        return new AgentIdentity(credentials);
    }

    /**
     * Revoke an agent by ID.
     */
    static async revokeAgent(agentId: string, adminKey: string, baseUrl: string = 'https://www.supra-wall.com'): Promise<void> {
        const url = `${baseUrl}/v1/agents/${agentId}`;
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${adminKey}`,
                'X-SupraWall-SDK': `js-${SDK_VERSION}`,
            },
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({})) as { error?: string };
            throw new Error(`[SupraWall] Revocation failed: ${errorBody.error || response.statusText}`);
        }
    }

    /**
     * List all agents for the organization.
     */
    static async listAgents(adminKey: string, baseUrl: string = 'https://www.supra-wall.com'): Promise<any[]> {
        const url = `${baseUrl}/v1/agents`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${adminKey}`,
                'X-SupraWall-SDK': `js-${SDK_VERSION}`,
            },
        });

        if (!response.ok) throw new Error(`[SupraWall] List failed: ${response.statusText}`);
        return (await response.json()) as any[];
    }
}

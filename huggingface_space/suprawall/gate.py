# Copyright 2026 SupraWall Contributors
# SPDX-License-Identifier: Apache-2.0

import functools
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal, Optional
import httpx

from .cost import estimate_cost, format_cost

DEFAULT_URL = "https://www.supra-wall.com/api/v1/evaluate"
SDK_VERSION = "1.0.0"
log = logging.getLogger("suprawall")

# ── In-memory trackers (Budget & Loops) ───────────────────────────────
_session_costs: dict = defaultdict(float)        # session_id -> cumulative USD
_session_iterations: dict = defaultdict(int)     # session_id -> total tool calls
_session_call_history: dict = defaultdict(list)  # session_id -> list of call sigs


# ---------------------------------------------------------------------------
# Budget control exceptions
# ---------------------------------------------------------------------------

class BudgetExceededError(Exception):
    """
    Raised when an agent session exceeds its configured cost budget.

    Attributes:
        limit_usd:  The configured hard cap in USD.
        actual_usd: The accumulated cost that triggered the cap.

    Example:
        try:
            result = gate.check("call_api", args, next_fn)
        except BudgetExceededError as e:
            print(f"Agent stopped: spent {e.actual_usd:.4f} / limit {e.limit_usd:.2f}")
    """
    def __init__(self, limit_usd: float, actual_usd: float):
        self.limit_usd = limit_usd
        self.actual_usd = actual_usd
        super().__init__(
            f"[SupraWall] Budget cap of {format_cost(limit_usd)} exceeded "
            f"(session spend: {format_cost(actual_usd)}). Agent halted."
        )

class SupraWallConnectionError(Exception):
    def __init__(self, message: str):
        super().__init__(f"\n[SupraWallConnectionError] {message}\n  → Docs: https://docs.supra-wall.com/troubleshooting/connection\n")

_has_verified_connection = False


class BudgetTracker:
    """
    Tracks accumulated cost for a single agent session and enforces limits.

    Usage:
        tracker = BudgetTracker(max_cost_usd=5.0, alert_usd=4.0)
        tracker.record(model="gpt-4o-mini", input_tokens=150, output_tokens=90)
        # Raises BudgetExceededError if over limit.
    """

    def __init__(
        self,
        max_cost_usd: Optional[float] = None,
        alert_usd: Optional[float] = None,
    ):
        self.max_cost_usd = max_cost_usd
        self.alert_usd = alert_usd
        self.session_cost: float = 0.0
        self._alert_fired: bool = False

    def record(
        self,
        model: str = "gpt-4o-mini",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: Optional[float] = None,
    ) -> float:
        """
        Record a single LLM call and enforce limits.

        Pass either `cost_usd` directly, or `model + input_tokens + output_tokens`
        for automatic estimation.

        Returns the incremental cost added (in USD).
        Raises BudgetExceededError if the hard cap is breached.
        """
        if cost_usd is None:
            cost_usd = estimate_cost(model, input_tokens, output_tokens)

        self.session_cost += cost_usd

        # Fire soft alert (once per session)
        if (
            self.alert_usd is not None
            and not self._alert_fired
            and self.session_cost >= self.alert_usd
        ):
            self._alert_fired = True
            log.warning(
                f"[SupraWall] Budget alert: session spend {format_cost(self.session_cost)} "
                f">= alert threshold {format_cost(self.alert_usd)}."
            )

        # Enforce hard cap
        if self.max_cost_usd is not None and self.session_cost >= self.max_cost_usd:
            raise BudgetExceededError(
                limit_usd=self.max_cost_usd,
                actual_usd=self.session_cost,
            )

        return cost_usd

    def reset(self) -> None:
        """Reset session cost (e.g. start a new agent run)."""
        self.session_cost = 0.0
        self._alert_fired = False

    @property
    def summary(self) -> str:
        """Human-readable cost summary for logs."""
        limit = format_cost(self.max_cost_usd) if self.max_cost_usd else "unlimited"
        return f"Session spend: {format_cost(self.session_cost)} / {limit}"


@dataclass
class SupraWallOptions:
    """
    Configuration for SupraWall.

    Only api_key is required. All other fields have sensible defaults.

    Example:
        options = SupraWallOptions(
            api_key="sw_your_key_here",
            max_cost_usd=5.00,      # Hard stop at $5 per session
            budget_alert_usd=4.00,  # Warn at $4
        )
    """
    api_key: str
    cloud_function_url: str = DEFAULT_URL
    on_network_error: Literal["fail-open", "fail-closed"] = "fail-open"
    timeout: float = 5.0
    # --- Budget & Safety (Phase 1 & 2) ---
    max_cost_usd: Optional[float] = None        # Hard cap per session in USD.
    budget_alert_usd: Optional[float] = None    # Soft alert threshold in USD.
    session_id: Optional[str] = None            # Groups calls for cost tracking
    agent_role: Optional[str] = None            # e.g. "researcher", "writer"
    max_iterations: Optional[int] = None       # Hard stop after N tool calls
    loop_detection: bool = False               # Detect repeated identical calls
    loop_threshold: int = 3                    # Block if same tool called N times consec.
    # --- Human-in-the-Loop (Phase 3) ---
    dashboard_api_url: str = "https://supra-wall.com"
    approval_timeout: int = 300                 # Max seconds to wait for human
    approval_poll_interval: int = 2            # Seconds between polls
    # --- Vault (JIT Secret Injection) ---
    tenant_id: str = "default-tenant"          # Tenant ID for vault lookups
    vault_scrub_url: Optional[str] = None      # Override URL for vault scrub endpoint
    # --- OpenRouter Attribution ---
    openrouter_attribution: Optional[dict] = None  # { "app_url": "...", "app_title": "...", "categories": "..." }


def _check_budget(options: SupraWallOptions) -> Optional[dict]:
    """
    Checks the current session cost against configured budget caps.
    Returns a DENY decision dict if the cap has been hit, else None.
    """
    if options.max_cost_usd is None:
        return None

    session_id = options.session_id or options.api_key
    if session_id not in _session_costs:
        _session_costs[session_id] = 0.0
    current = float(_session_costs[session_id])

    if options.budget_alert_usd is not None and current >= options.budget_alert_usd:
        log.warning(
            f"[SupraWall] 💰 Budget alert: ${current:.4f} of ${options.max_cost_usd:.2f} cap used "
            f"(session: {session_id!r})"
        )

    if options.max_cost_usd is not None and current >= options.max_cost_usd:
        return {
            "decision": "DENY",
            "reason": (
                f"Budget cap reached: ${current:.4f} >= ${options.max_cost_usd:.2f} limit. "
                "Agent stopped automatically to prevent overspend."
            ),
        }
    return None


def _check_loops(tool_name: str, args: Any, options: SupraWallOptions) -> Optional[dict]:
    """
    Checks for infinite loops and iteration limits.
    Returns a DENY decision dict if a safety breach is detected.
    """
    session_id = options.session_id or options.api_key

    # 1. Iteration Limit (Circuit Breaker)
    if options.max_iterations is not None:
        _session_iterations[session_id] += 1
        if _session_iterations[session_id] > options.max_iterations:
            return {
                "decision": "DENY",
                "reason": f"Circuit breaker: Exceeded maximum tool iterations ({options.max_iterations}).",
            }

    # 2. Loop Detection (Consecutive Identical Calls)
    if options.loop_detection:
        # Create a stable signature of the call
        call_sig = (tool_name, json.dumps(args, sort_keys=True, default=str))
        history = _session_call_history[session_id]
        history.append(call_sig)

        # Look at the last N elements
        recent = history[-options.loop_threshold :]
        if len(recent) == options.loop_threshold and len(set(recent)) == 1:
            return {
                "decision": "DENY",
                "reason": (
                    f"Loop detected: Tool '{tool_name}' called {options.loop_threshold}× "
                    "consecutively with identical arguments. Blocked for safety."
                ),
            }

    return None


def _record_cost(options: SupraWallOptions, response: dict) -> None:
    """Accumulates the call cost returned by the server into the session tracker."""
    cost = response.get("estimated_cost_usd")
    if cost and options.max_cost_usd is not None:
        session_id = options.session_id or options.api_key
        _session_costs[session_id] = float(_session_costs[session_id]) + float(cost)
        log.debug(
            f"[SupraWall] Cost recorded: +${cost:.6f} "
            f"(session total: ${_session_costs[session_id]:.4f})"
        )


def _derive_scrub_url(options: SupraWallOptions) -> str:
    if getattr(options, "vault_scrub_url", None):
        return options.vault_scrub_url
    return options.cloud_function_url.replace("/v1/evaluate", "/v1/scrub")


def _scrub_response(tool_response: Any, injected_secrets: list, options: SupraWallOptions) -> Any:
    """Calls server scrub endpoint to strip vault secret traces from response."""
    scrub_url = _derive_scrub_url(options)
    try:
        with httpx.Client(timeout=options.timeout) as client:
            resp = client.post(
                scrub_url,
                json={
                    "tenantId": options.tenant_id,
                    "secretNames": injected_secrets,
                    "toolResponse": tool_response,
                },
            )
            if resp.status_code == 200:
                return resp.json().get("scrubbedResponse", tool_response)
    except Exception as e:
        log.warning(f"[SupraWall] Vault scrub endpoint unreachable: {e} — returning redacted response")
    return "[Response redacted — vault scrub unavailable]"


async def _scrub_response_async(tool_response: Any, injected_secrets: list, options: SupraWallOptions) -> Any:
    """Async version of _scrub_response."""
    scrub_url = _derive_scrub_url(options)
    try:
        async with httpx.AsyncClient(timeout=options.timeout) as client:
            resp = await client.post(
                scrub_url,
                json={
                    "tenantId": options.tenant_id,
                    "secretNames": injected_secrets,
                    "toolResponse": tool_response,
                },
            )
            if resp.status_code == 200:
                return resp.json().get("scrubbedResponse", tool_response)
    except Exception as e:
        log.warning(f"[SupraWall] Vault scrub endpoint unreachable: {e} — returning redacted response")
    return "[Response redacted — vault scrub unavailable]"


def _poll_approval(request_id: str, options: SupraWallOptions) -> dict:
    """Blocks and polls the dashboard until a human approves or denies."""
    import time
    start_time = time.time()
    poll_url = f"{options.dashboard_api_url}/api/v1/approvals/{request_id}"
    log.warning(f"[SupraWall] ⏳ Action requires human intervention. Waiting for approval...")
    log.warning(f"[SupraWall] 👉 Approve at: {options.dashboard_api_url}/approvals")

    while time.time() - start_time < options.approval_timeout:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(poll_url)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    if status == "approved":
                        log.info("[SupraWall] ✅ Action APPROVED by human. Resuming...")
                        return {"decision": "ALLOW"}
                    if status == "denied":
                        log.error("[SupraWall] ❌ Action DENIED by human.")
                        return {"decision": "DENY", "reason": "Explicitly denied by human administrator."}
        except Exception as e:
            log.debug(f"[SupraWall] Polling error: {e}")
        time.sleep(options.approval_poll_interval)

    return {"decision": "DENY", "reason": f"Approval timed out after {options.approval_timeout}s."}


async def _poll_approval_async(request_id: str, options: SupraWallOptions) -> dict:
    """Non-blocking poll of the dashboard until a human approves or denies."""
    import asyncio, time
    start_time = time.time()
    poll_url = f"{options.dashboard_api_url}/api/v1/approvals/{request_id}"
    log.warning(f"[SupraWall] ⏳ Action requires human intervention. Waiting for approval...")
    log.warning(f"[SupraWall] 👉 Approve at: {options.dashboard_api_url}/approvals")

    while time.time() - start_time < options.approval_timeout:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(poll_url)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    if status == "approved":
                        log.info("[SupraWall] ✅ Action APPROVED by human. Resuming...")
                        return {"decision": "ALLOW"}
                    if status == "denied":
                        log.error("[SupraWall] ❌ Action DENIED by human.")
                        return {"decision": "DENY", "reason": "Explicitly denied by human administrator."}
        except Exception as e:
            log.debug(f"[SupraWall] Polling error: {e}")
        await asyncio.sleep(options.approval_poll_interval)

    return {"decision": "DENY", "reason": f"Approval timed out after {options.approval_timeout}s."}


def _evaluate(tool_name: str, args: Any, options: SupraWallOptions, source: str = "direct-sdk") -> dict:
    """Makes a synchronous policy check call to SupraWall."""
    # ── Safety Checks: Client-side fast-reject ──
    budget_block = _check_budget(options)
    if budget_block: return budget_block

    safety_block = _check_loops(tool_name, args, options)
    if safety_block: return safety_block

    session_id = options.session_id or options.api_key
    
    headers = {"X-SupraWall-SDK": f"python-{SDK_VERSION}"}
    if options.openrouter_attribution:
        attr = options.openrouter_attribution
        if attr.get("app_url"):
            headers["HTTP-Referer"] = attr["app_url"]
        if attr.get("app_title"):
            headers["X-Title"] = attr["app_title"]
        if attr.get("categories"):
            headers["X-OpenRouter-Categories"] = attr["categories"]

    global _has_verified_connection
    try:
        with httpx.Client(timeout=options.timeout) as client:
            resp = client.post(
                options.cloud_function_url,
                json={
                    "apiKey": options.api_key,
                    "toolName": tool_name,
                    "arguments": args or {},
                    "agentId": session_id,
                    "tenantId": options.tenant_id,
                    "sessionId": session_id,
                    "agentRole": options.agent_role,
                    "source": source,
                },
                headers=headers,
            )
    except httpx.RequestError as e:
        if not _has_verified_connection:
            raise SupraWallConnectionError(f"Cannot reach SupraWall server at {options.cloud_function_url}.")
        raise e

    if resp.status_code == 401 and not _has_verified_connection:
        raise SupraWallConnectionError(f"Invalid API key. Check your SUPRAWALL_API_KEY.\n  API Key: {options.api_key[:8]}...")
        
    if resp.status_code == 401:
        raise ValueError(
            "[SupraWall] Unauthorized. Check your API key at "
            "https://supra-wall.com/"
        )
    if resp.status_code == 429:
        return {"decision": "DENY", "reason": "Rate limit exceeded."}
    if resp.status_code == 403:
        return {"decision": "DENY", "reason": "Blocked by policy (HTTP 403)."}
    resp.raise_for_status()
    
    _has_verified_connection = True
    data = resp.json()
    _record_cost(options, data)

    # ── Handle Human-in-the-Loop Polling ──
    if data.get("decision") == "REQUIRE_APPROVAL" and data.get("requestId"):
        return _poll_approval(data["requestId"], options)

    return data


async def _evaluate_async(tool_name: str, args: Any, options: SupraWallOptions, source: str = "direct-sdk") -> dict:
    """Makes an async policy check call to SupraWall."""
    # ── Safety Checks: Client-side fast-reject ──
    budget_block = _check_budget(options)
    if budget_block: return budget_block

    safety_block = _check_loops(tool_name, args, options)
    if safety_block: return safety_block

    session_id = options.session_id or options.api_key

    headers = {"X-SupraWall-SDK": f"python-{SDK_VERSION}"}
    if options.openrouter_attribution:
        attr = options.openrouter_attribution
        if attr.get("app_url"):
            headers["HTTP-Referer"] = attr["app_url"]
        if attr.get("app_title"):
            headers["X-Title"] = attr["app_title"]
        if attr.get("categories"):
            headers["X-OpenRouter-Categories"] = attr["categories"]

    global _has_verified_connection
    try:
        async with httpx.AsyncClient(timeout=options.timeout) as client:
            resp = await client.post(
                options.cloud_function_url,
                json={
                    "apiKey": options.api_key,
                    "toolName": tool_name,
                    "arguments": args or {},
                    "agentId": session_id,
                    "tenantId": options.tenant_id,
                    "sessionId": session_id,
                    "agentRole": options.agent_role,
                    "source": source,
                },
                headers=headers,
            )
    except httpx.RequestError as e:
        if not _has_verified_connection:
            raise SupraWallConnectionError(f"Cannot reach SupraWall server at {options.cloud_function_url}.")
        raise e

    if resp.status_code == 401 and not _has_verified_connection:
        raise SupraWallConnectionError(f"Invalid API key. Check your SUPRAWALL_API_KEY.\n  API Key: {options.api_key[:8]}...")
        
    if resp.status_code == 401:
        raise ValueError(
            "[SupraWall] Unauthorized. Check your API key at "
            "https://supra-wall.com/"
        )
    if resp.status_code == 429:
        return {"decision": "DENY", "reason": "Rate limit exceeded."}
    if resp.status_code == 403:
        return {"decision": "DENY", "reason": "Blocked by policy (HTTP 403)."}
    resp.raise_for_status()
    
    _has_verified_connection = True
    data = resp.json()
    _record_cost(options, data)

    # ── Handle Human-in-the-Loop Polling ──
    if data.get("decision") == "REQUIRE_APPROVAL" and data.get("requestId"):
        return await _poll_approval_async(data["requestId"], options)

    return data


def _handle_decision(decision: str, reason: Optional[str], tool_name: str,
                     semantic_score: Optional[float] = None,
                     semantic_reasoning: Optional[str] = None) -> Optional[str]:
    """
    Returns an error string if the action should be blocked, or None if allowed.
    None = proceed with original call.

    If the response includes Layer 2 semantic analysis fields (semanticScore,
    semanticReasoning), these are logged for observability.
    """
    if semantic_score is not None:
        log.info(f"[SupraWall] Semantic score for '{tool_name}': {semantic_score:.2f}"
                 + (f" — {semantic_reasoning}" if semantic_reasoning else ""))
    if decision == "ALLOW":
        return None
    if decision == "DENY":
        log.warning(f"[SupraWall] DENIED '{tool_name}'. Reason: {reason or 'Policy violation.'}")
        return f"ERROR: Action blocked by SupraWall. {reason or ''}".strip()
    if decision == "REQUIRE_APPROVAL":
        log.warning(f"[SupraWall] PAUSED '{tool_name}'. Human approval required.")
        return (
            "ACTION PAUSED: This action requires human approval. "
            "Check your SupraWall dashboard at https://supra-wall.com/"
        )
    log.error(f"[SupraWall] Unknown decision '{decision}' received.")
    return "ERROR: Unknown SupraWall decision."


def with_suprawall(agent: Any, options: SupraWallOptions) -> Any:
    """
    Wraps any AI agent with SupraWall security enforcement.

    Intercepts the agent's primary execution method (run, invoke, or __call__)
    and checks every tool call against your policies before execution.

    Works with: LangChain, CrewAI, AutoGen, custom agents.
    For OpenAI Agents SDK, use wrap_openai_agent() instead.
    For LangChain tool-level enforcement, use SupraWallLangChainCallback.

    Args:
        agent:   Any agent object with a run, invoke, or __call__ method.
        options: SupraWallOptions — only api_key is required.

    Returns:
        The same agent instance, now protected by SupraWall.

    Example:
        from suprawall import with_suprawall, SupraWallOptions

        secured = with_suprawall(my_agent, SupraWallOptions(
            api_key="sw_your_key_here"
        ))
        result = secured.run("delete_file", {"path": "/etc/passwd"})
    """
    if not options.api_key.startswith(("sw_", "swc_", "ag_")):
        raise ValueError(
            f"[SupraWall] Invalid API key: '{options.api_key}'.\n"
            "  Get your free key at https://supra-wall.com/\n"
            "  Expected format: sw_xxxxxxxxxxxxxxxx"
        )

    # Detect which method to wrap: run > invoke > __call__
    method_name = None
    for candidate in ("run", "invoke", "__call__"):
        if callable(getattr(agent, candidate, None)):
            method_name = candidate
            break

    if method_name is None:
        raise ValueError(
            "[SupraWall] Could not find a callable method on this agent. "
            "Agent must have a 'run', 'invoke', or '__call__' method."
        )

    original_method = getattr(agent, method_name)
    is_async = hasattr(original_method, "__wrapped__") or (
        hasattr(original_method, "__func__") and
        hasattr(original_method.__func__, "__wrapped__")
    )

    # Try to detect if it's a coroutine function
    import asyncio
    import inspect
    method_is_coroutine = inspect.iscoroutinefunction(original_method)

    if method_is_coroutine:
        @functools.wraps(original_method)
        async def secured_async(tool_name: str = "", args: Any = None, *a, **kw):
            try:
                data = await _evaluate_async(tool_name, args, options)
                blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name, data.get("semanticScore"), data.get("semanticReasoning"))
                if blocked is not None:
                    return blocked
                return await original_method(tool_name, args, *a, **kw)
            except httpx.RequestError as e:
                log.error(f"[SupraWall] Network error: {e}")
                if options.on_network_error == "fail-closed":
                    return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
                log.warning("[SupraWall] Proceeding without policy check (fail-open). "
                            "Set on_network_error='fail-closed' in production.")
                return await original_method(tool_name, args, *a, **kw)

        setattr(agent, method_name, secured_async)
    else:
        @functools.wraps(original_method)
        def secured_sync(tool_name: str = "", args: Any = None, *a, **kw):
            try:
                data = _evaluate(tool_name, args, options)
                blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name, data.get("semanticScore"), data.get("semanticReasoning"))
                if blocked is not None:
                    return blocked
                return original_method(tool_name, args, *a, **kw)
            except httpx.RequestError as e:
                log.error(f"[SupraWall] Network error: {e}")
                if options.on_network_error == "fail-closed":
                    return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
                log.warning("[SupraWall] Proceeding without policy check (fail-open). "
                            "Set on_network_error='fail-closed' in production.")
                return original_method(tool_name, args, *a, **kw)

        setattr(agent, method_name, secured_sync)

    return agent

def protect(agent_or_runnable: Any, options: SupraWallOptions) -> Any:
    """
    Universal entry point for the SupraWall SDK.
    protects any AI agent framework in Python.

    Supports:
    - LangChain (BaseRunnables, AgentExecutors)
    - CrewAI (Agents and Crews)
    - AutoGen (Conversable Agents)
    
    Args:
        agent_or_runnable: The agent instance to protect.
        options: SupraWallOptions for configuration.
    """
    if agent_or_runnable is None:
        return None

    # 1. Detect LangChain (has with_config or callbacks attribute)
    if hasattr(agent_or_runnable, "with_config") or hasattr(agent_or_runnable, "callbacks"):
        try:
            from suprawall_langchain import wrap_langchain
            return wrap_langchain(agent_or_runnable, options)
        except ImportError:
            # Fallback to generic if suprawall-langchain is missing
            log.debug("[SupraWall] LangChain detected but 'suprawall-langchain' not installed.")

    # 2. Detect CrewAI (Agent or Crew)
    try:
        from crewai import Agent as CrewAgent, Crew as CrewSwarm
        if isinstance(agent_or_runnable, (CrewAgent, CrewSwarm)):
            return wrap_crewai(agent_or_runnable, options)
    except ImportError:
        pass

    # 3. Detect AutoGen (ConversableAgent)
    try:
        from autogen import ConversableAgent
        if isinstance(agent_or_runnable, ConversableAgent):
            return wrap_autogen(agent_or_runnable, options)
    except ImportError:
        pass

    # 4. Detect smolagents
    try:
        from smolagents import Agent as SmolAgent
        if isinstance(agent_or_runnable, SmolAgent):
            from .smolagents import wrap_smolagents
            return wrap_smolagents(agent_or_runnable, options)
    except ImportError:
        pass

    # 5. Fallback: Generic executeTool/run wrapper
    return with_suprawall(agent_or_runnable, options)

def wrap_crewai(agent_or_crew: Any, options: SupraWallOptions) -> Any:
    """Specialized wrapper for CrewAI objects."""
    # Since CrewAI uses LangChain AgentExecutor under the hood,
    # we can often just inject a callback.
    if hasattr(agent_or_crew, "agent_executor") and agent_or_crew.agent_executor:
        try:
            from suprawall_langchain import wrap_langchain
            wrap_langchain(agent_or_crew.agent_executor, options)
        except ImportError:
            pass
    elif hasattr(agent_or_crew, "agents"): # If it's a Crew swarm
        for agent in agent_or_crew.agents:
            wrap_crewai(agent, options)
    return agent_or_crew

def wrap_autogen(agent: Any, options: SupraWallOptions) -> Any:
    """Specialized wrapper for AutoGen framework."""
    import inspect
    original_generate = agent.generate_reply
    is_coroutine = inspect.iscoroutinefunction(original_generate)

    if is_coroutine:
        @functools.wraps(original_generate)
        async def secured_generate(*args, **kwargs):
            # Extract tool name from AutoGen's message structure
            tool_name = kwargs.get("function_call", {}).get("name", "autogen_reply")
            try:
                data = await _evaluate_async(tool_name, kwargs, options, source="autogen")
                blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name)
                if blocked is not None:
                    return blocked
            except httpx.RequestError as e:
                log.error(f"[SupraWall] Network error during AutoGen evaluation: {e}")
                if options.on_network_error == "fail-closed":
                    return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
            return await original_generate(*args, **kwargs)
        agent.generate_reply = secured_generate
    else:
        @functools.wraps(original_generate)
        def secured_generate_sync(*args, **kwargs):
            tool_name = kwargs.get("function_call", {}).get("name", "autogen_reply")
            try:
                data = _evaluate(tool_name, kwargs, options, source="autogen")
                blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name)
                if blocked is not None:
                    return blocked
            except httpx.RequestError as e:
                log.error(f"[SupraWall] Network error during AutoGen evaluation: {e}")
                if options.on_network_error == "fail-closed":
                    return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
            return original_generate(*args, **kwargs)
        agent.generate_reply = secured_generate_sync

    return agent


class SupraWallMiddleware:
    """
    Framework-agnostic middleware for MCP servers and custom agent pipelines.

    Use this when you control the tool dispatch loop directly and want to
    insert SupraWall as a middleware layer.

    Example (sync):
        from suprawall import SupraWallMiddleware, SupraWallOptions

        gate = SupraWallMiddleware(SupraWallOptions(api_key="ag_your_key"))

        def my_tool_dispatcher(tool_name, args):
            return gate.check(tool_name, args, lambda: run_tool(tool_name, args))

    Example (async):
        async def my_tool_dispatcher(tool_name, args):
            return await gate.check_async(tool_name, args,
                                          lambda: run_tool_async(tool_name, args))

    Example (as decorator):
        @gate.guard(tool_name="send_email")
        def send_email(to, subject, body):
            ...
    """

    def __init__(self, options: SupraWallOptions):
        self.options = options
        self.budget = BudgetTracker(
            max_cost_usd=options.max_cost_usd,
            alert_usd=options.budget_alert_usd,
        )

    def check(self, tool_name: str, args: Any, next_fn: callable) -> Any:
        """Synchronous policy check. Calls next_fn() if allowed."""
        self.budget.record()
        try:
            data = _evaluate(tool_name, args, self.options)
            blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name, data.get("semanticScore"), data.get("semanticReasoning"))
            if blocked is not None:
                return blocked
            result = next_fn()
            if data.get("vaultInjected") and data.get("injectedSecrets"):
                result = _scrub_response(result, data["injectedSecrets"], self.options)
            log.debug(f"[SupraWall] {self.budget.summary}")
            return result
        except httpx.RequestError as e:
            log.error(f"[SupraWall] Network error: {e}")
            if self.options.on_network_error == "fail-closed":
                return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
            return next_fn()

    async def check_async(self, tool_name: str, args: Any, next_fn: callable) -> Any:
        """Async policy check. Awaits next_fn() if allowed."""
        import inspect
        self.budget.record()
        try:
            data = await _evaluate_async(tool_name, args, self.options)
            blocked = _handle_decision(data.get("decision"), data.get("reason"), tool_name, data.get("semanticScore"), data.get("semanticReasoning"))
            if blocked is not None:
                return blocked
            result = next_fn()
            if inspect.isawaitable(result):
                result = await result
            if data.get("vaultInjected") and data.get("injectedSecrets"):
                result = await _scrub_response_async(result, data["injectedSecrets"], self.options)
            log.debug(f"[SupraWall] {self.budget.summary}")
            return result
        except httpx.RequestError as e:
            log.error(f"[SupraWall] Network error: {e}")
            if self.options.on_network_error == "fail-closed":
                return "ERROR: SupraWall unreachable. Action blocked (fail-closed)."
            result = next_fn()
            if inspect.isawaitable(result):
                return await result
            return result

    def guard(self, tool_name: Optional[str] = None):
        """
        Decorator that wraps a function with SupraWall enforcement.
        The tool_name defaults to the function name if not provided.

        Example:
            @gate.guard()
            def delete_user(user_id: str):
                ...

            @gate.guard(tool_name="send_email")
            def notify(address: str, message: str):
                ...
        """
        def decorator(fn):
            import inspect
            resolved_name = tool_name or fn.__name__

            if inspect.iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def async_wrapper(*args, **kwargs):
                    return await self.check_async(
                        resolved_name,
                        {"args": args, "kwargs": kwargs},
                        lambda: fn(*args, **kwargs),
                    )
                return async_wrapper
            else:
                @functools.wraps(fn)
                def sync_wrapper(*args, **kwargs):
                    return self.check(
                        resolved_name,
                        {"args": args, "kwargs": kwargs},
                        lambda: fn(*args, **kwargs),
                    )
                return sync_wrapper
        return decorator

class SupraWall:
    """
    The main entry point for the SupraWall Python SDK.
    
    Provides a simple, Stripe-like interface for securing AI agents.
    
    Example:
        from suprawall import SupraWall
        
        supra = SupraWall("ag_your_key")
        agent = supra.protect(my_agent)
    """
    def __init__(self, api_key: str, **kwargs):
        self.options = SupraWallOptions(api_key=api_key, **kwargs)
        self.middleware = SupraWallMiddleware(self.options)
        self.__version__ = SDK_VERSION

    def protect(self, agent_or_runnable: Any) -> Any:
        """
        Secures any supported AI agent framework (LangChain, CrewAI, AutoGen, etc.)
        """
        return protect(agent_or_runnable, self.options)

    def health(self) -> dict:
        """
        Checks connectivity to the SupraWall security cloud.
        """
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self.options.dashboard_api_url}/api/health")
                return {
                    "status": "ok" if resp.status_code == 200 else "error",
                    "code": resp.status_code,
                    "version": self.__version__
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "version": self.__version__}

    def verify_connection(self) -> dict:
        """
        Programmatic health check to verify connection, API keys, and active policies.
        """
        import time
        start = time.time()
        url = self.options.cloud_function_url.replace("/v1/evaluate", "/v1/shield/status")
        
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.options.api_key}",
                        "X-SupraWall-SDK": f"python-{SDK_VERSION}"
                    }
                )
            
            latency_ms = int((time.time() - start) * 1000)
            
            if resp.status_code == 401:
                return {
                    "status": "ERROR", 
                    "connected": False, 
                    "error": "Invalid API key. Check your SUPRAWALL_API_KEY."
                }
                
            resp.raise_for_status()
                
            data = resp.json()
            data["latencyMs"] = latency_ms
            
            policies_loaded = data.get("policiesLoaded", 0)
            log.info(f"[SupraWall] ✅ Connected. {policies_loaded} policies active. Shield is UP. ({latency_ms}ms)")
            
            global _has_verified_connection
            _has_verified_connection = True
            
            return data
            
        except httpx.RequestError as e:
            return {
                "status": "ERROR", 
                "connected": False, 
                "error": f"Cannot reach SupraWall server at {url}: {e}"
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "ERROR", 
                "connected": False, 
                "error": f"Server responded with error: {e.response.status_code}"
            }

    @property
    def guard(self):
        """Access to the functional middleware guard decorator."""
        return self.middleware.guard

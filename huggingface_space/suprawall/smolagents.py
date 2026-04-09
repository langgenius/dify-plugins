# Copyright 2026 SupraWall Contributors
# SPDX-License-Identifier: Apache-2.0

import functools
import inspect
import logging
from typing import Any, Optional
from .gate import _evaluate, _evaluate_async, _handle_decision, SupraWallOptions

log = logging.getLogger("suprawall")

def wrap_smolagents(agent: Any, options: SupraWallOptions) -> Any:
    """
    Wraps a smolagents Agent (CodeAgent or ToolCallingAgent) with SupraWall security.
    
    This replaces the tool execution logic to ensure every tool call is validated
    by SupraWall before running.
    
    Args:
        agent: The smolagents agent instance.
        options: SupraWallOptions for configuration.
    """
    if not hasattr(agent, "tools"):
        log.warning("[SupraWall] Agent does not appear to be a smolagents agent (no 'tools' attribute).")
        return agent

    # smolagents tools are stored in a dictionary: tool_name -> tool_object
    for tool_name, tool in agent.tools.items():
        original_forward = tool.forward

        if inspect.iscoroutinefunction(original_forward):
            # Async tools — use default arg binding to capture current loop values
            @functools.wraps(original_forward)
            async def secured_forward_async(
                *args,
                _sw_tool_name=tool_name,
                _sw_original=original_forward,
                **kwargs,
            ):
                eval_args = kwargs.copy()
                if args:
                    eval_args["_args"] = args

                data = await _evaluate_async(_sw_tool_name, eval_args, options, source="smolagents")
                blocked = _handle_decision(
                    data.get("decision"),
                    data.get("reason"),
                    _sw_tool_name,
                    data.get("semanticScore"),
                    data.get("semanticReasoning"),
                )

                if blocked is not None:
                    return blocked

                return await _sw_original(*args, **kwargs)

            tool.forward = secured_forward_async
        else:
            # Sync tools — use default arg binding to capture current loop values
            @functools.wraps(original_forward)
            def secured_forward(
                *args,
                _sw_tool_name=tool_name,
                _sw_original=original_forward,
                **kwargs,
            ):
                eval_args = kwargs.copy()
                if args:
                    eval_args["_args"] = args

                data = _evaluate(_sw_tool_name, eval_args, options, source="smolagents")
                blocked = _handle_decision(
                    data.get("decision"),
                    data.get("reason"),
                    _sw_tool_name,
                    data.get("semanticScore"),
                    data.get("semanticReasoning"),
                )

                if blocked is not None:
                    return blocked

                return _sw_original(*args, **kwargs)

            tool.forward = secured_forward

    log.info(f"[SupraWall] Secured {len(agent.tools)} tools for smolagents agent.")
    return agent

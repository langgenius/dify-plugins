# Copyright 2026 SupraWall Contributors
# SPDX-License-Identifier: Apache-2.0

"""
SupraWall integration for OpenAI Agents SDK.
"""

import logging
from typing import Any
from .gate import SupraWallOptions, with_suprawall

log = logging.getLogger("suprawall")

def wrap_openai_agent(agent: Any, options: SupraWallOptions) -> Any:
    """
    Wraps an OpenAI agent with SupraWall security enforcement.

    Falls back to the generic with_suprawall() wrapper which intercepts
    the agent's run/invoke/__call__ method.

    For full OpenAI Agents SDK integration, install ``suprawall[openai]``.
    """
    log.info("[SupraWall] Wrapping OpenAI agent via generic wrapper.")
    return with_suprawall(agent, options)

"""Destructive action confirmation gating.

Uses MCP elicitation when available, falls back to requiring confirm=True.
"""

from __future__ import annotations

import logging
from typing import Any

from .exceptions import ToolError

logger = logging.getLogger(__name__)


async def gate_destructive_action(
    ctx: Any,
    action: str,
    destructive_actions: set[str],
    confirm: bool,
    description: str | None = None,
) -> None:
    """Gate a destructive action behind user confirmation.

    Args:
        ctx: MCP context (may be None in tests or non-interactive flows).
        action: The action being performed (e.g., "stop", "kill").
        destructive_actions: Set of action names that require confirmation.
        confirm: Whether the caller explicitly confirmed the action.
        description: Optional human-readable description of the action.
    """
    if action not in destructive_actions:
        return

    if confirm:
        return

    # TODO: When MCP elicitation is widely supported, add ctx.elicit() path here.
    # For now, require confirm=True as the only confirmation mechanism.

    desc = f" ({description})" if description else ""
    raise ToolError(
        f"Action '{action}'{desc} is destructive and requires confirm=True. "
        f"Pass confirm=True to proceed."
    )

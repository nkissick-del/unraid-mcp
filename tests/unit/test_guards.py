"""Tests for destructive action confirmation gating."""

import pytest

from unraid_mcp.core.exceptions import ToolError


class TestGateDestructiveAction:
    """Tests for destructive action confirmation gating."""

    @pytest.mark.asyncio
    async def test_non_destructive_action_passes(self):
        from unraid_mcp.core.guards import gate_destructive_action

        # "start" is not in the destructive set — should pass
        await gate_destructive_action(
            ctx=None,
            action="start",
            destructive_actions={"stop", "kill"},
            confirm=False,
        )

    @pytest.mark.asyncio
    async def test_destructive_with_confirm_passes(self):
        from unraid_mcp.core.guards import gate_destructive_action

        await gate_destructive_action(
            ctx=None,
            action="stop",
            destructive_actions={"stop", "kill"},
            confirm=True,
        )

    @pytest.mark.asyncio
    async def test_destructive_without_confirm_raises(self):
        from unraid_mcp.core.guards import gate_destructive_action

        with pytest.raises(ToolError, match="requires confirm=True"):
            await gate_destructive_action(
                ctx=None,
                action="stop",
                destructive_actions={"stop", "kill"},
                confirm=False,
            )

    @pytest.mark.asyncio
    async def test_destructive_with_description(self):
        from unraid_mcp.core.guards import gate_destructive_action

        with pytest.raises(ToolError, match="requires confirm=True"):
            await gate_destructive_action(
                ctx=None,
                action="kill",
                destructive_actions={"stop", "kill"},
                confirm=False,
                description="Force-kill the container",
            )

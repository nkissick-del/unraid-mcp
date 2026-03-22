"""Parity check management tools.

This module is gated under the 'parity' module and disabled by default.
Parity check operations affect data integrity verification on the array.
"""

import asyncio
from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.constants import (
    PARITY_CHECK_ACTIONS,
    PARITY_OPERATION_SETTLE_DELAY_S,
    PARITY_STATE_BACKOFF_FACTOR,
    PARITY_STATE_INITIAL_DELAY_S,
    PARITY_STATE_MAX_RETRIES,
)
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import poll_with_backoff, validate_enum
from .queries.parity import PARITY_CHECK_MUTATIONS, PARITY_STATUS_QUERY


def register_parity_tools(mcp: FastMCP) -> None:
    """Register parity check tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    @tool_error_handler("manage parity check")
    async def manage_parity_check(
        action: str,
        correcting: bool = False,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Manages parity check operations: START, PAUSE, RESUME, or CANCEL.

        START requires confirm=True as a safety gate. The 'correcting' parameter
        only applies to START and determines whether errors are corrected during the check.

        Args:
            action: Parity check action - 'START', 'PAUSE', 'RESUME', or 'CANCEL'
            correcting: Whether to correct errors during check (only for START, default False)
            confirm: Safety gate for START - must be True to start a parity check

        Returns:
            Dict containing mutation result, current parity status, and success indicator
        """
        validated_action = validate_enum(action.upper(), PARITY_CHECK_ACTIONS, "action")

        if validated_action == "START" and not confirm:
            raise ToolError(
                "confirm must be True to start a parity check. "
                "This operation can take many hours and impacts array performance."
            )

        mutation = PARITY_CHECK_MUTATIONS[validated_action]
        variables: dict[str, Any] | None = (
            {"correct": correcting} if validated_action == "START" else None
        )

        response = await make_graphql_request(mutation, variables)

        parity_check = response.get("parityCheck")
        if parity_check is None:
            raise ToolError(f"Failed to {validated_action.lower()} parity check")
        mutation_result = parity_check.get(validated_action.lower())
        if mutation_result is None:
            raise ToolError(f"Failed to {validated_action.lower()} parity check")

        # Wait for state to settle, then poll for updated status
        await asyncio.sleep(PARITY_OPERATION_SETTLE_DELAY_S)

        async def _query_parity_status() -> dict[str, Any] | None:
            status_resp = await make_graphql_request(PARITY_STATUS_QUERY)
            array_data = status_resp.get("array")
            if isinstance(array_data, dict):
                return array_data
            return None

        polled = await poll_with_backoff(
            query_fn=_query_parity_status,
            max_retries=PARITY_STATE_MAX_RETRIES,
            initial_delay=PARITY_STATE_INITIAL_DELAY_S,
            backoff_factor=PARITY_STATE_BACKOFF_FACTOR,
            operation_name=f"parity {validated_action.lower()} state poll",
        )

        return {
            "mutation_result": mutation_result,
            "current_status": polled,
            "success": polled is not None,
            "message": (
                f"Parity check {validated_action.lower()} operation completed"
                if polled is not None
                else f"Parity check {validated_action.lower()} initiated but status verification timed out"
            ),
        }

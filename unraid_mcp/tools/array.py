"""Array management tools.

This module is gated under the 'array' module and disabled by default.
Array start/stop operations are CRITICAL and can cause data loss if misused.
"""

import asyncio
from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.constants import (
    ARRAY_OPERATION_SETTLE_DELAY_S,
    ARRAY_STATE_BACKOFF_FACTOR,
    ARRAY_STATE_INITIAL_DELAY_S,
    ARRAY_STATE_MAX_RETRIES,
)
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import poll_with_backoff, validate_enum
from .queries.array import ARRAY_SET_STATE_MUTATION, ARRAY_STATUS_QUERY


def register_array_tools(mcp: FastMCP) -> None:
    """Register array management tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    @tool_error_handler("manage array")
    async def manage_array(desired_state: str) -> dict[str, Any]:
        """Starts or stops the Unraid disk array. THIS IS A CRITICAL OPERATION.

        WARNING: Stopping the array will make all shares and data inaccessible.
        Starting the array initiates parity sync if needed. Use with extreme caution.

        Args:
            desired_state: Target array state - 'START' or 'STOP'

        Returns:
            Dict containing the array state after the operation
        """
        validated_state = validate_enum(desired_state.upper(), ["START", "STOP"], "desired_state")

        variables: dict[str, Any] = {"input": {"desiredState": validated_state}}
        response = await make_graphql_request(ARRAY_SET_STATE_MUTATION, variables)

        set_state_result = response.get("array", {}).get("setState")
        if not set_state_result:
            raise ToolError(f"Failed to {validated_state.lower()} the array")

        # Wait for state to settle, then poll for updated status
        await asyncio.sleep(ARRAY_OPERATION_SETTLE_DELAY_S)

        async def _query_array_status() -> dict[str, Any] | None:
            status_resp = await make_graphql_request(ARRAY_STATUS_QUERY)
            status = status_resp.get("array", {}).get("status")
            if isinstance(status, dict):
                return status
            return None

        polled = await poll_with_backoff(
            query_fn=_query_array_status,
            max_retries=ARRAY_STATE_MAX_RETRIES,
            initial_delay=ARRAY_STATE_INITIAL_DELAY_S,
            backoff_factor=ARRAY_STATE_BACKOFF_FACTOR,
            operation_name=f"array {validated_state.lower()} state poll",
        )

        return {
            "mutation_result": set_state_result,
            "current_status": polled,
            "success": polled is not None,
            "message": (
                f"Array {validated_state.lower()} operation completed"
                if polled is not None
                else f"Array {validated_state.lower()} initiated but status verification timed out"
            ),
        }

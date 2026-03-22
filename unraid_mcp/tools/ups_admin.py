"""UPS administration tools.

This module is gated under the 'ups-admin' module and disabled by default.
It provides UPS daemon configuration operations.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import require_confirm, validate_input_dict
from .queries.ups_admin import CONFIGURE_UPS_MUTATION


def register_ups_admin_tools(mcp: FastMCP) -> None:
    """Register UPS admin tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    @tool_error_handler("configure UPS")
    async def configure_ups(
        input_config: dict[str, Any],
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Configures the UPS daemon settings. Requires confirm=True.

        Use get_ups_configuration() first to see current settings and available field names.
        Accepts a dict of configuration fields (service, upsCable, upsType, device, etc.).

        Args:
            input_config: Dict of UPS configuration fields to set
            confirm: Safety gate - must be True to proceed

        Returns:
            Dict containing the updated UPS configuration
        """
        require_confirm(confirm, "configure UPS settings")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"config": input_config}
        response = await make_graphql_request(CONFIGURE_UPS_MUTATION, variables)

        result = response.get("configureUps")
        if not result:
            raise ToolError("Failed to configure UPS")

        return {
            "success": True,
            "configuration": result,
            "message": "UPS configuration updated successfully",
        }

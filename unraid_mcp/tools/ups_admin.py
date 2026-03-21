"""UPS administration tools.

This module is gated under the 'ups-admin' module and disabled by default.
It provides UPS daemon configuration operations.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from .queries.ups_admin import CONFIGURE_UPS_MUTATION


def register_ups_admin_tools(mcp: FastMCP) -> None:
    """Register UPS admin tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
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
        if not confirm:
            raise ToolError(
                "confirm must be True to configure UPS settings. "
                "Incorrect UPS configuration may affect shutdown behavior during power events."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing configure_ups")

            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(CONFIGURE_UPS_MUTATION, variables)

            result = response.get("configureUps")
            if not result:
                raise ToolError("Failed to configure UPS")

            return {
                "success": True,
                "configuration": result,
                "message": "UPS configuration updated successfully",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in configure_ups: {e}", exc_info=True)
            raise ToolError(f"Failed to configure UPS: {str(e)}") from e

    logger.info("UPS admin tools registered successfully")

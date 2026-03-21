"""Onboarding tools for managing the Unraid setup wizard.

This module is gated under the 'onboarding' module and disabled by default.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from .queries.onboarding import (
    BYPASS_ONBOARDING_MUTATION,
    CLEAR_ONBOARDING_OVERRIDE_MUTATION,
    CLOSE_ONBOARDING_MUTATION,
    COMPLETE_ONBOARDING_MUTATION,
    CREATE_INTERNAL_BOOT_POOL_MUTATION,
    IS_FRESH_INSTALL_QUERY,
    OPEN_ONBOARDING_MUTATION,
    REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION,
    RESET_ONBOARDING_MUTATION,
    RESUME_ONBOARDING_MUTATION,
    SET_ONBOARDING_OVERRIDE_MUTATION,
)


def register_onboarding_tools(mcp: FastMCP) -> None:
    """Register onboarding tools with the FastMCP instance."""

    @mcp.tool()
    async def is_fresh_install() -> dict[str, Any]:
        """Checks whether this Unraid server is a fresh installation."""
        try:
            logger.info("Executing is_fresh_install")
            response = await make_graphql_request(IS_FRESH_INSTALL_QUERY)
            return {"freshInstall": response.get("freshInstall", False)}
        except Exception as e:
            logger.error(f"Error in is_fresh_install: {e}", exc_info=True)
            raise ToolError(f"Failed to check fresh install status: {str(e)}") from e

    @mcp.tool()
    async def complete_onboarding() -> dict[str, Any]:
        """Marks the onboarding process as complete. Idempotent."""
        try:
            logger.info("Executing complete_onboarding")
            response = await make_graphql_request(COMPLETE_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("complete", {})
            return {"success": result.get("success", False), "action": "complete"}
        except Exception as e:
            logger.error(f"Error in complete_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to complete onboarding: {str(e)}") from e

    @mcp.tool()
    async def reset_onboarding() -> dict[str, Any]:
        """Resets the onboarding process to start over. Idempotent."""
        try:
            logger.info("Executing reset_onboarding")
            response = await make_graphql_request(RESET_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("reset", {})
            return {"success": result.get("success", False), "action": "reset"}
        except Exception as e:
            logger.error(f"Error in reset_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to reset onboarding: {str(e)}") from e

    @mcp.tool()
    async def open_onboarding() -> dict[str, Any]:
        """Opens the onboarding wizard. Idempotent."""
        try:
            logger.info("Executing open_onboarding")
            response = await make_graphql_request(OPEN_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("open", {})
            return {"success": result.get("success", False), "action": "open"}
        except Exception as e:
            logger.error(f"Error in open_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to open onboarding: {str(e)}") from e

    @mcp.tool()
    async def close_onboarding() -> dict[str, Any]:
        """Closes the onboarding wizard. Idempotent."""
        try:
            logger.info("Executing close_onboarding")
            response = await make_graphql_request(CLOSE_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("close", {})
            return {"success": result.get("success", False), "action": "close"}
        except Exception as e:
            logger.error(f"Error in close_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to close onboarding: {str(e)}") from e

    @mcp.tool()
    async def bypass_onboarding() -> dict[str, Any]:
        """Bypasses the onboarding process entirely. Idempotent."""
        try:
            logger.info("Executing bypass_onboarding")
            response = await make_graphql_request(BYPASS_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("bypass", {})
            return {"success": result.get("success", False), "action": "bypass"}
        except Exception as e:
            logger.error(f"Error in bypass_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to bypass onboarding: {str(e)}") from e

    @mcp.tool()
    async def resume_onboarding() -> dict[str, Any]:
        """Resumes a previously paused onboarding process. Idempotent."""
        try:
            logger.info("Executing resume_onboarding")
            response = await make_graphql_request(RESUME_ONBOARDING_MUTATION)
            result = response.get("onboarding", {}).get("resume", {})
            return {"success": result.get("success", False), "action": "resume"}
        except Exception as e:
            logger.error(f"Error in resume_onboarding: {e}", exc_info=True)
            raise ToolError(f"Failed to resume onboarding: {str(e)}") from e

    @mcp.tool()
    async def set_onboarding_override(input_config: dict[str, Any]) -> dict[str, Any]:
        """Sets an onboarding override configuration. Idempotent.

        Args:
            input_config: Dict of onboarding override fields to set
        """
        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing set_onboarding_override")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(SET_ONBOARDING_OVERRIDE_MUTATION, variables)
            result = response.get("onboarding", {}).get("setOverride", {})
            return {"success": result.get("success", False), "action": "setOverride"}
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in set_onboarding_override: {e}", exc_info=True)
            raise ToolError(f"Failed to set onboarding override: {str(e)}") from e

    @mcp.tool()
    async def clear_onboarding_override() -> dict[str, Any]:
        """Clears any onboarding override configuration. Idempotent."""
        try:
            logger.info("Executing clear_onboarding_override")
            response = await make_graphql_request(CLEAR_ONBOARDING_OVERRIDE_MUTATION)
            result = response.get("onboarding", {}).get("clearOverride", {})
            return {"success": result.get("success", False), "action": "clearOverride"}
        except Exception as e:
            logger.error(f"Error in clear_onboarding_override: {e}", exc_info=True)
            raise ToolError(f"Failed to clear onboarding override: {str(e)}") from e

    @mcp.tool()
    async def create_internal_boot_pool(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Creates the internal boot pool. Requires confirm=True.

        WARNING: This creates system-level storage infrastructure. Ensure you
        understand the implications before proceeding.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to create the internal boot pool. "
                "This creates system-level storage infrastructure."
            )

        try:
            logger.info("Executing create_internal_boot_pool")
            response = await make_graphql_request(CREATE_INTERNAL_BOOT_POOL_MUTATION)
            result = response.get("onboarding", {}).get("createInternalBootPool", {})
            return {
                "success": result.get("success", False),
                "action": "createInternalBootPool",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in create_internal_boot_pool: {e}", exc_info=True)
            raise ToolError(f"Failed to create internal boot pool: {str(e)}") from e

    @mcp.tool()
    async def refresh_internal_boot_context() -> dict[str, Any]:
        """Refreshes the internal boot context information."""
        try:
            logger.info("Executing refresh_internal_boot_context")
            response = await make_graphql_request(REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION)
            result = response.get("onboarding", {}).get("refreshInternalBootContext", {})
            return {
                "success": result.get("success", False),
                "action": "refreshInternalBootContext",
            }
        except Exception as e:
            logger.error(f"Error in refresh_internal_boot_context: {e}", exc_info=True)
            raise ToolError(f"Failed to refresh internal boot context: {str(e)}") from e

    logger.info("Onboarding tools registered successfully")

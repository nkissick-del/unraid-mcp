"""Onboarding tools for managing the Unraid setup wizard.

This module is gated under the 'onboarding' module and disabled by default.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.utils import require_confirm, validate_input_dict
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
    @tool_error_handler("check fresh install status")
    async def is_fresh_install() -> dict[str, Any]:
        """Checks whether this Unraid server is a fresh installation."""
        response = await make_graphql_request(IS_FRESH_INSTALL_QUERY)
        return {"freshInstall": response.get("isFreshInstall", False)}

    @mcp.tool()
    @tool_error_handler("complete onboarding")
    async def complete_onboarding() -> dict[str, Any]:
        """Marks the onboarding process as complete. Idempotent."""
        response = await make_graphql_request(COMPLETE_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("completeOnboarding", {})
        return {"success": result.get("success", False), "action": "complete"}

    @mcp.tool()
    @tool_error_handler("reset onboarding")
    async def reset_onboarding() -> dict[str, Any]:
        """Resets the onboarding process to start over. Idempotent."""
        response = await make_graphql_request(RESET_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("resetOnboarding", {})
        return {"success": result.get("success", False), "action": "reset"}

    @mcp.tool()
    @tool_error_handler("open onboarding")
    async def open_onboarding() -> dict[str, Any]:
        """Opens the onboarding wizard. Idempotent."""
        response = await make_graphql_request(OPEN_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("openOnboarding", {})
        return {"success": result.get("success", False), "action": "open"}

    @mcp.tool()
    @tool_error_handler("close onboarding")
    async def close_onboarding() -> dict[str, Any]:
        """Closes the onboarding wizard. Idempotent."""
        response = await make_graphql_request(CLOSE_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("closeOnboarding", {})
        return {"success": result.get("success", False), "action": "close"}

    @mcp.tool()
    @tool_error_handler("bypass onboarding")
    async def bypass_onboarding() -> dict[str, Any]:
        """Bypasses the onboarding process entirely. Idempotent."""
        response = await make_graphql_request(BYPASS_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("bypassOnboarding", {})
        return {"success": result.get("success", False), "action": "bypass"}

    @mcp.tool()
    @tool_error_handler("resume onboarding")
    async def resume_onboarding() -> dict[str, Any]:
        """Resumes a previously paused onboarding process. Idempotent."""
        response = await make_graphql_request(RESUME_ONBOARDING_MUTATION)
        result = response.get("onboarding", {}).get("resumeOnboarding", {})
        return {"success": result.get("success", False), "action": "resume"}

    @mcp.tool()
    @tool_error_handler("set onboarding override")
    async def set_onboarding_override(input_config: dict[str, Any]) -> dict[str, Any]:
        """Sets an onboarding override configuration. Idempotent.

        Args:
            input_config: Dict of onboarding override fields to set
        """
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(SET_ONBOARDING_OVERRIDE_MUTATION, variables)
        result = response.get("onboarding", {}).get("setOnboardingOverride", {})
        return {"success": result.get("success", False), "action": "setOverride"}

    @mcp.tool()
    @tool_error_handler("clear onboarding override")
    async def clear_onboarding_override() -> dict[str, Any]:
        """Clears any onboarding override configuration. Idempotent."""
        response = await make_graphql_request(CLEAR_ONBOARDING_OVERRIDE_MUTATION)
        result = response.get("onboarding", {}).get("clearOnboardingOverride", {})
        return {"success": result.get("success", False), "action": "clearOverride"}

    @mcp.tool()
    @tool_error_handler("create internal boot pool")
    async def create_internal_boot_pool(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Creates the internal boot pool. Requires confirm=True.

        WARNING: This creates system-level storage infrastructure. Ensure you
        understand the implications before proceeding.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "create the internal boot pool")

        response = await make_graphql_request(CREATE_INTERNAL_BOOT_POOL_MUTATION)
        result = response.get("onboarding", {}).get("createInternalBootPool", {})
        return {
            "success": result.get("success", False),
            "action": "createInternalBootPool",
        }

    @mcp.tool()
    @tool_error_handler("refresh internal boot context")
    async def refresh_internal_boot_context() -> dict[str, Any]:
        """Refreshes the internal boot context information."""
        response = await make_graphql_request(REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION)
        result = response.get("onboarding", {}).get("refreshInternalBootContext", {})
        return {
            "success": result.get("success", False),
            "action": "refreshInternalBootContext",
        }

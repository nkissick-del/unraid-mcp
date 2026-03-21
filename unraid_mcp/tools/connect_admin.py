"""Unraid Connect administration tools.

This module is gated under the 'connect' module and disabled by default.
It provides tools for managing Unraid Connect sign-in, remote access, and cloud settings.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, require_confirm, validate_input_dict
from .queries.connect_admin import (
    CONNECT_SIGN_IN_MUTATION,
    CONNECT_SIGN_OUT_MUTATION,
    ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION,
    GET_CLOUD_INFO_QUERY,
    GET_CONNECT_INFO_QUERY,
    GET_REMOTE_ACCESS_QUERY,
    SETUP_REMOTE_ACCESS_MUTATION,
    UPDATE_API_SETTINGS_MUTATION,
)


def register_connect_admin_tools(mcp: FastMCP) -> None:
    """Register Connect administration tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("retrieve Connect info")
    async def get_connect_info() -> dict[str, Any]:
        """Retrieves Unraid Connect status and sign-in information."""
        response = await make_graphql_request(GET_CONNECT_INFO_QUERY)
        return ensure_dict(response.get("connect", {}))

    @mcp.tool()
    @tool_error_handler("retrieve remote access info")
    async def get_remote_access() -> dict[str, Any]:
        """Retrieves remote access configuration and status."""
        response = await make_graphql_request(GET_REMOTE_ACCESS_QUERY)
        return ensure_dict(response.get("remoteAccess", {}))

    @mcp.tool()
    @tool_error_handler("retrieve cloud info")
    async def get_cloud_info() -> dict[str, Any]:
        """Retrieves cloud connection information and status."""
        response = await make_graphql_request(GET_CLOUD_INFO_QUERY)
        return ensure_dict(response.get("cloud", {}))

    @mcp.tool()
    @tool_error_handler("update API settings")
    async def update_api_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates API settings for the Unraid server. Requires confirm=True.

        Args:
            input_config: Dict of API settings to update
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update API settings")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_API_SETTINGS_MUTATION, variables)
        result = response.get("updateApiSettings", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": "API settings updated" if success else "Failed to update API settings",
        }

    @mcp.tool()
    @tool_error_handler("sign in to Connect")
    async def connect_sign_in(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Signs in to Unraid Connect. Requires confirm=True.

        Args:
            input_config: Dict with sign-in credentials
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "sign in to Unraid Connect")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(CONNECT_SIGN_IN_MUTATION, variables)
        result = response.get("connectSignIn", {})
        return {
            "success": result.get("success", False),
            "message": "Signed in to Unraid Connect",
        }

    @mcp.tool()
    @tool_error_handler("sign out of Connect")
    async def connect_sign_out(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Signs out of Unraid Connect. Requires confirm=True.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "sign out of Unraid Connect")

        response = await make_graphql_request(CONNECT_SIGN_OUT_MUTATION)
        result = response.get("connectSignOut", {})
        return {
            "success": result.get("success", False),
            "message": "Signed out of Unraid Connect",
        }

    @mcp.tool()
    @tool_error_handler("setup remote access")
    async def setup_remote_access(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Configures remote access settings. Requires confirm=True.

        Args:
            input_config: Dict of remote access settings (enabled, type, port, etc.)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "setup remote access")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(SETUP_REMOTE_ACCESS_MUTATION, variables)
        result = response.get("setupRemoteAccess")
        if not result:
            raise ToolError("Failed to setup remote access")
        return {
            "success": True,
            "remoteAccess": result,
            "message": "Remote access configured",
        }

    @mcp.tool()
    @tool_error_handler("enable dynamic remote access")
    async def enable_dynamic_remote_access(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Enables dynamic remote access with automatic port management. Requires confirm=True.

        Args:
            input_config: Dict of dynamic remote access settings
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "enable dynamic remote access")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION, variables)
        result = response.get("enableDynamicRemoteAccess")
        if not result:
            raise ToolError("Failed to enable dynamic remote access")
        return {
            "success": True,
            "remoteAccess": result,
            "message": "Dynamic remote access enabled",
        }

    logger.info("Connect admin tools registered successfully")

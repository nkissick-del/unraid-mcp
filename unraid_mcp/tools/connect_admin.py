"""Unraid Connect administration tools.

This module is gated under the 'connect' module and disabled by default.
It provides tools for managing Unraid Connect sign-in, remote access, and cloud settings.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict
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
    async def get_connect_info() -> dict[str, Any]:
        """Retrieves Unraid Connect status and sign-in information."""
        try:
            logger.info("Executing get_connect_info")
            response = await make_graphql_request(GET_CONNECT_INFO_QUERY)
            return ensure_dict(response.get("connect", {}))
        except Exception as e:
            logger.error(f"Error in get_connect_info: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve Connect info: {str(e)}") from e

    @mcp.tool()
    async def get_remote_access() -> dict[str, Any]:
        """Retrieves remote access configuration and status."""
        try:
            logger.info("Executing get_remote_access")
            response = await make_graphql_request(GET_REMOTE_ACCESS_QUERY)
            return ensure_dict(response.get("remoteAccess", {}))
        except Exception as e:
            logger.error(f"Error in get_remote_access: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve remote access info: {str(e)}") from e

    @mcp.tool()
    async def get_cloud_info() -> dict[str, Any]:
        """Retrieves cloud connection information and status."""
        try:
            logger.info("Executing get_cloud_info")
            response = await make_graphql_request(GET_CLOUD_INFO_QUERY)
            return ensure_dict(response.get("cloud", {}))
        except Exception as e:
            logger.error(f"Error in get_cloud_info: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve cloud info: {str(e)}") from e

    @mcp.tool()
    async def update_api_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates API settings for the Unraid server. Requires confirm=True.

        Args:
            input_config: Dict of API settings to update
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update API settings. "
                "Changing API settings may affect external integrations."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_api_settings")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(UPDATE_API_SETTINGS_MUTATION, variables)
            result = response.get("updateApiSettings", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": "API settings updated" if success else "Failed to update API settings",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_api_settings: {e}", exc_info=True)
            raise ToolError(f"Failed to update API settings: {str(e)}") from e

    @mcp.tool()
    async def connect_sign_in(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Signs in to Unraid Connect. Requires confirm=True.

        Args:
            input_config: Dict with sign-in credentials
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to sign in to Unraid Connect. "
                "This will authenticate the server with Unraid's cloud services."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing connect_sign_in")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(CONNECT_SIGN_IN_MUTATION, variables)
            result = response.get("connectSignIn", {})
            return {
                "success": result.get("success", False),
                "message": "Signed in to Unraid Connect",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error("Error in connect_sign_in", exc_info=False)
            raise ToolError(f"Failed to sign in to Connect: {str(e)}") from e

    @mcp.tool()
    async def connect_sign_out(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Signs out of Unraid Connect. Requires confirm=True.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to sign out of Unraid Connect. "
                "This will disconnect the server from Unraid's cloud services."
            )

        try:
            logger.info("Executing connect_sign_out")
            response = await make_graphql_request(CONNECT_SIGN_OUT_MUTATION)
            result = response.get("connectSignOut", {})
            return {
                "success": result.get("success", False),
                "message": "Signed out of Unraid Connect",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in connect_sign_out: {e}", exc_info=True)
            raise ToolError(f"Failed to sign out of Connect: {str(e)}") from e

    @mcp.tool()
    async def setup_remote_access(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Configures remote access settings. Requires confirm=True.

        Args:
            input_config: Dict of remote access settings (enabled, type, port, etc.)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to setup remote access. "
                "This may expose the server to external network access."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing setup_remote_access")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in setup_remote_access: {e}", exc_info=True)
            raise ToolError(f"Failed to setup remote access: {str(e)}") from e

    @mcp.tool()
    async def enable_dynamic_remote_access(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Enables dynamic remote access with automatic port management. Requires confirm=True.

        Args:
            input_config: Dict of dynamic remote access settings
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to enable dynamic remote access. "
                "This may expose the server to external network access."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing enable_dynamic_remote_access")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in enable_dynamic_remote_access: {e}", exc_info=True)
            raise ToolError(f"Failed to enable dynamic remote access: {str(e)}") from e

    logger.info("Connect admin tools registered successfully")

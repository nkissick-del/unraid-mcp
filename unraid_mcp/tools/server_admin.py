"""Server administration tools.

This module is gated under the 'server-admin' module and disabled by default.
It provides tools for managing server identity, SSH, settings, temperature, time, and backups.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import require_confirm, validate_input_dict
from .queries.server_admin import (
    INITIATE_FLASH_BACKUP_MUTATION,
    UPDATE_SERVER_IDENTITY_MUTATION,
    UPDATE_SETTINGS_MUTATION,
    UPDATE_SSH_SETTINGS_MUTATION,
    UPDATE_SYSTEM_TIME_MUTATION,
    UPDATE_TEMPERATURE_CONFIG_MUTATION,
)


def register_server_admin_tools(mcp: FastMCP) -> None:
    """Register server administration tools with the FastMCP instance."""

    @mcp.tool()
    @tool_error_handler("update server identity")
    async def update_server_identity(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates the server identity (name, comment, description). Requires confirm=True.

        Args:
            input_config: Dict of server identity fields to update
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update server identity")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {
            "name": input_config.get("name", ""),
            "comment": input_config.get("comment"),
            "sysModel": input_config.get("sysModel"),
        }
        response = await make_graphql_request(UPDATE_SERVER_IDENTITY_MUTATION, variables)
        result = response.get("updateServerIdentity")
        if not result:
            raise ToolError("Failed to update server identity")
        return {
            "success": True,
            "identity": result,
            "message": "Server identity updated",
        }

    @mcp.tool()
    @tool_error_handler("update SSH settings")
    async def update_ssh_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates SSH server settings. Requires confirm=True.

        Args:
            input_config: Dict of SSH settings (enabled, port, allowRootLogin, etc.)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update SSH settings")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_SSH_SETTINGS_MUTATION, variables)
        result = response.get("updateSshSettings")
        if not result:
            raise ToolError("Failed to update SSH settings")
        return {
            "success": True,
            "sshSettings": result,
            "message": "SSH settings updated",
        }

    @mcp.tool()
    @tool_error_handler("update settings")
    async def update_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates general server settings. Requires confirm=True.

        Args:
            input_config: Dict of settings to update
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update server settings")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_SETTINGS_MUTATION, variables)
        result = response.get("updateSettings")
        if not result:
            raise ToolError("Failed to update settings")
        return {
            "success": result.get("success", True),
            "message": "Server settings updated",
        }

    @mcp.tool()
    @tool_error_handler("update temperature config")
    async def update_temperature_config(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates temperature monitoring configuration. Requires confirm=True.

        Args:
            input_config: Dict of temperature config (unit, warning, critical thresholds)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update temperature configuration")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_TEMPERATURE_CONFIG_MUTATION, variables)
        result = response.get("updateTemperatureConfig")
        if not result:
            raise ToolError("Failed to update temperature config")
        return {
            "success": True,
            "temperatureConfig": result,
            "message": "Temperature configuration updated",
        }

    @mcp.tool()
    @tool_error_handler("update system time")
    async def update_system_time(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates system time settings (timezone, NTP). Requires confirm=True.

        Args:
            input_config: Dict of time settings (timezone, ntpEnabled, ntpServer)
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "update system time settings")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(UPDATE_SYSTEM_TIME_MUTATION, variables)
        result = response.get("updateSystemTime")
        if not result:
            raise ToolError("Failed to update system time")
        return {
            "success": True,
            "timeSettings": result,
            "message": "System time settings updated",
        }

    @mcp.tool()
    @tool_error_handler("initiate flash backup")
    async def initiate_flash_backup(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Initiates a backup of the USB flash drive. Requires confirm=True.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "initiate a flash backup")

        variables: dict[str, Any] = {"input": {}}
        response = await make_graphql_request(INITIATE_FLASH_BACKUP_MUTATION, variables)
        result = response.get("initiateFlashBackup")
        if not result:
            raise ToolError("Failed to initiate flash backup")
        return {
            "success": result.get("success", True),
            "message": "Flash backup initiated",
        }

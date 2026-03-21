"""Server administration tools.

This module is gated under the 'server-admin' module and disabled by default.
It provides tools for managing server identity, SSH, settings, temperature, time, and backups.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
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
    async def update_server_identity(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates the server identity (name, comment, description). Requires confirm=True.

        Args:
            input_config: Dict of server identity fields to update
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update server identity. "
                "This changes how the server is identified on the network."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_server_identity")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(UPDATE_SERVER_IDENTITY_MUTATION, variables)
            result = response.get("updateServerIdentity")
            if not result:
                raise ToolError("Failed to update server identity")
            return {
                "success": True,
                "identity": result,
                "message": "Server identity updated",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_server_identity: {e}", exc_info=True)
            raise ToolError(f"Failed to update server identity: {str(e)}") from e

    @mcp.tool()
    async def update_ssh_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates SSH server settings. Requires confirm=True.

        Args:
            input_config: Dict of SSH settings (enabled, port, allowRootLogin, etc.)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update SSH settings. "
                "Incorrect SSH configuration may lock you out of the server."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_ssh_settings")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_ssh_settings: {e}", exc_info=True)
            raise ToolError(f"Failed to update SSH settings: {str(e)}") from e

    @mcp.tool()
    async def update_settings(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates general server settings. Requires confirm=True.

        Args:
            input_config: Dict of settings to update
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update server settings. "
                "Changing settings may affect server behavior."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_settings")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(UPDATE_SETTINGS_MUTATION, variables)
            result = response.get("updateSettings")
            if not result:
                raise ToolError("Failed to update settings")
            return {
                "success": result.get("success", True),
                "message": "Server settings updated",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_settings: {e}", exc_info=True)
            raise ToolError(f"Failed to update settings: {str(e)}") from e

    @mcp.tool()
    async def update_temperature_config(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates temperature monitoring configuration. Requires confirm=True.

        Args:
            input_config: Dict of temperature config (unit, warning, critical thresholds)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update temperature configuration. "
                "Incorrect thresholds may cause unnecessary alerts or miss real issues."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_temperature_config")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_temperature_config: {e}", exc_info=True)
            raise ToolError(f"Failed to update temperature config: {str(e)}") from e

    @mcp.tool()
    async def update_system_time(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Updates system time settings (timezone, NTP). Requires confirm=True.

        Args:
            input_config: Dict of time settings (timezone, ntpEnabled, ntpServer)
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update system time settings. "
                "Incorrect time settings may affect scheduled tasks and logging."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_system_time")
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
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_system_time: {e}", exc_info=True)
            raise ToolError(f"Failed to update system time: {str(e)}") from e

    @mcp.tool()
    async def initiate_flash_backup(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Initiates a backup of the USB flash drive. Requires confirm=True.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to initiate a flash backup. "
                "This will create a backup of the boot USB flash drive."
            )

        try:
            logger.info("Executing initiate_flash_backup")
            response = await make_graphql_request(INITIATE_FLASH_BACKUP_MUTATION)
            result = response.get("initiateFlashBackup")
            if not result:
                raise ToolError("Failed to initiate flash backup")
            return {
                "success": result.get("success", True),
                "message": "Flash backup initiated",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in initiate_flash_backup: {e}", exc_info=True)
            raise ToolError(f"Failed to initiate flash backup: {str(e)}") from e

    logger.info("Server admin tools registered successfully")

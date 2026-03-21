"""Plugin management tools.

This module is gated under the 'plugins' module and disabled by default.
It provides tools for listing, installing, and removing Unraid plugins.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list
from .queries.plugins import (
    ADD_PLUGIN_MUTATION,
    GET_PLUGIN_INSTALL_OPERATION_QUERY,
    INSTALL_PLUGIN_MUTATION,
    LIST_INSTALLED_UNRAID_PLUGINS_QUERY,
    LIST_PLUGIN_INSTALL_OPERATIONS_QUERY,
    LIST_PLUGINS_QUERY,
    REMOVE_PLUGIN_MUTATION,
)


def register_plugins_tools(mcp: FastMCP) -> None:
    """Register plugin tools with the FastMCP instance."""

    @mcp.tool()
    async def list_plugins() -> dict[str, Any]:
        """Lists all available plugins with their status, version, and metadata."""
        try:
            logger.info("Executing list_plugins")
            response = await make_graphql_request(LIST_PLUGINS_QUERY)
            plugins = ensure_list(response.get("plugins", []))
            return {"count": len(plugins), "plugins": plugins}
        except Exception as e:
            logger.error(f"Error in list_plugins: {e}", exc_info=True)
            raise ToolError(f"Failed to list plugins: {str(e)}") from e

    @mcp.tool()
    async def list_installed_unraid_plugins() -> dict[str, Any]:
        """Lists only the currently installed Unraid plugins."""
        try:
            logger.info("Executing list_installed_unraid_plugins")
            response = await make_graphql_request(LIST_INSTALLED_UNRAID_PLUGINS_QUERY)
            plugins = ensure_list(response.get("installedUnraidPlugins", []))
            return {"count": len(plugins), "plugins": plugins}
        except Exception as e:
            logger.error(f"Error in list_installed_unraid_plugins: {e}", exc_info=True)
            raise ToolError(f"Failed to list installed plugins: {str(e)}") from e

    @mcp.tool()
    async def get_plugin_install_operation(
        operation_id: str,
    ) -> dict[str, Any]:
        """Gets the status of a specific plugin install operation.

        Args:
            operation_id: The ID of the install operation to check
        """
        if not operation_id or not isinstance(operation_id, str):
            raise ToolError("operation_id must be a non-empty string")

        try:
            logger.info(f"Executing get_plugin_install_operation: {operation_id}")
            variables: dict[str, Any] = {"operationId": operation_id}
            response = await make_graphql_request(GET_PLUGIN_INSTALL_OPERATION_QUERY, variables)
            return ensure_dict(response.get("pluginInstallOperation", {}))
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in get_plugin_install_operation: {e}", exc_info=True)
            raise ToolError(f"Failed to get plugin install operation: {str(e)}") from e

    @mcp.tool()
    async def list_plugin_install_operations() -> dict[str, Any]:
        """Lists all plugin install operations and their statuses."""
        try:
            logger.info("Executing list_plugin_install_operations")
            response = await make_graphql_request(LIST_PLUGIN_INSTALL_OPERATIONS_QUERY)
            operations = ensure_list(response.get("pluginInstallOperations", []))
            return {"count": len(operations), "operations": operations}
        except Exception as e:
            logger.error(f"Error in list_plugin_install_operations: {e}", exc_info=True)
            raise ToolError(f"Failed to list plugin install operations: {str(e)}") from e

    @mcp.tool()
    async def add_plugin(url: str, confirm: bool = False) -> dict[str, Any]:
        """Adds a plugin from a URL. Requires confirm=True.

        Args:
            url: URL of the plugin to add
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to add a plugin. "
                "Adding plugins can modify system behavior and security."
            )

        if not url or not isinstance(url, str):
            raise ToolError("url must be a non-empty string")

        try:
            logger.info(f"Executing add_plugin: {url}")
            variables: dict[str, Any] = {"url": url}
            response = await make_graphql_request(ADD_PLUGIN_MUTATION, variables)
            result = response.get("addPlugin")
            if not result:
                raise ToolError("Failed to add plugin")
            return {
                "success": True,
                "plugin": result,
                "message": f"Plugin added from {url}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in add_plugin: {e}", exc_info=True)
            raise ToolError(f"Failed to add plugin: {str(e)}") from e

    @mcp.tool()
    async def remove_plugin(name: str, confirm: bool = False) -> dict[str, Any]:
        """Removes an installed plugin. Requires confirm=True.

        Args:
            name: Name of the plugin to remove
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to remove a plugin. "
                "Removing plugins may affect system functionality."
            )

        if not name or not isinstance(name, str):
            raise ToolError("name must be a non-empty string")

        try:
            logger.info(f"Executing remove_plugin: {name}")
            variables: dict[str, Any] = {"name": name}
            response = await make_graphql_request(REMOVE_PLUGIN_MUTATION, variables)
            result = response.get("removePlugin", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": (
                    f"Plugin '{name}' removed" if success else f"Failed to remove plugin '{name}'"
                ),
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in remove_plugin: {e}", exc_info=True)
            raise ToolError(f"Failed to remove plugin: {str(e)}") from e

    @mcp.tool()
    async def install_plugin(url: str, confirm: bool = False) -> dict[str, Any]:
        """Installs a plugin from a URL. Requires confirm=True.

        Args:
            url: URL of the plugin to install
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to install a plugin. "
                "Installing plugins can modify system behavior and security."
            )

        if not url or not isinstance(url, str):
            raise ToolError("url must be a non-empty string")

        try:
            logger.info(f"Executing install_plugin: {url}")
            variables: dict[str, Any] = {"url": url}
            response = await make_graphql_request(INSTALL_PLUGIN_MUTATION, variables)
            result = response.get("installPlugin")
            if not result:
                raise ToolError("Failed to install plugin")
            return {
                "success": True,
                "operation": result,
                "message": f"Plugin installation started from {url}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in install_plugin: {e}", exc_info=True)
            raise ToolError(f"Failed to install plugin: {str(e)}") from e

    logger.info("Plugin tools registered successfully")

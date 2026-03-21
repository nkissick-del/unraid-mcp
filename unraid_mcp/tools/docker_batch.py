"""Docker batch operation tools.

This module is gated under the 'docker-batch' module and disabled by default.
It provides bulk container update operations with extended timeouts.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import get_timeout_for_operation, make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import validate_string_not_empty
from .queries.docker_batch import (
    DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
    DOCKER_UPDATE_AUTOSTART_MUTATION,
    DOCKER_UPDATE_CONTAINERS_MUTATION,
)


def register_docker_batch_tools(mcp: FastMCP) -> None:
    """Register Docker batch operation tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def update_docker_containers(
        container_ids: list[str],
    ) -> dict[str, Any]:
        """Updates multiple Docker containers to their latest image versions.

        Takes a list of container IDs (not names) and updates them sequentially.
        Uses an extended timeout since batch updates can take several minutes.

        Args:
            container_ids: List of container IDs to update (PrefixedID format)

        Returns:
            Dict containing the list of updated containers
        """
        if not container_ids:
            raise ToolError("container_ids must be a non-empty list")

        try:
            logger.info(f"Executing update_docker_containers for {len(container_ids)} containers")

            variables: dict[str, Any] = {"ids": container_ids}
            custom_timeout = get_timeout_for_operation("docker_batch_update")

            response = await make_graphql_request(
                DOCKER_UPDATE_CONTAINERS_MUTATION,
                variables,
                custom_timeout=custom_timeout,
            )

            results = response.get("docker", {}).get("updateContainers")
            if results is None:
                raise ToolError("Failed to update Docker containers")

            return {
                "success": True,
                "updated_containers": results,
                "count": len(results),
                "message": f"Successfully updated {len(results)} container(s)",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_docker_containers: {e}", exc_info=True)
            raise ToolError(f"Failed to update Docker containers: {str(e)}") from e

    @mcp.tool()
    async def update_all_docker_containers(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Updates ALL Docker containers to their latest image versions.

        This is a bulk operation that updates every container. Requires confirm=True.
        Uses an extended timeout since updating all containers can take several minutes.

        Args:
            confirm: Safety gate - must be True to proceed

        Returns:
            Dict containing the list of all updated containers
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to update all containers. "
                "This will update every Docker container on the system."
            )

        try:
            logger.info("Executing update_all_docker_containers")

            custom_timeout = get_timeout_for_operation("docker_batch_update")

            response = await make_graphql_request(
                DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
                custom_timeout=custom_timeout,
            )

            results = response.get("docker", {}).get("updateAllContainers")
            if results is None:
                raise ToolError("Failed to update all Docker containers")

            return {
                "success": True,
                "updated_containers": results,
                "count": len(results),
                "message": f"Successfully updated all {len(results)} container(s)",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_all_docker_containers: {e}", exc_info=True)
            raise ToolError(f"Failed to update all Docker containers: {str(e)}") from e

    @mcp.tool()
    async def update_docker_autostart(
        container_id: str,
        autostart: bool,
    ) -> dict[str, Any]:
        """Toggles the autostart configuration for a Docker container.

        Args:
            container_id: The container ID to update
            autostart: Whether the container should autostart

        Returns:
            Dict containing the updated container autostart configuration
        """
        validate_string_not_empty(container_id, "container_id")

        try:
            logger.info(
                f"Executing update_docker_autostart: id={container_id}, autostart={autostart}"
            )

            variables: dict[str, Any] = {"input": {"id": container_id, "autoStart": autostart}}

            response = await make_graphql_request(DOCKER_UPDATE_AUTOSTART_MUTATION, variables)

            result = response.get("docker", {}).get("updateAutostartConfiguration")
            if result is None:
                raise ToolError("Failed to update Docker autostart configuration")

            return {
                "success": True,
                "container": result,
                "message": f"Autostart {'enabled' if autostart else 'disabled'} for container",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_docker_autostart: {e}", exc_info=True)
            raise ToolError(f"Failed to update Docker autostart configuration: {str(e)}") from e

    logger.info("Docker batch tools registered successfully")

"""Docker container administrative tools (destructive operations).

This module is gated under the 'docker-admin' module and disabled by default.
It provides container removal and update operations.
"""

import asyncio
from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import get_timeout_for_operation, make_graphql_request
from ..core.constants import (
    CONTAINER_DISPLAY_LIMIT,
    DOCKER_OPERATION_SETTLE_DELAY_S,
    DOCKER_STATE_BACKOFF_FACTOR,
    DOCKER_STATE_INITIAL_DELAY_S,
    DOCKER_STATE_MAX_RETRIES,
)
from ..core.exceptions import ToolError
from ..core.utils import poll_with_backoff, validate_string_not_empty
from .docker import (
    _is_container_id,
    find_container_by_identifier,
    get_available_container_names,
)
from .queries.docker import (
    CONTAINER_LIST_FIELDS,
    DOCKER_REMOVE_CONTAINER_MUTATION,
    DOCKER_UPDATE_CONTAINER_MUTATION,
)


def register_docker_admin_tools(mcp: FastMCP) -> None:
    """Register Docker admin tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def remove_docker_container(
        container_identifier: str,
        with_image: bool = False,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Removes a Docker container. This is a DESTRUCTIVE operation.

        You must pass confirm=True to proceed. Optionally removes the container image too.

        Args:
            container_identifier: Container ID or name to remove
            with_image: Also remove the container's image (default False)
            confirm: Safety gate - must be True to proceed

        Returns:
            Dict with removal result
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to remove a container. "
                "This is a destructive operation that cannot be undone."
            )
        validate_string_not_empty(container_identifier, "container_identifier")

        try:
            logger.info(f"Executing remove_docker_container for: {container_identifier}")

            # Resolve name -> ID if needed
            actual_id = container_identifier
            if not _is_container_id(container_identifier):
                list_query = """
                query ResolveContainerID {
                  docker {
                    containers(skipCache: true) {
                      id
                      names
                    }
                  }
                }
                """
                list_response = await make_graphql_request(list_query)
                if not list_response.get("docker"):
                    raise ToolError("Failed to retrieve container list for ID resolution")
                containers = list_response["docker"].get("containers", [])
                resolved = find_container_by_identifier(container_identifier, containers)
                if resolved:
                    actual_id = str(resolved.get("id", ""))
                else:
                    available_names = get_available_container_names(containers)
                    error_msg = f"Container '{container_identifier}' not found."
                    if available_names:
                        error_msg += f" Available containers: {', '.join(available_names[:CONTAINER_DISPLAY_LIMIT])}"
                    raise ToolError(error_msg)

            variables: dict[str, Any] = {"id": actual_id, "withImage": with_image}
            response = await make_graphql_request(DOCKER_REMOVE_CONTAINER_MUTATION, variables)

            removed = response.get("docker", {}).get("removeContainer", False)

            return {
                "success": bool(removed),
                "container_id": actual_id,
                "with_image": with_image,
                "message": (
                    "Container removed successfully"
                    + (" (image also removed)" if with_image else "")
                    if removed
                    else "Container removal returned unexpected result"
                ),
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in remove_docker_container: {e}", exc_info=True)
            raise ToolError(f"Failed to remove Docker container: {str(e)}") from e

    @mcp.tool()
    async def update_docker_container(
        container_identifier: str,
    ) -> dict[str, Any]:
        """Updates a Docker container to the latest version of its image.

        This pulls the latest image and recreates the container.

        Args:
            container_identifier: Container ID or name to update

        Returns:
            Dict containing the updated container information
        """
        validate_string_not_empty(container_identifier, "container_identifier")

        try:
            logger.info(f"Executing update_docker_container for: {container_identifier}")

            # Resolve name -> ID if needed
            actual_id = container_identifier
            if not _is_container_id(container_identifier):
                list_query = """
                query ResolveContainerID {
                  docker {
                    containers(skipCache: true) {
                      id
                      names
                    }
                  }
                }
                """
                list_response = await make_graphql_request(list_query)
                if not list_response.get("docker"):
                    raise ToolError("Failed to retrieve container list for ID resolution")
                containers = list_response["docker"].get("containers", [])
                resolved = find_container_by_identifier(container_identifier, containers)
                if resolved:
                    actual_id = str(resolved.get("id", ""))
                else:
                    available_names = get_available_container_names(containers)
                    error_msg = f"Container '{container_identifier}' not found."
                    if available_names:
                        error_msg += f" Available containers: {', '.join(available_names[:CONTAINER_DISPLAY_LIMIT])}"
                    raise ToolError(error_msg)

            variables: dict[str, Any] = {"id": actual_id}
            custom_timeout = get_timeout_for_operation("docker_update")

            response = await make_graphql_request(
                DOCKER_UPDATE_CONTAINER_MUTATION,
                variables,
                custom_timeout=custom_timeout,
            )

            update_result = response.get("docker", {}).get("updateContainer")
            if not update_result:
                raise ToolError("Failed to update Docker container")

            # Wait for state to settle, then poll for updated details
            await asyncio.sleep(DOCKER_OPERATION_SETTLE_DELAY_S)

            async def _query_container_state() -> dict[str, Any] | None:
                list_query = f"""
                query GetUpdatedContainerState($skipCache: Boolean!) {{
                  docker {{
                    containers(skipCache: $skipCache) {{
                      {CONTAINER_LIST_FIELDS}
                    }}
                  }}
                }}
                """
                list_resp = await make_graphql_request(list_query, {"skipCache": True})
                if list_resp.get("docker"):
                    containers = list_resp["docker"].get("containers", [])
                    return find_container_by_identifier(container_identifier, containers)
                return None

            polled = await poll_with_backoff(
                query_fn=_query_container_state,
                max_retries=DOCKER_STATE_MAX_RETRIES,
                initial_delay=DOCKER_STATE_INITIAL_DELAY_S,
                backoff_factor=DOCKER_STATE_BACKOFF_FACTOR,
                operation_name="container update state poll",
            )

            return {
                "update_result": update_result,
                "container_details": polled,
                "success": True,
                "message": "Container updated successfully",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_docker_container: {e}", exc_info=True)
            raise ToolError(f"Failed to update Docker container: {str(e)}") from e

    logger.info("Docker admin tools registered successfully")

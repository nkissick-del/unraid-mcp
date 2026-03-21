"""Docker container management tools.

This module provides tools for Docker container lifecycle and management
including listing containers with caching options, start/stop operations,
and detailed container information retrieval.
"""

import asyncio
import re
from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.constants import (
    CONTAINER_DISPLAY_LIMIT,
    CONTAINER_ID_PATTERN,
    CONTAINER_PREFIXED_ID_PATTERN,
    DOCKER_OPERATION_SETTLE_DELAY_S,
    DOCKER_STATE_BACKOFF_FACTOR,
    DOCKER_STATE_INITIAL_DELAY_S,
    DOCKER_STATE_MAX_RETRIES,
)
from ..core.exceptions import ToolError
from ..core.utils import ensure_list, poll_with_backoff, validate_enum, validate_string_not_empty
from .queries.docker import CONTAINER_LIST_FIELDS, DOCKER_ACTION_MUTATIONS


def _is_container_id(identifier: str) -> bool:
    """Check if a string looks like a Docker container ID.

    Docker container IDs are 64-char hex strings (full) or 12+ char hex prefixes (short).
    The Unraid API uses colon-delimited prefixed IDs (e.g., 'sha256:abc123...').
    """
    if ":" in identifier:
        return bool(re.match(CONTAINER_PREFIXED_ID_PATTERN, identifier))
    return bool(re.fullmatch(CONTAINER_ID_PATTERN, identifier))


def find_container_by_identifier(
    container_identifier: str, containers: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Find a container by ID or name with fuzzy matching.

    Args:
        container_identifier: Container ID or name to find
        containers: List of container dictionaries to search

    Returns:
        Container dictionary if found, None otherwise
    """
    if not containers:
        return None

    # Exact matches first
    for container in containers:
        if container.get("id") == container_identifier:
            return container

        # Check all names for exact match
        names = container.get("names", [])
        if container_identifier in names:
            return container

    # Fuzzy matching - case insensitive partial matches
    container_identifier_lower = container_identifier.lower()
    for container in containers:
        names = container.get("names", [])
        for name in names:
            if (
                container_identifier_lower in name.lower()
                or name.lower() in container_identifier_lower
            ):
                logger.info(
                    f"Found container via fuzzy match: '{container_identifier}' -> '{name}'"
                )
                return container

    return None


def get_available_container_names(containers: list[dict[str, Any]]) -> list[str]:
    """Extract all available container names for error reporting.

    Args:
        containers: List of container dictionaries

    Returns:
        List of container names
    """
    names = []
    for container in containers:
        container_names = container.get("names", [])
        names.extend(container_names)
    return names


def register_docker_tools(mcp: FastMCP) -> None:
    """Register all Docker tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def list_docker_containers() -> list[dict[str, Any]]:
        """Lists all Docker containers on the Unraid system.

        Returns:
            List of Docker container information dictionaries
        """
        query = f"""
        query ListDockerContainers {{
          docker {{
            containers(skipCache: false) {{
              {CONTAINER_LIST_FIELDS}
            }}
          }}
        }}
        """
        try:
            logger.info("Executing list_docker_containers tool")
            response_data = await make_graphql_request(query)
            if response_data.get("docker"):
                containers = response_data["docker"].get("containers", [])
                return ensure_list(containers)
            logger.warning("GraphQL response missing 'docker' field — returning empty list")
            return []
        except Exception as e:
            logger.error(f"Error in list_docker_containers: {e}", exc_info=True)
            raise ToolError(f"Failed to list Docker containers: {str(e)}") from e

    @mcp.tool()
    async def manage_docker_container(container_id: str, action: str) -> dict[str, Any]:
        """Starts or stops a specific Docker container. Action must be 'start' or 'stop'.

        Args:
            container_id: Container ID to manage
            action: Action to perform - 'start' or 'stop'

        Returns:
            Dict containing operation result and container information
        """
        validate_string_not_empty(container_id, "container_id")
        mutation_name = validate_enum(action.lower(), list(DOCKER_ACTION_MUTATIONS), "action")
        operation_query = DOCKER_ACTION_MUTATIONS[mutation_name]

        variables = {"id": container_id}

        try:
            logger.info(f"Executing manage_docker_container: action={action}, id={container_id}")

            # Step 1: Resolve container identifier to actual container ID if needed
            actual_container_id = container_id
            if not _is_container_id(container_id):
                # This looks like a name, not a full container ID - need to resolve it
                logger.info(
                    f"Resolving container identifier '{container_id}' to actual container ID"
                )
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
                if list_response.get("docker"):
                    containers = list_response["docker"].get("containers", [])
                    resolved_container = find_container_by_identifier(container_id, containers)
                    if resolved_container:
                        actual_container_id = str(resolved_container.get("id", ""))
                        logger.info(
                            f"Resolved '{container_id}' to container ID: {actual_container_id}"
                        )
                    else:
                        available_names = get_available_container_names(containers)
                        error_msg = f"Container '{container_id}' not found for {action} operation."
                        if available_names:
                            error_msg += f" Available containers: {', '.join(available_names[:CONTAINER_DISPLAY_LIMIT])}"
                        raise ToolError(error_msg)

            # Update variables with the actual container ID
            variables = {"id": actual_container_id}

            # Execute the operation with idempotent error handling
            operation_context = {"operation": action}
            operation_response = await make_graphql_request(
                operation_query, variables, operation_context=operation_context
            )

            # Handle idempotent success case
            if operation_response.get("idempotent_success"):
                logger.info(
                    f"Container {action} operation was idempotent: {operation_response.get('message')}"
                )
                # Get current container state since the operation was already complete
                try:
                    list_query = f"""
                    query GetContainerStateAfterIdempotent($skipCache: Boolean!) {{
                      docker {{
                        containers(skipCache: $skipCache) {{
                          {CONTAINER_LIST_FIELDS}
                        }}
                      }}
                    }}
                    """
                    list_response = await make_graphql_request(list_query, {"skipCache": True})

                    if list_response.get("docker"):
                        containers = list_response["docker"].get("containers", [])
                        container = find_container_by_identifier(container_id, containers)

                        if container:
                            return {
                                "operation_result": {
                                    "id": container_id,
                                    "names": container.get("names", []),
                                },
                                "container_details": container,
                                "success": True,
                                "message": f"Container {action} operation was already complete - current state returned",
                                "idempotent": True,
                            }

                except Exception as lookup_error:
                    logger.warning(
                        f"Could not retrieve container state after idempotent operation: {lookup_error}"
                    )

                return {
                    "operation_result": {"id": container_id},
                    "container_details": None,
                    "success": True,
                    "message": f"Container {action} operation was already complete",
                    "idempotent": True,
                }

            # Handle normal successful operation
            if not (
                operation_response.get("docker") and operation_response["docker"].get(mutation_name)
            ):
                raise ToolError(f"Failed to execute {action} operation on container")

            operation_result = operation_response["docker"][mutation_name]
            logger.info(f"Container {action} operation completed for {container_id}")

            # Step 2: Wait briefly for state to propagate, then fetch current container details
            await asyncio.sleep(DOCKER_OPERATION_SETTLE_DELAY_S)

            # Step 3: Try to get updated container details with retry logic
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
                list_response = await make_graphql_request(list_query, {"skipCache": True})
                if list_response.get("docker"):
                    containers = list_response["docker"].get("containers", [])
                    container = find_container_by_identifier(container_id, containers)
                    if container:
                        logger.info(f"Found updated container state for {container_id}")
                        return container
                return None

            polled_container = await poll_with_backoff(
                query_fn=_query_container_state,
                max_retries=DOCKER_STATE_MAX_RETRIES,
                initial_delay=DOCKER_STATE_INITIAL_DELAY_S,
                backoff_factor=DOCKER_STATE_BACKOFF_FACTOR,
                operation_name=f"container {action} state poll",
            )

            if polled_container is not None:
                return {
                    "operation_result": operation_result,
                    "container_details": polled_container,
                    "success": True,
                    "message": f"Container {action} operation completed successfully",
                }

            # All retries exhausted — operation succeeded but state not found
            logger.warning(
                f"Container {container_id} not found in any retry attempt after {action}"
            )
            return {
                "operation_result": operation_result,
                "container_details": None,
                "success": True,
                "message": f"Container {action} operation completed, but container not found in subsequent queries",
                "warning": "Container not found in updated state - this may indicate the operation succeeded but container is no longer listed",
            }

        except Exception as e:
            logger.error(f"Error in manage_docker_container ({action}): {e}", exc_info=True)
            raise ToolError(f"Failed to {action} Docker container: {str(e)}") from e

    @mcp.tool()
    async def get_docker_container_details(container_identifier: str) -> dict[str, Any]:
        """Retrieves detailed information for a specific Docker container by its ID or name.

        Args:
            container_identifier: Container ID or name to retrieve details for

        Returns:
            Dict containing detailed container information
        """
        validate_string_not_empty(container_identifier, "container_identifier")
        # This tool fetches all containers and then filters by ID or name.
        # More detailed query for a single container if found:
        detailed_query_fields = """
              id
              names
              image
              imageId
              command
              created
              ports { ip privatePort publicPort type }
              sizeRootFs
              labels # JSONObject
              state
              status
              hostConfig { networkMode }
              networkSettings # JSONObject
              mounts # JSONObject array
              autoStart
        """

        # Fetch all containers first
        list_query = f"""
        query GetAllContainerDetailsForFiltering {{
          docker {{
            containers(skipCache: false) {{
              {detailed_query_fields}
            }}
          }}
        }}
        """
        try:
            logger.info(
                f"Executing get_docker_container_details for identifier: {container_identifier}"
            )
            response_data = await make_graphql_request(list_query)

            containers = []
            if response_data.get("docker"):
                containers = response_data["docker"].get("containers", [])

            # Use our enhanced container lookup
            container = find_container_by_identifier(container_identifier, containers)
            if container:
                logger.info(f"Found container {container_identifier}")
                return container

            # Container not found - provide helpful error message with available containers
            available_names = get_available_container_names(containers)
            logger.warning(f"Container with identifier '{container_identifier}' not found.")
            logger.info(f"Available containers: {available_names}")

            error_msg = f"Container '{container_identifier}' not found."
            if available_names:
                error_msg += (
                    f" Available containers: {', '.join(available_names[:CONTAINER_DISPLAY_LIMIT])}"
                )
                if len(available_names) > CONTAINER_DISPLAY_LIMIT:
                    error_msg += f" (and {len(available_names) - CONTAINER_DISPLAY_LIMIT} more)"
            else:
                error_msg += " No containers are currently available."

            raise ToolError(error_msg)

        except Exception as e:
            logger.error(f"Error in get_docker_container_details: {e}", exc_info=True)
            raise ToolError(f"Failed to retrieve Docker container details: {str(e)}") from e

    logger.info("Docker tools registered successfully")

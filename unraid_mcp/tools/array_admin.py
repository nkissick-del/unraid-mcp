"""Array disk administration tools.

This module is gated under the 'array-admin' module and disabled by default.
It provides tools for managing array disk assignments, mounting, and statistics.

WARNING: Several operations in this module are EXTREMELY DESTRUCTIVE.
Adding or removing disks from the array can cause irreversible data loss
if the wrong disk is selected.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from ..core.utils import ensure_list
from .queries.array_admin import (
    ADD_DISK_TO_ARRAY_MUTATION,
    CLEAR_ARRAY_DISK_STATISTICS_MUTATION,
    LIST_ASSIGNABLE_DISKS_QUERY,
    MOUNT_ARRAY_DISK_MUTATION,
    REMOVE_DISK_FROM_ARRAY_MUTATION,
    UNMOUNT_ARRAY_DISK_MUTATION,
)


def register_array_admin_tools(mcp: FastMCP) -> None:
    """Register array administration tools with the FastMCP instance."""

    @mcp.tool()
    async def list_assignable_disks() -> dict[str, Any]:
        """Lists all disks that can be assigned to the array, with device info and status."""
        try:
            logger.info("Executing list_assignable_disks")
            response = await make_graphql_request(LIST_ASSIGNABLE_DISKS_QUERY)
            disks = ensure_list(response.get("assignableDisks", []))
            return {"count": len(disks), "disks": disks}
        except Exception as e:
            logger.error(f"Error in list_assignable_disks: {e}", exc_info=True)
            raise ToolError(f"Failed to list assignable disks: {str(e)}") from e

    @mcp.tool()
    async def add_disk_to_array(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Adds a disk to the array. Requires confirm=True.

        WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause
        irreversible data loss if the wrong disk is selected.
        Verify the disk identifier carefully before proceeding.

        Use list_assignable_disks() first to see available disks.

        Args:
            input_config: Dict identifying the disk to add (e.g. {id: "...", slot: "..."})
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to add a disk to the array. "
                "WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause "
                "irreversible data loss if the wrong disk is selected. "
                "Verify the disk identifier carefully before proceeding."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info(f"Executing add_disk_to_array: {input_config}")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(ADD_DISK_TO_ARRAY_MUTATION, variables)
            result = response.get("addDiskToArray", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": "Disk added to array" if success else "Failed to add disk to array",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in add_disk_to_array: {e}", exc_info=True)
            raise ToolError(f"Failed to add disk to array: {str(e)}") from e

    @mcp.tool()
    async def remove_disk_from_array(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Removes a disk from the array. Requires confirm=True.

        WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause
        irreversible data loss if the wrong disk is selected.
        Verify the disk identifier carefully before proceeding.

        Args:
            input_config: Dict identifying the disk to remove
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to remove a disk from the array. "
                "WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause "
                "irreversible data loss if the wrong disk is selected. "
                "Verify the disk identifier carefully before proceeding."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info(f"Executing remove_disk_from_array: {input_config}")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(REMOVE_DISK_FROM_ARRAY_MUTATION, variables)
            result = response.get("removeDiskFromArray", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": (
                    "Disk removed from array" if success else "Failed to remove disk from array"
                ),
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in remove_disk_from_array: {e}", exc_info=True)
            raise ToolError(f"Failed to remove disk from array: {str(e)}") from e

    @mcp.tool()
    async def mount_array_disk(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Mounts an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to mount
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to mount an array disk. "
                "This will make the disk accessible to the system."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info(f"Executing mount_array_disk: {input_config}")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(MOUNT_ARRAY_DISK_MUTATION, variables)
            result = response.get("mountArrayDisk", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": "Array disk mounted" if success else "Failed to mount array disk",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in mount_array_disk: {e}", exc_info=True)
            raise ToolError(f"Failed to mount array disk: {str(e)}") from e

    @mcp.tool()
    async def unmount_array_disk(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Unmounts an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to unmount
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to unmount an array disk. "
                "This will make the disk inaccessible until remounted."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info(f"Executing unmount_array_disk: {input_config}")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(UNMOUNT_ARRAY_DISK_MUTATION, variables)
            result = response.get("unmountArrayDisk", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": "Array disk unmounted" if success else "Failed to unmount array disk",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unmount_array_disk: {e}", exc_info=True)
            raise ToolError(f"Failed to unmount array disk: {str(e)}") from e

    @mcp.tool()
    async def clear_array_disk_statistics(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Clears statistics for an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to clear statistics for
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to clear array disk statistics. "
                "This will reset all accumulated disk statistics."
            )

        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info(f"Executing clear_array_disk_statistics: {input_config}")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(CLEAR_ARRAY_DISK_STATISTICS_MUTATION, variables)
            result = response.get("clearArrayDiskStatistics", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": (
                    "Array disk statistics cleared"
                    if success
                    else "Failed to clear array disk statistics"
                ),
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in clear_array_disk_statistics: {e}", exc_info=True)
            raise ToolError(f"Failed to clear array disk statistics: {str(e)}") from e

    logger.info("Array admin tools registered successfully")

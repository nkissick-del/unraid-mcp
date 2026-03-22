"""Array disk administration tools.

This module is gated under the 'array-admin' module and disabled by default.
It provides tools for managing array disk assignments, mounting, and statistics.

WARNING: Several operations in this module are EXTREMELY DESTRUCTIVE.
Adding or removing disks from the array can cause irreversible data loss
if the wrong disk is selected.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.utils import ensure_list, require_confirm, validate_input_dict
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
    @tool_error_handler("list assignable disks")
    async def list_assignable_disks() -> dict[str, Any]:
        """Lists all disks that can be assigned to the array, with device info and status."""
        response = await make_graphql_request(LIST_ASSIGNABLE_DISKS_QUERY)
        disks = ensure_list(response.get("assignableDisks", []))
        return {"count": len(disks), "disks": disks}

    @mcp.tool()
    @tool_error_handler("add disk to array")
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
        require_confirm(
            confirm,
            "add a disk to the array",
            "WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause irreversible data loss if the wrong disk is selected. Verify the disk identifier carefully before proceeding.",
        )
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(ADD_DISK_TO_ARRAY_MUTATION, variables)
        result = (response.get("array") or {}).get("addDiskToArray", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": "Disk added to array" if success else "Failed to add disk to array",
        }

    @mcp.tool()
    @tool_error_handler("remove disk from array")
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
        require_confirm(
            confirm,
            "remove a disk from the array",
            "WARNING: This is an EXTREMELY DESTRUCTIVE operation that can cause irreversible data loss if the wrong disk is selected. Verify the disk identifier carefully before proceeding.",
        )
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"input": input_config}
        response = await make_graphql_request(REMOVE_DISK_FROM_ARRAY_MUTATION, variables)
        result = (response.get("array") or {}).get("removeDiskFromArray", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": (
                "Disk removed from array" if success else "Failed to remove disk from array"
            ),
        }

    @mcp.tool()
    @tool_error_handler("mount array disk")
    async def mount_array_disk(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Mounts an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to mount
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "mount an array disk")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"id": input_config.get("id", input_config.get("diskId"))}
        response = await make_graphql_request(MOUNT_ARRAY_DISK_MUTATION, variables)
        result = (response.get("array") or {}).get("mountArrayDisk", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": "Array disk mounted" if success else "Failed to mount array disk",
        }

    @mcp.tool()
    @tool_error_handler("unmount array disk")
    async def unmount_array_disk(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Unmounts an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to unmount
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "unmount an array disk")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"id": input_config.get("id", input_config.get("diskId"))}
        response = await make_graphql_request(UNMOUNT_ARRAY_DISK_MUTATION, variables)
        result = (response.get("array") or {}).get("unmountArrayDisk", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": "Array disk unmounted" if success else "Failed to unmount array disk",
        }

    @mcp.tool()
    @tool_error_handler("clear array disk statistics")
    async def clear_array_disk_statistics(
        input_config: dict[str, Any], confirm: bool = False
    ) -> dict[str, Any]:
        """Clears statistics for an array disk. Requires confirm=True.

        Args:
            input_config: Dict identifying the disk to clear statistics for
            confirm: Safety gate - must be True to proceed
        """
        require_confirm(confirm, "clear array disk statistics")
        validate_input_dict(input_config)

        variables: dict[str, Any] = {"id": input_config.get("id", input_config.get("diskId"))}
        response = await make_graphql_request(CLEAR_ARRAY_DISK_STATISTICS_MUTATION, variables)
        result = (response.get("array") or {}).get("clearArrayDiskStatistics", {})
        success = result.get("success", False)
        return {
            "success": success,
            "message": (
                "Array disk statistics cleared"
                if success
                else "Failed to clear array disk statistics"
            ),
        }

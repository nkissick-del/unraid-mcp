"""Docker organization tools for folder management and template operations.

This module is gated under the 'docker-organize' module and disabled by default.
It provides Docker UI folder management and template maintenance operations.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError
from .queries.docker_organize import (
    CREATE_DOCKER_FOLDER_MUTATION,
    CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION,
    DELETE_DOCKER_ENTRIES_MUTATION,
    MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION,
    MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION,
    REFRESH_DOCKER_DIGESTS_MUTATION,
    RENAME_DOCKER_FOLDER_MUTATION,
    RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION,
    SET_DOCKER_FOLDER_CHILDREN_MUTATION,
    SYNC_DOCKER_TEMPLATE_PATHS_MUTATION,
    UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION,
)


def register_docker_organize_tools(mcp: FastMCP) -> None:
    """Register Docker organization tools with the FastMCP instance."""

    @mcp.tool()
    async def create_docker_folder(name: str, icon: str = "") -> dict[str, Any]:
        """Creates a new Docker UI folder for organizing containers.

        Args:
            name: Name for the new folder
            icon: Optional icon identifier for the folder
        """
        if not name or not isinstance(name, str):
            raise ToolError("name must be a non-empty string")

        try:
            logger.info(f"Executing create_docker_folder: {name}")
            variables: dict[str, Any] = {"name": name}
            if icon:
                variables["icon"] = icon
            response = await make_graphql_request(CREATE_DOCKER_FOLDER_MUTATION, variables)
            result = response.get("docker", {}).get("createFolder")
            if not result:
                raise ToolError("Failed to create Docker folder")
            return {
                "success": True,
                "folder": result,
                "message": f"Docker folder '{name}' created",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in create_docker_folder: {e}", exc_info=True)
            raise ToolError(f"Failed to create Docker folder: {str(e)}") from e

    @mcp.tool()
    async def set_docker_folder_children(folder_id: str, children: list[str]) -> dict[str, Any]:
        """Sets the child entries for a Docker UI folder.

        Args:
            folder_id: ID of the folder to update
            children: List of entry IDs to set as children
        """
        if not folder_id or not isinstance(folder_id, str):
            raise ToolError("folder_id must be a non-empty string")
        if not isinstance(children, list):
            raise ToolError("children must be a list of strings")

        try:
            logger.info(f"Executing set_docker_folder_children: {folder_id}")
            variables: dict[str, Any] = {
                "folderId": folder_id,
                "children": children,
            }
            response = await make_graphql_request(SET_DOCKER_FOLDER_CHILDREN_MUTATION, variables)
            result = response.get("docker", {}).get("setFolderChildren")
            if not result:
                raise ToolError("Failed to set folder children")
            return {
                "success": True,
                "folder": result,
                "message": f"Folder children updated for {folder_id}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in set_docker_folder_children: {e}", exc_info=True)
            raise ToolError(f"Failed to set folder children: {str(e)}") from e

    @mcp.tool()
    async def delete_docker_entries(ids: list[str], confirm: bool = False) -> dict[str, Any]:
        """Deletes Docker UI entries (folders or containers). Requires confirm=True.

        Args:
            ids: List of entry IDs to delete
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to delete Docker entries. "
                "This will remove the selected entries from the Docker UI."
            )

        if not ids or not isinstance(ids, list):
            raise ToolError("ids must be a non-empty list of strings")

        try:
            logger.info(f"Executing delete_docker_entries: {len(ids)} entries")
            variables: dict[str, Any] = {"ids": ids}
            response = await make_graphql_request(DELETE_DOCKER_ENTRIES_MUTATION, variables)
            result = response.get("docker", {}).get("deleteEntries", {})
            success = result.get("success", False)
            return {
                "success": success,
                "message": (
                    f"Deleted {len(ids)} Docker entries"
                    if success
                    else "Failed to delete Docker entries"
                ),
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_docker_entries: {e}", exc_info=True)
            raise ToolError(f"Failed to delete Docker entries: {str(e)}") from e

    @mcp.tool()
    async def move_docker_entries_to_folder(folder_id: str, entry_ids: list[str]) -> dict[str, Any]:
        """Moves Docker entries into a folder.

        Args:
            folder_id: Target folder ID
            entry_ids: List of entry IDs to move
        """
        if not folder_id or not isinstance(folder_id, str):
            raise ToolError("folder_id must be a non-empty string")
        if not entry_ids or not isinstance(entry_ids, list):
            raise ToolError("entry_ids must be a non-empty list of strings")

        try:
            logger.info(
                f"Executing move_docker_entries_to_folder: {len(entry_ids)} entries -> {folder_id}"
            )
            variables: dict[str, Any] = {
                "folderId": folder_id,
                "entryIds": entry_ids,
            }
            response = await make_graphql_request(MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION, variables)
            result = response.get("docker", {}).get("moveEntriesToFolder", {})
            return {
                "success": result.get("success", False),
                "message": f"Moved {len(entry_ids)} entries to folder {folder_id}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in move_docker_entries_to_folder: {e}", exc_info=True)
            raise ToolError(f"Failed to move entries to folder: {str(e)}") from e

    @mcp.tool()
    async def move_docker_items_to_position(item_ids: list[str], position: int) -> dict[str, Any]:
        """Moves Docker items to a specific position in the UI ordering.

        Args:
            item_ids: List of item IDs to reposition
            position: Target position index
        """
        if not item_ids or not isinstance(item_ids, list):
            raise ToolError("item_ids must be a non-empty list of strings")

        try:
            logger.info(
                f"Executing move_docker_items_to_position: {len(item_ids)} items -> position {position}"
            )
            variables: dict[str, Any] = {
                "itemIds": item_ids,
                "position": position,
            }
            response = await make_graphql_request(MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION, variables)
            result = response.get("docker", {}).get("moveItemsToPosition", {})
            return {
                "success": result.get("success", False),
                "message": f"Moved {len(item_ids)} items to position {position}",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in move_docker_items_to_position: {e}", exc_info=True)
            raise ToolError(f"Failed to move items to position: {str(e)}") from e

    @mcp.tool()
    async def rename_docker_folder(folder_id: str, name: str) -> dict[str, Any]:
        """Renames a Docker UI folder.

        Args:
            folder_id: ID of the folder to rename
            name: New name for the folder
        """
        if not folder_id or not isinstance(folder_id, str):
            raise ToolError("folder_id must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ToolError("name must be a non-empty string")

        try:
            logger.info(f"Executing rename_docker_folder: {folder_id} -> {name}")
            variables: dict[str, Any] = {"folderId": folder_id, "name": name}
            response = await make_graphql_request(RENAME_DOCKER_FOLDER_MUTATION, variables)
            result = response.get("docker", {}).get("renameFolder")
            if not result:
                raise ToolError("Failed to rename Docker folder")
            return {
                "success": True,
                "folder": result,
                "message": f"Folder renamed to '{name}'",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in rename_docker_folder: {e}", exc_info=True)
            raise ToolError(f"Failed to rename Docker folder: {str(e)}") from e

    @mcp.tool()
    async def create_docker_folder_with_items(name: str, item_ids: list[str]) -> dict[str, Any]:
        """Creates a new Docker UI folder and moves items into it in one operation.

        Args:
            name: Name for the new folder
            item_ids: List of item IDs to place in the folder
        """
        if not name or not isinstance(name, str):
            raise ToolError("name must be a non-empty string")
        if not item_ids or not isinstance(item_ids, list):
            raise ToolError("item_ids must be a non-empty list of strings")

        try:
            logger.info(
                f"Executing create_docker_folder_with_items: '{name}' with {len(item_ids)} items"
            )
            variables: dict[str, Any] = {"name": name, "itemIds": item_ids}
            response = await make_graphql_request(
                CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION, variables
            )
            result = response.get("docker", {}).get("createFolderWithItems")
            if not result:
                raise ToolError("Failed to create folder with items")
            return {
                "success": True,
                "folder": result,
                "message": f"Folder '{name}' created with {len(item_ids)} items",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in create_docker_folder_with_items: {e}", exc_info=True)
            raise ToolError(f"Failed to create folder with items: {str(e)}") from e

    @mcp.tool()
    async def update_docker_view_preferences(
        input_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Updates Docker UI view preferences (layout, sorting, etc.).

        Args:
            input_config: Dict of view preference fields to update
        """
        if not input_config or not isinstance(input_config, dict):
            raise ToolError("input_config must be a non-empty dictionary")

        try:
            logger.info("Executing update_docker_view_preferences")
            variables: dict[str, Any] = {"input": input_config}
            response = await make_graphql_request(
                UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION, variables
            )
            result = response.get("docker", {}).get("updateViewPreferences", {})
            return {
                "success": result.get("success", False),
                "message": "Docker view preferences updated",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in update_docker_view_preferences: {e}", exc_info=True)
            raise ToolError(f"Failed to update Docker view preferences: {str(e)}") from e

    @mcp.tool()
    async def sync_docker_template_paths() -> dict[str, Any]:
        """Synchronizes Docker template paths with the file system."""
        try:
            logger.info("Executing sync_docker_template_paths")
            response = await make_graphql_request(SYNC_DOCKER_TEMPLATE_PATHS_MUTATION)
            result = response.get("docker", {}).get("syncTemplatePaths", {})
            return {
                "success": result.get("success", False),
                "message": "Docker template paths synchronized",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in sync_docker_template_paths: {e}", exc_info=True)
            raise ToolError(f"Failed to sync Docker template paths: {str(e)}") from e

    @mcp.tool()
    async def reset_docker_template_mappings(
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Resets all Docker template mappings to defaults. Requires confirm=True.

        Args:
            confirm: Safety gate - must be True to proceed
        """
        if not confirm:
            raise ToolError(
                "confirm must be True to reset Docker template mappings. "
                "This will reset all template mappings to their defaults."
            )

        try:
            logger.info("Executing reset_docker_template_mappings")
            response = await make_graphql_request(RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION)
            result = response.get("docker", {}).get("resetTemplateMappings", {})
            return {
                "success": result.get("success", False),
                "message": "Docker template mappings reset to defaults",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in reset_docker_template_mappings: {e}", exc_info=True)
            raise ToolError(f"Failed to reset Docker template mappings: {str(e)}") from e

    @mcp.tool()
    async def refresh_docker_digests() -> dict[str, Any]:
        """Refreshes Docker image digests to check for available updates."""
        try:
            logger.info("Executing refresh_docker_digests")
            response = await make_graphql_request(REFRESH_DOCKER_DIGESTS_MUTATION)
            result = response.get("docker", {}).get("refreshDigests", {})
            return {
                "success": result.get("success", False),
                "message": "Docker digests refreshed",
            }
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in refresh_docker_digests: {e}", exc_info=True)
            raise ToolError(f"Failed to refresh Docker digests: {str(e)}") from e

    logger.info("Docker organize tools registered successfully")

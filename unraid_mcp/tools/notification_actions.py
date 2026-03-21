"""Notification management tools (archive, delete).

This module is gated under the 'notifications' module and disabled by default.
These operations modify or delete notification state.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.constants import (
    NOTIFICATION_IMPORTANCE_VALUES,
    NOTIFICATION_TYPE_VALUES,
)
from ..core.exceptions import ToolError
from ..core.utils import validate_enum, validate_string_not_empty
from .queries.notifications import (
    ARCHIVE_ALL_NOTIFICATIONS_MUTATION,
    ARCHIVE_NOTIFICATION_MUTATION,
    DELETE_ARCHIVED_NOTIFICATIONS_MUTATION,
    DELETE_NOTIFICATION_MUTATION,
)


def register_notification_tools(mcp: FastMCP) -> None:
    """Register notification management tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def archive_notification(notification_id: str) -> dict[str, Any]:
        """Archives a single notification by its ID.

        Args:
            notification_id: The ID of the notification to archive

        Returns:
            Dict containing the archived notification details
        """
        validate_string_not_empty(notification_id, "notification_id")

        try:
            logger.info(f"Executing archive_notification: id={notification_id}")
            variables: dict[str, Any] = {"id": notification_id}
            response = await make_graphql_request(ARCHIVE_NOTIFICATION_MUTATION, variables)

            result = response.get("archiveNotification")
            if not result:
                raise ToolError(f"Failed to archive notification '{notification_id}'")

            return {
                "success": True,
                "notification": result,
                "message": "Notification archived successfully",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in archive_notification: {e}", exc_info=True)
            raise ToolError(f"Failed to archive notification: {str(e)}") from e

    @mcp.tool()
    async def archive_all_notifications(
        importance: str | None = None,
    ) -> dict[str, Any]:
        """Archives all notifications, optionally filtered by importance level.

        Args:
            importance: Optional filter - 'INFO', 'WARNING', or 'ALERT'

        Returns:
            Dict containing updated notification overview counts
        """
        variables: dict[str, Any] = {}
        if importance is not None:
            validated = validate_enum(
                importance.upper(),
                NOTIFICATION_IMPORTANCE_VALUES,
                "importance",
            )
            variables["importance"] = validated

        try:
            logger.info(f"Executing archive_all_notifications: importance={importance}")
            response = await make_graphql_request(ARCHIVE_ALL_NOTIFICATIONS_MUTATION, variables)

            result = response.get("archiveAll")
            if not result:
                raise ToolError("Failed to archive all notifications")

            return {
                "success": True,
                "overview": result,
                "message": "All notifications archived successfully",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in archive_all_notifications: {e}", exc_info=True)
            raise ToolError(f"Failed to archive all notifications: {str(e)}") from e

    @mcp.tool()
    async def delete_notification(
        notification_id: str,
        notification_type: str,
    ) -> dict[str, Any]:
        """Deletes a single notification. This is a DESTRUCTIVE operation.

        Args:
            notification_id: The ID of the notification to delete
            notification_type: The notification type - 'UNREAD' or 'ARCHIVE'

        Returns:
            Dict containing updated notification overview counts
        """
        validate_string_not_empty(notification_id, "notification_id")
        validated_type = validate_enum(
            notification_type.upper(),
            NOTIFICATION_TYPE_VALUES,
            "notification_type",
        )

        try:
            logger.info(
                f"Executing delete_notification: id={notification_id}, type={validated_type}"
            )
            variables: dict[str, Any] = {
                "id": notification_id,
                "type": validated_type,
            }
            response = await make_graphql_request(DELETE_NOTIFICATION_MUTATION, variables)

            result = response.get("deleteNotification")
            if not result:
                raise ToolError(f"Failed to delete notification '{notification_id}'")

            return {
                "success": True,
                "overview": result,
                "message": "Notification deleted successfully",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_notification: {e}", exc_info=True)
            raise ToolError(f"Failed to delete notification: {str(e)}") from e

    @mcp.tool()
    async def delete_archived_notifications() -> dict[str, Any]:
        """Deletes ALL archived notifications. This is a DESTRUCTIVE operation that cannot be undone.

        Returns:
            Dict containing updated notification overview counts
        """
        try:
            logger.info("Executing delete_archived_notifications")
            response = await make_graphql_request(DELETE_ARCHIVED_NOTIFICATIONS_MUTATION)

            result = response.get("deleteArchivedNotifications")
            if not result:
                raise ToolError("Failed to delete archived notifications")

            return {
                "success": True,
                "overview": result,
                "message": "All archived notifications deleted",
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_archived_notifications: {e}", exc_info=True)
            raise ToolError(f"Failed to delete archived notifications: {str(e)}") from e

    logger.info("Notification tools registered successfully")

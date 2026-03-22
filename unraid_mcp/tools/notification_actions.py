"""Notification management tools (archive, delete).

This module is gated under the 'notifications' module and disabled by default.
These operations modify or delete notification state.
"""

from typing import Any

from fastmcp import FastMCP

from ..core.client import make_graphql_request
from ..core.constants import (
    NOTIFICATION_IMPORTANCE_VALUES,
    NOTIFICATION_TYPE_VALUES,
)
from ..core.decorators import tool_error_handler
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
    @tool_error_handler("archive notification")
    async def archive_notification(notification_id: str) -> dict[str, Any]:
        """Archives a single notification by its ID.

        Args:
            notification_id: The ID of the notification to archive

        Returns:
            Dict containing the archived notification details
        """
        validate_string_not_empty(notification_id, "notification_id")

        variables: dict[str, Any] = {"id": notification_id}
        response = await make_graphql_request(ARCHIVE_NOTIFICATION_MUTATION, variables)

        result = response.get("archiveNotification")
        if result is None:
            raise ToolError(f"Failed to archive notification '{notification_id}'")

        return {
            "success": True,
            "notification": result,
            "message": "Notification archived successfully",
        }

    @mcp.tool()
    @tool_error_handler("archive all notifications")
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

        response = await make_graphql_request(ARCHIVE_ALL_NOTIFICATIONS_MUTATION, variables)

        result = response.get("archiveAll")
        if result is None:
            raise ToolError("Failed to archive all notifications")

        return {
            "success": True,
            "overview": result,
            "message": "All notifications archived successfully",
        }

    @mcp.tool()
    @tool_error_handler("delete notification")
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

        variables: dict[str, Any] = {
            "id": notification_id,
            "type": validated_type,
        }
        response = await make_graphql_request(DELETE_NOTIFICATION_MUTATION, variables)

        result = response.get("deleteNotification")
        if result is None:
            raise ToolError(f"Failed to delete notification '{notification_id}'")

        return {
            "success": True,
            "overview": result,
            "message": "Notification deleted successfully",
        }

    @mcp.tool()
    @tool_error_handler("delete archived notifications")
    async def delete_archived_notifications() -> dict[str, Any]:
        """Deletes ALL archived notifications. This is a DESTRUCTIVE operation that cannot be undone.

        Returns:
            Dict containing updated notification overview counts
        """
        response = await make_graphql_request(DELETE_ARCHIVED_NOTIFICATIONS_MUTATION)

        result = response.get("deleteArchivedNotifications")
        if result is None:
            raise ToolError("Failed to delete archived notifications")

        return {
            "success": True,
            "overview": result,
            "message": "All archived notifications deleted",
        }

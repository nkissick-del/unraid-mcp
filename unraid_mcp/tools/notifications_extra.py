"""Extended notification management tools.

This module is gated under the 'notifications-extra' module and disabled by default.
It provides creation, unarchive, and recalculation operations for notifications.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.constants import NOTIFICATION_IMPORTANCE_VALUES
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import validate_enum, validate_string_not_empty
from .queries.notifications_extra import (
    ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
    CREATE_NOTIFICATION_MUTATION,
    NOTIFY_IF_UNIQUE_MUTATION,
    RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
    UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
    UNARCHIVE_NOTIFICATIONS_MUTATION,
    UNREAD_NOTIFICATION_MUTATION,
)


def register_notifications_extra_tools(mcp: FastMCP) -> None:
    """Register extended notification tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    @tool_error_handler("create notification")
    async def create_notification(
        subject: str,
        description: str,
        importance: str = "INFO",
    ) -> dict[str, Any]:
        """Creates a new notification on the Unraid server.

        Args:
            subject: Notification subject/title
            description: Notification body/description
            importance: Importance level - 'INFO', 'WARNING', or 'ALERT' (default 'INFO')

        Returns:
            Dict containing the created notification details
        """
        validate_string_not_empty(subject, "subject")
        validate_string_not_empty(description, "description")
        validated_importance = validate_enum(
            importance.upper(), NOTIFICATION_IMPORTANCE_VALUES, "importance"
        )

        variables: dict[str, Any] = {
            "input": {
                "subject": subject,
                "description": description,
                "importance": validated_importance,
            }
        }

        response = await make_graphql_request(CREATE_NOTIFICATION_MUTATION, variables)

        result = response.get("createNotification")
        if not result:
            raise ToolError("Failed to create notification")

        return {
            "success": True,
            "notification": result,
            "message": "Notification created successfully",
        }

    @mcp.tool()
    @tool_error_handler("archive notifications")
    async def archive_notifications(
        notification_ids: list[str],
    ) -> dict[str, Any]:
        """Archives multiple notifications by their IDs in a single batch operation.

        Args:
            notification_ids: List of notification IDs to archive

        Returns:
            Dict containing updated notification overview counts
        """
        if not notification_ids:
            raise ToolError("notification_ids must be a non-empty list")
        for nid in notification_ids:
            validate_string_not_empty(nid, "notification_id")

        variables: dict[str, Any] = {"ids": notification_ids}
        response = await make_graphql_request(ARCHIVE_NOTIFICATIONS_BATCH_MUTATION, variables)

        result = response.get("archiveNotifications")
        if not result:
            raise ToolError("Failed to archive notifications")

        return {
            "success": True,
            "overview": result,
            "message": f"Archived {len(notification_ids)} notification(s)",
        }

    @mcp.tool()
    @tool_error_handler("create unique notification")
    async def notify_if_unique(
        subject: str,
        description: str,
        importance: str = "INFO",
    ) -> dict[str, Any]:
        """Creates a notification only if no matching unread notification exists.

        Args:
            subject: Notification subject/title
            description: Notification body/description
            importance: Importance level - 'INFO', 'WARNING', or 'ALERT' (default 'INFO')

        Returns:
            Dict containing the notification details (created or existing)
        """
        validate_string_not_empty(subject, "subject")
        validate_string_not_empty(description, "description")
        validated_importance = validate_enum(
            importance.upper(), NOTIFICATION_IMPORTANCE_VALUES, "importance"
        )

        variables: dict[str, Any] = {
            "input": {
                "subject": subject,
                "description": description,
                "importance": validated_importance,
            }
        }

        response = await make_graphql_request(NOTIFY_IF_UNIQUE_MUTATION, variables)

        result = response.get("notifyIfUnique")
        if not result:
            raise ToolError("Failed to create unique notification")

        return {
            "success": True,
            "notification": result,
            "message": "Unique notification created or matched existing",
        }

    @mcp.tool()
    @tool_error_handler("unread notification")
    async def unread_notification(
        notification_id: str,
    ) -> dict[str, Any]:
        """Moves an archived notification back to unread status.

        Args:
            notification_id: The ID of the notification to mark as unread

        Returns:
            Dict containing the notification details
        """
        validate_string_not_empty(notification_id, "notification_id")

        variables: dict[str, Any] = {"id": notification_id}
        response = await make_graphql_request(UNREAD_NOTIFICATION_MUTATION, variables)

        result = response.get("unreadNotification")
        if not result:
            raise ToolError(f"Failed to mark notification '{notification_id}' as unread")

        return {
            "success": True,
            "notification": result,
            "message": "Notification marked as unread",
        }

    @mcp.tool()
    @tool_error_handler("unarchive notifications")
    async def unarchive_notifications(
        notification_ids: list[str],
    ) -> dict[str, Any]:
        """Unarchives multiple notifications by their IDs in a single batch operation.

        Args:
            notification_ids: List of notification IDs to unarchive

        Returns:
            Dict containing updated notification overview counts
        """
        if not notification_ids:
            raise ToolError("notification_ids must be a non-empty list")
        for nid in notification_ids:
            validate_string_not_empty(nid, "notification_id")

        variables: dict[str, Any] = {"ids": notification_ids}
        response = await make_graphql_request(UNARCHIVE_NOTIFICATIONS_MUTATION, variables)

        result = response.get("unarchiveNotifications")
        if not result:
            raise ToolError("Failed to unarchive notifications")

        return {
            "success": True,
            "overview": result,
            "message": f"Unarchived {len(notification_ids)} notification(s)",
        }

    @mcp.tool()
    @tool_error_handler("unarchive all notifications")
    async def unarchive_all_notifications() -> dict[str, Any]:
        """Unarchives all archived notifications.

        Returns:
            Dict containing updated notification overview counts
        """
        response = await make_graphql_request(UNARCHIVE_ALL_NOTIFICATIONS_MUTATION)

        result = response.get("unarchiveAll")
        if not result:
            raise ToolError("Failed to unarchive all notifications")

        return {
            "success": True,
            "overview": result,
            "message": "All notifications unarchived",
        }

    @mcp.tool()
    @tool_error_handler("recalculate notification overview")
    async def recalculate_notification_overview() -> dict[str, Any]:
        """Force-recalculates notification overview counts.

        Useful when notification counts appear out of sync.

        Returns:
            Dict containing the recalculated notification overview
        """
        response = await make_graphql_request(RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION)

        result = response.get("recalculateOverview")
        if not result:
            raise ToolError("Failed to recalculate notification overview")

        return {
            "success": True,
            "overview": result,
            "message": "Notification overview recalculated",
        }

    logger.info("Notifications-extra tools registered successfully")

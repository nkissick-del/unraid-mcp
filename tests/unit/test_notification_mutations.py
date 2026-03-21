"""Tests for notification mutation queries and validation."""

import pytest

from unraid_mcp.core.constants import (
    NOTIFICATION_IMPORTANCE_VALUES,
    NOTIFICATION_TYPE_VALUES,
)
from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_enum
from unraid_mcp.tools.queries.notifications import (
    ARCHIVE_ALL_NOTIFICATIONS_MUTATION,
    ARCHIVE_NOTIFICATION_MUTATION,
    DELETE_ARCHIVED_NOTIFICATIONS_MUTATION,
    DELETE_NOTIFICATION_MUTATION,
)


class TestNotificationQueryStrings:
    def test_archive_notification_is_top_level(self):
        """Notification mutations must be top-level, not nested under a namespace."""
        assert "archiveNotification" in ARCHIVE_NOTIFICATION_MUTATION
        assert "$id" in ARCHIVE_NOTIFICATION_MUTATION

    def test_archive_all_is_top_level(self):
        assert "archiveAll" in ARCHIVE_ALL_NOTIFICATIONS_MUTATION
        assert "$importance" in ARCHIVE_ALL_NOTIFICATIONS_MUTATION

    def test_delete_notification_is_top_level(self):
        assert "deleteNotification" in DELETE_NOTIFICATION_MUTATION
        assert "$id" in DELETE_NOTIFICATION_MUTATION
        assert "$type" in DELETE_NOTIFICATION_MUTATION

    def test_delete_archived_is_top_level(self):
        assert "deleteArchivedNotifications" in DELETE_ARCHIVED_NOTIFICATIONS_MUTATION

    def test_all_mutations_are_graphql(self):
        for mutation in [
            ARCHIVE_NOTIFICATION_MUTATION,
            ARCHIVE_ALL_NOTIFICATIONS_MUTATION,
            DELETE_NOTIFICATION_MUTATION,
            DELETE_ARCHIVED_NOTIFICATIONS_MUTATION,
        ]:
            assert "mutation" in mutation


class TestNotificationEnumValidation:
    def test_valid_importance_values(self):
        for val in NOTIFICATION_IMPORTANCE_VALUES:
            result = validate_enum(val, NOTIFICATION_IMPORTANCE_VALUES, "importance")
            assert result == val

    def test_invalid_importance_raises(self):
        with pytest.raises(ValidationError, match="Invalid importance"):
            validate_enum("CRITICAL", NOTIFICATION_IMPORTANCE_VALUES, "importance")

    def test_valid_type_values(self):
        for val in NOTIFICATION_TYPE_VALUES:
            result = validate_enum(val, NOTIFICATION_TYPE_VALUES, "notification_type")
            assert result == val

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError, match="Invalid notification_type"):
            validate_enum("DELETED", NOTIFICATION_TYPE_VALUES, "notification_type")

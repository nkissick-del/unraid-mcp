"""Tests for extended notification management tools."""

import pytest

from unraid_mcp.core.constants import NOTIFICATION_IMPORTANCE_VALUES
from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_enum
from unraid_mcp.tools.queries.notifications_extra import (
    ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
    CREATE_NOTIFICATION_MUTATION,
    NOTIFY_IF_UNIQUE_MUTATION,
    RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
    UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
    UNARCHIVE_NOTIFICATIONS_MUTATION,
    UNREAD_NOTIFICATION_MUTATION,
)


class TestNotificationsExtraMutationStrings:
    def test_create_notification_has_input_variable(self):
        assert "$input" in CREATE_NOTIFICATION_MUTATION
        assert "NotificationData" in CREATE_NOTIFICATION_MUTATION

    def test_archive_batch_has_ids_variable(self):
        assert "$ids" in ARCHIVE_NOTIFICATIONS_BATCH_MUTATION

    def test_notify_if_unique_has_input_variable(self):
        assert "$input" in NOTIFY_IF_UNIQUE_MUTATION
        assert "NotificationData" in NOTIFY_IF_UNIQUE_MUTATION

    def test_unread_notification_has_id_variable(self):
        assert "$id" in UNREAD_NOTIFICATION_MUTATION

    def test_unarchive_has_ids_variable(self):
        assert "$ids" in UNARCHIVE_NOTIFICATIONS_MUTATION

    def test_all_mutations_are_graphql(self):
        all_mutations = [
            CREATE_NOTIFICATION_MUTATION,
            ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
            NOTIFY_IF_UNIQUE_MUTATION,
            UNREAD_NOTIFICATION_MUTATION,
            UNARCHIVE_NOTIFICATIONS_MUTATION,
            UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
            RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
        ]
        for mutation in all_mutations:
            assert "mutation" in mutation

    def test_detail_mutations_contain_detail_fields(self):
        detail_mutations = [
            CREATE_NOTIFICATION_MUTATION,
            NOTIFY_IF_UNIQUE_MUTATION,
            UNREAD_NOTIFICATION_MUTATION,
        ]
        for mutation in detail_mutations:
            assert "subject" in mutation
            assert "description" in mutation
            assert "importance" in mutation
            assert "timestamp" in mutation

    def test_overview_mutations_contain_overview_fields(self):
        overview_mutations = [
            ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
            UNARCHIVE_NOTIFICATIONS_MUTATION,
            UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
            RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
        ]
        for mutation in overview_mutations:
            assert "unread" in mutation
            assert "archive" in mutation
            assert "total" in mutation

    def test_mutations_are_top_level(self):
        """All notification-extra mutations should be top-level, not nested under a namespace."""
        all_mutations = [
            CREATE_NOTIFICATION_MUTATION,
            ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
            NOTIFY_IF_UNIQUE_MUTATION,
            UNREAD_NOTIFICATION_MUTATION,
            UNARCHIVE_NOTIFICATIONS_MUTATION,
            UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
            RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
        ]
        for mutation in all_mutations:
            # None of these should have a namespace like "docker {" or "parityCheck {"
            assert "docker {" not in mutation
            assert "parityCheck {" not in mutation


class TestNotificationImportanceValidation:
    @pytest.mark.parametrize("importance", NOTIFICATION_IMPORTANCE_VALUES)
    def test_valid_importance_accepted(self, importance: str):
        result = validate_enum(importance, NOTIFICATION_IMPORTANCE_VALUES, "importance")
        assert result == importance

    def test_invalid_importance_raises(self):
        with pytest.raises(ValidationError, match="Invalid importance"):
            validate_enum("CRITICAL", NOTIFICATION_IMPORTANCE_VALUES, "importance")

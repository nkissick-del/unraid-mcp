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
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (
                CREATE_NOTIFICATION_MUTATION,
                [
                    "mutation",
                    "$input",
                    "NotificationData",
                    "subject",
                    "description",
                    "importance",
                    "timestamp",
                ],
            ),
            (
                ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
                ["mutation", "$ids", "unread", "archive", "total"],
            ),
            (
                NOTIFY_IF_UNIQUE_MUTATION,
                [
                    "mutation",
                    "$input",
                    "NotificationData",
                    "subject",
                    "description",
                    "importance",
                    "timestamp",
                ],
            ),
            (
                UNREAD_NOTIFICATION_MUTATION,
                ["mutation", "$id", "subject", "description", "importance", "timestamp"],
            ),
            (UNARCHIVE_NOTIFICATIONS_MUTATION, ["mutation", "$ids", "unread", "archive", "total"]),
            (UNARCHIVE_ALL_NOTIFICATIONS_MUTATION, ["mutation", "unread", "archive", "total"]),
            (
                RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
                ["mutation", "unread", "archive", "total"],
            ),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation

    @pytest.mark.parametrize(
        "mutation",
        [
            CREATE_NOTIFICATION_MUTATION,
            ARCHIVE_NOTIFICATIONS_BATCH_MUTATION,
            NOTIFY_IF_UNIQUE_MUTATION,
            UNREAD_NOTIFICATION_MUTATION,
            UNARCHIVE_NOTIFICATIONS_MUTATION,
            UNARCHIVE_ALL_NOTIFICATIONS_MUTATION,
            RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION,
        ],
    )
    def test_mutations_are_top_level(self, mutation):
        """All notification-extra mutations should be top-level, not nested under a namespace."""
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

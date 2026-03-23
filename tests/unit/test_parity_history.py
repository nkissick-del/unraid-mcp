"""Tests for parity history query definition."""

from graphql import parse as gql_parse

from unraid_mcp.tools.queries.system_extra import PARITY_HISTORY_QUERY


class TestParityHistoryQuery:
    def test_query_is_valid_graphql(self):
        doc = gql_parse(PARITY_HISTORY_QUERY)
        assert len(doc.definitions) == 1

    def test_query_contains_parity_history(self):
        assert "parityHistory" in PARITY_HISTORY_QUERY

    def test_query_contains_date_field(self):
        assert "date" in PARITY_HISTORY_QUERY

    def test_query_contains_speed_field(self):
        assert "speed" in PARITY_HISTORY_QUERY

    def test_query_contains_status_field(self):
        assert "status" in PARITY_HISTORY_QUERY

    def test_query_contains_progress_field(self):
        assert "progress" in PARITY_HISTORY_QUERY

    def test_query_contains_correcting_field(self):
        assert "correcting" in PARITY_HISTORY_QUERY

    def test_query_contains_running_field(self):
        assert "running" in PARITY_HISTORY_QUERY

    def test_query_contains_paused_field(self):
        assert "paused" in PARITY_HISTORY_QUERY

    def test_query_does_not_contain_errors_field(self):
        # errors field removed to avoid Int overflow on the live API
        assert "errors" not in PARITY_HISTORY_QUERY

    def test_query_does_not_contain_duration_field(self):
        # duration field removed to avoid Int overflow on the live API
        assert "duration" not in PARITY_HISTORY_QUERY

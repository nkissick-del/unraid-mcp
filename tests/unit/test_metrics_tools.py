"""Tests for metrics tools query definitions and structure."""

from graphql import parse as gql_parse

from unraid_mcp.tools.queries.system_extra import SYSTEM_METRICS_QUERY


class TestSystemMetricsQuery:
    def test_query_is_valid_graphql(self):
        doc = gql_parse(SYSTEM_METRICS_QUERY)
        assert len(doc.definitions) == 1

    def test_query_contains_cpu_field(self):
        assert "cpu" in SYSTEM_METRICS_QUERY

    def test_query_contains_memory_field(self):
        assert "memory" in SYSTEM_METRICS_QUERY

    def test_query_contains_temperature_field(self):
        assert "temperature" in SYSTEM_METRICS_QUERY

    def test_query_contains_percent_total(self):
        assert "percentTotal" in SYSTEM_METRICS_QUERY

    def test_query_contains_sensors(self):
        assert "sensors" in SYSTEM_METRICS_QUERY

    def test_query_contains_summary(self):
        assert "summary" in SYSTEM_METRICS_QUERY

    def test_query_contains_cpu_nested_fields(self):
        assert "percentUser" in SYSTEM_METRICS_QUERY
        assert "percentSystem" in SYSTEM_METRICS_QUERY
        assert "percentIdle" in SYSTEM_METRICS_QUERY

    def test_query_contains_memory_fields(self):
        assert "total" in SYSTEM_METRICS_QUERY
        assert "used" in SYSTEM_METRICS_QUERY
        assert "free" in SYSTEM_METRICS_QUERY
        assert "available" in SYSTEM_METRICS_QUERY
        assert "swapTotal" in SYSTEM_METRICS_QUERY

    def test_query_contains_temperature_sensor_fields(self):
        assert "name" in SYSTEM_METRICS_QUERY
        assert "type" in SYSTEM_METRICS_QUERY
        assert "location" in SYSTEM_METRICS_QUERY
        assert "current" in SYSTEM_METRICS_QUERY
        assert "warning" in SYSTEM_METRICS_QUERY
        assert "critical" in SYSTEM_METRICS_QUERY

    def test_query_contains_summary_fields(self):
        assert "average" in SYSTEM_METRICS_QUERY
        assert "warningCount" in SYSTEM_METRICS_QUERY
        assert "criticalCount" in SYSTEM_METRICS_QUERY


class TestGetSystemTimeQuery:
    def test_query_is_valid_graphql(self):
        query = "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_current_time(self):
        query = "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }"
        assert "currentTime" in query

    def test_query_contains_timezone(self):
        query = "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }"
        assert "timeZone" in query

    def test_query_contains_use_ntp(self):
        query = "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }"
        assert "useNtp" in query

    def test_query_contains_ntp_servers(self):
        query = "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }"
        assert "ntpServers" in query


class TestGetTimezoneOptionsQuery:
    def test_query_is_valid_graphql(self):
        query = "query GetTimezoneOptions { timeZoneOptions { value label } }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_value_field(self):
        query = "query GetTimezoneOptions { timeZoneOptions { value label } }"
        assert "value" in query

    def test_query_contains_label_field(self):
        query = "query GetTimezoneOptions { timeZoneOptions { value label } }"
        assert "label" in query

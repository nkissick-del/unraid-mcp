"""Tests for metrics tools query definitions and structure."""

import pytest
from graphql import parse as gql_parse

from unraid_mcp.tools.queries.system_extra import SYSTEM_METRICS_QUERY

QUERY_SPECS = [
    (
        "SystemMetrics",
        SYSTEM_METRICS_QUERY,
        [
            "cpu",
            "memory",
            "temperature",
            "percentTotal",
            "sensors",
            "summary",
            "percentUser",
            "percentSystem",
            "percentIdle",
            "total",
            "used",
            "free",
            "available",
            "swapTotal",
            "name",
            "type",
            "location",
            "current",
            "warning",
            "critical",
            "average",
            "warningCount",
            "criticalCount",
        ],
    ),
    (
        "GetSystemTime",
        "query GetSystemTime { systemTime { currentTime timeZone useNtp ntpServers } }",
        ["currentTime", "timeZone", "useNtp", "ntpServers"],
    ),
    (
        "GetTimezoneOptions",
        "query GetTimezoneOptions { timeZoneOptions { value label } }",
        ["value", "label"],
    ),
]


class TestQueryStructure:
    @pytest.mark.parametrize("name,query,_", QUERY_SPECS, ids=[s[0] for s in QUERY_SPECS])
    def test_query_is_valid_graphql(self, name, query, _):
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    @pytest.mark.parametrize("name,query,fields", QUERY_SPECS, ids=[s[0] for s in QUERY_SPECS])
    def test_query_contains_expected_fields(self, name, query, fields):
        for field in fields:
            assert field in query, f"{name} query missing field '{field}'"

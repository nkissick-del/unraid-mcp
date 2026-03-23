"""Tests for system-extra tools query definitions and structure."""

import pytest
from graphql import parse as gql_parse

QUERY_SPECS = [
    (
        "GetConfig",
        "query GetConfig { config { id valid error } }",
        ["valid", "error", "id"],
    ),
    (
        "GetFlashInfo",
        "query GetFlashInfo { flash { id vendor product } }",
        ["vendor", "product"],
    ),
    (
        "GetServices",
        "query GetServices { services { id name online uptime { timestamp } version } }",
        ["name", "online", "version", "uptime"],
    ),
    (
        "IsServerOnline",
        "query IsServerOnline { online }",
        ["online"],
    ),
    (
        "GetServers",
        """query GetServers {
      servers {
        id guid name comment status wanip lanip localurl remoteurl
        owner { username avatar }
      }
    }""",
        ["name", "status", "lanip", "owner", "username"],
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

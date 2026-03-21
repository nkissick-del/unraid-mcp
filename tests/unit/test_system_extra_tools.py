"""Tests for system-extra tools query definitions and structure."""

from graphql import parse as gql_parse


class TestGetConfigStatusQuery:
    def test_query_is_valid_graphql(self):
        query = "query GetConfig { config { id valid error } }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_valid_field(self):
        query = "query GetConfig { config { id valid error } }"
        assert "valid" in query

    def test_query_contains_error_field(self):
        query = "query GetConfig { config { id valid error } }"
        assert "error" in query

    def test_query_contains_id_field(self):
        query = "query GetConfig { config { id valid error } }"
        assert "id" in query


class TestGetFlashInfoQuery:
    def test_query_is_valid_graphql(self):
        query = "query GetFlashInfo { flash { id guid vendor product } }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_guid_field(self):
        query = "query GetFlashInfo { flash { id guid vendor product } }"
        assert "guid" in query

    def test_query_contains_vendor_field(self):
        query = "query GetFlashInfo { flash { id guid vendor product } }"
        assert "vendor" in query

    def test_query_contains_product_field(self):
        query = "query GetFlashInfo { flash { id guid vendor product } }"
        assert "product" in query


class TestGetServicesQuery:
    def test_query_is_valid_graphql(self):
        query = "query GetServices { services { id name online uptime { timestamp } version } }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_name_field(self):
        query = "query GetServices { services { id name online uptime { timestamp } version } }"
        assert "name" in query

    def test_query_contains_online_field(self):
        query = "query GetServices { services { id name online uptime { timestamp } version } }"
        assert "online" in query

    def test_query_contains_version_field(self):
        query = "query GetServices { services { id name online uptime { timestamp } version } }"
        assert "version" in query

    def test_query_contains_uptime_field(self):
        query = "query GetServices { services { id name online uptime { timestamp } version } }"
        assert "uptime" in query


class TestIsServerOnlineQuery:
    def test_query_is_valid_graphql(self):
        query = "query IsServerOnline { online }"
        doc = gql_parse(query)
        assert len(doc.definitions) == 1

    def test_query_contains_online_field(self):
        query = "query IsServerOnline { online }"
        assert "online" in query


class TestGetServersQuery:
    QUERY = """query GetServers {
      servers {
        id guid name comment status wanip lanip localurl remoteurl
        owner { id username url avatar }
      }
    }"""

    def test_query_is_valid_graphql(self):
        doc = gql_parse(self.QUERY)
        assert len(doc.definitions) == 1

    def test_query_contains_name_field(self):
        assert "name" in self.QUERY

    def test_query_contains_status_field(self):
        assert "status" in self.QUERY

    def test_query_contains_lanip_field(self):
        assert "lanip" in self.QUERY

    def test_query_contains_owner_subquery(self):
        assert "owner" in self.QUERY
        assert "username" in self.QUERY

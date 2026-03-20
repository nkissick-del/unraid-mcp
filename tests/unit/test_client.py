"""Tests for the GraphQL client module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from unraid_mcp.core.client import (
    get_timeout_for_operation,
    is_idempotent_error,
    make_graphql_request,
    sanitize_query,
)
from unraid_mcp.core.constants import QUERY_TRUNCATION_LENGTH
from unraid_mcp.core.exceptions import ToolError


class TestSanitizeQuery:
    def test_basic_sanitization(self):
        query = "query { field }"
        result = sanitize_query(query)
        assert "field" in result

    def test_variable_replacement(self):
        query = "query ($id: ID!, $name: String) { field }"
        result = sanitize_query(query)
        assert "$id" not in result or "$VARIABLE" in result

    def test_truncation(self):
        query = "x" * 1000
        result = sanitize_query(query)
        assert len(result) == QUERY_TRUNCATION_LENGTH


class TestIsIdempotentError:
    def test_already_started_with_start(self):
        assert is_idempotent_error("Container already started", "start") is True

    def test_already_stopped_with_stop(self):
        assert is_idempotent_error("Container already stopped", "stop") is True

    def test_http_304_start(self):
        assert is_idempotent_error("HTTP code 304", "start") is True

    def test_http_304_stop(self):
        assert is_idempotent_error("HTTP code 304", "stop") is True

    def test_unrelated_error(self):
        assert is_idempotent_error("Something went wrong", "start") is False

    def test_wrong_operation(self):
        assert is_idempotent_error("already started", "stop") is False

    def test_unknown_operation(self):
        assert is_idempotent_error("already started", "restart") is False


class TestMakeGraphqlRequest:
    @pytest.mark.asyncio
    async def test_success_returns_data(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"info": {"id": "1"}}}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test:8080/graphql"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "test-key"),
        ):
            result = await make_graphql_request("query { info { id } }")
            assert result == {"info": {"id": "1"}}

    @pytest.mark.asyncio
    async def test_missing_api_url_raises(self):
        with patch("unraid_mcp.core.client.UNRAID_API_URL", ""):
            with pytest.raises(ToolError, match="UNRAID_API_URL"):
                await make_graphql_request("query { test }")

    @pytest.mark.asyncio
    async def test_missing_api_key_raises(self):
        with (
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", ""),
        ):
            with pytest.raises(ToolError, match="UNRAID_API_KEY"):
                await make_graphql_request("query { test }")

    @pytest.mark.asyncio
    async def test_graphql_errors_raise(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"message": "Field not found"}],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "key"),
        ):
            with pytest.raises(ToolError, match="GraphQL API error"):
                await make_graphql_request("query { bad }")

    @pytest.mark.asyncio
    async def test_idempotent_error_returns_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"message": "Container already started"}],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "key"),
        ):
            result = await make_graphql_request(
                "mutation { start }", operation_context={"operation": "start"}
            )
            assert result["idempotent_success"] is True

    @pytest.mark.asyncio
    async def test_http_error_raises(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        request = httpx.Request("POST", "http://test")
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=request, response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "key"),
        ):
            with pytest.raises(ToolError, match="HTTP error"):
                await make_graphql_request("query { test }")

    @pytest.mark.asyncio
    async def test_network_error_raises(self):
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "key"),
        ):
            with pytest.raises(ToolError, match="Network connection error"):
                await make_graphql_request("query { test }")

    @pytest.mark.asyncio
    async def test_invalid_json_raises(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("bad", "", 0)

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.is_closed = False

        with (
            patch("unraid_mcp.core.client._get_http_client", return_value=mock_client),
            patch("unraid_mcp.core.client.UNRAID_API_URL", "http://test"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "key"),
        ):
            with pytest.raises(ToolError, match="Invalid JSON"):
                await make_graphql_request("query { test }")


class TestGetTimeoutForOperation:
    def test_default_timeout(self):
        timeout = get_timeout_for_operation("default")
        assert isinstance(timeout, httpx.Timeout)

    def test_disk_timeout(self):
        timeout = get_timeout_for_operation("disk_operations")
        assert isinstance(timeout, httpx.Timeout)

    def test_disk_timeout_has_longer_read(self):
        default = get_timeout_for_operation("default")
        disk = get_timeout_for_operation("disk_operations")
        assert disk.read > default.read

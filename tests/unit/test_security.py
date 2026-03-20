"""Security invariant tests — cross-cutting concerns that verify defense-in-depth."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from unraid_mcp.core.exceptions import ToolError


class TestQueryUnraidApiRejectsMutation:
    """Verify the full tool path blocks mutations, not just the AST parser."""

    @pytest.mark.asyncio
    async def test_rejects_mutation(self):
        from unraid_mcp.tools.api import register_api_tools

        mcp = MagicMock()
        captured_tools: dict = {}

        def fake_tool():
            def decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return decorator

        mcp.tool = fake_tool
        register_api_tools(mcp)

        query_fn = captured_tools["query_unraid_api"]
        with pytest.raises(ToolError, match="mutations are not allowed"):
            await query_fn(graphql_query='mutation { deleteContainer(id: "abc") }')

    @pytest.mark.asyncio
    async def test_rejects_subscription(self):
        from unraid_mcp.tools.api import register_api_tools

        mcp = MagicMock()
        captured_tools: dict = {}

        def fake_tool():
            def decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return decorator

        mcp.tool = fake_tool
        register_api_tools(mcp)

        query_fn = captured_tools["query_unraid_api"]
        with pytest.raises(ToolError, match="subscriptions are not allowed"):
            await query_fn(graphql_query="subscription { onEvent { id } }")


class TestHttpErrorDoesNotLeakResponseBody:
    @pytest.mark.asyncio
    async def test_status_code_only_in_tool_error(self):
        """ToolError message should contain only the status code, not the response body."""
        from unraid_mcp.core.client import make_graphql_request

        sensitive_body = "Internal error at /opt/unraid/db/secrets.sqlite: stack trace here"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = sensitive_body
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
            with pytest.raises(ToolError, match="HTTP 500") as exc_info:
                await make_graphql_request("query { test }")

            error_msg = str(exc_info.value)
            assert "secrets.sqlite" not in error_msg
            assert "stack trace" not in error_msg
            assert "/opt/unraid" not in error_msg


class TestWsAuthPayloadMinimal:
    def test_payload_has_exactly_two_keys(self):
        """Auth payload should contain only Authorization and x-api-key."""
        from unraid_mcp.subscriptions.manager import _build_ws_auth_payload

        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key-12345"):
            payload = _build_ws_auth_payload()

        assert set(payload.keys()) == {"Authorization", "x-api-key"}
        assert "headers" not in payload

    def test_payload_contains_bearer_token(self):
        from unraid_mcp.subscriptions.manager import _build_ws_auth_payload

        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key-12345"):
            payload = _build_ws_auth_payload()

        assert payload["Authorization"] == "Bearer test-key-12345"


class TestRedactingFilter:
    def _make_record(self, msg: str) -> logging.LogRecord:
        return logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )

    def test_masks_api_key(self):
        from unraid_mcp.config.logging import RedactingFilter

        with patch("unraid_mcp.config.settings.UNRAID_API_KEY", "super-secret-key-12345678"):
            rf = RedactingFilter()

        record = self._make_record("Connecting with key super-secret-key-12345678 now")
        rf.filter(record)
        assert "super-secret-key-12345678" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_masks_bearer_token(self):
        from unraid_mcp.config.logging import RedactingFilter

        rf = RedactingFilter()
        record = self._make_record("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload")
        rf.filter(record)
        assert "eyJhbGciOiJIUzI1NiJ9" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_masks_api_key_pattern(self):
        from unraid_mcp.config.logging import RedactingFilter

        rf = RedactingFilter()
        record = self._make_record("Header api_key=mysecretvalue sent")
        rf.filter(record)
        assert "mysecretvalue" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_preserves_non_sensitive_messages(self):
        from unraid_mcp.config.logging import RedactingFilter

        rf = RedactingFilter()
        record = self._make_record("GraphQL request successful")
        rf.filter(record)
        assert record.msg == "GraphQL request successful"

    def test_redacts_in_args_tuple(self):
        from unraid_mcp.config.logging import RedactingFilter

        rf = RedactingFilter()
        record = self._make_record("Header: %s")
        record.args = ("Bearer secret_token_value",)
        rf.filter(record)
        assert "secret_token_value" not in record.args[0]

    def test_redacts_in_args_dict(self):
        from unraid_mcp.config.logging import RedactingFilter

        rf = RedactingFilter()
        record = self._make_record("%(header)s")
        record.args = {"header": "Bearer secret_token_value"}
        rf.filter(record)
        assert "secret_token_value" not in record.args["header"]


class TestGraphqlErrorDoesNotExposeInternalDetails:
    @pytest.mark.asyncio
    async def test_graphql_error_uses_message_field_only(self):
        """GraphQL errors should surface the message field, not raw internals."""
        from unraid_mcp.core.client import make_graphql_request

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [
                {
                    "message": "Field 'foo' not found",
                    "locations": [{"line": 1, "column": 3}],
                    "extensions": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "stacktrace": ["at Resolver.resolve()"],
                    },
                }
            ],
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
            with pytest.raises(ToolError, match="Field 'foo' not found") as exc_info:
                await make_graphql_request("query { foo }")

            error_msg = str(exc_info.value)
            assert "stacktrace" not in error_msg
            assert "Resolver.resolve" not in error_msg

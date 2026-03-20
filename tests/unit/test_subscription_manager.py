"""Tests for the SubscriptionManager class."""

from unittest.mock import AsyncMock, patch

import pytest

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.subscriptions.manager import (
    SubscriptionManager,
    _build_ws_auth_payload,
    _build_ws_url,
    _validate_subscription_query,
)


class TestBuildWsAuthPayload:
    def test_returns_dict_with_api_key(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key-123"):
            payload = _build_ws_auth_payload()
            assert len(payload) == 2
            assert payload["Authorization"] == "Bearer test-key-123"
            assert payload["x-api-key"] == "test-key-123"

    def test_no_duplicate_or_nested_keys(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key-123"):
            payload = _build_ws_auth_payload()
            assert "headers" not in payload
            assert len(payload) == 2


class TestBuildWsUrl:
    def test_https_to_wss(self):
        assert _build_ws_url("https://host/api") == "wss://host/api/graphql"

    def test_http_to_ws(self):
        assert _build_ws_url("http://tower:8080") == "ws://tower:8080/graphql"

    def test_preserves_existing_graphql_path(self):
        assert _build_ws_url("https://host/graphql") == "wss://host/graphql"

    def test_strips_trailing_slash(self):
        assert _build_ws_url("https://host/api/") == "wss://host/api/graphql"

    def test_preserves_port(self):
        assert _build_ws_url("https://host:9443/api") == "wss://host:9443/api/graphql"

    def test_rejects_empty_host(self):
        with pytest.raises(ValueError, match="no host"):
            _build_ws_url("https:///path")

    def test_rejects_userinfo(self):
        with pytest.raises(ValueError, match="userinfo"):
            _build_ws_url("https://user:pass@host")

    def test_rejects_fragment(self):
        with pytest.raises(ValueError, match="fragment"):
            _build_ws_url("https://host#frag")

    def test_rejects_unsupported_scheme(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            _build_ws_url("ftp://host")


class TestValidateSubscriptionQuery:
    def test_valid_subscription(self):
        _validate_subscription_query("subscription { onUpdate }")

    def test_named_subscription(self):
        _validate_subscription_query("subscription MySubscription { onUpdate { id } }")

    def test_mutation_rejected(self):
        with pytest.raises(ValidationError, match="Only subscription operations are allowed"):
            _validate_subscription_query("mutation { delete }")

    def test_query_rejected(self):
        with pytest.raises(ValidationError, match="Only subscription operations are allowed"):
            _validate_subscription_query("query { info }")

    def test_anonymous_query_rejected(self):
        with pytest.raises(ValidationError, match="Only subscription operations are allowed"):
            _validate_subscription_query("{ info }")

    def test_invalid_syntax_rejected(self):
        with pytest.raises(ValidationError, match="Invalid GraphQL syntax"):
            _validate_subscription_query("not a valid query {{{")

    def test_mixed_operations_rejected(self):
        with pytest.raises(ValidationError, match="Only subscription operations are allowed"):
            _validate_subscription_query("subscription Sub { onUpdate } query Q { info }")


class TestSubscriptionManagerInit:
    def test_default_state(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            assert mgr.active_subscriptions == {}
            assert mgr.resource_data == {}
            assert mgr.websocket is None


class TestGetResourceData:
    @pytest.mark.asyncio
    async def test_none_for_unknown(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            assert await mgr.get_resource_data("nonexistent") is None

    @pytest.mark.asyncio
    async def test_returns_data_for_known(self):
        from datetime import datetime

        from unraid_mcp.core.types import SubscriptionData

        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            mgr.resource_data["test"] = SubscriptionData(
                data={"value": 42},
                last_updated=datetime.now(),
                subscription_type="test",
            )
            assert await mgr.get_resource_data("test") == {"value": 42}


class TestListActiveSubscriptions:
    def test_empty_initially(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            assert mgr.list_active_subscriptions() == []


class TestGetSubscriptionStatus:
    @pytest.mark.asyncio
    async def test_returns_expected_structure(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            status = await mgr.get_subscription_status()
            assert "logFileSubscription" in status
            sub = status["logFileSubscription"]
            assert "config" in sub
            assert "runtime" in sub
            assert "data" in sub
            assert sub["runtime"]["active"] is False


class TestStartSubscription:
    @pytest.mark.asyncio
    async def test_creates_task(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            # Mock the subscription loop to avoid real websocket
            mgr._subscription_loop = AsyncMock()

            await mgr.start_subscription("test_sub", "subscription { test }")
            assert "test_sub" in mgr.active_subscriptions
            # Clean up
            await mgr.stop_subscription("test_sub")

    @pytest.mark.asyncio
    async def test_skips_if_already_active(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            mgr._subscription_loop = AsyncMock()

            await mgr.start_subscription("test_sub", "subscription { test }")
            # Second call should skip
            await mgr.start_subscription("test_sub", "subscription { test }")
            assert "test_sub" in mgr.active_subscriptions
            await mgr.stop_subscription("test_sub")


class TestStopSubscription:
    @pytest.mark.asyncio
    async def test_cancels_task_and_clears(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            mgr._subscription_loop = AsyncMock()

            await mgr.start_subscription("test_sub", "subscription { test }")
            await mgr.stop_subscription("test_sub")
            assert "test_sub" not in mgr.active_subscriptions
            assert mgr.connection_states.get("test_sub") == "stopped"


class TestStopAllSubscriptions:
    @pytest.mark.asyncio
    async def test_cancels_all(self):
        with patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"):
            mgr = SubscriptionManager()
            mgr._subscription_loop = AsyncMock()

            await mgr.start_subscription("sub1", "subscription { a }")
            await mgr.start_subscription("sub2", "subscription { b }")
            await mgr.stop_all_subscriptions()
            assert mgr.active_subscriptions == {}

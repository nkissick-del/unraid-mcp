"""Tests for the dynamic unraid://live/{action} fallback resource."""

import json
from unittest.mock import AsyncMock, patch

import pytest


class TestLiveSubscriptionFallback:
    @pytest.fixture
    def fallback_handler(self):
        from unraid_mcp.subscriptions.resources import _live_subscription_fallback

        return _live_subscription_fallback

    async def test_unknown_action_returns_error(self, fallback_handler):
        result = await fallback_handler("nonexistent_action")
        data = json.loads(result)
        assert data["error"] == "Unknown subscription action"
        assert "nonexistent_action" in data["requested"]
        assert "available" in data
        assert len(data["available"]) > 0

    async def test_known_action_calls_subscribe_once(self, fallback_handler):
        mock_data = {"systemMetricsCpu": {"percentTotal": 42.5}}
        with patch(
            "unraid_mcp.subscriptions.resources.subscribe_once",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await fallback_handler("systemMetricsCpu")
            data = json.loads(result)
            assert data == mock_data

    async def test_subscribe_once_timeout_returns_error(self, fallback_handler):
        with patch(
            "unraid_mcp.subscriptions.resources.subscribe_once",
            new_callable=AsyncMock,
            side_effect=Exception("Subscription timed out after 10s"),
        ):
            result = await fallback_handler("systemMetricsCpu")
            data = json.loads(result)
            assert "error" in data

"""Tests for middleware configuration in settings.py."""

import importlib
import os
from unittest.mock import patch


class TestMiddlewareSettings:
    """Verify middleware env vars load with correct defaults and overrides."""

    def _reload_settings(self):
        import warnings

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            return settings_mod

    def test_defaults(self):
        for k in [
            "UNRAID_MCP_RATE_LIMIT",
            "UNRAID_MCP_RATE_WINDOW_MINUTES",
            "UNRAID_MCP_MAX_RESPONSE_KB",
            "UNRAID_MCP_CACHE_TTL",
            "UNRAID_MCP_CACHE_ENABLED",
        ]:
            os.environ.pop(k, None)
        s = self._reload_settings()
        assert s.MCP_RATE_LIMIT == 540
        assert s.MCP_RATE_WINDOW_MINUTES == 1
        assert s.MCP_MAX_RESPONSE_KB == 512
        assert s.MCP_CACHE_TTL == 30
        assert s.MCP_CACHE_ENABLED is True

    def test_custom_overrides(self):
        with patch.dict(
            os.environ,
            {
                "UNRAID_MCP_RATE_LIMIT": "200",
                "UNRAID_MCP_RATE_WINDOW_MINUTES": "5",
                "UNRAID_MCP_MAX_RESPONSE_KB": "1024",
                "UNRAID_MCP_CACHE_TTL": "60",
                "UNRAID_MCP_CACHE_ENABLED": "false",
            },
        ):
            s = self._reload_settings()
            assert s.MCP_RATE_LIMIT == 200
            assert s.MCP_RATE_WINDOW_MINUTES == 5
            assert s.MCP_MAX_RESPONSE_KB == 1024
            assert s.MCP_CACHE_TTL == 60
            assert s.MCP_CACHE_ENABLED is False

    def test_cache_disabled_variants(self):
        for val in ["false", "0", "no", "False", "NO"]:
            with patch.dict(os.environ, {"UNRAID_MCP_CACHE_ENABLED": val}):
                s = self._reload_settings()
                assert s.MCP_CACHE_ENABLED is False, f"Failed for value: {val}"

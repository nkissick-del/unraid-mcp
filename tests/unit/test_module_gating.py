"""Tests for ENABLED_MODULES configuration parsing."""

import importlib
from unittest.mock import patch


class TestEnabledModulesDefault:
    def test_default_modules_when_env_not_set(self):
        """When UNRAID_MCP_ENABLED_MODULES is not set, default modules are enabled."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove the env var if set
            import os

            os.environ.pop("UNRAID_MCP_ENABLED_MODULES", None)
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            expected = frozenset(
                {
                    "system",
                    "docker",
                    "vms",
                    "storage",
                    "health",
                    "rclone",
                    "api",
                    "diagnostics",
                    "system-extra",
                    "metrics",
                    "ups",
                }
            )
            assert settings_mod.ENABLED_MODULES == expected


class TestEnabledModulesAll:
    def test_all_enables_everything(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "all"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "docker-admin" in settings_mod.ENABLED_MODULES
            assert "notifications" in settings_mod.ENABLED_MODULES
            assert "array" in settings_mod.ENABLED_MODULES
            assert "subscriptions" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "system-extra" in settings_mod.ENABLED_MODULES
            assert "metrics" in settings_mod.ENABLED_MODULES
            assert "ups" in settings_mod.ENABLED_MODULES
            assert "parity" in settings_mod.ENABLED_MODULES
            assert "docker-batch" in settings_mod.ENABLED_MODULES
            assert "notifications-extra" in settings_mod.ENABLED_MODULES
            assert "ups-admin" in settings_mod.ENABLED_MODULES

    def test_all_case_insensitive(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "ALL"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "docker-admin" in settings_mod.ENABLED_MODULES


class TestEnabledModulesCustom:
    def test_default_plus_array(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default,array"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "system" in settings_mod.ENABLED_MODULES
            assert "array" in settings_mod.ENABLED_MODULES
            assert "docker-admin" not in settings_mod.ENABLED_MODULES

    def test_minimal_set(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "system,docker"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert settings_mod.ENABLED_MODULES == frozenset({"system", "docker"})

    def test_invalid_module_ignored(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "system,nonexistent,docker"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "nonexistent" not in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "docker" in settings_mod.ENABLED_MODULES

    def test_whitespace_handling(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": " system , docker , health "}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert settings_mod.ENABLED_MODULES == frozenset({"system", "docker", "health"})

    def test_explicit_system_excludes_new_defaults(self):
        """When specifying explicit modules, new default modules are NOT included."""
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "system"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "system" in settings_mod.ENABLED_MODULES
            assert "system-extra" not in settings_mod.ENABLED_MODULES
            assert "metrics" not in settings_mod.ENABLED_MODULES
            assert "ups" not in settings_mod.ENABLED_MODULES

    def test_default_includes_phase1_modules(self):
        """The 'default' keyword includes system-extra, metrics, and ups."""
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "system-extra" in settings_mod.ENABLED_MODULES
            assert "metrics" in settings_mod.ENABLED_MODULES
            assert "ups" in settings_mod.ENABLED_MODULES

    def test_default_plus_subscriptions(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default,subscriptions"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "subscriptions" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "diagnostics" in settings_mod.ENABLED_MODULES

    def test_default_plus_parity(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default,parity"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "parity" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "docker" in settings_mod.ENABLED_MODULES


class TestPhase2ModulesDisabledByDefault:
    def test_parity_not_in_default(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "parity" not in settings_mod.ENABLED_MODULES

    def test_docker_batch_not_in_default(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "docker-batch" not in settings_mod.ENABLED_MODULES

    def test_notifications_extra_not_in_default(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "notifications-extra" not in settings_mod.ENABLED_MODULES

    def test_ups_admin_not_in_default(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "ups-admin" not in settings_mod.ENABLED_MODULES

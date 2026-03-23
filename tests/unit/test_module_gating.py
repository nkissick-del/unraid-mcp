"""Tests for ENABLED_MODULES configuration parsing."""

import importlib
from unittest.mock import patch

import pytest

from unraid_mcp.registry import MODULE_REGISTRY


class TestRegistryConsistency:
    def test_registry_keys_match_all_modules(self):
        """MODULE_REGISTRY must cover every module in _ALL_MODULES."""
        import unraid_mcp.config.settings as settings_mod

        assert set(MODULE_REGISTRY.keys()) == set(settings_mod._ALL_MODULES)


class TestEnabledModulesDefault:
    def test_default_modules_when_env_not_set(self):
        """When UNRAID_MCP_ENABLED_MODULES is not set, default modules are enabled."""
        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("UNRAID_MCP_ENABLED_MODULES", None)
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            expected = frozenset(
                {
                    "system",
                    "docker",
                    "storage",
                    "health",
                    "api",
                    "system-extra",
                    "metrics",
                    "ups",
                }
            )
            assert settings_mod.ENABLED_MODULES == expected

    def test_default_excludes_vms(self):
        """VMs are not in default — moved to extended."""
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "vms" not in settings_mod.ENABLED_MODULES

    def test_default_excludes_rclone(self):
        """RClone is not in default — moved to extended."""
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "rclone" not in settings_mod.ENABLED_MODULES

    def test_default_excludes_diagnostics(self):
        """Diagnostics is not in default — moved to extended."""
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "diagnostics" not in settings_mod.ENABLED_MODULES


class TestEnabledModulesExtended:
    def test_extended_includes_default(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "extended"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "system" in settings_mod.ENABLED_MODULES
            assert "docker" in settings_mod.ENABLED_MODULES
            assert "storage" in settings_mod.ENABLED_MODULES
            assert "health" in settings_mod.ENABLED_MODULES

    def test_extended_includes_management_modules(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "extended"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            for mod in [
                "docker-admin",
                "docker-batch",
                "notifications",
                "notifications-extra",
                "array",
                "parity",
                "plugins",
                "customization",
                "connect",
                "rclone",
                "diagnostics",
            ]:
                assert mod in settings_mod.ENABLED_MODULES, f"{mod} missing from extended"

    def test_extended_excludes_admin_modules(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "extended"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            for mod in [
                "vms",
                "onboarding",
                "docker-organize",
                "server-admin",
                "auth",
                "array-admin",
                "ups-admin",
            ]:
                assert mod not in settings_mod.ENABLED_MODULES, f"{mod} should not be in extended"

    def test_extended_plus_auth(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "extended,auth"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "auth" in settings_mod.ENABLED_MODULES
            assert "plugins" in settings_mod.ENABLED_MODULES  # still has extended


class TestEnabledModulesAll:
    def test_all_enables_everything(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "all"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "docker-admin" in settings_mod.ENABLED_MODULES
            assert "notifications" in settings_mod.ENABLED_MODULES
            assert "array" in settings_mod.ENABLED_MODULES
            assert "subscriptions" in settings_mod.ENABLED_MODULES
            assert "subscriptions-extra" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "system-extra" in settings_mod.ENABLED_MODULES
            assert "metrics" in settings_mod.ENABLED_MODULES
            assert "ups" in settings_mod.ENABLED_MODULES
            assert "parity" in settings_mod.ENABLED_MODULES
            assert "docker-batch" in settings_mod.ENABLED_MODULES
            assert "notifications-extra" in settings_mod.ENABLED_MODULES
            assert "ups-admin" in settings_mod.ENABLED_MODULES
            assert "customization" in settings_mod.ENABLED_MODULES
            assert "onboarding" in settings_mod.ENABLED_MODULES
            assert "docker-organize" in settings_mod.ENABLED_MODULES
            assert "plugins" in settings_mod.ENABLED_MODULES
            assert "server-admin" in settings_mod.ENABLED_MODULES
            assert "connect" in settings_mod.ENABLED_MODULES
            assert "auth" in settings_mod.ENABLED_MODULES
            assert "array-admin" in settings_mod.ENABLED_MODULES
            assert "vms" in settings_mod.ENABLED_MODULES

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

    def test_default_plus_parity(self):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default,parity"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "parity" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "docker" in settings_mod.ENABLED_MODULES


class TestNonDefaultModulesExcluded:
    @pytest.mark.parametrize(
        "module",
        [
            "vms",
            "rclone",
            "diagnostics",
            "parity",
            "docker-batch",
            "docker-admin",
            "notifications",
            "notifications-extra",
            "ups-admin",
            "subscriptions",
            "subscriptions-extra",
            "customization",
            "onboarding",
            "docker-organize",
            "plugins",
            "server-admin",
            "connect",
            "auth",
            "array",
            "array-admin",
        ],
    )
    def test_module_not_in_default(self, module):
        with patch.dict("os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default"}):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert module not in settings_mod.ENABLED_MODULES

    def test_default_plus_subscriptions_extra(self):
        with patch.dict(
            "os.environ", {"UNRAID_MCP_ENABLED_MODULES": "default,subscriptions-extra"}
        ):
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            assert "subscriptions-extra" in settings_mod.ENABLED_MODULES
            assert "system" in settings_mod.ENABLED_MODULES
            assert "docker" in settings_mod.ENABLED_MODULES

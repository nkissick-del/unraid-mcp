"""Tests for subscription configuration entries."""

import pytest

from unraid_mcp.subscriptions.configs import SUBSCRIPTION_CONFIGS
from unraid_mcp.subscriptions.manager import SubscriptionManager


class TestSubscriptionConfigs:
    def setup_method(self):
        self.manager = SubscriptionManager()
        self.configs = self.manager.subscription_configs

    def test_docker_stats_config_exists(self):
        assert "dockerContainerStats" in self.configs

    def test_cpu_metrics_config_exists(self):
        assert "systemMetricsCpu" in self.configs

    def test_memory_metrics_config_exists(self):
        assert "systemMetricsMemory" in self.configs

    def test_array_subscription_config_exists(self):
        assert "arraySubscription" in self.configs

    def test_all_configs_have_required_keys(self):
        required_keys = {"query", "resource", "description", "auto_start"}
        for name, config in self.configs.items():
            for key in required_keys:
                assert key in config, f"{name} missing key '{key}'"

    def test_new_configs_are_auto_start(self):
        """The 4 new subscription configs should all have auto_start=True."""
        new_subs = [
            "dockerContainerStats",
            "systemMetricsCpu",
            "systemMetricsMemory",
            "arraySubscription",
        ]
        for name in new_subs:
            assert self.configs[name]["auto_start"] is True, f"{name} should auto_start"

    def test_log_subscription_is_not_auto_start(self):
        assert self.configs["logFileSubscription"]["auto_start"] is False

    def test_resource_uris_are_unique(self):
        uris = [c["resource"] for c in self.configs.values()]
        assert len(uris) == len(set(uris)), "Duplicate resource URIs found"

    def test_queries_contain_subscription_keyword(self):
        for name, config in self.configs.items():
            assert (
                "subscription" in config["query"].lower()
            ), f"{name} query missing 'subscription' keyword"

    def test_total_subscription_count(self):
        """Should have 16 subscription configs total (5 original + 11 new)."""
        assert len(self.configs) == 16


class TestConfigsModuleConstant:
    """Tests that the extracted SUBSCRIPTION_CONFIGS matches the manager's runtime copy."""

    def test_module_constant_keys_match_manager(self):
        manager = SubscriptionManager()
        assert set(SUBSCRIPTION_CONFIGS.keys()) == set(manager.subscription_configs.keys())

    def test_manager_copy_is_independent(self):
        """Runtime mutations to manager.subscription_configs don't affect the module constant."""
        manager = SubscriptionManager()
        manager.subscription_configs["_test_key"] = {"test": True}
        assert "_test_key" not in SUBSCRIPTION_CONFIGS


class TestExtraSubscriptionConfigs:
    """Tests for the 11 new subscription configs added in Phase 3."""

    def setup_method(self):
        self.manager = SubscriptionManager()
        self.configs = self.manager.subscription_configs

    @pytest.mark.parametrize(
        "name",
        [
            "notificationAdded",
            "notificationsWarningsAndAlerts",
            "parityHistorySubscription",
            "systemMetricsTemperature",
            "notificationsOverview",
            "systemMetricsCpuTelemetry",
            "upsUpdates",
            "pluginInstallUpdates",
            "displaySubscription",
            "ownerSubscription",
            "serversSubscription",
        ],
    )
    def test_extra_subscription_exists(self, name):
        assert name in self.configs, f"Missing subscription config: {name}"

    def test_plugin_install_updates_not_auto_start(self):
        """pluginInstallUpdates is event-driven and should NOT auto-start."""
        assert self.configs["pluginInstallUpdates"]["auto_start"] is False

    @pytest.mark.parametrize(
        "name",
        [
            "notificationAdded",
            "notificationsWarningsAndAlerts",
            "parityHistorySubscription",
            "systemMetricsTemperature",
            "notificationsOverview",
            "systemMetricsCpuTelemetry",
            "upsUpdates",
            "displaySubscription",
            "ownerSubscription",
            "serversSubscription",
        ],
    )
    def test_extra_subscription_auto_start(self, name):
        """All extra subscriptions except pluginInstallUpdates should auto-start."""
        assert self.configs[name]["auto_start"] is True, f"{name} should auto_start"

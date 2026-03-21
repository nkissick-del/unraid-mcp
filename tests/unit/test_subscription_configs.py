"""Tests for subscription configuration entries."""

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
        """Should have 5 subscription configs total (1 original + 4 new)."""
        assert len(self.configs) == 5

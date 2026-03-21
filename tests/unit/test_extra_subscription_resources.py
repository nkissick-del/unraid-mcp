"""Tests for extra subscription resource registration."""

from unraid_mcp.subscriptions.manager import SubscriptionManager
from unraid_mcp.subscriptions.resources import _EXTRA_SUBSCRIPTION_RESOURCES


class TestExtraSubscriptionResources:
    def setup_method(self):
        self.manager = SubscriptionManager()
        self.configs = self.manager.subscription_configs

    def test_extra_resources_count(self):
        """Should have exactly 11 extra subscription resource entries."""
        assert len(_EXTRA_SUBSCRIPTION_RESOURCES) == 11

    def test_all_uris_match_manager_configs(self):
        """Every URI in _EXTRA_SUBSCRIPTION_RESOURCES must match a manager config."""
        manager_uris = {c["resource"] for c in self.configs.values()}
        for _sub_name, uri, _desc in _EXTRA_SUBSCRIPTION_RESOURCES:
            assert uri in manager_uris, f"URI {uri} not found in manager configs"

    def test_all_sub_names_match_manager_configs(self):
        """Every subscription name in _EXTRA_SUBSCRIPTION_RESOURCES must exist in manager."""
        for sub_name, _uri, _desc in _EXTRA_SUBSCRIPTION_RESOURCES:
            assert sub_name in self.configs, f"Subscription {sub_name} not in manager"

    def test_all_uris_follow_unraid_pattern(self):
        """All resource URIs should start with 'unraid://'."""
        for _sub_name, uri, _desc in _EXTRA_SUBSCRIPTION_RESOURCES:
            assert uri.startswith("unraid://"), f"URI {uri} doesn't follow unraid:// pattern"

    def test_descriptions_are_non_empty(self):
        """All descriptions should be non-empty strings."""
        for _sub_name, _uri, desc in _EXTRA_SUBSCRIPTION_RESOURCES:
            assert isinstance(desc, str) and len(desc) > 0, "Empty description found"

    def test_no_duplicate_uris_in_extras(self):
        """No duplicate URIs within the extra subscription resources."""
        uris = [uri for _, uri, _ in _EXTRA_SUBSCRIPTION_RESOURCES]
        assert len(uris) == len(set(uris)), "Duplicate URIs in _EXTRA_SUBSCRIPTION_RESOURCES"

    def test_no_overlap_with_base_resources(self):
        """Extra resource URIs should not overlap with the 5 base subscription URIs."""
        base_uris = {
            "unraid://logs/stream",
            "unraid://docker/stats",
            "unraid://system/cpu",
            "unraid://system/memory",
            "unraid://array/status",
        }
        extra_uris = {uri for _, uri, _ in _EXTRA_SUBSCRIPTION_RESOURCES}
        overlap = base_uris & extra_uris
        assert len(overlap) == 0, f"URIs overlap with base resources: {overlap}"

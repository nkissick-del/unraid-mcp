"""Tests for module registry structure and cache classification."""

from unraid_mcp.registry import MODULE_REGISTRY

EXPECTED_CACHEABLE = {
    "system",
    "system-extra",
    "metrics",
    "ups",
    "health",
    "storage",
    "docker",
    "api",
    "notifications",
    "notifications-extra",
    "parity",
    "diagnostics",
    "connect",
}

EXPECTED_NON_CACHEABLE = {
    "docker-admin",
    "docker-batch",
    "docker-organize",
    "array",
    "array-admin",
    "rclone",
    "server-admin",
    "plugins",
    "customization",
    "onboarding",
    "auth",
    "vms",
    "ups-admin",
}


class TestModuleRegistry:
    def test_all_entries_have_required_keys(self):
        for name, entry in MODULE_REGISTRY.items():
            assert "import" in entry, f"Module '{name}' missing 'import' key"
            assert "register" in entry, f"Module '{name}' missing 'register' key"
            assert "cacheable" in entry, f"Module '{name}' missing 'cacheable' key"
            assert isinstance(entry["cacheable"], bool)

    def test_cacheable_modules_classified_correctly(self):
        for name in EXPECTED_CACHEABLE:
            if name in MODULE_REGISTRY:
                assert MODULE_REGISTRY[name]["cacheable"] is True, f"'{name}' should be cacheable"

    def test_non_cacheable_modules_classified_correctly(self):
        for name in EXPECTED_NON_CACHEABLE:
            if name in MODULE_REGISTRY:
                assert MODULE_REGISTRY[name]["cacheable"] is False, (
                    f"'{name}' should NOT be cacheable"
                )

    def test_all_modules_classified(self):
        classified = EXPECTED_CACHEABLE | EXPECTED_NON_CACHEABLE
        resource_modules = {"subscriptions", "subscriptions-extra"}
        for name in MODULE_REGISTRY:
            assert name in classified or name in resource_modules, f"'{name}' not classified"

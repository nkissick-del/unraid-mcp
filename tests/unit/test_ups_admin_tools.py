"""Tests for UPS administration tools."""

from unraid_mcp.tools.queries.ups_admin import CONFIGURE_UPS_MUTATION


class TestUpsAdminMutationStrings:
    def test_configure_ups_has_config_variable(self):
        assert "$config" in CONFIGURE_UPS_MUTATION
        assert "UPSConfigInput" in CONFIGURE_UPS_MUTATION

    def test_configure_ups_is_valid_graphql(self):
        assert "mutation" in CONFIGURE_UPS_MUTATION
        assert "configureUps" in CONFIGURE_UPS_MUTATION

    def test_configure_ups_returns_config_fields(self):
        assert "service" in CONFIGURE_UPS_MUTATION
        assert "upsType" in CONFIGURE_UPS_MUTATION
        assert "device" in CONFIGURE_UPS_MUTATION
        assert "upsCable" in CONFIGURE_UPS_MUTATION
        assert "batteryLevel" in CONFIGURE_UPS_MUTATION

    def test_configure_ups_returns_all_expected_fields(self):
        expected_fields = [
            "service",
            "upsCable",
            "customUpsCable",
            "upsType",
            "device",
            "overrideUpsCapacity",
            "batteryLevel",
            "minutes",
            "timeout",
            "killUps",
            "nisIp",
            "netServer",
            "upsName",
            "modelName",
        ]
        for field in expected_fields:
            assert field in CONFIGURE_UPS_MUTATION, f"Missing field: {field}"

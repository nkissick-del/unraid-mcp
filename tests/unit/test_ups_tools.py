"""Tests for UPS tools query definitions and validation."""

import pytest
from graphql import parse as gql_parse

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_string_not_empty
from unraid_mcp.tools.queries.ups import (
    UPS_CONFIGURATION_QUERY,
    UPS_DEVICE_BY_ID_QUERY,
    UPS_DEVICES_QUERY,
)


class TestUpsDevicesQuery:
    def test_query_is_valid_graphql(self):
        doc = gql_parse(UPS_DEVICES_QUERY)
        assert len(doc.definitions) == 1

    def test_query_contains_name_field(self):
        assert "name" in UPS_DEVICES_QUERY

    def test_query_contains_model_field(self):
        assert "model" in UPS_DEVICES_QUERY

    def test_query_contains_status_field(self):
        assert "status" in UPS_DEVICES_QUERY

    def test_query_contains_battery_fields(self):
        assert "battery" in UPS_DEVICES_QUERY
        assert "chargeLevel" in UPS_DEVICES_QUERY
        assert "estimatedRuntime" in UPS_DEVICES_QUERY
        assert "health" in UPS_DEVICES_QUERY

    def test_query_contains_power_fields(self):
        assert "power" in UPS_DEVICES_QUERY
        assert "inputVoltage" in UPS_DEVICES_QUERY
        assert "outputVoltage" in UPS_DEVICES_QUERY
        assert "loadPercentage" in UPS_DEVICES_QUERY
        assert "nominalPower" in UPS_DEVICES_QUERY
        assert "currentPower" in UPS_DEVICES_QUERY


class TestUpsDeviceByIdQuery:
    def test_query_is_valid_graphql(self):
        doc = gql_parse(UPS_DEVICE_BY_ID_QUERY)
        assert len(doc.definitions) == 1

    def test_query_has_id_variable(self):
        assert "$id" in UPS_DEVICE_BY_ID_QUERY

    def test_query_has_string_type_variable(self):
        assert "String!" in UPS_DEVICE_BY_ID_QUERY

    def test_query_contains_battery_and_power(self):
        assert "battery" in UPS_DEVICE_BY_ID_QUERY
        assert "power" in UPS_DEVICE_BY_ID_QUERY


class TestUpsConfigurationQuery:
    def test_query_is_valid_graphql(self):
        doc = gql_parse(UPS_CONFIGURATION_QUERY)
        assert len(doc.definitions) == 1

    def test_query_contains_service_field(self):
        assert "service" in UPS_CONFIGURATION_QUERY

    def test_query_contains_ups_type_field(self):
        assert "upsType" in UPS_CONFIGURATION_QUERY

    def test_query_contains_device_field(self):
        assert "device" in UPS_CONFIGURATION_QUERY

    def test_query_contains_cable_field(self):
        assert "upsCable" in UPS_CONFIGURATION_QUERY

    def test_query_contains_shutdown_fields(self):
        assert "batteryLevel" in UPS_CONFIGURATION_QUERY
        assert "minutes" in UPS_CONFIGURATION_QUERY
        assert "timeout" in UPS_CONFIGURATION_QUERY
        assert "killUps" in UPS_CONFIGURATION_QUERY

    def test_query_contains_network_fields(self):
        assert "nisIp" in UPS_CONFIGURATION_QUERY
        assert "netServer" in UPS_CONFIGURATION_QUERY


class TestUpsDeviceValidation:
    def test_empty_device_id_raises_validation_error(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("", "device_id")

    def test_whitespace_device_id_raises_validation_error(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("   ", "device_id")

    def test_valid_device_id_passes(self):
        # Should not raise
        validate_string_not_empty("ups-1", "device_id")

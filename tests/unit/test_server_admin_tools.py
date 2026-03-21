"""Tests for server administration tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.queries.server_admin import (
    INITIATE_FLASH_BACKUP_MUTATION,
    UPDATE_SERVER_IDENTITY_MUTATION,
    UPDATE_SETTINGS_MUTATION,
    UPDATE_SSH_SETTINGS_MUTATION,
    UPDATE_SYSTEM_TIME_MUTATION,
    UPDATE_TEMPERATURE_CONFIG_MUTATION,
)
from unraid_mcp.tools.server_admin import register_server_admin_tools


class TestServerAdminMutations:
    def test_update_server_identity_mutation(self):
        assert "mutation" in UPDATE_SERVER_IDENTITY_MUTATION
        assert "$input" in UPDATE_SERVER_IDENTITY_MUTATION
        assert "updateServerIdentity" in UPDATE_SERVER_IDENTITY_MUTATION

    def test_update_ssh_settings_mutation(self):
        assert "mutation" in UPDATE_SSH_SETTINGS_MUTATION
        assert "$input" in UPDATE_SSH_SETTINGS_MUTATION
        assert "updateSshSettings" in UPDATE_SSH_SETTINGS_MUTATION

    def test_update_settings_mutation(self):
        assert "mutation" in UPDATE_SETTINGS_MUTATION
        assert "$input" in UPDATE_SETTINGS_MUTATION
        assert "updateSettings" in UPDATE_SETTINGS_MUTATION

    def test_update_temperature_config_mutation(self):
        assert "mutation" in UPDATE_TEMPERATURE_CONFIG_MUTATION
        assert "$input" in UPDATE_TEMPERATURE_CONFIG_MUTATION
        assert "updateTemperatureConfig" in UPDATE_TEMPERATURE_CONFIG_MUTATION

    def test_update_system_time_mutation(self):
        assert "mutation" in UPDATE_SYSTEM_TIME_MUTATION
        assert "$input" in UPDATE_SYSTEM_TIME_MUTATION
        assert "updateSystemTime" in UPDATE_SYSTEM_TIME_MUTATION

    def test_initiate_flash_backup_mutation(self):
        assert "mutation" in INITIATE_FLASH_BACKUP_MUTATION
        assert "initiateFlashBackup" in INITIATE_FLASH_BACKUP_MUTATION


class TestServerAdminConfirmGates:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "update_server_identity",
            "update_ssh_settings",
            "update_settings",
            "update_temperature_config",
            "update_system_time",
            "initiate_flash_backup",
        ],
    )
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self, tool_name):
        tool_fn = get_tool_fn(register_server_admin_tools, tool_name)

        if tool_name == "initiate_flash_backup":
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(confirm=False)
        else:
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(input_config={"key": "value"}, confirm=False)


class TestServerAdminInputValidation:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "update_server_identity",
            "update_ssh_settings",
            "update_settings",
            "update_temperature_config",
            "update_system_time",
        ],
    )
    @pytest.mark.asyncio
    async def test_empty_config_raises(self, tool_name):
        tool_fn = get_tool_fn(register_server_admin_tools, tool_name)
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={}, confirm=True)


class TestServerAdminToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_server_admin_tools)
        expected = {
            "update_server_identity",
            "update_ssh_settings",
            "update_settings",
            "update_temperature_config",
            "update_system_time",
            "initiate_flash_backup",
        }
        assert expected.issubset(tool_names)

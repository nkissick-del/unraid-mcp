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
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (
                UPDATE_SERVER_IDENTITY_MUTATION,
                ["mutation", "$name", "$comment", "$sysModel", "updateServerIdentity"],
            ),
            (UPDATE_SSH_SETTINGS_MUTATION, ["mutation", "$input", "updateSshSettings"]),
            (UPDATE_SETTINGS_MUTATION, ["mutation", "$input", "updateSettings"]),
            (UPDATE_TEMPERATURE_CONFIG_MUTATION, ["mutation", "$input", "updateTemperatureConfig"]),
            (UPDATE_SYSTEM_TIME_MUTATION, ["mutation", "$input", "updateSystemTime"]),
            (INITIATE_FLASH_BACKUP_MUTATION, ["mutation", "initiateFlashBackup"]),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


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

"""Tests for Connect administration tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.connect_admin import register_connect_admin_tools
from unraid_mcp.tools.queries.connect_admin import (
    CONNECT_SIGN_IN_MUTATION,
    CONNECT_SIGN_OUT_MUTATION,
    ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION,
    GET_CLOUD_INFO_QUERY,
    GET_CONNECT_INFO_QUERY,
    GET_REMOTE_ACCESS_QUERY,
    SETUP_REMOTE_ACCESS_MUTATION,
    UPDATE_API_SETTINGS_MUTATION,
)


class TestConnectAdminQueries:
    def test_get_connect_info_query(self):
        assert "query" in GET_CONNECT_INFO_QUERY
        assert "connect" in GET_CONNECT_INFO_QUERY

    def test_connect_info_has_expected_fields(self):
        assert "dynamicRemoteAccess" in GET_CONNECT_INFO_QUERY
        assert "settings" in GET_CONNECT_INFO_QUERY
        assert "dataSchema" in GET_CONNECT_INFO_QUERY

    def test_get_remote_access_query(self):
        assert "query" in GET_REMOTE_ACCESS_QUERY
        assert "remoteAccess" in GET_REMOTE_ACCESS_QUERY

    def test_remote_access_has_expected_fields(self):
        assert "accessType" in GET_REMOTE_ACCESS_QUERY
        assert "forwardType" in GET_REMOTE_ACCESS_QUERY
        assert "port" in GET_REMOTE_ACCESS_QUERY

    def test_get_cloud_info_query(self):
        assert "query" in GET_CLOUD_INFO_QUERY
        assert "cloud" in GET_CLOUD_INFO_QUERY

    def test_cloud_info_has_expected_fields(self):
        assert "error" in GET_CLOUD_INFO_QUERY
        assert "apiKey" in GET_CLOUD_INFO_QUERY
        assert "relay" in GET_CLOUD_INFO_QUERY


class TestConnectAdminMutations:
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (UPDATE_API_SETTINGS_MUTATION, ["mutation", "$input", "updateApiSettings"]),
            (CONNECT_SIGN_IN_MUTATION, ["mutation", "$input", "connectSignIn"]),
            (CONNECT_SIGN_OUT_MUTATION, ["mutation", "connectSignOut"]),
            (SETUP_REMOTE_ACCESS_MUTATION, ["mutation", "$input", "setupRemoteAccess"]),
            (
                ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION,
                ["mutation", "$input", "enableDynamicRemoteAccess"],
            ),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


class TestConnectAdminConfirmGates:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "update_api_settings",
            "connect_sign_in",
            "connect_sign_out",
            "setup_remote_access",
            "enable_dynamic_remote_access",
        ],
    )
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self, tool_name):
        tool_fn = get_tool_fn(register_connect_admin_tools, tool_name)

        if tool_name == "connect_sign_out":
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(confirm=False)
        else:
            with pytest.raises(ToolError, match="confirm must be True"):
                await tool_fn(input_config={"key": "value"}, confirm=False)


class TestConnectAdminInputValidation:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "update_api_settings",
            "connect_sign_in",
            "setup_remote_access",
            "enable_dynamic_remote_access",
        ],
    )
    @pytest.mark.asyncio
    async def test_empty_config_raises(self, tool_name):
        tool_fn = get_tool_fn(register_connect_admin_tools, tool_name)
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={}, confirm=True)


class TestConnectAdminToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_connect_admin_tools)
        expected = {
            "get_connect_info",
            "get_remote_access",
            "get_cloud_info",
            "update_api_settings",
            "connect_sign_in",
            "connect_sign_out",
            "setup_remote_access",
            "enable_dynamic_remote_access",
        }
        assert expected.issubset(tool_names)

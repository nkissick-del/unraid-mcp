"""Tests for Connect administration tools."""

import pytest

from unraid_mcp.core.exceptions import ToolError
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
        assert "status" in GET_CONNECT_INFO_QUERY
        assert "signedIn" in GET_CONNECT_INFO_QUERY
        assert "username" in GET_CONNECT_INFO_QUERY

    def test_get_remote_access_query(self):
        assert "query" in GET_REMOTE_ACCESS_QUERY
        assert "remoteAccess" in GET_REMOTE_ACCESS_QUERY

    def test_remote_access_has_expected_fields(self):
        assert "enabled" in GET_REMOTE_ACCESS_QUERY
        assert "url" in GET_REMOTE_ACCESS_QUERY
        assert "port" in GET_REMOTE_ACCESS_QUERY

    def test_get_cloud_info_query(self):
        assert "query" in GET_CLOUD_INFO_QUERY
        assert "cloud" in GET_CLOUD_INFO_QUERY

    def test_cloud_info_has_expected_fields(self):
        assert "status" in GET_CLOUD_INFO_QUERY
        assert "apiKey" in GET_CLOUD_INFO_QUERY


class TestConnectAdminMutations:
    def test_update_api_settings_mutation(self):
        assert "mutation" in UPDATE_API_SETTINGS_MUTATION
        assert "$input" in UPDATE_API_SETTINGS_MUTATION
        assert "updateApiSettings" in UPDATE_API_SETTINGS_MUTATION

    def test_connect_sign_in_mutation(self):
        assert "mutation" in CONNECT_SIGN_IN_MUTATION
        assert "$input" in CONNECT_SIGN_IN_MUTATION
        assert "connectSignIn" in CONNECT_SIGN_IN_MUTATION

    def test_connect_sign_out_mutation(self):
        assert "mutation" in CONNECT_SIGN_OUT_MUTATION
        assert "connectSignOut" in CONNECT_SIGN_OUT_MUTATION

    def test_setup_remote_access_mutation(self):
        assert "mutation" in SETUP_REMOTE_ACCESS_MUTATION
        assert "$input" in SETUP_REMOTE_ACCESS_MUTATION
        assert "setupRemoteAccess" in SETUP_REMOTE_ACCESS_MUTATION

    def test_enable_dynamic_remote_access_mutation(self):
        assert "mutation" in ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION
        assert "$input" in ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION
        assert "enableDynamicRemoteAccess" in ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION


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
        from fastmcp import FastMCP

        from unraid_mcp.tools.connect_admin import register_connect_admin_tools

        test_mcp = FastMCP("test")
        register_connect_admin_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == tool_name:
                tool_fn = tool.fn
                break

        assert tool_fn is not None, f"{tool_name} tool not registered"

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
        from fastmcp import FastMCP

        from unraid_mcp.tools.connect_admin import register_connect_admin_tools

        test_mcp = FastMCP("test")
        register_connect_admin_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == tool_name:
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={}, confirm=True)


class TestConnectAdminToolRegistration:
    def test_all_tools_registered(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.connect_admin import register_connect_admin_tools

        test_mcp = FastMCP("test")
        register_connect_admin_tools(test_mcp)

        tool_names = set(test_mcp._tool_manager._tools.keys())
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

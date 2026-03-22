"""Tests for plugin management tools."""

import pytest

from tests.helpers import get_registered_tool_names, get_tool_fn
from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.plugins import register_plugins_tools
from unraid_mcp.tools.queries.plugins import (
    ADD_PLUGIN_MUTATION,
    GET_PLUGIN_INSTALL_OPERATION_QUERY,
    INSTALL_PLUGIN_MUTATION,
    LIST_INSTALLED_UNRAID_PLUGINS_QUERY,
    LIST_PLUGIN_INSTALL_OPERATIONS_QUERY,
    LIST_PLUGINS_QUERY,
    REMOVE_PLUGIN_MUTATION,
)


class TestPluginQueries:
    def test_list_plugins_query(self):
        assert "query" in LIST_PLUGINS_QUERY
        assert "plugins" in LIST_PLUGINS_QUERY

    def test_list_plugins_has_expected_fields(self):
        assert "name" in LIST_PLUGINS_QUERY
        assert "version" in LIST_PLUGINS_QUERY
        assert "status" in LIST_PLUGINS_QUERY

    def test_list_installed_plugins_query(self):
        assert "query" in LIST_INSTALLED_UNRAID_PLUGINS_QUERY
        assert "installedUnraidPlugins" in LIST_INSTALLED_UNRAID_PLUGINS_QUERY

    def test_get_plugin_install_operation_query(self):
        assert "query" in GET_PLUGIN_INSTALL_OPERATION_QUERY
        assert "$operationId" in GET_PLUGIN_INSTALL_OPERATION_QUERY
        assert "pluginInstallOperation" in GET_PLUGIN_INSTALL_OPERATION_QUERY

    def test_list_plugin_install_operations_query(self):
        assert "query" in LIST_PLUGIN_INSTALL_OPERATIONS_QUERY
        assert "pluginInstallOperations" in LIST_PLUGIN_INSTALL_OPERATIONS_QUERY


class TestPluginMutations:
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (ADD_PLUGIN_MUTATION, ["mutation", "$input", "PluginManagementInput", "addPlugin"]),
            (
                REMOVE_PLUGIN_MUTATION,
                ["mutation", "$input", "PluginManagementInput", "removePlugin"],
            ),
            (INSTALL_PLUGIN_MUTATION, ["mutation", "$input", "PluginManagementInput", "addPlugin"]),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


class TestPluginConfirmGates:
    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            ("add_plugin", {"url": "https://example.com/plugin.plg", "confirm": False}),
            ("remove_plugin", {"name": "test-plugin", "confirm": False}),
            ("install_plugin", {"url": "https://example.com/plugin.plg", "confirm": False}),
        ],
    )
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self, tool_name, kwargs):
        tool_fn = get_tool_fn(register_plugins_tools, tool_name)
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(**kwargs)


class TestPluginInputValidation:
    @pytest.mark.asyncio
    async def test_get_operation_empty_id_raises(self):
        tool_fn = get_tool_fn(register_plugins_tools, "get_plugin_install_operation")
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(operation_id="")


class TestPluginToolRegistration:
    def test_all_tools_registered(self):
        tool_names = get_registered_tool_names(register_plugins_tools)
        expected = {
            "list_plugins",
            "list_installed_unraid_plugins",
            "get_plugin_install_operation",
            "list_plugin_install_operations",
            "add_plugin",
            "remove_plugin",
            "install_plugin",
        }
        assert expected.issubset(tool_names)

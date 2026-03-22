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
    def test_add_plugin_mutation(self):
        assert "mutation" in ADD_PLUGIN_MUTATION
        assert "$input" in ADD_PLUGIN_MUTATION
        assert "PluginManagementInput" in ADD_PLUGIN_MUTATION
        assert "addPlugin" in ADD_PLUGIN_MUTATION

    def test_remove_plugin_mutation(self):
        assert "mutation" in REMOVE_PLUGIN_MUTATION
        assert "$input" in REMOVE_PLUGIN_MUTATION
        assert "PluginManagementInput" in REMOVE_PLUGIN_MUTATION
        assert "removePlugin" in REMOVE_PLUGIN_MUTATION

    def test_install_plugin_mutation(self):
        assert "mutation" in INSTALL_PLUGIN_MUTATION
        assert "$input" in INSTALL_PLUGIN_MUTATION
        assert "PluginManagementInput" in INSTALL_PLUGIN_MUTATION
        assert "addPlugin" in INSTALL_PLUGIN_MUTATION


class TestAddPluginConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = get_tool_fn(register_plugins_tools, "add_plugin")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(url="https://example.com/plugin.plg", confirm=False)


class TestRemovePluginConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = get_tool_fn(register_plugins_tools, "remove_plugin")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(name="test-plugin", confirm=False)


class TestInstallPluginConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        tool_fn = get_tool_fn(register_plugins_tools, "install_plugin")
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(url="https://example.com/plugin.plg", confirm=False)


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

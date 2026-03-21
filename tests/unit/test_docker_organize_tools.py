"""Tests for Docker organization tools."""

import pytest

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.queries.docker_organize import (
    CREATE_DOCKER_FOLDER_MUTATION,
    CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION,
    DELETE_DOCKER_ENTRIES_MUTATION,
    MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION,
    MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION,
    REFRESH_DOCKER_DIGESTS_MUTATION,
    RENAME_DOCKER_FOLDER_MUTATION,
    RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION,
    SET_DOCKER_FOLDER_CHILDREN_MUTATION,
    SYNC_DOCKER_TEMPLATE_PATHS_MUTATION,
    UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION,
)


class TestDockerOrganizeMutations:
    def test_create_folder_mutation(self):
        assert "mutation" in CREATE_DOCKER_FOLDER_MUTATION
        assert "$name" in CREATE_DOCKER_FOLDER_MUTATION
        assert "createFolder" in CREATE_DOCKER_FOLDER_MUTATION

    def test_set_folder_children_mutation(self):
        assert "mutation" in SET_DOCKER_FOLDER_CHILDREN_MUTATION
        assert "$folderId" in SET_DOCKER_FOLDER_CHILDREN_MUTATION
        assert "$children" in SET_DOCKER_FOLDER_CHILDREN_MUTATION

    def test_delete_entries_mutation(self):
        assert "mutation" in DELETE_DOCKER_ENTRIES_MUTATION
        assert "$ids" in DELETE_DOCKER_ENTRIES_MUTATION
        assert "deleteEntries" in DELETE_DOCKER_ENTRIES_MUTATION

    def test_move_entries_to_folder_mutation(self):
        assert "mutation" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION
        assert "$folderId" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION
        assert "$entryIds" in MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION

    def test_move_items_to_position_mutation(self):
        assert "mutation" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION
        assert "$itemIds" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION
        assert "$position" in MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION

    def test_rename_folder_mutation(self):
        assert "mutation" in RENAME_DOCKER_FOLDER_MUTATION
        assert "$folderId" in RENAME_DOCKER_FOLDER_MUTATION
        assert "$name" in RENAME_DOCKER_FOLDER_MUTATION

    def test_create_folder_with_items_mutation(self):
        assert "mutation" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION
        assert "$name" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION
        assert "$itemIds" in CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION

    def test_update_view_preferences_mutation(self):
        assert "mutation" in UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION
        assert "$input" in UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION

    def test_sync_template_paths_mutation(self):
        assert "mutation" in SYNC_DOCKER_TEMPLATE_PATHS_MUTATION
        assert "syncTemplatePaths" in SYNC_DOCKER_TEMPLATE_PATHS_MUTATION

    def test_reset_template_mappings_mutation(self):
        assert "mutation" in RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION
        assert "resetTemplateMappings" in RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION

    def test_refresh_digests_mutation(self):
        assert "mutation" in REFRESH_DOCKER_DIGESTS_MUTATION
        assert "refreshDigests" in REFRESH_DOCKER_DIGESTS_MUTATION


class TestDeleteDockerEntriesConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "delete_docker_entries":
                tool_fn = tool.fn
                break

        assert tool_fn is not None, "delete_docker_entries tool not registered"
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(ids=["entry1"], confirm=False)

    @pytest.mark.asyncio
    async def test_confirm_default_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "delete_docker_entries":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(ids=["entry1"])


class TestResetTemplateMappingsConfirmGate:
    @pytest.mark.asyncio
    async def test_confirm_false_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "reset_docker_template_mappings":
                tool_fn = tool.fn
                break

        assert tool_fn is not None, "reset_docker_template_mappings tool not registered"
        with pytest.raises(ToolError, match="confirm must be True"):
            await tool_fn(confirm=False)


class TestDockerOrganizeInputValidation:
    @pytest.mark.asyncio
    async def test_create_folder_empty_name_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "create_docker_folder":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(name="")

    @pytest.mark.asyncio
    async def test_set_folder_children_empty_id_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "set_docker_folder_children":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="non-empty string"):
            await tool_fn(folder_id="", children=["a"])

    @pytest.mark.asyncio
    async def test_view_preferences_empty_config_raises(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_fn = None
        for tool in test_mcp._tool_manager._tools.values():
            if tool.name == "update_docker_view_preferences":
                tool_fn = tool.fn
                break

        assert tool_fn is not None
        with pytest.raises(ToolError, match="non-empty dictionary"):
            await tool_fn(input_config={})


class TestDockerOrganizeToolRegistration:
    def test_all_tools_registered(self):
        from fastmcp import FastMCP

        from unraid_mcp.tools.docker_organize import register_docker_organize_tools

        test_mcp = FastMCP("test")
        register_docker_organize_tools(test_mcp)

        tool_names = set(test_mcp._tool_manager._tools.keys())
        expected = {
            "create_docker_folder",
            "set_docker_folder_children",
            "delete_docker_entries",
            "move_docker_entries_to_folder",
            "move_docker_items_to_position",
            "rename_docker_folder",
            "create_docker_folder_with_items",
            "update_docker_view_preferences",
            "sync_docker_template_paths",
            "reset_docker_template_mappings",
            "refresh_docker_digests",
        }
        assert expected.issubset(tool_names)
